"""
File to define all important configurations, data paths etc. 
"""
DATA_PATH = "processed_landslides_alps.csv"
PREDICTION_OUTPUT_PATH = "bayesian_landslide_predictions.csv"

RANDOM_SEED = 42
TEST_SIZE = 0.25
THRESHOLD = 0.4

TARGET = "landslide"

FEATURES = [
    "slope_degrees",
    "elevation_m",
    "temperature_2m_C",
    "soil_temperature_level_1_C",
    "soil_temperature_level_2_C",
    "precip_hourly_mm",
    "precip_3h_mm",
    "precip_1d_mm",
    "precip_3d_mm",
]