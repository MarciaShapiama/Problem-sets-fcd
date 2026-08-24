"""
=============================================================================
SCRIPT DE FILTRADO DE VARIABLES - ENAHO Módulo 1 (2019 - 2025)
=============================================================================

"""

import os
import pandas as pd

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN Y RUTAS DE TRABAJO
# -----------------------------------------------------------------------------
# Único parámetro que debe cambiarse al trasladar el script a otra máquina.
ruta_datos = "C:/Users/YENNY/Desktop/PROYECTOS INEI/problem-sets-fcd/"
ruta_salida = os.path.join(ruta_datos, "problem-set-1", "p2")
os.makedirs(ruta_salida, exist_ok=True)

anios = range(2019, 2026)

# -----------------------------------------------------------------------------
# 2. VARIABLES SELECCIONADAS
# -----------------------------------------------------------------------------
# Justificación (sección 1.2 de ENTENDIMIENTODELOSDATOS.md):
# - año, mes, conglome, vivienda, hogar: identificadores de la unidad muestral
#   y de la ronda de recolección.
# - dominio, ubigeo, estrato: variables geográficas, disponibles para el
#   100% de las viviendas visitadas (con o sin respuesta).
# - periodo, tipenc: variables de gestión de campo / diseño muestral.
# - panel: indica si el hogar fue entrevistado el año anterior; es el
#   predictor individual más informativo identificado en este trabajo
#   (ver sección 2 de ENTENDIMIENTODELOSDATOS.md).
# - result: variable a partir de la cual se construye la variable objetivo
#   'target' en la fase de transformación.
variables_filtrar = [
    "año", "mes", "conglome", "vivienda", "hogar",
    "dominio", "ubigeo", "estrato", "periodo", "tipenc",
    "panel", "result",
]

# -----------------------------------------------------------------------------
# 3. BUCLE DE LECTURA, FILTRADO Y GUARDADO POR AÑO
# -----------------------------------------------------------------------------
resumen_filtrado = []

for anio in anios:
    archivo = os.path.join(ruta_datos, f"Enaho01-{anio}-100.csv")

    if not os.path.exists(archivo):
        print(f"Advertencia: no se encontró el archivo del año {anio}. Se omite.")
        continue

    try:
        df = pd.read_csv(archivo, encoding="latin-1", sep=None, engine="python")
    except Exception as e:
        print(f"Advertencia: no se pudo leer el archivo del año {anio}: {e}")
        continue

    df.columns = df.columns.str.lower()

    # Nos quedamos solo con las variables seleccionadas que efectivamente
    # existan en el archivo de ese año (por robustez ante cambios de
    # nomenclatura entre años, documentados en la Parte 1 de este trabajo).
    columnas_disponibles = [c for c in variables_filtrar if c in df.columns]
    columnas_faltantes = [c for c in variables_filtrar if c not in df.columns]

    if columnas_faltantes:
        print(f"Año {anio}: no se encontraron las columnas {columnas_faltantes} (se omiten).")

    df_filtrado = df[columnas_disponibles].copy()

    archivo_salida = os.path.join(ruta_salida, f"enaho_filtrado_{anio}.csv")
    df_filtrado.to_csv(archivo_salida, index=False)

    resumen_filtrado.append({
        "anio": anio,
        "n_hogares": len(df_filtrado),
        "n_variables": len(columnas_disponibles),
    })
    print(f"Año {anio}: {len(df_filtrado)} hogares, {len(columnas_disponibles)} variables -> {archivo_salida}")

# -----------------------------------------------------------------------------
# 4. RESUMEN FINAL
# -----------------------------------------------------------------------------
if resumen_filtrado:
    df_resumen = pd.DataFrame(resumen_filtrado)
    ruta_resumen = os.path.join(ruta_salida, "resumen_filtrado_por_anio.csv")
    df_resumen.to_csv(ruta_resumen, index=False)
    print("\n=========================================================")
    print("FILTRADO COMPLETADO PARA TODOS LOS AÑOS DISPONIBLES")
    print("=========================================================")
    print(df_resumen.to_string(index=False))
else:
    print("Error crítico: no se procesó ningún archivo. Verifique la ubicación de los CSV.")
