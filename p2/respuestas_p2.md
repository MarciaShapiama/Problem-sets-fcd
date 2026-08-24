# Problem Set 1 — Parte 2
## Entendimiento de los datos: la variable RESULT y sus implicancias metodológicas

**Curso:** Fundamentos de Ciencia de Datos

---

## 1. Tratamiento de valores faltantes en la variable `result` y su impacto metodológico

### 1.1. ¿Cómo altera esto nuestro problema?

Cuando una vivienda seleccionada en el marco muestral de la ENAHO registra un resultado distinto de encuesta completa o incompleta (vivienda desocupada, hogar ausente o rechazo del informante), el operativo de campo se interrumpe antes de iniciar los módulos posteriores al Módulo 1. Esto genera una ausencia estructural y no aleatoria de información en dichos módulos. Metodológicamente, esta circunstancia altera de manera sustancial el problema: no se trata de un escenario de datos faltantes susceptible de resolverse mediante técnicas de imputación estadística convencionales bajo los supuestos de aleatoriedad completa (*MCAR*) o aleatoriedad condicionada a variables observadas (*MAR*). Se trata, en cambio, de un mecanismo de **selección determinista**, en el que la ausencia de información constituye precisamente el fenómeno que el modelo busca predecir. En consecuencia, cualquier variable derivada de módulos posteriores al Módulo 1 no puede emplearse como predictor, dado que dicha variable no existe —por diseño— para la población de interés (los hogares con no respuesta).

Al calcular la distribución real de la variable `RESULT` para el período 2019–2025 a partir de los siete archivos del Módulo 1, se observa un patrón que refuerza este argumento y que, adicionalmente, revela un problema metodológico adicional no mencionado en el enunciado del PS1.

![Evolución de las categorías de RESULT, 2019-2025](evolucion_result_2019_2025.png)

*Nota.* Elaboración propia a partir de los archivos `Enaho01-{año}-100.csv` (Módulo 1) correspondientes a los años 2019 a 2025. El cuadro completo de porcentajes se encuentra en `porcentaje_no_respuesta_por_anio.csv`.

El hallazgo más relevante de este gráfico no es la magnitud de la no respuesta en un año determinado, sino la anomalía del año 2020: la categoría "Otro" pasa de representar entre el 11 % y el 13 % del total en años normales a un **28,7 %** en 2020, mientras que la categoría "Completa" cae de aproximadamente 66 % a 58 %. Esta discontinuidad no debe interpretarse como una variación sustantiva del fenómeno de no respuesta, sino como evidencia de un **cambio de instrumento de medición** asociado a la pandemia: es razonable inferir que el protocolo de campo del INEI durante 2020 —con restricciones de movilidad y probables adaptaciones del cuestionario o del criterio de codificación— generó una proporción inusualmente alta de casos que los encuestadores no pudieron clasificar dentro de las categorías estándar (rechazo, ausencia, vivienda desocupada) y que, por tanto, quedaron registrados como "Otro". Cualquier modelo de no respuesta que incluya el año 2020 sin una variable de control específica para dicho período corre el riesgo de confundir un artefacto de medición con una señal predictiva genuina, en línea con la advertencia general planteada en la Parte 1 de este documento respecto de la variabilidad metodológica del INEI entre 2019 y 2025.

### 1.2. ¿Cuáles son las variables que podemos utilizar?

Dado que la información del hogar no existe para las unidades no encuestadas, el modelo predictivo debe construirse exclusivamente a partir de variables estructurales, geográficas y de gestión de campo registradas en el Módulo 1 (Carátula) durante el primer contacto, con independencia del resultado final de la entrevista. Estas incluyen:

- **Ubicación geográfica:** departamento, provincia y distrito, derivados de `ubigeo`.
- **Estrato geográfico** (`estrato`): permite distinguir áreas urbanas (categorías 1 a 5) de áreas rurales (categorías 6 en adelante).
- **Dominio geográfico** (`dominio`): permite construir la variable de región natural (Costa, Sierra, Selva, Lima Metropolitana).
- **Variables de gestión de campo:** mes y trimestre de ejecución (`mes`), tipo de selección del conglomerado (`tipenc`).
- **Variable panel** (`panel`): indica si el hogar fue entrevistado el año anterior. Como se documenta en la sección 3 de este documento, esta variable presenta el poder predictivo individual más alto de todas las disponibles en el Módulo 1.

### 1.3. ¿Podemos utilizar el Módulo 2?

**No.** El Módulo 2 recopila las características demográficas de los residentes del hogar y únicamente se levanta cuando la entrevista se completó exitosamente. En consecuencia, las viviendas con no respuesta (desocupadas, con rechazo o con ausencia del informante) no cuentan con registros en dicho módulo. Emplear variables del Módulo 2 como predictores implicaría la eliminación por listas (*listwise deletion*) de la totalidad de la población objetivo que el modelo busca anticipar, lo cual invalida por completo el ejercicio predictivo. Esta restricción confirma, desde una perspectiva empírica, uno de los puntos centrales discutidos en la Parte 1 de este trabajo: el "entendimiento de los datos" en este proyecto no puede tratarse como una fase neutral de exploración, dado que la propia estructura de disponibilidad de los datos está determinada por la variable que se pretende predecir.

---

## 2. El hallazgo más relevante del Módulo 1: el efecto de la variable PANEL

