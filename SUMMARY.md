# Resumen del Proyecto: Obtención y Preparación de Datos

## 1. Introducción y Justificación de Herramientas

Este proyecto aborda el proceso completo de recolección, limpieza, transformación y análisis inicial de datos para un ecommerce minorista ficticio. Para llevar a cabo estas tareas, se emplearon las bibliotecas **NumPy** y **Pandas** debido a sus características complementarias:

- **NumPy:** Se optó por NumPy para la generación de datos simulados debido a su eficiencia y rendimiento en la ejecución de operaciones matemáticas sobre grandes arreglos. Su base fundamentada en C permite simular grandes volúmenes numéricos y aplicar eficientemente distribuciones estadísticas probabilísticas.
- **Pandas:** Una vez conformados los arreglos básicos por NumPy, Pandas resulta fundamental para la manipulación analítica estructurada. Aporta representaciones de tipo DataFrame, alineamiento óptimo de datos, gestión nativa de fechas/tiempos y múltiples funciones integradas para agregación, limpieza, y filtrado, dotando de contexto y flexibilidad a los vectores generados.

## 2. Descripción del Dataset Generado y Fuentes Externas

Se generaron tres bases de datos simuladas y correlacionales para representar la operación histórica anual de una tienda de tecnología:

- **Clientes:** 600 registros con perfiles realistas. Contiene identificadores, nombres, ubicación por ciudad, fechas de nacimiento, y la cuota de recurrencia en compras.
- **Productos:** Catálogo de artículos tecnológicos divididos en categorías como Periféricos y Monitores, entre otros. Integra valoraciones de precio de venta (CLP) y costo base en divisa extranjera (USD), además de la fecha de compra.
- **Transacciones:** Historial de ventas para el periodo general 2025, vinculando dinámicamente clientes con el portafolio de productos, inyectando variabilidad mediante aplicación de descuentos aleatorios y fechas específicas de operación comercial.

**Fuentes externas integradas:**
Dado que los costos de adquisición de productos del inventario asumen haber sido establecidos originariamente en USD durante el año 2024, resultó esencial recurrir a la integración externa vía Web Scraping. Para ello, se obtuvo exitosamente la tabla estructurada del valor del dólar oficial promedio para cada día del año consumiendo el portal oficial del **Servicio de Impuestos Internos (SII)**.

## 3. Técnicas de Limpieza y Transformación Exploradas

- **Manejo de Valores Nulos:** Se identificaron valores ausentes inyectados estratégicamente en fechas de nacimiento. Tras comprobar la muy leve desviación sobre la media y la varianza, se procedió a **imputar** estos usando la mediana de la edad del total de registros válidos resguardando el volumen de retención útil sobre la muestra de usuarios.
- **Detección de Outliers (Valores Atípicos):** Se emplearon iterativamente metodologías cruzadas de límites estadísticos: uso de Rango Intercuartílico (**IQR**) valorado por su robustez frente a colas asimétricas presentes en facturaciones y volúmenes (asimetría derecha), y **Z-Score** usado para evaluar posibles fronteras de anomalías en distribuciones de índoles más referenciales/gaussianas como la edad.
- **Adecuación de Series Temporales:** Creación de tablas de cruce de consulta ("lookup") vectorizada para consumir la tasa de cambio del dólar, la que fue moldeada utilizando métodos paramétricos de repetición contigua de valores pasados/futuros (*Forward/Backward fill*). Al hacerlo, se mitigó el impacto por huecos nulos originados de los cierres operativos en fines de semana y festivos durante el cruce aduanero frente a los perfiles del SII.  
- **Optimización de Escala o Memoria (Downcasting):** Transformación de tipos de datos en cada uno de los vectores numéricos disminuyendo óptimamente la precisión de los mismos (`int64 -> int16 / int8` y `float64 -> float32`), traduciéndose en mejoras superiores al 30% en el consumo real en disco/ram.

## 4. Principales Decisiones y Desafíos

- **El reto de simular la realidad:** La generación y depuración de un conjunto de tablas que, no solo tuviese interrelación, sino que reflejara lógicas de mercados consistentes (volúmenes de venta por perfil socioeconómico, asimetría razonable en canastas, descuentos realistas), conllevó cruzar restricciones y probar reiteradamente antes de asentar los scripts de la primera etapa.
- **Iteración Dinámica del Flujo de Procesos:** El flujo de trabajo preestablecido de manera secuencial para una pauta de 6 fases demostró carecer de flexibilidad. Frecuentemente, transformar o detectar irregularidades generó ramificaciones para las que hubiese sido más conveniente un cambio de orden. Quedó de manifiesto empíricamente que el orden idóneo varía en base a los hallazgos exploratorios, necesitando rebobinar y correr la limpieza en cascada a medida que se construyen nuevas dimensiones compuestas.

