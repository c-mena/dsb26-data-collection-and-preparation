import numpy as np
import pandas as pd
from IPython.display import display, HTML
from pandas.io.formats.style import Styler

rng = np.random.default_rng()


def calculate_birthdate(ages: np.ndarray | pd.Series, unique_days: bool = False) -> np.ndarray | pd.Series:
    """
    Calcula la fecha de nacimiento a partir de la edad.

    Esta función estima el año de nacimiento restando la edad al año actual y
    asigna un día aleatorio dentro de ese año.

    Args:
        ages (np.array | pd.Series): Arreglo o Serie de edades (enteros).
        unique_days (bool, opcional): Controla cómo se generan los días aleatorios.
            - False (por defecto): cada elemento recibe un día aleatorio independiente,
              incluso si comparte la misma edad con otro elemento.
            - True: se genera un único día aleatorio por cada valor de edad distinto,
              garantizando que elementos con la misma edad reciban exactamente la misma fecha.

    Returns:
        np.array | pd.Series: Arreglo o Serie de fechas de nacimiento (datetime64),
                              del mismo tipo que el argumento recibido.
    """
    # Detectamos si la entrada es una Serie de Pandas para preservar el tipo al retornar
    is_pandas_series = isinstance(ages, pd.Series)

    # Obtenemos el año de nacimiento como datetime64[Y] restando la edad al año actual.
    # ages_arr se convierte a timedelta64[Y] para operar directamente con datetime64[Y]
    # Castear datetime64[Y] a datetime64[D] proyecta automáticamente al 1° de enero de cada año
    current_year = np.datetime64("today").astype("datetime64[Y]")
    birth_years_y = current_year - np.asarray(ages).astype("timedelta64[Y]")

    if unique_days:
        # Un offset por año de nacimiento único: misma edad → misma fecha
        unique_years, inverse_idx = np.unique(birth_years_y, return_inverse=True)
        random_days_offset = rng.integers(0, 365, size=unique_years.size)[inverse_idx]
    else:
        # Un offset independiente por elemento (comportamiento por defecto)
        random_days_offset = rng.integers(0, 365, size=birth_years_y.size)

    birthdates = birth_years_y.astype("datetime64[D]") + random_days_offset.astype("timedelta64[D]")

    # Retornamos una Serie de Pandas si la entrada también lo era, conservando índice y nombre
    if is_pandas_series:
        return pd.Series(birthdates, index=ages.index, name=ages.name)

    return birthdates


def calculate_age(birthdates: np.ndarray | pd.Series, reference_date: str | None = None) -> np.ndarray | pd.Series:
    """
    Calcula la edad a partir de la fecha de nacimiento.

    Esta función es la inversa de calculate_birthdate. Calcula la edad basándose
    en la diferencia de años entre la fecha actual (o fecha de referencia) y el año de nacimiento.

    Args:
        birthdates (np.array | pd.Series): Arreglo o Serie de fechas de nacimiento (datetime64).
        reference_date (str | similar a datetime, opcional): Fecha de referencia para el cálculo.
                                                        Por defecto es la fecha actual.

    Returns:
        np.array | pd.Series: Arreglo o Serie de edades (enteros). Cuando la entrada es un
                              pd.Series, el dtype del resultado es Int64 (entero nullable de Pandas).
    """
    is_pandas_series = isinstance(birthdates, pd.Series)

    if reference_date is None:
        current_year = np.datetime64("today").astype("datetime64[Y]")
    else:
        current_year = np.datetime64(reference_date).astype("datetime64[Y]")

    # Convertimos directamente a datetime64[Y] para evitar conversiones intermedias
    birthdates_y = np.asarray(birthdates, dtype="datetime64[Y]")

    # La resta de dos datetime64[Y] produce timedelta64[Y]; astype(int) da los años directamente
    ages = (current_year - birthdates_y).astype(int)

    if is_pandas_series:
        # Int64 (mayúscula) es el entero nullable de Pandas, compatible con NaN
        return pd.Series(ages, index=birthdates.index, name=birthdates.name, dtype="Int64")

    return ages


