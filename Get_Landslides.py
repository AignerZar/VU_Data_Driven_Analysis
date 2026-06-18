import pandas as pd

def load_landslides(filepath_landslides, lat_min, lat_max, lon_min, lon_max):
    data = pd.read_csv(filepath_landslides, usecols=["event_date", "event_time", "longitude", "latitude"])
    print("Anzahl vor Filterung:", len(data))

    data_alps = data[
        (data["latitude"] >= lat_min) &
        (data["latitude"] <= lat_max) &
        (data["longitude"] >= lon_min) &
        (data["longitude"] <= lon_max)
    ].copy()  #alle Einträge außerhalb des Rechtecks um die Alpen werden nicht beachtet

    print("Anzahl nach Filterung:", len(data_alps))

    return data_alps
