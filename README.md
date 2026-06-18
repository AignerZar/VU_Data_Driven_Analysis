Wir beziehen unsere Daten aus den folgenden Quellen:

Nasa Landslide Katalog:
https://data.nasa.gov/dataset/global-landslide-catalog-export/resource/7dc0d8c1-05f6-4c5c-8fee-20834e4d5d31
- The GLC considers all types of mass movements triggered by rainfall, which have been reported in the media, disaster databases, scientific reports, or other sources.
- The GLC has been compiled since 2007 at NASA Goddard Space Flight Center.
- Achtung, die Koordinatenangaben können problematisch sein. Slopes an diesen Koordinaten sind oft flach, was bedeuten könnte dass die Koordinate nicht immer nur den Anrisspunkt des landslides widerspiegelt sondern vielleicht hin und wieder auch nur den auslaufpunkt im flachen Gelände

Topographiemodell:
https://portal.opentopography.org/raster?opentopoID=OTSDEM.032021.4326.3
- Ein Höhenwert repräsentiert eine Fläche von etwa 30 × 30 m
- Das Copernicus GLO-30 DEM ist ein Raster mit einer Gitterweite von 1 Bogensekunde (0,0002777778° × 0,0002777778°); das entspricht am Äquator etwa 30,9 m × 30,9 m, während die Ost-West-Ausdehnung der Zellen zu den Polen hin aufgrund der Meridiankonvergenz kleiner wird und damit in dieser Richtung feiner als 30 m ist (Ost-West-Auflösung an bestimmten Breitengraden z.B.: Wien (48° N) ca. 20,7 m, 60° N ca. 15,5 m, 80° N ca. 5,4 m)

#[
ERA-5 Land Daten:
https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land?tab=overview
- Land Surface Reanalysis Dataset, aso eine Kombination aus Wetterstationen, Satelliten, Radar und Wettermodellen, die in ein physikalisches Wettermodell eingefügt werden
- Räumliche Auflösung: 0.1° × 0.1° (ungefähr 11 km × 11 km in Mitteleuropa)
- Achtung, räumliche Auflösung ist deutlich ungenauer wie die Hangneigung beispielsweise, also lokale Abweichungen können auftreten.
- Zeitliche Auflösung: 1 Stunde (Die angegebenen Werte gelten also immer für diese eine Stunde)
- ERA5 hat 4 Schichten für die Bodenfeuchte:
    volumetric_soil_water_layer_1
    0 - 7 cm

    volumetric_soil_water_layer_2
    7 - 28 cm

    volumetric_soil_water_layer_3
    28 - 100 cm

    volumetric_soil_water_layer_4
    100 - 289 cm
- ERA5 hat auch die Temperatur: 
    2m_temperature
- Achtung, hat Probleme mit langen Zeitreihen
]#

ERA5 Land hourly time-series data from 1950 to present:
https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-timeseries?tab=overview
- gemacht für timeseries
- Temporal coverage: 1950 to present
- Horizontal resolution: 0.1˚ x 0.1˚
- Temporal resolution: Hourly



Es gibt 3 Files, die nur zur Beschaffung der jeweiligen Daten dienen:

1. Get_Landslides.py:
    - load_landslides(): Funktion, die aus dem NASA Landslide Katalog ein Rechteck um bestimmte Koordinaten rausschneidet und nur die Landslides in dem Rechteck als neue Tabelle ausgibt

2. Get_Slopes.py:
    - download_cop30_dem(): Funktion, die in einem bestimmten Koordinaten Rechteck alle Elevations herunterlädt und in einer TIF Datei speichert. Heruntergeladen wird von
    - ensure_dem_exists(): Funktion die überprüft ob die DEM (Digital Elevation Model) Datei schon existiert oder nochmal neu heruntergeladen werden muss. Werden die Koordinaten für das Rechteck geändert muss die DEM Datei also erst nochmal gelöscht werden, damit der Code das neue Rechteck nochmal herunterlädt
    - get_slope_at_coordinate(): bestimmt die Hangneigung einer Koordinate, indem er ein 3x3-Pixelraster um die gewünschte Koordinate aus der DEM Datei entnimmt und dann aus den Höhenunterschieden die Hangneigung berechnet.
    - create_alps_cmap(): erstellt eine colormap, die für eine elevations Karte gut aussieht
    - plot_dem(): plottet einmal das gesamte Rechteck in dem Landslides betrachtet werden in einer etwas weniger aufgelösten auflösung wie die DEM File, um einen Plot mit unnötig großer Auflösung zu vermeiden

3. Get_ERA5.py:
    -



stehen die ganzen relevanten Funktionen zur Verfügung um an die Daten zu kommen, so werden alle Daten in der File Create_processed_data.py zu einer Tabelle mit allen Events zusammengefügt. Die vollständige Tabelle wird in einer csv Datei gespeichert, sodass in der folgenden main.py Datei mit der Tabelle gearbeitet werden kann und das ML Modell an den Daten trainieren lassen kann.

die ausgeworfene Tabelle processed_landslides_alps.csv besteht also aus folgenden Spalten:
- event_date
- event_time
- longitude
- latitude
- slope_degrees
- elevation_m
(- 3-Tagessumme Niederschlag) ausstehend
(- 1-Tagessumme Niederschlag) ausstehend
(- Ereignisklassifizierung (1:Landslide, 0:kein Landslide))



noch zu tun:

- Ausgabe der 3-Tages- und 1-Tagessumme Niederschlag einer Koordinate und einer Zeit
- Ausgabe der 5-stärksten 3-Tagessumme Niederschlagsevents für eine Koordinate und vor einem Zeitpunkt. (return: 3-Tagessumme, Zeitpunkt, 1-Tagessumme)
- Split der Tabelle in Trainings und Testdaten mit vorgegebenen Split
- überprüfen ob auch die Bodenfeuchte aus den ERA5 Daten herausgelesen werden können



Für den Kartenausschnitt um die Alpen würde ich folgende Koordinaten als Eckpfeiler nehmen:
    links oben (NW): lat(48), lon(5)
    rechts oben (NO): lat(48), lon(15)
    rechts unten (SO): lat(43), lon(15)
    links unten (SW): lat(43), lon(5)
