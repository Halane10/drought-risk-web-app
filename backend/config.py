from pathlib import Path

# Main project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Important folders
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

# Dataset path
DATASET_PATH = DATA_DIR / "Southern_Somalia_Dataset.csv"

# Model file paths
RANDOM_FOREST_MODEL_PATH = MODELS_DIR / "random_forest_model.pkl"
XGBOOST_MODEL_PATH = MODELS_DIR / "xgboost_model.pkl"
SVM_MODEL_PATH = MODELS_DIR / "svm_model.pkl"

LABEL_ENCODER_PATH = MODELS_DIR / "label_encoder.pkl"
FEATURE_COLUMNS_PATH = MODELS_DIR / "feature_columns.pkl"
CAT_COLS_PATH = MODELS_DIR / "cat_cols.pkl"
NUM_COLS_PATH = MODELS_DIR / "num_cols.pkl"
METADATA_PATH = MODELS_DIR / "model_metadata.pkl"

# Model dropdown options
MODEL_REGISTRY = {
    "SVM + Class Weight Balanced (Final Selected Model)": SVM_MODEL_PATH,
    "XGBoost + Class Weight": XGBOOST_MODEL_PATH,
    "Random Forest + SMOTENC": RANDOM_FOREST_MODEL_PATH,
}

# Model input columns
CAT_COLS = ["Month", "Region", "District"]

NUM_COLS = [
    "NDVI",
    "NDVI_lag1",
    "NDVI_lag2",
    "Soil_Moisture",
    "Soil_Moisture_lag1",
    "Soil_Moisture_lag2",
    "Temperature",
    "Temperature_lag1",
    "Temperature_lag2",
    "Rainfall",
    "Rainfall_lag1",
    "Rainfall_lag2",
]

FEATURE_COLUMNS = CAT_COLS + NUM_COLS

TARGET_COLUMN = "Drought_Risk_Class"

# Class colors for UI
CLASS_COLORS = {
    "Normal": "#2E7D32",
    "Moderate": "#F9A825",
    "Severe": "#C62828",
}