def get_iqr_summary(df: pd.DataFrame, columns: list[str], display_format: str = "{:.2f}") -> Styler:
    """
    Calcula los límites IQR de las columnas indicadas e incluye mín, máx y σ/μ para contexto.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        columns (list[str]): Lista de columnas numéricas a analizar.
        display_format (str, opcional): Formato numérico para el Styler. Por defecto "{:.2f}".

    Returns:
        Styler: DataFrame estilizado con límites, conteo y porcentaje de outliers (incluye columna oculta 'Method').
    """
    summary_data = []
    for col in columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        low_lim = q1 - 1.5 * iqr
        high_lim = q3 + 1.5 * iqr

        # Calculamos estadísticas de la columna
        min_val = df[col].min()
        max_val = df[col].max()
        vc_val = df[col].std() / df[col].mean()  # coeficiente de variación
        outliers = df[(df[col] < low_lim) | (df[col] > high_lim)]
        count = len(outliers)
        perc = 100 * count / len(df)

        summary_data.append(
            {
                "Column": col,
                "Method": "IQR",
                "Lower Limit": low_lim,
                "Upper Limit": high_lim,
                "Outlier Count": count,
                "Outlier %": perc,
                "Min Column": min_val,
                "Max Column": max_val,
                "σ/μ Column": vc_val,
            }
        )

    output_df = pd.DataFrame(summary_data)
    # Aplicamos formato global mediante Styler (requiere jinja2)
    numeric_cols = ["Lower Limit", "Upper Limit", "Max Column", "Min Column", "σ/μ Column"]
    return (
        output_df.style.format({col: display_format for col in numeric_cols} | {"Outlier %": "{:.2f}%"})
        .hide(axis="index")
        .hide(subset=["Method"], axis="columns")
    )


def get_zscore_summary(
    df: pd.DataFrame, columns: list[str], threshold: int | float = 3, display_format: str = "{:.2f}"
) -> Styler:
    """
    Calcula los límites Z-score de las columnas indicadas e incluye mín, máx y σ/μ para contexto.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        columns (list[str]): Lista de columnas numéricas a analizar.
        threshold (int | float, opcional): Número de desviaciones estándar para definir el límite. Por defecto 3.
        display_format (str, opcional): Formato numérico para el Styler. Por defecto "{:.2f}".

    Returns:
        Styler: DataFrame estilizado con límites, conteo y porcentaje de outliers (incluye columna oculta 'Method').
    """
    summary_data = []
    for col in columns:
        mean_val = df[col].mean()
        std_val = df[col].std()
        low_lim = mean_val - (threshold * std_val)
        high_lim = mean_val + (threshold * std_val)

        # Calculamos estadísticas de la columna
        min_val = df[col].min()
        max_val = df[col].max()
        cv_val = std_val / mean_val  # coeficiente de variación
        outliers = df[((df[col] - mean_val) / std_val).abs() > threshold]
        count = len(outliers)
        perc = 100 * count / len(df)

        summary_data.append(
            {
                "Column": col,
                "Method": "Z-Score",
                "Lower Limit": low_lim,
                "Upper Limit": high_lim,
                "Outlier Count": count,
                "Outlier %": perc,
                "Min Column": min_val,
                "Max Column": max_val,
                "σ/μ Column": cv_val,
            }
        )

    output_df = pd.DataFrame(summary_data)
    numeric_cols = ["Lower Limit", "Upper Limit", "Max Column", "Min Column", "σ/μ Column"]
    return (
        output_df.style.format({col: display_format for col in numeric_cols} | {"Outlier %": "{:.2f}%"})
        .hide(axis="index")
        .hide(subset=["Method"], axis="columns")
    )


