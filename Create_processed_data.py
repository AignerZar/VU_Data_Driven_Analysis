from Get_Landslides import load_landslides
from Get_Slopes import ensure_dem_exists, get_slope_at_coordinate, plot_dem
from Get_ERA5 import get_era5_timeseries_for_coordinate, get_era5_grid_point

import pandas as pd


API_KEY_DEM = "12d43f23569bed975a82c9f065e9b071"

NORTH = 48
SOUTH = 43
WEST = 5
EAST = 15

DEM_FILE = "alps_cop30_dem.tif"
LANDSLIDE_FILE = "Global_Landslide_Catalog_Export_rows.csv"

PROCESSED_DATA_FILE = "processed_landslides_alps.csv"

ERA5_START_DATE = "1950-01-01"
ERA5_END_DATE = "2024-12-31"

NEGATIVE_EVENTS_PER_GRID_POINT = 5
NEGATIVE_EVENT_EXCLUSION_DAYS = 7 #Negative Events dürfen nicht innerhalb von ±7 Tagen um einen bekannten Landslide liegen.
NEGATIVE_EVENT_SEPARATION_DAYS = 3



#macht aus event_date ein datetime format, weil da eh datum und zeit drinnensteht
def create_event_datetime(row):
    return pd.to_datetime(row["event_date"], errors="coerce")



#fügt ERA5 Daten hinzu
def add_era5_data_to_landslides(data):
    data = data.copy()

    data["event_datetime"] = data.apply(create_event_datetime, axis=1)

    era5_rows = []

    for index, row in data.iterrows():
        lat = row["latitude"]
        lon = row["longitude"]
        event_datetime = row["event_datetime"]

        if pd.isna(event_datetime):
            print(f"Ungültige Zeit bei Index {index}")
            era5_rows.append({})
            continue

        era5_df = get_era5_timeseries_for_coordinate(
            lat=lat,
            lon=lon,
            start_date=ERA5_START_DATE,
            end_date=ERA5_END_DATE,
            save_csv=True
        )

        era5_df["datetime"] = pd.to_datetime(era5_df["datetime"])

        nearest_index = (era5_df["datetime"] - event_datetime).abs().idxmin()
        era5_event = era5_df.loc[nearest_index].to_dict()

        if pd.isna(era5_event.get("precip_3d_mm")):
            print(f"ERA5 NaN bei Landslide Index {index}, lat={lat}, lon={lon}")

        era5_rows.append(era5_event)

    era5_data = pd.DataFrame(era5_rows)

    columns_to_add = [
        "temperature_2m_C",
        "soil_temperature_level_1_C",
        "soil_temperature_level_2_C",
        "precip_hourly_mm",
        "precip_3h_mm",
        "precip_1d_mm",
        "precip_3d_mm",
    ]

    for col in columns_to_add:
        data[col] = era5_data[col].values

    data["landslide"] = 1

    data = data.drop(
        columns=["event_date", "event_time"],
        errors="ignore"
    )

    return data



