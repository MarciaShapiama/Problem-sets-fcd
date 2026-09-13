<div align="right">
  <img src="assets/inei_logo.png" width="130" alt="Logo INEI">
</div>

# Indicadores Sociodemográficos, Censo 2017 Amazonas

**Curso:** Fundamentos de Ciencia de Datos
**Docente:** Carla Solis Uehara
**Alumna:** Marcia Shapiama De La Cruz
**Fecha:** Setiembre 2026

---

## Índice

1. [Introducción](#introducción)
2. [Estructura del proyecto](#estructura-del-proyecto)
3. [Cómo funciona](#cómo-funciona)
4. [1. Niños sin desagüe por red pública](#1-niños-de-0-a-5-años-sin-desagüe-por-red-pública)
5. [2. Afiliación a seguro de salud por grupo etario](#2-afiliación-a-seguro-de-salud-por-grupo-etario)
6. [3. Tasa de empleo](#3-tasa-de-empleo-15-64-años)
7. [Extra: resumen de indicadores](#extra-resumen-de-indicadores)
8. [Cómo usarlo](#cómo-usarlo)
9. [Resultados obtenidos](#resultados-obtenidos)

---

## Introducción

Cálculo de 3 indicadores sociodemográficos para la región Amazonas. Se usan los microdatos del Censo 2017 (INEI) de vivienda y población, y DuckDB para las consultas SQL.

## Estructura del proyecto

```text
Problem Set 4/
│
├── cpv2017_viv01.dta   <- microdato de vivienda (Amazonas)
├── cpv2017_pob01.dta   <- microdato de población (Amazonas)
├── indicadores.py       <- clase CensoAmazonas con los 3 indicadores
└── README.md
```

| Archivo | Para qué sirve |
|---|---|
| `cpv2017_viv01.dta` | Microdato de vivienda del Censo 2017 para Amazonas (código de departamento 01). |
| `cpv2017_pob01.dta` | Microdato de población del Censo 2017 para Amazonas. |
| `indicadores.py` | Define la clase `CensoAmazonas`. Carga los `.dta`, valida las columnas, y tiene un método por cada indicador. |

## Cómo funciona

Los `.dta` se leen directamente con `pandas` y `pyreadstat`, y se registran como tablas en DuckDB con `con.register()`. No se pasa antes por Parquet: para el tamaño de estos archivos no hace falta ese paso intermedio, y así no queda una carpeta `data/` generada de más.

```text
.dta (pandas)  --con.register()-->  DuckDB en memoria  --SQL-->  resultado
```

Las queries usan `COUNT(*) FILTER (WHERE ...)` para los conteos condicionales, en vez de `SUM(CASE WHEN ...)`. Es la sintaxis propia de DuckDB y queda más corta.

Todas parten de la misma base: un `JOIN` entre `poblacion` y `vivienda` por `id_viv_imp_f`, filtrando solo viviendas con `c2_p2 = 1` (ocupada, con personas presentes), como pide el enunciado.

## 1. Niños de 0 a 5 años sin desagüe por red pública

`indicador_desague_ninos()` calcula el porcentaje de niños de 0 a 5 años (`c5_p4_1` entre 0 y 5) en viviendas cuyo servicio higiénico (`c2_p10`) no es red pública, ni dentro ni fuera de la vivienda (códigos 1 y 2). Cualquier otro código cuenta como sin red pública: pozo séptico, letrina, pozo ciego, río, campo abierto, etc.

## 2. Afiliación a seguro de salud por grupo etario

`indicador_afiliacion_seguro()` arma 5 grupos etarios a partir de `c5_p4_1`: `0-5`, `5-15`, `15-35`, `35-65`, `65+`. Los intervalos son cerrados por la izquierda y abiertos por la derecha, salvo el último grupo.

Calcula el porcentaje de personas afiliadas a algún seguro de salud. Basta que una de estas columnas sea 1: SIS (`c5_p8_1`), EsSalud (`c5_p8_2`), seguro de FFAA o Policial (`c5_p8_3`), seguro privado (`c5_p8_4`), u otro (`c5_p8_5`).

## 3. Tasa de empleo (15-64 años)

`indicador_tasa_empleo()` calcula la tasa de empleo sobre la población en edad de trabajar (`c5_p4_1` entre 15 y 64). Cuenta como ocupado quien trabajó por algún pago la semana pasada (`c5_p16 = 1`). También cuenta quien no trabajó esa semana pero cae en alguna de estas categorías de `c5_p17`:

| Código `c5_p17` | Categoría |
|---|---|
| 1 | No trabajó pero tenía trabajo |
| 2 | Tiene negocio propio al que volver |
| 3 | Trabajo ocasional (cachuelo) por pago |
| 4 | Labores en chacra o crianza de animales |
| 5 | Ayudó en la tienda o negocio de un familiar |

## Extra: resumen de indicadores

`resumen()` no lo pide el enunciado. Junta el número principal de cada indicador, más el detalle por grupo etario del segundo, en una sola tabla lista para pegar en un informe.

También se agregó una validación al cargar los datos. Si a algún `.dta` le falta una columna necesaria (por ejemplo, si se usa por error el archivo de otro departamento), el programa avisa de inmediato con un mensaje claro, en vez de fallar más adelante con un error de SQL difícil de rastrear.

## Cómo usarlo

Requisitos:

```bash
pip install pandas pyreadstat duckdb
```

Coloca `cpv2017_viv01.dta` y `cpv2017_pob01.dta` en la misma carpeta que `indicadores.py`, y corre:

```bash
python indicadores.py
```

O usa la clase directamente:

```python
from indicadores import CensoAmazonas

censo = CensoAmazonas("cpv2017_viv01.dta", "cpv2017_pob01.dta")
censo.indicador_desague_ninos()
censo.indicador_afiliacion_seguro()
censo.indicador_tasa_empleo()
censo.resumen()
```

## Resultados obtenidos

Sobre los microdatos de Amazonas: 139,328 viviendas y 379,384 personas.

| Indicador | Resultado |
|---|---|
| % niños 0-5 sin desagüe por red pública | 62.23% (29,166 de 46,870) |
| Tasa de empleo (15-64 años) | 52.00% (113,747 de 218,733) |
| % afiliación a seguro, 0-5 años | 93.52% |
| % afiliación a seguro, 5-15 años | 93.16% |
| % afiliación a seguro, 15-35 años | 82.82% |
| % afiliación a seguro, 35-65 años | 82.90% |
| % afiliación a seguro, 65+ años | 84.03% |