def get_outlier_mask(df: pd.DataFrame, summary_styler: Styler, column_name: str) -> pd.Series:
    """
    Genera una máscara booleana que identifica los outliers de una columna,
    usando los límites almacenados en un resumen de outliers (IQR o Z-Score).

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        summary_styler (Styler): Styler retornado por
            get_iqr_summary o get_zscore_summary.
        column_name (str): Nombre de la columna a evaluar.

    Returns:
        pd.Series[bool]: Serie booleana del mismo largo que df, con True en las
                         filas cuyos valores caen fuera de los límites.
    """
    # Extraemos los datos crudos del objeto Styler
    row = summary_styler.data
    row = row[row["Column"] == column_name].iloc[0]

    return (df[column_name] < row["Lower Limit"]) | (df[column_name] > row["Upper Limit"])


def inspect_outliers(
    df: pd.DataFrame,
    summary_styler: Styler,
    column_name: str,
    columns_to_show: list[str] | None = None,
    rows: int = 5,
    list_outliers: bool = True,
    display_format: str = "{:.2f}",
) -> None:
    """
    Muestra un reporte detallado de outliers para una columna específica.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        summary_styler (Styler): Styler retornado por get_iqr_summary o get_zscore_summary.
        column_name (str): Nombre de la columna a inspeccionar.
        columns_to_show (list[str], opcional): Columnas a mostrar en el listado de outliers.
                                               Por defecto muestra solo la columna analizada.
        rows (int, opcional): Número de filas a mostrar del extremo inferior y superior. Por defecto 5.
        list_outliers (bool, opcional): Si es True, muestra el detalle de los outliers. Por defecto True.
        display_format (str, opcional): Formato numérico para el Styler. Por defecto "{:.2f}".

    Returns:
        None: Imprime el reporte en consola y, si list_outliers=True, muestra un DataFrame estilizado.
    """
    # Extraemos los datos crudos del objeto Styler
    summary_df = summary_styler.data
    row = summary_df[summary_df["Column"] == column_name].iloc[0]

    # Extraemos el especificador de formato sin llaves para usarlo en f-strings (ej: "{:.2f}" → ".2f")
    clean_fmt = display_format.replace("{:", "").replace("}", "")

    # Obtenemos el método, si no está presente mostramos "Desconocido" por compatibilidad
    method_name = row.get("Method", "Desconocido")

    header = f"--- Reporte de outliers ({method_name}) para la variable {column_name} ---"
    print(header)
    print(f"Rango de la variable: [{row['Min Column']:{clean_fmt}}  a  {row['Max Column']:{clean_fmt}}]")
    print(f"Límites de outliers:  [{row['Lower Limit']:{clean_fmt}}  a  {row['Upper Limit']:{clean_fmt}}]")
    print(f"Total de outliers:    {int(row['Outlier Count'])} ({row['Outlier %']:.2f}%)")
    print("-" * len(header))

    if list_outliers:
        # Filtramos los outliers reales
        outlier_mask = (df[column_name] < row["Lower Limit"]) | (df[column_name] > row["Upper Limit"])
        all_outliers = df[outlier_mask].sort_values(by=column_name)

        if not all_outliers.empty:
            # Seleccionamos solo las columnas deseadas
            if columns_to_show is None:
                columns_to_show = [column_name]

            # Preparamos cabeza y cola del listado de outliers
            if len(all_outliers) <= (rows * 2):
                display_df = all_outliers[columns_to_show]
                show_all_outliers = True
            else:
                display_df = pd.concat([all_outliers.head(rows), all_outliers.tail(rows)])[columns_to_show]
                show_all_outliers = False

            display_df.sort_values(by=column_name, ascending=True, inplace=True)
            if show_all_outliers:
                print(f"Mostrando todos los outliers ordenados de menor a mayor:")
            else:
                print(f"Mostrando los {rows} outliers más altos y más bajos, ordenados de menor a mayor:")
            # Aplica formato numérico solo a columnas numéricas para evitar error con strings
            numeric_cols = display_df.select_dtypes(include="number").columns.tolist()
            fmt_dict = {col: display_format for col in numeric_cols}
            # Convierte el índice en columna "Índice" para que se muestre en la misma fila de encabezados
            display_df = display_df.rename_axis("Índice").reset_index()
            display(display_df.style.format(fmt_dict, precision=2).hide(axis="index"))
        else:
            print("No se encontraron outliers para esta variable.")


