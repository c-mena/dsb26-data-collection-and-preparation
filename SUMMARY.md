# Resumen del Proyecto

## 1. Introducción y Justificación de Herramientas

Este proyecto aborda el proceso completo de recolección, limpieza, transformación y análisis inicial de datos para un ecommerce minorista ficticio. Para llevar a cabo estas tareas, se emplearon las bibliotecas **NumPy** y **Pandas** debido a sus características complementarias y a su excepcional integración y compatibilidad con una gran variedad de otras bibliotecas del ecosistema de Python:

- **NumPy:** Se optó por NumPy para la generación de datos simulados debido a su eficiencia y rendimiento en la ejecución de operaciones matemáticas sobre arreglos de grandes dimensiones. Su base fundamentada en C permite simular grandes volúmenes numéricos y realizar operaciones matemáticas de manera eficiente.
- **Pandas:** Una vez conformados los arreglos básicos por NumPy, Pandas resulta fundamental para la manipulación analítica estructurada. Aporta representaciones de tipo DataFrame, alineamiento óptimo de datos, gestión nativa de fechas/tiempos y múltiples funciones integradas para agregación, limpieza, y filtrado, dotando de contexto y flexibilidad a los vectores generados.

## 2. Descripción del Dataset Generado y Fuentes Externas

Se generaron tres bases de datos simuladas y correlacionadas para representar la operación histórica anual de una tienda de tecnología:

- **Clientes:** 600 registros con perfiles realistas. Contiene identificadores, nombres, ubicación por ciudad, fechas de nacimiento, y la cuota de recurrencia en compras.
- **Productos:** Catálogo con más de 100 artículos tecnológicos divididos en categorías. Integra valoraciones de precio de venta (CLP) y costo base en divisa extranjera (USD), además de la fecha de compra.
- **Transacciones:** Historial de ventas para el periodo general 2025, vinculando dinámicamente clientes con el portafolio de productos, inyectando variabilidad mediante aplicación de descuentos aleatorios y fechas específicas de operación comercial.

**Simulación de inconsistencias ("Ensuciado" de datos):**
Para crear un escenario de limpieza realista y exigente, se alteró deliberadamente la integridad de los DataFrames generados (tal como se describe en las secciones 1.2 y 1.3 del notebook). Esto incluyó la inyección de registros duplicados idénticos en transacciones, la generación de valores extremos en distintos vectores, manteniendo la integridad de los datos, y la inyección estratégica de valores nulos (vacíos) en las fechas de nacimiento del vector de clientes.

**Fuentes externas integradas:**
Dado que los costos de adquisición de productos del inventario asumen haber sido establecidos originariamente en USD durante el año 2024, se recurrió a la integración externa vía Web Scraping. Para ello, se obtuvo exitosamente la tabla estructurada del valor del dólar oficial promedio para cada día del año consumiendo el portal oficial del Servicio de Impuestos Internos (SII).

## 3. Técnicas de Limpieza y Transformación Exploradas

- **Manejo de Valores Nulos:** Frente a los valores ausentes detectados en las fechas de nacimiento, y tras comprobar la muy leve desviación sobre la media y la varianza, respecto a la simple eliminación, se procedió a **imputar** estos usando la mediana de la edad del total de registros válidos, priorizando una mayor muestra de usuarios.
- **Detección de Outliers (Valores Atípicos):** Se emplearon metodologías cruzadas de límites estadísticos: uso de Rango Intercuartílico (**IQR**), valorado por su robustez frente a colas asimétricas presentes en facturaciones y volúmenes (asimetría derecha), y **Z-Score**, usado para evaluar posibles fronteras de outliers en distribuciones de índole más gaussianas como resulta ser la edad.
- **Adecuación de Series Temporales:** Creación de tabla de cruce de consulta ("lookup") vectorizada para consumir la tasa de cambio del dólar, la que fue moldeada utilizando métodos paramétricos de repetición contigua de valores pasados/futuros (*Forward/Backward fill*). Al hacerlo, se mitigó el impacto por huecos nulos originados de los cierres operativos en fines de semana y festivos presentes en los datos del SII.
- **Optimización de Escala o Memoria (Downcasting):** Transformación de tipos de datos en cada uno de los vectores numéricos, disminuyendo óptimamente la precisión de los mismos (`int64 -> int16 / int8` y `float64 -> float32`), traduciéndose en mejoras superiores al 30% en el consumo real en disco/ram.

## 4. Principales Decisiones y Desafíos

