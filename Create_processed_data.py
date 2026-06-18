from Get_Landslides import load_landslides
from Get_Slopes import ensure_dem_exists, get_slope_at_coordinate, plot_dem


API_KEY_DEM = "12d43f23569bed975a82c9f065e9b071"

NORTH = 48
SOUTH = 43
WEST = 5
EAST = 15

DEM_FILE = "alps_cop30_dem.tif"
LANDSLIDE_FILE = "Global_Landslide_Catalog_Export_rows.csv"

PROCESSED_DATA_FILE = "processed_landslides_alps.csv"



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



# ERA5 Daten hinzufügen:
#def add_era5_data(data):

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

    # später ERA5 hier ergänzen:
    #data = add_era5_data(data)

    if save_to_file:
        data.to_csv(PROCESSED_DATA_FILE, index=False)
        print(f"Processed data gespeichert als: {PROCESSED_DATA_FILE}")

    return data



#Nur ausführen, wenn Datei direkt gestartet wird
if __name__ == "__main__":
    dataset = build_dataset(save_to_file=True)

    print(dataset.head())
    print("Fertige Spalten:")
    print(dataset.columns)
    
    plot_dem(DEM_FILE)