# erzeugt negative Events
def create_negative_events(data):
    negative_rows = []

    data = data.copy()
    data["era5_grid_lat"], data["era5_grid_lon"] = zip(
        *data.apply(
            lambda row: get_era5_grid_point(row["latitude"], row["longitude"]),
            axis=1
        )
    )

    grouped = data.groupby(["era5_grid_lat", "era5_grid_lon"])

    for (grid_lat, grid_lon), group in grouped:
        print(f"Erzeuge negative Events für ERA5 grid: {grid_lat}, {grid_lon}")

        reference_row = group.iloc[0]

        era5_df = get_era5_timeseries_for_coordinate(
            lat=grid_lat,
            lon=grid_lon,
            start_date=ERA5_START_DATE,
            end_date=ERA5_END_DATE,
            save_csv=True
        )

        era5_df["datetime"] = pd.to_datetime(era5_df["datetime"])

        era5_df = era5_df.dropna(subset=["precip_3d_mm"])

        if len(era5_df) == 0:
            print(f"Keine gültigen ERA5-Daten für grid {grid_lat}, {grid_lon}")
            continue

        landslide_times = pd.to_datetime(group["event_datetime"]).dropna()

        candidate_df = era5_df.copy()

        for landslide_time in landslide_times:
            min_time = landslide_time - pd.Timedelta(days=NEGATIVE_EVENT_EXCLUSION_DAYS)
            max_time = landslide_time + pd.Timedelta(days=NEGATIVE_EVENT_EXCLUSION_DAYS)

            candidate_df = candidate_df[
                ~(
                    (candidate_df["datetime"] >= min_time) &
                    (candidate_df["datetime"] <= max_time)
                )
            ]

        top_rain_events = []
        candidate_df = candidate_df.sort_values("precip_3d_mm", ascending=False)

        while len(top_rain_events) < NEGATIVE_EVENTS_PER_GRID_POINT and len(candidate_df) > 0:
            selected_event = candidate_df.iloc[0]
            top_rain_events.append(selected_event)

            selected_time = selected_event["datetime"]

            min_time = selected_time - pd.Timedelta(days=NEGATIVE_EVENT_SEPARATION_DAYS)
            max_time = selected_time + pd.Timedelta(days=NEGATIVE_EVENT_SEPARATION_DAYS)

            candidate_df = candidate_df[
                ~(
                    (candidate_df["datetime"] >= min_time) &
                    (candidate_df["datetime"] <= max_time)
                )
            ]

        top_rain_events = pd.DataFrame(top_rain_events)

        for _, era5_row in top_rain_events.iterrows():
            negative_rows.append({
                "event_datetime": era5_row["datetime"],
                "longitude": reference_row["longitude"],
                "latitude": reference_row["latitude"],
                "slope_degrees": reference_row["slope_degrees"],
                "elevation_m": reference_row["elevation_m"],
                "temperature_2m_C": era5_row["temperature_2m_C"],
                "soil_temperature_level_1_C": era5_row["soil_temperature_level_1_C"],
                "soil_temperature_level_2_C": era5_row["soil_temperature_level_2_C"],
                "precip_hourly_mm": era5_row["precip_hourly_mm"],
                "precip_3h_mm": era5_row["precip_3h_mm"],
                "precip_1d_mm": era5_row["precip_1d_mm"],
                "precip_3d_mm": era5_row["precip_3d_mm"],
                "landslide": 0,
            })

    return pd.DataFrame(negative_rows)



# Slopes hinzufügen
def add_slope_data(data, dem_file):
    slopes = []
    elevations = []

    for index, row in data.iterrows():
        lat = row["latitude"]
        lon = row["longitude"]

        try:
            slope, elevation = get_slope_at_coordinate(
                lat=lat,
                lon=lon,
                dem_file=dem_file
            )

        except Exception as e:
            print(f"Fehler bei Index {index}, lat={lat}, lon={lon}: {e}")
            slope = None
            elevation = None

        slopes.append(slope)
        elevations.append(elevation)

    data = data.copy()
    data["slope_degrees"] = slopes
    data["elevation_m"] = elevations

    return data



# Processed Data File erstellen
def build_dataset(save_to_file=True):
    ensure_dem_exists(
        south=SOUTH,
        north=NORTH,
        west=WEST,
        east=EAST,
        dem_file=DEM_FILE,
        api_key=API_KEY_DEM
    )

    data = load_landslides(
        filepath_landslides=LANDSLIDE_FILE,
        lat_min=SOUTH,
        lat_max=NORTH,
        lon_min=WEST,
        lon_max=EAST
    )

    data = add_slope_data(
        data=data,
        dem_file=DEM_FILE
    )

    data = add_era5_data_to_landslides(data)

    negative_data = create_negative_events(data)

    data = pd.concat(
        [data, negative_data],
        ignore_index=True
    )

    if save_to_file:
        print("\nSpalten vor dem Speichern:")
        print(data.columns.tolist())
        data.to_csv(PROCESSED_DATA_FILE, index=False)
        print(f"Processed data gespeichert als: {PROCESSED_DATA_FILE}")

    return data



#Nur ausführen, wenn Datei direkt gestartet wird
if __name__ == "__main__":
    dataset = build_dataset(save_to_file=True)
    #dataset = pd.read_csv(PROCESSED_DATA_FILE) #falls nur der plot gemacht werden soll und processed data file schon existiert

    print(dataset.head())
    print("Fertige Spalten:")
    print(dataset.columns)
    
    plot_dem(DEM_FILE, landslides=dataset)