## 5. Conclusiones y Estado Final

Al cierre de la secuencia de iteraciones proyectadas, se consiguió consolidar y preservar el corazón analítico en un dataset final que representa una evolución sustancial respecto a la matriz original de datos agrupados.

El dataframe unificado consolidó un estado final mucho más pulido e idóneo para procesos de modelado y agregación estadística. Pasó de su conformación bruta original, llena de registros redundantes sin historial intermedio y con fechas superpuestas de limitada interpretación, hacia la construcción de potentes variables funcionales listas para el análisis transversal. Los desarrollos y cambios estructurales más significativos alcanzados sobre el set definitivo ("*6_final_df.parquet*") son:

1. **Transformación de fechas nominales en métricas de interpretación directa:** Se erradicó por completo la dependencia a fechas estáticas como `ClientBirthdate` (transformada en `ClientAge` y posteriormente en la categoría etaria `ClientAgeGroup`), `TxnDate` (traducido a un factor `TxnDateIsWeekend` para perfilar hábitos), y `ProdPurchaseDate` (relegado completamente por la dimensión funcional `ProdInventoryHoldTime`, la cual muestra fehacientemente los días transcurridos hasta la venta del producto o *permanencia en estantería*).
2. **Evolución desde contadores estáticos hacia métricas de acumulación:** Las variables de registro total que se repetían indistintamente por transacción (`ClientPurchases` y `ClientTotalPaid`) entregaban sólo la estampa general estática. Éstas fueron refinadas mediante un proceso iterativo de suma construyendo paso a paso `ClientPurchasesAccum` y `ClientTotalPaidAccum`. Estas contabilidades entregan tracción histórica indicando el ciclo evolutivo escalonado en el se gestó cada transacción puntual para cada cliente.
3. **Estandarización monetaria final y cruce de utilidad:** Lo que inicialmente era un simple registro en divisa extranjera (`ProdCostUSD`) se integró a moneda local mediante el histórico cambiario, entregando la homologada `ProdCostCLP`, facilitando crear en conjunción al precio público (`ProdPriceCLP`) la métrica rectora sobre desempeño transaccional: el Margen o `GrossProfit` absoluto.

Desde la perspectiva general de ejecución, se extraen formalmente las siguientes conclusiones de valor para proyectos venideros:

1. **La Condición de Negocio Sobre La Condición del Outlier:** Se determinó taxativamente la trascendencia de validar cualitativamente los llamados  \"Outliers Estadísticos\". Previo a marginar estos valores anómalos o aplicar filtros normalizadores por sobre umbrales arbitrarios, es necesario cerciorarse si realmente incurren en imposibilidades lógicas de base. Por norma general en finanzas, varianzas voluminosas o frecuencias exorbitantes pueden no ser errores sino lisa y llanamente clientes mayoristas infrecuentes.
2. **El Sesgo Condicionado por la Granularidad Transaccional:** Se puso atención al nivel de perturbación (y consiguiente riesgo de diagnóstico equívoco) provocado por fusiones y apilamientos del conjunto (Sección 4.2.11). Analizar indicadores calculando medias sobre un DataFrame fusionado donde cada transacción repite una biometría, altera masivamente la realidad de una muestra. Evaluar si buscar anomalías agrupando a nivel de *Cliente Único*, *Producto*, o netamente dejando *correr cada Evento de Compra* dependerá absolutamente de la respuesta que el estudio pretenda entregar.
3. **Visión Temprana de los Objetivos de Análisis:** La selección, limpieza y la conceptualización e inserción de nuevas columnas derivadas no arrojarán los rendimientos deseados si no se cuenta con los objetivos de análisis fijados claramente. En base al diseño estratégico se decantan los indicadores precisos a recolectar.
4. **La Protección Inicial en Declaración de Tipo Fecha:** Uno de los problemas subsanados ilustró la enorme ventaja técnica que significa explicitar anticipadamente el parseo de registros con estructura temporal u horaria (`parse_dates=`) en el exacto bloque donde se cargan o rescatan fuentes tabulares (*CSV*), para así prevenir incompatibilidades arrastradas y colisiones en funciones cronológicas.
