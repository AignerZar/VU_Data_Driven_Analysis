import os
import cdsapi
import pandas as pd
import zipfile

URL = "https://cds.climate.copernicus.eu/api"
API_KEY = "e036f094-6038-41b9-abd6-66a5ecf3d040"

ERA5_BASE_FOLDER = "era5_timeseries"
ERA5_ZIP_FOLDER = os.path.join(ERA5_BASE_FOLDER, "zip")
ERA5_CSV_FOLDER = os.path.join(ERA5_BASE_FOLDER, "csv")

ERA5_VARIABLES = [
    "2m_temperature",
    "soil_temperature_level_1",
    "soil_temperature_level_2",
    "total_precipitation",
    #"volumetric_soil_water_layer_1",
    #"volumetric_soil_water_layer_2",
]



#Überprüft ob die ordnerstruktur schon existiert:
def ensure_era5_folders_exist():
    os.makedirs(ERA5_ZIP_FOLDER, exist_ok=True)
    os.makedirs(ERA5_CSV_FOLDER, exist_ok=True)



#Bestimmt den Rasterpunkt einer Koordinate
def get_era5_grid_point(lat, lon):
    grid_lat = round(lat, 1)
    grid_lon = round(lon, 1)
    return grid_lat, grid_lon



#erstellt filename für eine Koordinate:
def format_coordinate_for_filename(value):
    return str(value).replace("-", "m").replace(".", "p") #macht aus 47.3 den string 47p3, wichtig für den Dateinamen



#Funktion erstellt die Filenamen für eine bestimmte Koordinate und einen bestimmten Zeitraum
def get_era5_file_paths(lat, lon, start_date, end_date):
    ensure_era5_folders_exist()

    grid_lat, grid_lon = get_era5_grid_point(lat, lon)

    lat_name = format_coordinate_for_filename(grid_lat)
    lon_name = format_coordinate_for_filename(grid_lon)

    start_name = start_date.replace("-", "")
    end_name = end_date.replace("-", "")

    base_name = f"era5_land_timeseries_lat_{lat_name}_lon_{lon_name}_{start_name}_{end_name}"

    zip_file = os.path.join(ERA5_ZIP_FOLDER, base_name + ".zip")
    csv_file = os.path.join(ERA5_CSV_FOLDER, base_name + ".csv")

    return zip_file, csv_file



#Funktion lädt die gesamte Zeitreihe für den angegebenen Zeitraum für eine Koordinate, Ergebnis wird al zip Datei gespeichert
def download_era5_timeseries_for_coordinate(
    lat,
    lon,
    start_date,
    end_date,
    zip_file
):
    client = cdsapi.Client(url=URL, key=API_KEY)

    client.retrieve(
        "reanalysis-era5-land-timeseries",
        {
            "variable": ERA5_VARIABLES,
            "location": {
                "latitude": lat,
                "longitude": lon,
            },
            "date": [
                start_date,
                end_date
            ],
            "data_format": "csv"
        },
        zip_file
    )

    return zip_file



#Öffnet die heruntergeladene ZIP-Datei, liest alle darin enthaltenen CSV-Dateien und verbindet sie zu einem gemeinsamen DataFrame.
def read_era5_zip_as_dataframe(zip_file):
    dataframes = []

    with zipfile.ZipFile(zip_file, "r") as z:
        csv_files = [
            filename for filename in z.namelist()
            if filename.endswith(".csv")
        ]

        for filename in csv_files:
            with z.open(filename) as f:
                df_part = pd.read_csv(f)

            dataframes.append(df_part)

    if len(dataframes) == 0:
        raise ValueError("No CSV files found inside ERA5 zip file.")

    df = dataframes[0]

    for df_part in dataframes[1:]:
        common_columns = list(set(df.columns) & set(df_part.columns))

        merge_columns = [
            col for col in common_columns
            if col.lower() in ["time", "valid_time", "date", "datetime", "latitude", "longitude"]
        ]

        if len(merge_columns) == 0:
           raise ValueError("No common merge columns found between ERA5 CSV files.")

        df = pd.merge(
            df,
            df_part,
            on=merge_columns,
            how="outer"
        )

    return df



