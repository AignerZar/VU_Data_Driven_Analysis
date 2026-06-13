import pandas as pd
import numpy

#Landslide Katalog einlesen
filepath_landslides = "Global_Landslide_Catalog_Export_rows.csv"
data = pd.read_csv(filepath_landslides, usecols=["event_date", "event_time", "longitude", "latitude"])
print("Anzahl vor Filterung:", len(data))

lat_min, lat_max = 43, 48 #nur Landslides in den Alpen
lon_min, lon_max = 5, 15

data_alps = data[
    (data["latitude"] >= lat_min) &
    (data["latitude"] <= lat_max) &
    (data["longitude"] >= lon_min) &
    (data["longitude"] <= lon_max)
] #alle Einträge außerhalb des Rechtecks um die Alpen rausschmeißen

print("Anzahl nach Filterung:", len(data_alps))
print(data_alps.head())

