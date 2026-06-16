import pandas as pd

from backend.validation import prepare_single_input, prepare_batch_input
from backend.config import FEATURE_COLUMNS


def predict_single(model, label_encoder, input_data: dict):
    """
    Predict drought risk for one user input.

    Parameters:
        model: loaded trained model pipeline
        label_encoder: loaded label encoder
        input_data: dictionary containing all required feature values

    Returns:
        dictionary containing prediction, confidence, and probabilities
    """

    input_df = prepare_single_input(input_data)

    prediction_encoded = model.predict(input_df)
    prediction_label = label_encoder.inverse_transform(prediction_encoded)[0]

    result = {
        "prediction": prediction_label,
        "confidence": None,
        "probabilities": {}
    }

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(input_df)[0]
        class_names = label_encoder.classes_

        probability_dict = {
            class_name: float(probability)
            for class_name, probability in zip(class_names, probabilities)
        }

        result["probabilities"] = probability_dict
        result["confidence"] = max(probability_dict.values())

    return result


def predict_batch(model, label_encoder, uploaded_df: pd.DataFrame):
    """
    Predict drought risk for multiple rows from an uploaded CSV file.

    Parameters:
        model: loaded trained model pipeline
        label_encoder: loaded label encoder
        uploaded_df: dataframe uploaded by user

    Returns:
        dataframe with prediction results added
    """

    input_df = prepare_batch_input(uploaded_df)

    prediction_encoded = model.predict(input_df)
    prediction_labels = label_encoder.inverse_transform(prediction_encoded)

    output_df = uploaded_df.copy()
    output_df["Predicted_Drought_Risk"] = prediction_labels

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(input_df)
        class_names = label_encoder.classes_

        for index, class_name in enumerate(class_names):
            output_df[f"Probability_{class_name}"] = probabilities[:, index]

        output_df["Confidence"] = probabilities.max(axis=1)

    return output_df


def get_prediction_message(prediction: str):
    """
    Return a simple explanation message based on predicted drought class.
    """

    if prediction == "Normal":
        return {
            "status": "Normal",
            "message": "The model predicts normal conditions based on the provided drought-related indicators.",
            "risk_level": "Low"
        }

    if prediction == "Moderate":
        return {
            "status": "Moderate",
            "message": "The model predicts moderate drought risk. Monitoring and preparedness are recommended.",
            "risk_level": "Medium"
        }

    if prediction == "Severe":
        return {
            "status": "Severe",
            "message": "The model predicts severe drought risk. Immediate attention and response planning are recommended.",
            "risk_level": "High"
        }

    return {
        "status": prediction,
        "message": "Prediction completed.",
        "risk_level": "Unknown"
    }