#Benennt die ERA5-Spalten verständlicher um, wandelt Temperaturen von Kelvin in Celsius um, Niederschlag von Meter in Millimeter, und berechnet 3h-, 1-Tages- und 3-Tages-Niederschlagssummen.
def clean_era5_dataframe(df):
    print("Original ERA5 columns:")
    print(df.columns)

    rename_dict = {}

    for col in df.columns:
        col_lower = col.lower()

        if "valid_time" in col_lower or col_lower == "time":
            rename_dict[col] = "datetime"

        elif "2m_temperature" in col_lower or col_lower == "t2m":
            rename_dict[col] = "temperature_2m_K"

        elif "soil_temperature_level_1" in col_lower or col_lower == "stl1":
            rename_dict[col] = "soil_temperature_level_1_K"

        elif "soil_temperature_level_2" in col_lower or col_lower == "stl2":
            rename_dict[col] = "soil_temperature_level_2_K"

        elif "total_precipitation" in col_lower or col_lower == "tp":
            rename_dict[col] = "precip_hourly_m"

        elif "volumetric_soil_water_layer_1" in col_lower or col_lower == "swvl1":
            rename_dict[col] = "soil_water_layer_1"

        elif "volumetric_soil_water_layer_2" in col_lower or col_lower == "swvl2":
            rename_dict[col] = "soil_water_layer_2"

    df = df.rename(columns=rename_dict)

    if "datetime" not in df.columns:
        raise ValueError("No datetime column found. Check printed ERA5 columns.")

    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)

    if "temperature_2m_K" in df.columns:
        df["temperature_2m_C"] = df["temperature_2m_K"] - 273.15

    if "soil_temperature_level_1_K" in df.columns:
        df["soil_temperature_level_1_C"] = df["soil_temperature_level_1_K"] - 273.15

    if "soil_temperature_level_2_K" in df.columns:
        df["soil_temperature_level_2_C"] = df["soil_temperature_level_2_K"] - 273.15

    if "precip_hourly_m" in df.columns:
        df["precip_hourly_mm"] = df["precip_hourly_m"] * 1000

        df["precip_3h_mm"] = df["precip_hourly_mm"].rolling(
            window=3,
            min_periods=1
        ).sum()

        df["precip_1d_mm"] = df["precip_hourly_mm"].rolling(
            window=24,
            min_periods=1
        ).sum()

        df["precip_3d_mm"] = df["precip_hourly_mm"].rolling(
            window=72,
            min_periods=1
        ).sum()

    wanted_columns = [
        "datetime",
        "latitude",
        "longitude",
        "temperature_2m_C",
        "soil_temperature_level_1_C",
        "soil_temperature_level_2_C",
        "precip_hourly_mm",
        "precip_3h_mm",
        "precip_1d_mm",
        "precip_3d_mm",
        #"soil_water_layer_1",
        #"soil_water_layer_2",
    ]

    existing_columns = [
        col for col in wanted_columns
        if col in df.columns
    ]

    return df[existing_columns]



#Kombiniert zwei Schritte: ZIP-Datei lesen und die Rohdaten anschließend bereinigen. Gibt eine saubere ERA5-Zeitreihe als DataFrame zurück.
def load_era5_timeseries_as_dataframe(zip_file):
    df_raw = read_era5_zip_as_dataframe(zip_file)
    df_clean = clean_era5_dataframe(df_raw)

    return df_clean



#Das ist die Hauptfunktion für später.
#Sie prüft zuerst, ob die fertige CSV schon existiert. Falls ja, wird sie geladen. Falls nein, prüft sie, ob die ZIP-Datei schon existiert. Falls auch die fehlt, wird ERA5 heruntergeladen. Danach wird die ZIP verarbeitet und als fertige CSV gespeichert.
def get_era5_timeseries_for_coordinate(
    lat,
    lon,
    start_date,
    end_date,
    save_csv=True
):
    grid_lat, grid_lon = get_era5_grid_point(lat, lon)

    zip_file, csv_file = get_era5_file_paths(
        lat=lat,
        lon=lon,
        start_date=start_date,
        end_date=end_date
    )

    if os.path.exists(csv_file):
        print(f"ERA5 CSV already exists, loading: {csv_file}")
        return pd.read_csv(csv_file, parse_dates=["datetime"])

    if os.path.exists(zip_file):
        print(f"ERA5 ZIP already exists, loading: {zip_file}")
    else:
        print(f"Downloading ERA5 timeseries for lat={lat}, lon={lon}")
        download_era5_timeseries_for_coordinate(
            lat=grid_lat,
            lon=grid_lon,
            start_date=start_date,
            end_date=end_date,
            zip_file=zip_file
        )

    df = load_era5_timeseries_as_dataframe(zip_file)

    if save_csv:
        df.to_csv(csv_file, index=False)
        print(f"ERA5 CSV saved: {csv_file}")

    return df



#Testlauf
if __name__ == "__main__":

    df = get_era5_timeseries_for_coordinate(
        lat=47.2692,
        lon=11.4041,
        start_date="2020-01-01",
        end_date="2020-01-31",
        save_csv=True
    )

    print("\nErste 5 Zeilen:")
    print(df.head())

    print("\nLetzte 5 Zeilen:")
    print(df.tail())

    print("\nSpalten:")
    print(df.columns.tolist())

    print("\nAnzahl Zeilen:")
    print(len(df))

    print("\nDatentypen:")
    print(df.dtypes)