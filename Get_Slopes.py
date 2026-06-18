#um zu prüfen ob DEM Datei schon existiert:
import os

#damit mach man die Anfrage an die OpenTopography-API:
import requests

#zum lesen und verarbeiten von GeoTIFF-Dateien:
import rasterio
from rasterio.warp import Resampling #für das downsampling zum plotten

#für Geo-Operationen
from pyproj import Transformer, Geod

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

# Download Digital Elevation Model (DEM)
def download_cop30_dem(south, north, west, east, out_file, api_key):
    url = "https://portal.opentopography.org/API/globaldem"

    params = {
        "demtype": "COP30", # 30-Meter Auflösung
        "south": south,
        "north": north,
        "west": west,
        "east": east,
        "outputFormat": "GTiff",
        "API_Key": api_key,
    }

    r = requests.get(url, params=params) #Befehl sendet die Anfrage an OpenTopography
    r.raise_for_status() #Falls ein Fehler kommt bricht python hier ab

    with open(out_file, "wb") as f: #Datei wird geschrieben
        f.write(r.content)

    return out_file



def ensure_dem_exists(south, north, west, east, dem_file, api_key):
    if not os.path.exists(dem_file):
        print("Downloading DEM...")
        download_cop30_dem(
            south=south,
            north=north,
            west=west,
            east=east,
            out_file=dem_file,
            api_key=api_key
        )
        print("Download finished.")
    else:
        print("DEM already exists, skipping download.")



# Hangneigung einer einzelnen Koordinate berechnen:
def get_slope_at_coordinate(lat, lon, dem_file):
    geod = Geod(ellps="WGS84") #Erdmodell wird erstellt um abstände zwischen koordinaten zu berechnen, da längengrade nicht überall gleichweit auseinander sind

    with rasterio.open(dem_file) as src:

        # Falls DEM nicht in EPSG:4326 ist, Koordinate ins DEM-Koordinatensystem transformieren
        if src.crs.to_string() != "EPSG:4326":
            transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
            x, y = transformer.transform(lon, lat)
        else:
            x, y = lon, lat

        row, col = rasterio.transform.rowcol(src.transform, x, y) #aus der Koordinate wird ein Rasterpixel

        # 3x3 Fenster um den Punkt lesen
        window = rasterio.windows.Window(col - 1, row - 1, 3, 3)
        elevation = src.read(1, window=window).astype(float)

        if src.nodata is not None:
            elevation[elevation == src.nodata] = np.nan

        if elevation.shape != (3, 3):
            raise ValueError("Koordinate liegt zu nah am Rand des DEMs.")

        if np.isnan(elevation).any():
            raise ValueError("Im 3x3-Fenster gibt es NoData-Werte.")

        z_center = elevation[1, 1]

        # Koordinaten der Nachbarpixel bestimmen
        x_left, y_left = src.xy(row, col - 1)
        x_right, y_right = src.xy(row, col + 1)
        x_up, y_up = src.xy(row - 1, col)
        x_down, y_down = src.xy(row + 1, col)

        # Distanzen in Metern berechnen
        _, _, dx = geod.inv(x_left, y_left, x_right, y_right)
        _, _, dy = geod.inv(x_up, y_up, x_down, y_down)

        # Höhenänderung pro Meter
        dz_dx = (elevation[1, 2] - elevation[1, 0]) / dx
        dz_dy = (elevation[2, 1] - elevation[0, 1]) / dy

        slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
        slope_deg = np.degrees(slope_rad)

        return float(slope_deg), float(z_center)



#colormap
def create_alps_cmap():
    return LinearSegmentedColormap.from_list(
        "alps",
        [
            "#16662a",
            "#65af2c",
            "#ccba84",
            "#836343",
            "#bdbdbd",
            "#ffffff",
        ]
    )



# PLOT DEM OVER ALPS
def plot_dem(dem_file, max_pixels=1200, sea_level_threshold=0.1):
    alps_cmap = create_alps_cmap()

    with rasterio.open(dem_file) as src:

        # Downsampling-Faktor bestimmen
        scale = max(src.width / max_pixels, src.height / max_pixels, 1)

        out_height = int(src.height / scale)
        out_width = int(src.width / scale)

        elevation = src.read(
            1,
            out_shape=(out_height, out_width),
            resampling=Resampling.bilinear
        ).astype(float)

        if src.nodata is not None:
            elevation[elevation == src.nodata] = np.nan

        bounds = src.bounds

        # Meer/Wasser: alles <= 0.1 m
        sea_mask = elevation <= sea_level_threshold

        # Landdaten: Wasser ausblenden
        land = elevation.copy()
        land[sea_mask] = np.nan

        plt.figure(figsize=(10, 6))

        # Erst Land plotten
        plt.imshow(
            land,
            extent=[bounds.left, bounds.right, bounds.bottom, bounds.top],
            origin="upper",
            cmap=alps_cmap,
            vmin=0,
            vmax=np.nanmax(land)
        )

        plt.colorbar(label="Elevation [m]")

        # Dann Meer als eigene blaue Maske darüberlegen
        sea_layer = np.where(sea_mask, 1, np.nan)

        sea_cmap = ListedColormap(["deepskyblue"])

        plt.imshow(
            sea_layer,
            extent=[bounds.left, bounds.right, bounds.bottom, bounds.top],
            origin="upper",
            cmap=sea_cmap,
            alpha=1.0
        )

        sea_patch = mpatches.Patch(color="deepskyblue", label="Sea / ≤ 0.1 m")
        plt.legend(handles=[sea_patch], loc="lower right")

        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title("Copernicus GLO-30 DEM over the Alps")
        plt.tight_layout()
        plt.show()
