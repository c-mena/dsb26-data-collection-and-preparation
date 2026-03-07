# Proyecto: Obtención y Preparación de Datos

Este repositorio alberga el proyecto del **Módulo 3: Obtención y Preparación de Datos**, perteneciente al **"Bootcamp Fundamentos de Ciencias de Datos 2026"** de **Talento Digital para Chile - SENCE**.

El objetivo principal es implementar un flujo de trabajo, preestablecido por la pauta del enunciado del proyecto, para preparar datos de un ecommerce minorista ficticio. Para ello, simulamos desde cero la creación de datos de clientes, productos y transacciones; además, extraemos datos de la web para complementar el dataset y finalmente aplicamos técnicas de limpieza, validación de outliers y enriquecimiento de las tablas originales, todo apoyado en las bibliotecas analíticas NumPy y Pandas del ecosistema de Python.

## Estructura del Proyecto

- [`main.ipynb`](main.ipynb): Es el *Jupyter Notebook* central y único archivo ejecutable requerido del proyecto finalizado. Expone detalladamente, sección por sección (6 en total), el fundamento de cada análisis, simulando iteración a iteración el ciclo de vida de los datos, explicados interactivamente mediante la combinación de celdas Markdown y código Python.
- [`tools.py`](tools.py): Módulo auxiliar de utilidades en Python que agrupa todas las funciones hechas a medida que apoyan y extienden las reglas de limpieza y agrupación, reduciendo la densidad visual del Notebook principal.
- [`/data`](data): Subdirectorio para contener los archivos crudos y transformados exportados desde las secciones productivas (Soporta archivos temporales iterativos en formato *.csv*, *.npz*, *.xlsx* y *.parquet*).
- [`SUMMARY.md`](SUMMARY.md): Un documento funcional y condensado que evalúa las técnicas ejecutadas, analiza los fallos del procedimiento y resume conclusiones importantes en las tomas de decisiones.

## Requisitos y Tecnologías

El proyecto se despliega fundamentalmente sobre:

- `numpy` (Para simulaciones estadísticas veloces)
- `pandas` (Para estructuración, unión y limpieza del dataset)
- `requests` (Capacidad HTTP para consumir el valor en divisa vía web scraping desde SII, el fisco chileno)
- `lxml` (Complemento operacional para el parseo y extracción de datos desde HTML)
- `openpyxl` (Gestión de compatibilidad en exportación y carga nativa en archivos Excel)
- `pyarrow` / `fastparquet` (Motores subyacentes para serialización tabular robusta en formato Parquet)
- `matplotlib` (Para creación de visualizaciones y gráficos)
- `jinja2` (Motor de plantillas empleado internamente para estilos y reportes visuales)

## Instalación y Despliegue Local

Para inspeccionar o recrear el análisis transaccional directamente en tu equipo, simplemente sigue esta ruta predeterminada de acción:

1. **Clonar el proyecto**

```bash
git clone https://github.com/tu-usuario/proyecto-dsb26.git
cd proyecto-dsb26
```

1. **Crear e inicializar un entorno virtual**

Esto ayuda aislar y no contaminar tu versión global de Python y sus dependencias.

```bash
# Windows PowerShell / CMD:
python -m venv .venv
.venv\Scripts\activate

# Distribuciones Mac/Linux:
python3 -m venv .venv
source .venv/bin/activate
```

1. **Cargar dependencias necesarias**

Recomendamos instalar las bibliotecas requeridas utilizando el archivo `requirements.txt` incluido en el proyecto, lo que garantiza operar con las versiones exactas y probadas:

```bash
pip install -r requirements.txt
```

*(Como alternativa, puedes instalar los paquetes principales de forma manual:* `pip install numpy pandas requests lxml openpyxl pyarrow fastparquet matplotlib jinja2 ipykernel`*)*

1. **Ejecutar el Proyecto**

La alternativa recomendada para inicializar y observar el proyecto es emplear **Visual Studio Code (VS Code)** con su extensión de **Jupyter** instalada. Sólo debes abrir la carpeta del repositorio en VS Code, seleccionar tu entorno virtual `.venv` como tu Kernel de ejecución, y abrir el archivo `main.ipynb` para visualizar el código y sus correspondientes anotaciones en simultáneo.

*(Otra alternativa válida, desde la consola y con tu entorno activo, es ejecutar el comando `jupyter notebook` para levantar el servidor y entrar a `main.ipynb` directamente mediante tu navegador web).*

---
