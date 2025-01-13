import pandas as pd


def load_and_clean_data(file_path, output_log, sheet_name="Sheet1"):
    """
    Loads an Excel file into a DataFrame and cleans its structure.

    Parameters:
    ----------
    file_path : str
        Path to the Excel file.

    output_log : ScrolledText
        The Tkinter ScrolledText widget for logging actions.

    sheet_name : str, optional
        The sheet name to load when reading an Excel file.

    Returns:
    -------
    pd.DataFrame
        A cleaned pandas DataFrame.
    """

    def log(message):
        output_log.insert("end", message + "\n")
        output_log.see("end")

    try:

        df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)
        df.columns = [str(col).strip() for col in df.columns]
        log(f"File '{file_path}' loaded successfully.")
        log(f"Initial column headers: {df.columns.tolist()}")

        df.columns = [f"Column_{i + 1}" for i, col in enumerate(df.columns)]
        log(f"Cleaned column headers: {df.columns.tolist()}")
        df.dropna(how="all", inplace=True)
        df.reset_index(drop=True, inplace=True)
        log(f"Data cleaned successfully. Rows: {df.shape[0]}, Columns: {df.shape[1]}")
        return df

    except Exception as e:
        log(f"Error loading file: {e}")
        return pd.DataFrame()


def clean_data_with_logging(file_path, output_log, sheet_name="Sheet1"):
    """
    Cleans data and logs actions without erasing valid data.

    Parameters:
    ----------
    file_path : str
        Path to the Excel file.

    output_log : ScrolledText
        The Tkinter ScrolledText widget for logging actions.

    sheet_name : str, optional
        The sheet name to process when reading the Excel file.

    Returns:
    -------
    pd.DataFrame
        The cleaned pandas DataFrame.
    """

    def log(message):
        output_log.insert("end", message + "\n")
        output_log.see("end")
    df = load_and_clean_data(file_path, output_log, sheet_name)
    if df.empty:
        log("No data to clean. Exiting.")
        return df
    for col in df.columns:
        for i in df.index:
            value = df.at[i, col]
            if pd.isnull(value):
                df.at[i, col] = "MISSING"
                log(f"Row {i}, Column '{col}': Replaced NULL with 'MISSING'.")
    log("Data cleaning complete.")
    return df
