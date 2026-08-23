# Análisis Crítico: La Plataforma Michelangelo de Uber a través de CRISP-DM y el Modelo de Trayectorias (DST)

## 1. Introducción y Marco Teórico de Partida
La conceptualización de los proyectos de analítica de datos y Machine Learning ha evolucionado desde metodologías tradicionales orientadas a procesos secuenciales hasta arquitecturas de ingeniería a escala industrial. Para evaluar críticamente este tránsito, la literatura académica establece un contraste fundamental entre el estándar clásico **CRISP-DM** (*Cross-Industry Standard Process for Data Mining*), formulado por Wirth (2000), y las revisiones contemporáneas que abordan las trayectorias reales de la ciencia de datos, como el marco **DST** (*Data Science Trajectories*) propuesto por Martínez-Plumed et al. (2019). Este análisis se enmarca en la comprensión de cómo plataformas hiperescalares, tal es el caso de **Michelangelo** en Uber (Uber Engineering, 2017, 2024), replican o desafían estos marcos teóricos, un dilema metodológico que adquiere matices particulares al contrastarse con las limitaciones estructurales y de infraestructura del entorno socioeconómico peruano.

---

## 2. Aspectos de la Plataforma Michelangelo Enmarcados en CRISP-DM (Wirth, 2000)
El modelo CRISP-DM de Wirth (2000) estructuró el ciclo de vida del análisis de datos en seis fases interconectadas: Comprensión del negocio, Comprensión de los datos, Preparación de los datos, Modelado, Evaluación y Despliegue (*Deployment*). Al examinar la arquitectura de la plataforma Michelangelo de Uber (Uber Engineering, 2017), se advierte que los componentes operativos de mayor madurez dentro de esta infraestructura se alinean de manera directa con las dos fases finales del modelo clásico:

* **La Fase de Despliegue (*Deployment*) a Escala Masiva:** En la formulación de Wirth (2000), el despliegue representa la etapa donde los resultados del modelo se traducen en acciones operativas o de negocio. Michelangelo institucionaliza esta fase mediante la estandarización de microservicios y contenedores automatizados que permiten empaquetar modelos predictivos para su consumo masivo tanto en tiempo real (*online prediction service*) como por lotes (*batch*), resolviendo la tradicional fricción entre el entorno de desarrollo y el de producción (Uber Engineering, 2017).
* **La Fase de Evaluación (*Evaluation*) Continua:** Mientras que CRISP-DM concibe la evaluación como un hito previo al pase a producción para verificar el cumplimiento de los objetivos de negocio (Wirth, 2000), Michelangelo amplía este concepto incorporando sistemas automatizados de monitoreo en tiempo real que supervisan el rendimiento del modelo en producción, detectando de manera temprana la degradación predictiva o la deriva de los datos (*data drift*) (Uber Engineering, 2024).

![Esquema Comparativo CRISP-DM vs DST](michelangelo_crispdm_vs_dst.png)

---

## 3. Limitaciones de CRISP-DM y Perspectiva desde el Paper de Martínez-Plumed et al. (2019)
A pesar de la utilidad analítica de CRISP-DM para identificar hitos de despliegue y evaluación en Michelangelo, la revisión crítica realizada por Martínez-Plumed et al. (2019) demuestra que el modelo estático de Wirth (2000) resulta insuficiente para capturar la complejidad y el dinamismo de los sistemas de inteligencia artificial modernos:

* **De la Linealidad Secuencial al Espacio de Trayectorias de Datos (*Data Science Trajectories*):** CRISP-DM plantea un flujo semicircular y ordenado. Sin embargo, como argumentan Martínez-Plumed et al. (2019), la ciencia de datos contemporánea opera mediante trayectorias abiertas, exploratorias e iterativas donde la fase de preparación de datos y el modelado no ocurren de forma aislada, sino de manera concurrente a través de componentes centrales de infraestructura como los almacenes centralizados de características (*Feature Stores*) descritos en la evolución de Michelangelo (Uber Engineering, 2024).
* **La Infraestructura, el MLOps y la Deuda Técnica Oculta:** El trabajo de Martínez-Plumed et al. (2019) enfatiza que los marcos tradicionales omiten los costos masivos de la ingeniería de software y la gestión de infraestructura distribuida. Michelangelo no es meramente un conjunto de modelos predictivos, sino una plataforma integral de MLOps que orquesta pipelines complejos de macrodatos (Apache Spark, Kafka, HDFS, Cassandra), control de versiones y reentrenamiento automatizado, dimensiones completamente ausentes en la concepción original de Wirth (2000).

