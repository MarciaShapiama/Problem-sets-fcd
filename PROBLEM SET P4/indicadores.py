"""
Problem Set 4 - Indicadores sociodemográficos, Amazonas (Censo 2017)

Clase CensoAmazonas: carga los microdatos de vivienda y población,
y calcula los 3 indicadores que pide el enunciado.
"""

import pandas as pd
import pyreadstat
import duckdb


class CensoAmazonas:
    """
    Encapsula la conexión a DuckDB y los 3 indicadores del Censo 2017
    para la región Amazonas.

    Los .dta se leen con pandas y se registran directamente como
    tablas en DuckDB, con con.register(). No se pasa antes por
    Parquet. Para el tamaño de estos archivos no hace falta ese paso
    intermedio.
    """

    def __init__(self, ruta_vivienda: str, ruta_poblacion: str):
        self.con = duckdb.connect()
        self._cargar_datos(ruta_vivienda, ruta_poblacion)

    def _cargar_datos(self, ruta_vivienda: str, ruta_poblacion: str) -> None:
        viv, _ = pyreadstat.read_dta(ruta_vivienda, encoding="latin1")
        pob, _ = pyreadstat.read_dta(ruta_poblacion, encoding="latin1")

        # Validación básica: si faltan las columnas que se necesitan,
        # mejor fallar aquí mismo con un mensaje claro que dejar que
        # las queries de más abajo truenen con un error críptico de SQL.
        columnas_requeridas_viv = {"id_viv_imp_f", "c2_p2", "c2_p10"}
        columnas_requeridas_pob = {
            "id_viv_imp_f", "c5_p4_1",
            "c5_p8_1", "c5_p8_2", "c5_p8_3", "c5_p8_4", "c5_p8_5",
            "c5_p16", "c5_p17",
        }
        faltantes_viv = columnas_requeridas_viv - set(viv.columns)
        faltantes_pob = columnas_requeridas_pob - set(pob.columns)
        if faltantes_viv:
            raise ValueError(f"Faltan columnas en vivienda: {faltantes_viv}")
        if faltantes_pob:
            raise ValueError(f"Faltan columnas en población: {faltantes_pob}")

        self.con.register("vivienda", viv)
        self.con.register("poblacion", pob)

        self.n_viviendas = len(viv)
        self.n_personas = len(pob)

    # ------------------------------------------------------------
    # Indicador 1: % de niños de 0 a 5 años sin desagüe por red pública
    # ------------------------------------------------------------
    def indicador_desague_ninos(self) -> pd.DataFrame:
        """
        % de niños de 0 a 5 años en hogares cuyo baño no está
        conectado a la red pública de desagüe. Solo sobre viviendas
        con personas presentes.

        c2_p10 en (1, 2) son las dos categorías de red pública:
        dentro de la vivienda, o fuera pero dentro de la edificación.
        Cualquier otro valor cuenta como sin red pública: pozo
        séptico, letrina, río, campo abierto, etc.
        """
        return self.con.sql("""
            SELECT
                COUNT(*) AS total_ninos_0_5,
                COUNT(*) FILTER (WHERE v.c2_p10 NOT IN (1, 2)) AS ninos_sin_red_publica,
                ROUND(
                    100.0 * COUNT(*) FILTER (WHERE v.c2_p10 NOT IN (1, 2)) / COUNT(*),
                2) AS pct_sin_red_publica
            FROM poblacion p
            JOIN vivienda v ON p.id_viv_imp_f = v.id_viv_imp_f
            WHERE v.c2_p2 = 1
              AND p.c5_p4_1 BETWEEN 0 AND 5
        """).df()

    # ------------------------------------------------------------
    # Indicador 2: % de afiliación a seguro de salud por grupo etario
    # ------------------------------------------------------------
    def indicador_afiliacion_seguro(self) -> pd.DataFrame:
        """
        % de afiliación a algún seguro de salud (SIS, EsSalud, FFAA/
        Policial, privado, u otro), por grupo etario. Intervalos
        cerrados por la izquierda, abiertos por la derecha, salvo el
        último grupo.
        """
        return self.con.sql("""
            SELECT
                grupo_etario,
                COUNT(*) AS total_personas,
                COUNT(*) FILTER (WHERE afiliado = 1) AS total_afiliados,
                ROUND(100.0 * AVG(afiliado), 2) AS pct_afiliacion
            FROM (
                SELECT
                    CASE
                        WHEN c5_p4_1 >= 0  AND c5_p4_1 < 5  THEN '0-5'
                        WHEN c5_p4_1 >= 5  AND c5_p4_1 < 15 THEN '5-15'
                        WHEN c5_p4_1 >= 15 AND c5_p4_1 < 35 THEN '15-35'
                        WHEN c5_p4_1 >= 35 AND c5_p4_1 < 65 THEN '35-65'
                        ELSE '65+'
                    END AS grupo_etario,
                    CASE
                        WHEN c5_p4_1 >= 0  AND c5_p4_1 < 5  THEN 1
                        WHEN c5_p4_1 >= 5  AND c5_p4_1 < 15 THEN 2
                        WHEN c5_p4_1 >= 15 AND c5_p4_1 < 35 THEN 3
                        WHEN c5_p4_1 >= 35 AND c5_p4_1 < 65 THEN 4
                        ELSE 5
                    END AS orden_grupo,
                    CASE WHEN c5_p8_1 = 1 OR c5_p8_2 = 1 OR c5_p8_3 = 1
                              OR c5_p8_4 = 1 OR c5_p8_5 = 1 THEN 1 ELSE 0 END AS afiliado
                FROM poblacion p
                JOIN vivienda v ON p.id_viv_imp_f = v.id_viv_imp_f
                WHERE v.c2_p2 = 1
            ) sub
            GROUP BY grupo_etario, orden_grupo
            ORDER BY orden_grupo
        """).df()

    # ------------------------------------------------------------
    # Indicador 3: tasa de empleo (población de 15 a 64 años)
    # ------------------------------------------------------------
    def indicador_tasa_empleo(self) -> pd.DataFrame:
        """
        Tasa de empleo sobre población en edad de trabajar (15-64).

        Cuenta como ocupado quien trabajó por pago (c5_p16 = 1).
        También cuenta quien no trabajó esa semana pero cae en
        alguna categoría de c5_p17 que el enunciado considera
        empleo: 1 no trabajó pero tenía trabajo, 2 negocio propio,
        3 cachuelo, 4 chacra o crianza, 5 ayudó en negocio familiar.
        """
        return self.con.sql("""
            WITH base AS (
                SELECT p.*
                FROM poblacion p
                JOIN vivienda v ON p.id_viv_imp_f = v.id_viv_imp_f
                WHERE v.c2_p2 = 1
                  AND p.c5_p4_1 BETWEEN 15 AND 64
            )
            SELECT
                COUNT(*) AS total_pet,
                COUNT(*) FILTER (
                    WHERE c5_p16 = 1 OR c5_p17 IN (1, 2, 3, 4, 5)
                ) AS total_ocupados,
                ROUND(
                    100.0 * COUNT(*) FILTER (
                        WHERE c5_p16 = 1 OR c5_p17 IN (1, 2, 3, 4, 5)
                    ) / COUNT(*),
                2) AS tasa_empleo
            FROM base
        """).df()

    # ------------------------------------------------------------
    # Extra: resumen de los 3 indicadores en una sola tabla
    # ------------------------------------------------------------
    def resumen(self) -> pd.DataFrame:
        """
        Junta el porcentaje principal de cada indicador en una sola
        tabla, útil para pegar directo en el informe o en el README.
        No lo pide el enunciado, pero facilita revisar los 3
        resultados de un vistazo.
        """
        ind1 = self.indicador_desague_ninos()
        ind2 = self.indicador_afiliacion_seguro()
        ind3 = self.indicador_tasa_empleo()

        filas = [
            {
                "indicador": "% niños 0-5 sin desagüe por red pública",
                "valor": ind1["pct_sin_red_publica"].iloc[0],
                "n": int(ind1["total_ninos_0_5"].iloc[0]),
            },
            {
                "indicador": "Tasa de empleo (15-64 años)",
                "valor": ind3["tasa_empleo"].iloc[0],
                "n": int(ind3["total_pet"].iloc[0]),
            },
        ]
        for _, fila in ind2.iterrows():
            filas.append({
                "indicador": f"% afiliación a seguro, grupo {fila['grupo_etario']}",
                "valor": fila["pct_afiliacion"],
                "n": int(fila["total_personas"]),
            })

        return pd.DataFrame(filas)


if __name__ == "__main__":
    censo = CensoAmazonas("cpv2017_viv01.dta", "cpv2017_pob01.dta")

    print(f"Viviendas cargadas: {censo.n_viviendas:,}")
    print(f"Personas cargadas: {censo.n_personas:,}")

    print("\n=== 1. % niños 0-5 sin desagüe por red pública ===")
    print(censo.indicador_desague_ninos())

    print("\n=== 2. % afiliación a seguro por grupo etario ===")
    print(censo.indicador_afiliacion_seguro())

    print("\n=== 3. Tasa de empleo (15-64 años) ===")
    print(censo.indicador_tasa_empleo())

    print("\n=== Resumen ===")
    print(censo.resumen())
