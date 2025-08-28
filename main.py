import numpy as np
from bmi_topography import Topography
import matplotlib.pyplot as plt
from scipy.ndimage import zoom
import soundfile as sf  # optional for saving
from enum import Enum



def bbox_from_center(center_lat: float, center_lon: float, side_km: float):
    """Berechne (south, north, west, east) für eine quadratische Bounding-Box
    mit gegebener Seitenlänge (in km) und Mittelpunkt (lat, lon).

    Näherung: 1° Breite ≈ 111.32 km, 1° Länge ≈ 111.32 * cos(Breite) km.
    """
    km_per_deg_lat = 111.32
    km_per_deg_lon = 111.32 * np.cos(np.deg2rad(center_lat))
    half_side_km = side_km / 2.0
    dlat = half_side_km / km_per_deg_lat
    dlon = half_side_km / km_per_deg_lon
    south = center_lat - dlat
    north = center_lat + dlat
    west = center_lon - dlon
    east = center_lon + dlon
    return south, north, west, east

def load_topography(center_str: str, side_km: float):
    center_lat, center_lon = map(float, center_str.split(", "))
    south, north, west, east = bbox_from_center(center_lat, center_lon, side_km)

    params = Topography.DEFAULT.copy()
    # Bounding-Box setzen
    params["south"] = south
    params["north"] = north
    params["west"] = west
    params["east"] = east

    topo = Topography(**params)
    print("download finished")
    # print("Download-URL:", topo.url)
    # dem_path = topo.fetch()
    # print("Heruntergeladene Datei:", dem_path)

    da = topo.load().as_numpy().squeeze()
    return da

def resample_data(data, frameSize, numFrames):
    src_rows, src_cols = data.shape
    zoom_factors = (numFrames / src_rows, frameSize / src_cols)
    resampledData = zoom(data, zoom_factors, order=1)
    return np.flipud(resampledData)

def plot_topography(data, side_km):
    x = np.linspace(-side_km/2, side_km/2, data.shape[1])
    y = np.linspace(-side_km/2, side_km/2, data.shape[0])
    X, Y = np.meshgrid(x, y)

    print("close plot window to continue")

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(X, Y, data, cmap="terrain")
    ax.set_xlabel("West/East (km)")
    ax.set_ylabel("North/South (km)")
    ax.set_zlabel("Elevation (m)")
    plt.show()


def export_wavetable(grid: np.ndarray, filename: str | None = None) -> np.ndarray:

    if grid.ndim != 2:
        raise ValueError("grid must be 2D (numFrames, frameSize)")

    print("exporting wavetable...")

    table = grid.astype(np.float32).reshape(-1)

    peak = float(np.max(np.abs(table))) if table.size else 1.0
    if peak > 0:
        table = ((table / peak) * 2.0 - 1.0).astype(np.float32)

    if filename and sf is not None:
        sf.write(filename, table, 44100)
    return table

class TopDir(Enum):
    N = "N"
    E = "E"
    S = "S"
    W = "W"

def rotate_data(data, topDir: TopDir):
    if topDir == TopDir.N:
        return data
    elif topDir == TopDir.E:
        return np.rot90(data, k=1)
    elif topDir == TopDir.S:
        return np.rot90(data, k=2)
    elif topDir == TopDir.W:
        return np.rot90(data, k=3)

if __name__ == "__main__":
    center_str = "46.18870992001379, 8.843108172745026"
    side_km = 10.0
    frameSize = 2048  # Ableton 1024, Vital 2048
    numFrames = 256   # Ableton <= 256

    data = load_topography(center_str, side_km)
    resampledData = resample_data(data, frameSize, numFrames)
    plot_topography(resampledData, side_km)
    export_wavetable(resampledData, "test.wav")