def inspect_outliers2(
    df: pd.DataFrame,
    iqr_summary: Styler,
    zscore_summary: Styler,
    column_name: str,
    rows: int = 5,
    list_outliers: bool = True,
    display_format: str = "{:.2f}",
) -> None:
    """
    Muestra un reporte comparativo de outliers IQR vs Z-Score para una columna específica.

    A diferencia de inspect_outliers, esta función recibe ambos resúmenes (IQR y Z-Score)
    y muestra los outliers de cada método lado a lado en una sola tabla.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        iqr_summary (Styler): Styler retornado por get_iqr_summary.
        zscore_summary (Styler): Styler retornado por get_zscore_summary.
        column_name (str): Nombre de la columna a inspeccionar.
        rows (int, opcional): Número de filas a mostrar del extremo inferior y superior. Por defecto 5.
        list_outliers (bool, opcional): Si es True, muestra el detalle de los outliers. Por defecto True.
        display_format (str, opcional): Formato numérico para el Styler. Por defecto "{:.2f}".

    Returns:
        None: Imprime el reporte en consola y, si list_outliers=True, muestra un DataFrame estilizado.
    """
    # Extraemos los datos crudos de ambos Stylers
    iqr_row = iqr_summary.data
    iqr_row = iqr_row[iqr_row["Column"] == column_name].iloc[0]

    zscore_row = zscore_summary.data
    zscore_row = zscore_row[zscore_row["Column"] == column_name].iloc[0]

    # Extraemos el especificador de formato sin llaves para usarlo en f-strings (ej: "{:.2f}" → ".2f")
    clean_fmt = display_format.replace("{:", "").replace("}", "")

    header = f"--- Reporte de outliers para la variable {column_name} ---"
    print(header)
    print(
        f"Rango de la variable:          [{iqr_row['Min Column']:{clean_fmt}}  a  {iqr_row['Max Column']:{clean_fmt}}]"
    )
    print(
        f"Límites de outliers (IQR):     [{iqr_row['Lower Limit']:{clean_fmt}}  a  {iqr_row['Upper Limit']:{clean_fmt}}]"
    )
    print(
        f"Límites de outliers (Z-Score): [{zscore_row['Lower Limit']:{clean_fmt}}  a  {zscore_row['Upper Limit']:{clean_fmt}}]"
    )
    print(f"Total de outliers (IQR):       {int(iqr_row['Outlier Count'])} ({iqr_row['Outlier %']:.2f}%)")
    print(f"Total de outliers (Z-Score):   {int(zscore_row['Outlier Count'])} ({zscore_row['Outlier %']:.2f}%)")
    print("-" * len(header))

    if list_outliers:

        def _get_outlier_display(row_data: pd.Series, label: str) -> tuple[pd.DataFrame, bool]:
            """Filtra, recorta y prepara outliers para un método dado."""
            mask = (df[column_name] < row_data["Lower Limit"]) | (df[column_name] > row_data["Upper Limit"])
            outliers = df[mask].sort_values(by=column_name)

            if outliers.empty:
                return pd.DataFrame()

            # Preparamos cabeza y cola del listado de outliers
            if len(outliers) <= (rows * 2):
                result = outliers[[column_name]]
                show_all = True
            else:
                result = pd.concat([outliers.head(rows), outliers.tail(rows)])[[column_name]]
                show_all = False

            result = result.sort_values(by=column_name, ascending=True)

            # Convierte índice a columna y renombra con sufijo del método
            result = result.rename_axis(f"Índice {label}").reset_index()
            result = result.rename(columns={column_name: f"{column_name} ({label})"})
            result = result.reset_index(drop=True)
            return result, show_all

        iqr_display, show_all_iqr = _get_outlier_display(iqr_row, "IQR")
        zscore_display, show_all_zscore = _get_outlier_display(zscore_row, "Z-Score")

        if iqr_display.empty and zscore_display.empty:
            print("No se encontraron outliers para esta variable en ningún método.")
            return

        # Combina ambos métodos lado a lado (rellena con NaN si difieren en largo)
        combined = pd.concat([iqr_display, zscore_display], axis=1)
        show_all_outliers = show_all_iqr and show_all_zscore

        if show_all_outliers:
            print(f"Mostrando todos los outliers ordenados de menor a mayor:")
        else:
            print(f"Mostrando los {rows} outliers más altos y más bajos, ordenados de menor a mayor:")
        # Aplica formato numérico solo a columnas de datos, excluyendo las de Índice
        numeric_cols = [c for c in combined.select_dtypes(include="number").columns if not c.startswith("Índice")]
        fmt_dict = {col: display_format for col in numeric_cols}
        display(combined.style.format(fmt_dict, precision=2, na_rep="").hide(axis="index"))