- **El reto de simular la realidad:** La generación y depuración de un conjunto de tablas que, no solo tuviese interrelación, sino que reflejara lógicas de mercados consistentes (volúmenes de venta por perfil socioeconómico, asimetría razonable en canastas, descuentos realistas), conllevó cruzar restricciones y probar reiteradamente antes de asentar los scripts de la primera etapa.
- **Iteración Dinámica del Flujo de Procesos:** El flujo de trabajo preestablecido de manera secuencial para una pauta de 6 fases demostró carecer de flexibilidad. Frecuentemente, transformar o detectar irregularidades generó ramificaciones para las que hubiese sido más conveniente un cambio de orden. Quedó de manifiesto empíricamente que el orden idóneo varía en base a los hallazgos exploratorios, necesitando rebobinar y correr la limpieza en cascada a medida que se construyen nuevas dimensiones compuestas.

## 5. Conclusiones y Estado Final

Al finalizar las etapas de procesamiento, se obtuvo un dataset definitivo que representa una evolución técnica respecto a los datos agrupados iniciales.

El resultado es un dataframe optimizado para procesos de modelado. El set de datos pasó de un estado bruto (con redundancias y cronologías difíciles de interpretar) a uno compuesto por variables útiles para el análisis. A continuación, se detallan las mejoras estructurales aplicadas y consolidadas en el archivo final ("*6_final_df.parquet*"):

1. **Transformación de fechas nominales en métricas de interpretación directa:** Se erradicó la dependencia a fechas estáticas como `ClientBirthdate` (transformada en `ClientAge` y posteriormente en la categoría etaria `ClientAgeGroup`), `TxnDate` (traducido a un factor `TxnDateIsWeekend` para perfilar hábitos), y `ProdPurchaseDate` (relegado por la dimensión funcional `ProdInventoryHoldTime`, la cual muestra los días transcurridos hasta la venta del producto o *permanencia en estantería*).
2. **Evolución desde contadores estáticos hacia métricas de acumulación:** Las variables de registro total que se repetían indistintamente por transacción (`ClientPurchases` y `ClientTotalPaid`) entregaban sólo la la información final estática. Éstas fueron refinadas mediante un proceso iterativo de suma construyendo paso a paso `ClientPurchasesAccum` y `ClientTotalPaidAccum`. Estas cantidades entregan información histórica, indicando el ciclo temporal escalonado en el que se concretó cada transacción para cada cliente.
3. **Estandarización monetaria final y cruce de utilidad:** El registro de costo en divisa extranjera inicial (`ProdCostUSD`) se integró a moneda local mediante el histórico cambiario, produciendo la homologada `ProdCostCLP`, la que junto al precio de venta (`ProdPriceCLP`) permitió calcular una métrica fundamental para el análisis de desempeño transaccional: la utilidad bruta (`GrossProfit`).

Desde la perspectiva general de ejecución, se extraen las siguientes conclusiones de valor para proyectos futuros:

1. **El Contexto del Negocio por Sobre los Outliers Estadísticos:** Es fundamental validar de forma cualitativa los valores atípicos ("outliers") antes de eliminarlos o filtrarlos. No basta con aplicar umbrales matemáticos; se debe verificar si estos valores son realmente errores. En contextos comerciales o financieros, cifras muy altas o compras muy frecuentes pueden no ser anomalías, sino representar de forma legítima a clientes mayoristas.
2. **El Riesgo de Sesgo al Unir Tablas (Granularidad):** Se debe tener cuidado al calcular indicadores sobre un DataFrame donde se han fusionado múltiples fuentes. Por ejemplo, al unir datos de clientes con cada transacción, la información biográfica (como la edad) se repite por cada compra, lo que distorsiona enormemente el cálculo de promedios (como se demostró en la Sección 4.2.11). Por ello, el nivel de agrupación adecuado (por *Cliente Único*, por *Producto*, o por *Transacción*) dependerá exclusivamente de lo que se busque responder en el análisis.
3. **Definición Temprana de los Objetivos del Análisis:** Las tareas de selección, limpieza y creación de nuevas variables (columnas derivadas) no serán efectivas si no se establecen los objetivos del análisis desde el principio. Los indicadores específicos que se deben calcular nacen directamente de esta planificación inicial.
4. **Transformación Analítica de Fechas a Métricas Numéricas:** Se evidenció la conveniencia y necesidad de transformar la información cronológica (registros de fecha y tiempo) en métricas numéricas derivadas, como edad o días transcurridos. Este enfoque no solo facilita enormemente la interpretación del comportamiento, sino que resulta virtualmente obligatorio a fin de posibilitar su procesamiento fluido en modelos y algoritmos analíticos de ciencia de datos vinculados al machine learning.
5. **Lectura Anticipada de Fechas:** Se comprobó que es una gran ventaja técnica definir explícitamente qué columnas representan fechas desde el momento en que se cargan los archivos de datos (por ejemplo, especificando `parse_dates=` al leer un archivo CSV). Esto previene problemas de compatibilidad y facilita la aplicación posterior de funciones cronológicas directas.
