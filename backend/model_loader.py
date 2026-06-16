import joblib
import streamlit as st

from backend.config import (
    MODEL_REGISTRY,
    LABEL_ENCODER_PATH,
    FEATURE_COLUMNS_PATH,
    CAT_COLS_PATH,
    NUM_COLS_PATH,
    METADATA_PATH
)


@st.cache_resource
def load_model(model_name: str):
    """
    Load a trained machine learning model based on the selected model name.
    """

    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model selected: {model_name}")

    model_path = MODEL_REGISTRY[model_name]

    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = joblib.load(model_path)
    return model


@st.cache_resource
def load_label_encoder():
    """
    Load the label encoder used to convert model output numbers
    back into drought risk class names.
    """

    if not LABEL_ENCODER_PATH.exists():
        raise FileNotFoundError(f"Label encoder file not found: {LABEL_ENCODER_PATH}")

    return joblib.load(LABEL_ENCODER_PATH)


@st.cache_resource
def load_feature_columns():
    """
    Load the feature columns used during model training.
    """

    if FEATURE_COLUMNS_PATH.exists():
        return joblib.load(FEATURE_COLUMNS_PATH)

    return None


@st.cache_resource
def load_cat_cols():
    """
    Load categorical feature column names.
    """

    if CAT_COLS_PATH.exists():
        return joblib.load(CAT_COLS_PATH)

    return None


@st.cache_resource
def load_num_cols():
    """
    Load numeric feature column names.
    """

    if NUM_COLS_PATH.exists():
        return joblib.load(NUM_COLS_PATH)

    return None


@st.cache_resource
def load_metadata():
    """
    Load model metadata such as performance results and recommended model.
    """

    if METADATA_PATH.exists():
        return joblib.load(METADATA_PATH)

    return {}


def get_available_models():
    """
    Return only the models that actually exist in the models folder.
    """

    available_models = []

    for model_name, model_path in MODEL_REGISTRY.items():
        if model_path.exists():
            available_models.append(model_name)

    return available_models