def format_numeric(df_stats: pd.DataFrame, format: str = "{:,.1f}") -> Styler:
    """
    Aplica formato numérico a las columnas numéricas y formato de fecha a las columnas
    de tipo datetime de un DataFrame.

    Las columnas datetime se formatean automáticamente como "yyyy-mm-dd", ocultando
    la parte de la hora. Útil para mejorar la visualización de describe() en Jupyter.

    Args:
        df_stats (pd.DataFrame): DataFrame a formatear (típicamente la salida de describe()).
        format (str, opcional): Cadena de formato para los valores numéricos. Por defecto "{:,.1f}".

    Returns:
        Styler: Objeto Styler con los formatos aplicados.
    """
    # Seleccionamos las columnas numéricas por dtype
    numeric_cols = df_stats.select_dtypes(include=["number"]).columns

    # Detectamos columnas datetime inspeccionando valores reales, ya que describe()
    # mezcla tipos (int, Timestamp, Timedelta) y el dtype resultante es 'object'
    datetime_cols = [
        col
        for col in df_stats.columns
        if col not in numeric_cols and df_stats[col].apply(lambda v: isinstance(v, pd.Timestamp)).any()
    ]

    # Función formateadora para valores datetime (maneja Timestamps y otros tipos mezclados)
    def _format_datetime(v: object) -> str:
        if isinstance(v, pd.Timestamp):
            return v.strftime("%Y-%m-%d")
        if pd.isna(v):
            return "-"
        return str(v)

    # Construimos el diccionario de formatos: numérico para números, fecha para datetimes
    format_dict = {col: format for col in numeric_cols}
    format_dict.update({col: _format_datetime for col in datetime_cols})

    # Retornamos el Styler con todos los formatos aplicados
    return df_stats.style.format(format_dict, na_rep="-")