![Gráfico de Severidad ENAHO](enaho_severidad_critica.png)

---

## 4. Contraste Crítico con la Realidad Institucional e Infraestructural del Perú
Contrastar los postulados de CRISP-DM (Wirth, 2000), las trayectorias de Martínez-Plumed et al. (2019) y la sofisticación arquitectónica de Michelangelo (Uber Engineering, 2017, 2024) frente a la coyuntura del **Perú** expone profundas asimetrías estructurales:

* **Incompatibilidad de Infraestructura y Brecha Digital:** Mientras que Michelangelo presupone un ecosistema tecnológico hiperescalar con conectividad de alta velocidad y almacenamiento distribuido, el tejido empresarial peruano —dominado ampliamente por micro y pequeñas empresas (MYPEs)— y gran parte de la administración pública operan en un nivel de madurez rudimentario, sustentado en hojas de cálculo locales, ausencia de gobernanza de datos y una conectividad geográfica fragmentada que imposibilita la adopción de flujos MLOps automatizados.
* **El Colapso Institucional en la Fase de Datos:** Tanto CRISP-DM como los modelos de trayectorias asumen un estándar mínimo de calidad y formalidad en los datos. En un país donde la informalidad laboral supera sistemáticamente el 70% (Instituto Nacional de Estadística e Informática [INEI], 2025) y los registros institucionales arrastran sesgos y omisiones históricas, las fases iniciales de entendimiento y preparación de datos colapsan, demostrando que los retos analíticos en economías periféricas son fundamentalmente de índole socioinstitucional y no meramente técnicos.

---

## 5. Propuestas de Mejora Metodológica y Gobernanza
Para conciliar la rigurosidad de los marcos teóricos con las restricciones operativas de realidades como la peruana, se plantean las siguientes líneas de mejora:
1. **Contextualización Institucional del Ciclo del Dato:** Integrar variables sociodemográficas y de informalidad en las fases iniciales de comprensión del negocio para evitar la aplicación ciega de marcos diseñados para economías formalizadas.
2. **Arquitecturas Modulares de Bajo Costo:** Fomentar el desarrollo de pipelines analíticos basados en tecnologías de código abierto (*open source*) adaptadas a restricciones presupuestarias y de infraestructura local, distanciándose de la dependencia exclusiva de nubes hiperescalares inalcanzables.
3. **Gobernanza Cívica y Auditoría de Sesgos:** Institucionalizar protocolos de evaluación ética de datos para impedir que los modelos predictivos automaticen y amplifiquen las desigualdades estructurales preexistentes en el sector público o financiero nacional.

---

## 6. Conclusiones
1. **Alineación operativa parcial:** Los componentes de Michelangelo que encajan en CRISP-DM (Wirth, 2000) se restringen estrictamente a las fases finales de evaluación continua y despliegue automatizado a escala industrial (Uber Engineering, 2017, 2024).
2. **Insuficiencia metodológica estructural:** Tal como evidencian Martínez-Plumed et al. (2019), CRISP-DM resulta un marco estático e insuficiente para explicar la complejidad dinámica, iterativa y distribuida de las plataformas modernas basadas en MLOps.
3. **Condicionamiento periférico:** La implementación de estos paradigmas en el Perú se ve severamente limitada por la precariedad de la infraestructura y la informalidad institucional del entorno.

---

## 7. Referencias Bibliográficas (Formato APA)
* Instituto Nacional de Estadística e Informática [INEI]. (2025). *Producción y empleo nacional: Informe técnico sobre la informalidad laboral y dinámica empresarial en el Perú*. Lima, Perú: INEI.
* Martínez-Plumed, F., Contreras-Ochando, L., Sempere-FileLine, A., Ferri, C., Hernández-Orallo, J., & Ramírez-Quintana, M. J. (2019). CRISP-DM twenty years later: From data mining processes to data science trajectories. *ACM Computing Surveys (CSUR)*, 52(6), 1-35. https://doi.org/10.1145/3350764
* Uber Engineering. (2017). *Michelangelo: Uber’s Machine Learning Platform*. Uber Engineering Blog. Recuperado de https://www.uber.com/blog/michelangelo-machine-learning-platform/
* Uber Engineering. (2024). *Scaling and Evolving Michelangelo: The Next Generation of Machine Learning at Uber*. Uber Engineering Blog.
* Wirth, R. (2000). CRISP-DM: Towards a standard process model for data mining. *Proceedings of the 4th International Conference on the Practical Application of Knowledge Discovery and Data Mining*, 29-39.