Si bien el enunciado del PS1 no solicita explícitamente el cálculo de esta relación, un análisis crítico de los datos disponibles en el Módulo 1 revela que la variable `PANEL` constituye, con amplio margen, el predictor individual más informativo de la no respuesta entre todas las variables disponibles antes del contacto con el hogar.

![Tasa de no respuesta según la variable PANEL](tasa_no_respuesta_panel.png)

*Nota.* Elaboración propia a partir de los archivos transformados `enaho_transformado_2024.csv` y `enaho_transformado_2025.csv`, mediante el cruce de las variables `target` y `panel`.

Los hogares que fueron entrevistados el año anterior (`panel = 1`) presentan una tasa de no respuesta de **1,7 %** en 2024 y **1,3 %** en 2025, mientras que los hogares nuevos (sin valor registrado en `panel`) presentan una tasa de **30,8 %** en 2024 y **31,0 %** en 2025. La diferencia es de un orden de magnitud aproximado de dieciocho veces. Esta relación resulta consistente con lo señalado en la Parte 1 de este trabajo respecto de la variable `PANEL`: los hogares panel han superado un proceso de contacto y colaboración previo con el INEI, lo cual reduce sustancialmente las probabilidades de rechazo, ausencia o vivienda desocupada en la ronda siguiente. Dicho de otro modo, gran parte de la varianza que el modelo busca explicar no proviene de las características socioeconómicas ni geográficas del hogar, sino de su historial de contacto con la propia institución encuestadora, una variable de naturaleza esencialmente distinta a las utilizadas habitualmente en modelos de no respuesta basados exclusivamente en características estructurales del hogar.

Esta relación tiene, además, una implicancia práctica directa para la fase de modelado de la Parte 2 del proyecto: omitir `PANEL` del conjunto de predictores no solo reduce el desempeño del modelo, sino que puede generar una interpretación errónea de la importancia relativa de las demás variables (geográficas, temporales), dado que estas podrían absorber parcialmente el efecto de una variable panel omitida si ambas se encuentran correlacionadas con el diseño muestral.

---

## 3. Un patrón geográfico contraintuitivo: la Sierra frente a la Selva

El cruce de la variable `target` con la región natural, calculado a partir de los archivos transformados de 2024 y 2025, muestra un patrón que contradice el supuesto —razonable a priori— de que la mayor dispersión geográfica y las mayores dificultades de acceso físico determinan la mayor no respuesta.

![Tasa de no respuesta por región natural](tasa_no_respuesta_region.png)

*Nota.* Elaboración propia a partir de `resumen_no_respuesta_2024.csv` y `resumen_no_respuesta_2025.csv`.

La Sierra presenta la tasa de no respuesta más alta de las cuatro regiones (27,6 % en 2024 y 27,7 % en 2025), superando incluso a Lima Metropolitana (26,6 % y 26,0 %, respectivamente). La Selva, pese a ser la región con mayores restricciones objetivas de acceso —dispersión poblacional, distancias fluviales, menor cobertura vial—, presenta la tasa más baja de las cuatro regiones (21,9 % y 21,4 %). Este resultado sugiere que la no respuesta en la ENAHO no está determinada principalmente por el costo logístico de acceso físico a la vivienda, sino por otros mecanismos —posiblemente relacionados con patrones de movilidad laboral, composición urbana de los centros poblados de la Sierra, o con la proporción de hogares nuevos (no panel) en cada región— que no pueden identificarse únicamente a partir de la variable de región natural. Esta observación constituye una razón adicional, complementaria a la discutida en la Parte 1 de este documento, para no asumir que el "costo de visitar" mencionado en el enunciado del PS1 es equivalente a la distancia geográfica: ambos conceptos pueden estar débilmente correlacionados, y un modelo que solo capture proximidad geográfica dejaría sin explicar buena parte de la varianza observada en la Sierra.

---

## 4. Conclusiones de la fase de entendimiento de datos

- La no respuesta en la ENAHO corresponde a un mecanismo de selección determinista y no a un problema de datos faltantes aleatorios, lo cual descarta el uso de variables del Módulo 2 como predictores y de técnicas de imputación convencionales para tratar la variable objetivo.
- La distribución de `RESULT` presenta una discontinuidad clara en 2020, atribuible a un cambio en el protocolo de campo durante la pandemia y no a una variación sustantiva del fenómeno; esta discontinuidad debe controlarse explícitamente en cualquier modelo que incluya dicho año.
- La variable `PANEL` constituye el predictor individual más informativo disponible en el Módulo 1, con una diferencia de aproximadamente dieciocho veces en la tasa de no respuesta entre hogares panel y hogares nuevos, y debe incorporarse como variable de control obligatoria en la fase de modelado.
- El patrón geográfico de no respuesta no resulta explicado por la accesibilidad física de la región, dado que la Sierra —de menor dispersión relativa que la Selva— presenta la tasa más alta de las cuatro regiones naturales.

---

## Referencias

Instituto Nacional de Estadística e Informática. (2024). *Encuesta Nacional de Hogares (ENAHO) 2024 "Condiciones de vida y pobreza": Manual del encuestador* (Doc. ENAHO 08.01). https://proyectos.inei.gob.pe/iinei/srienaho/Descarga/DocumentosMetodologicos/2024-55/13_Manual_del_Encuestador.pdf

Instituto Nacional de Estadística e Informática. (2024). *Encuesta Nacional de Hogares (ENAHO) 2024: Diccionario de variables, módulo 100*. https://proyectos.inei.gob.pe/iinei/srienaho/Descarga/DocumentosMetodologicos/2024-55/20_Diccionario_2024.pdf