def compare_granularity_bias(merged_df: pd.DataFrame, pct_format: str = "{:+.1f}%") -> None:
    """
    Simula la reconstrucción de las entidades originales (clientes, productos, transacciones)
    desde el DataFrame fusionado para visualizar el sesgo probabilístico introducido
    matemáticamente por el cambio de granularidad al fusionar los datos (relación muchos a uno).

    NOTA: Esta función no mide el "sesgo de selección" por pérdida de
    información durante un Inner Join (ej. clientes sin compras), sino la distorsión
    en las estadísticas descriptivas (media, std, etc.) causada por la repetición
    mecánica de datos de clientes y productos en cada transacción.

    Codificación de colores del heatmap:
        Verde oscuro  = 0%   (sin diferencia)
        Verde suave   < ±5%  (sesgo despreciable)
        Amarillo      < ±20% (sesgo moderado)
        Rojo          ≥ ±20% (sesgo significativo)

    Args:
        merged_df (pd.DataFrame): DataFrame unificado post-merge (sección 2.3).
        pct_format (str, opcional): Formato de porcentaje. Por defecto "{:+.1f}%".

    Returns:
        None: Despliega directamente el heatmap en el notebook.
    """
    # --- Reconstrucción de entidades únicas (sobre muestra fusionada) ---
    client_cols = ["ClientId", "ClientName", "ClientCity", "ClientBirthdate", "ClientPurchases", "ClientTotalPaid"]
    product_cols = ["ProdId", "ProdName", "ProdCategory", "ProdPriceCLP", "ProdCostUSD", "ProdPurchaseDate"]
    txn_cols = ["TxnId", "ClientId", "ProdName", "TxnAmount", "TxnDate"]

    clients_df = merged_df[client_cols].drop_duplicates(subset="ClientId").reset_index(drop=True)
    products_df = merged_df[product_cols].drop_duplicates(subset="ProdId").reset_index(drop=True)
    txn_df = merged_df[txn_cols].drop_duplicates(subset="TxnId").reset_index(drop=True)

    # Agregamos ClientAge a clients_df (se calculó desde ClientBirthdate post-merge)
    if "ClientAge" in merged_df.columns:
        age_map = (
            merged_df[["ClientId", "ClientAge"]].drop_duplicates(subset="ClientId").set_index("ClientId")["ClientAge"]
        )
        clients_df["ClientAge"] = clients_df["ClientId"].map(age_map)

    # Mapa columna → (DataFrame original, etiqueta de origen)
    col_source = {
        "ClientAge": (clients_df, "clients_df"),
        "ClientPurchases": (clients_df, "clients_df"),
        "ClientTotalPaid": (clients_df, "clients_df"),
        "TxnAmount": (txn_df, "transactions_df"),
        "ProdPriceCLP": (products_df, "products_df"),
        "ProdCostUSD": (products_df, "products_df"),
    }

    # Estadísticos a comparar
    stats_funcs = {
        "mean": lambda s: s.mean(),
        "std": lambda s: s.std(),
        "median": lambda s: s.median(),
        "min": lambda s: s.min(),
        "max": lambda s: s.max(),
    }

    def _pct(orig: float, fused: float) -> float:
        """Diferencia porcentual con casos especiales.

        - Ambos nulos (NaN)  → 0.0
        - Ambos cero (0)     → 0.0  ← caso numérico explícito
        - orig nulo o cero   → NaN  (división indefinida)
        """
        orig_na = pd.isna(orig)
        fused_na = pd.isna(fused)
        if orig_na and fused_na:
            return 0.0
        # Ambos numéricamente cero → sin diferencia
        if (not orig_na) and (not fused_na) and orig == 0 and fused == 0:
            return 0.0
        if orig_na or orig == 0:
            return float("nan")
        return (fused - orig) / abs(orig) * 100

    def _highlight(val: float) -> str:
        """Colorea celdas Δ% según magnitud."""
        if pd.isna(val):
            return ""
        if val == 0:
            # Sin diferencia: verde oscuro
            return "background-color: #7fbf8e; color: #0a2e14"
        if abs(val) < 5:
            # Sesgo despreciable: verde suave
            return "background-color: #d4edda; color: #155724"
        elif abs(val) < 20:
            # Sesgo moderado: amarillo
            return "background-color: #fff3cd; color: #856404"
        else:
            # Sesgo significativo: rojo
            return "background-color: #f8d7da; color: #721c24"

    # --- Construcción del heatmap: filas = columnas, columnas = Origen + estadísticos ---
    stat_names = list(stats_funcs.keys())
    rows = []
    for col, (src_df, label) in col_source.items():
        if col not in src_df.columns or col not in merged_df.columns:
            continue
        src_series = src_df[col].dropna()
        merged_series = merged_df[col].dropna()
        row = {"Origin": label}
        for stat, fn in stats_funcs.items():
            row[stat] = _pct(fn(src_series), fn(merged_series))
        rows.append((col, row))

    # Armamos el DataFrame con índice = nombre de columna
    heat_df = pd.DataFrame({col: row for col, row in rows}).T
    heat_df = heat_df[["Origin"] + stat_names]  # orden explícito de columnas

    # Convierte columnas de estadísticos a float (vienen como object por mezcla con str)
    heat_df[stat_names] = heat_df[stat_names].astype(float)

    # Renombra estadísticos con sufijo ' Δ%' para identificarlos en el encabezado
    stat_cols_renamed = {s: f"{s} Δ%" for s in stat_names}
    heat_df = heat_df.rename(columns=stat_cols_renamed)
    stat_display_names = list(stat_cols_renamed.values())

    # Lleva el índice (nombre de columna) a una columna real llamada 'Column'
    # para que aparezca en la misma fila de encabezados que los estadísticos.
    heat_df = heat_df.reset_index(names="Column")

    # --- Estilizado del heatmap ---
    from IPython.display import display

    display(
        heat_df.style.format({s: pct_format for s in stat_display_names}, na_rep="-")
        .map(_highlight, subset=stat_display_names)
        .hide(axis="index")  # oculta el índice numérico creado por reset_index
    )


def compare_granularity_bias2(
    merged_df: pd.DataFrame, numeric_format: str = "{:,.2f}", pct_format: str = "{:+.1f}%"
) -> None:
    """
    Muestra tres tablas anchas (clientes, productos, transacciones) de distorsión
    por granularidad. Cada tabla incluye columnas Orig | Fus | Δ% para cada
    estadístico (media, std, mediana, min, max).

    Al igual que compare_granularity_bias, esto ilustra el efecto de "repetir"
    información de tablas dimensionales en la tabla de hechos, causando
    que entidades con mayor frecuencia de transacciones dominen los cálculos.
    No corresponde al sesgo por pérdida de filas del join original.

    Args:
        merged_df (pd.DataFrame): DataFrame unificado post-merge (sección 2.3).
        numeric_format (str, opcional): Formato de valores absolutos. Por defecto "{:,.2f}".
        pct_format (str, opcional): Formato de diferencia porcentual. Por defecto "{:+.1f}%".

    Returns:
        None: Despliega directamente las tablas en el notebook.
    """
    from IPython.display import display, HTML

    # --- Reutilizamos la lógica de deduplicación de compare_granularity_bias ---
    client_cols = ["ClientId", "ClientName", "ClientCity", "ClientBirthdate", "ClientPurchases", "ClientTotalPaid"]
    product_cols = ["ProdId", "ProdName", "ProdCategory", "ProdPriceCLP", "ProdCostUSD", "ProdPurchaseDate"]
    txn_cols = ["TxnId", "ClientId", "ProdName", "TxnAmount", "TxnDate"]

    clients_df = merged_df[client_cols].drop_duplicates(subset="ClientId").reset_index(drop=True)
    products_df = merged_df[product_cols].drop_duplicates(subset="ProdId").reset_index(drop=True)
    txn_df = merged_df[txn_cols].drop_duplicates(subset="TxnId").reset_index(drop=True)

    # Agrega variable derivada ClientAge a clients_df si está presente en merged_df
    if "ClientAge" in merged_df.columns:
        age_map = (
            merged_df[["ClientId", "ClientAge"]].drop_duplicates(subset="ClientId").set_index("ClientId")["ClientAge"]
        )
        clients_df["ClientAge"] = clients_df["ClientId"].map(age_map)

    # Mapa columna → DataFrame de origen
    col_source = {
        "ClientAge": (clients_df, "clients_df"),
        "ClientPurchases": (clients_df, "clients_df"),
        "ClientTotalPaid": (clients_df, "clients_df"),
        "TxnAmount": (txn_df, "transactions_df"),
        "ProdPriceCLP": (products_df, "products_df"),
        "ProdCostUSD": (products_df, "products_df"),
    }

    stats_funcs = {
        "mean": lambda s: s.mean(),
        "std": lambda s: s.std(),
        "median": lambda s: s.median(),
        "min": lambda s: s.min(),
        "max": lambda s: s.max(),
    }

    def _pct(orig: float, fused: float) -> float:
        """Diferencia porcentual con casos especiales.

        - Ambos nulos (NaN)  → 0.0
        - Ambos cero (0)     → 0.0  ← caso numérico explícito
        - orig nulo o cero   → NaN  (división indefinida)
        """
        orig_na = pd.isna(orig)
        fused_na = pd.isna(fused)
        if orig_na and fused_na:
            return 0.0
        # Ambos numéricamente cero → sin diferencia
        if (not orig_na) and (not fused_na) and orig == 0 and fused == 0:
            return 0.0
        if orig_na or orig == 0:
            return float("nan")
        return (fused - orig) / abs(orig) * 100

    def _highlight(val: float) -> str:
        """Colorea celdas Δ% según magnitud."""
        if pd.isna(val):
            return ""
        if val == 0:
            return "background-color: #7fbf8e; color: #0a2e14"
        if abs(val) < 5:
            return "background-color: #d4edda; color: #155724"
        elif abs(val) < 20:
            return "background-color: #fff3cd; color: #856404"
        else:
            return "background-color: #f8d7da; color: #721c24"

    # --- Agrupamos columnas por DataFrame de origen ---
    groups = {
        "clients_df": [],
        "transactions_df": [],
        "products_df": [],
    }
    for col, (src_df, label) in col_source.items():
        if col in src_df.columns and col in merged_df.columns:
            groups[label].append((col, src_df))

    group_titles = {
        "clients_df": "📋 clients_df — columnas con sesgo potencial",
        "transactions_df": "📋 transactions_df — columnas sin sesgo (lado 'muchos')",
        "products_df": "📋 products_df — columnas con sesgo potencial",
    }

    # Acumulamos datos para el heatmap compacto
    heatmap_data = {}  # {col: {stat: pct_diff}}
    heatmap_colors = {}  # {col: {stat: style_str}}

    # --- Construcción y visualización de las 3 tablas anchas ---
    for group_name, cols_srcs in groups.items():
        if not cols_srcs:
            continue

        display(HTML(f"<h4 style='margin-top:1.2em'>{group_titles[group_name]}</h4>"))

        # Columnas del DataFrame ancho: Column + (orig, fus, Δ%) por cada estadístico
        wide_cols = ["Column"]
        for stat in stats_funcs:
            wide_cols += [f"{stat} (Orig)", f"{stat} (Fus)", f"{stat} Δ%"]

        rows_wide = []
        pct_cols = [c for c in wide_cols if c.endswith("Δ%")]

        for col, src_df in cols_srcs:
            src_series = src_df[col].dropna()
            merged_series = merged_df[col].dropna()
            row = {"Column": col}

            heatmap_data.setdefault(col, {})
            heatmap_colors.setdefault(col, {})

            for stat, fn in stats_funcs.items():
                v_orig = fn(src_series)
                v_merged = fn(merged_series)
                pct = _pct(v_orig, v_merged)
                row[f"{stat} (Orig)"] = v_orig
                row[f"{stat} (Fus)"] = v_merged
                row[f"{stat} Δ%"] = pct

                # Guardamos para el heatmap
                heatmap_data[col][stat] = pct
                heatmap_colors[col][stat] = _highlight(pct)

            rows_wide.append(row)

        wide_df = pd.DataFrame(rows_wide)

        # Identificamos columnas numéricas (no Δ%, no Column)
        num_cols = [c for c in wide_cols if c not in (["Column"] + pct_cols)]

        fmt_dict = {c: numeric_format for c in num_cols}
        fmt_dict.update({c: pct_format for c in pct_cols})

        styler = (
            wide_df[wide_cols].style.format(fmt_dict, na_rep="-").map(_highlight, subset=pct_cols).hide(axis="index")
        )
        display(styler)
