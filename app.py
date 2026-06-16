import streamlit as st
import pandas as pd
import plotly.express as px

from backend.config import DATASET_PATH, ASSETS_DIR, CLASS_COLORS
from backend.model_loader import (
    get_available_models,
    load_model,
    load_label_encoder,
    load_metadata
)
from backend.predictor import (
    predict_single,
    get_prediction_message
)


# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Drought Risk Prediction System",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -----------------------------
# Load CSS
# -----------------------------
def load_css(dark_mode=True):
    css_path = ASSETS_DIR / "styles.css"

    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as file:
            st.markdown(f"<style>{file.read()}</style>", unsafe_allow_html=True)

    # Hide Streamlit default top menu / deploy area
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        [data-testid="stToolbar"] {
            display: none !important;
        }

        [data-testid="stDecoration"] {
            display: none !important;
        }

        [data-testid="stStatusWidget"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Light mode override
    if not dark_mode:
        st.markdown(
            """
            <style>
            /* -----------------------------
               Professional Light Mode
            ----------------------------- */

            .stApp {
                background: #F8FAFC !important;
                color: #0F172A !important;
            }

            .block-container {
                max-width: 1180px !important;
                padding-top: 2rem !important;
                padding-left: 3rem !important;
                padding-right: 3rem !important;
                color: #0F172A !important;
            }

            /* Sidebar */
            [data-testid="stSidebar"] {
                background: #FFFFFF !important;
                border-right: 1px solid #E2E8F0 !important;
                box-shadow: 6px 0 24px rgba(15, 23, 42, 0.06) !important;
            }

            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] span {
                color: #0F172A !important;
            }

            [data-testid="stSidebar"] p {
                color: #475569 !important;
            }

            /* Sidebar nav items */
            [data-testid="stSidebar"] [role="radiogroup"] label {
                background: #FFFFFF !important;
                color: #0F172A !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 12px !important;
                padding: 10px 12px !important;
                margin-bottom: 10px !important;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04) !important;
            }

            [data-testid="stSidebar"] [role="radiogroup"] label:hover {
                background: #ECFDF5 !important;
                border-color: #22C55E !important;
                transform: translateX(3px);
            }

            /* Hero header */
            .hero-section {
                background: #FFFFFF !important;
                border: 1px solid #D1FAE5 !important;
                border-left: 8px solid #16A34A !important;
                border-radius: 22px !important;
                padding: 34px 36px !important;
                box-shadow: 0 18px 45px rgba(15, 23, 42, 0.10) !important;
            }

            .hero-badge {
                background: #DCFCE7 !important;
                color: #047857 !important;
                border: 1px solid #BBF7D0 !important;
                font-weight: 900 !important;
            }

            .main-title {
                color: #064E3B !important;
                font-weight: 950 !important;
            }

            .subtitle {
                color: #334155 !important;
            }

            /* Headings */
            h1, h2, h3, h4, h5, h6 {
                color: #0F172A !important;
                font-weight: 900 !important;
            }

            p, label, span {
                color: #0F172A !important;
            }

            /* Information cards */
            .info-card {
                background: #FFFFFF !important;
                color: #0F172A !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 18px !important;
                box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08) !important;
            }

            .info-card b {
                color: #047857 !important;
            }

            /* Home metric cards */
            .metric-card {
                background: #FFFFFF !important;
                color: #0F172A !important;
                border: 1px solid #E2E8F0 !important;
                border-left: 7px solid #16A34A !important;
                box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08) !important;
            }

            .metric-card h3 {
                color: #064E3B !important;
            }

            .metric-card p {
                color: #475569 !important;
            }

            /* Form design */
            [data-testid="stForm"] {
                background: #FFFFFF !important;
                border: 2px solid #BBF7D0 !important;
                border-radius: 22px !important;
                box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08) !important;
            }

            [data-testid="stForm"] h2,
            [data-testid="stForm"] h3,
            [data-testid="stForm"] label {
                color: #0F172A !important;
            }

            /* Inputs */
            [data-testid="stTextInput"] input,
            [data-testid="stNumberInput"] input {
                background-color: #F8FAFC !important;
                color: #0F172A !important;
                border: 1px solid #CBD5E1 !important;
                border-radius: 10px !important;
            }

            [data-testid="stSelectbox"] div {
                background-color: #F8FAFC !important;
                color: #0F172A !important;
                border-color: #CBD5E1 !important;
            }

            /* Buttons */
            .stButton > button,
            div[data-testid="stFormSubmitButton"] button {
                background: linear-gradient(135deg, #16A34A, #059669) !important;
                color: #FFFFFF !important;
                border: none !important;
                box-shadow: 0 10px 24px rgba(22, 163, 74, 0.22) !important;
            }

            .stButton > button:hover,
            div[data-testid="stFormSubmitButton"] button:hover {
                background: linear-gradient(135deg, #22C55E, #10B981) !important;
                color: #FFFFFF !important;
            }

            /* Streamlit metrics */
            [data-testid="stMetric"] {
                background: #FFFFFF !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 18px !important;
                padding: 18px !important;
                box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08) !important;
            }

            [data-testid="stMetricLabel"] {
                color: #475569 !important;
                font-weight: 800 !important;
            }

            [data-testid="stMetricValue"] {
                color: #064E3B !important;
                font-weight: 950 !important;
            }

            /* Model information cards */
            .model-summary-card {
                background: #FFFFFF !important;
                border: 1px solid #D1FAE5 !important;
                border-left: 8px solid #16A34A !important;
                box-shadow: 0 16px 35px rgba(15, 23, 42, 0.08) !important;
            }

            .model-summary-title {
                color: #064E3B !important;
            }

            .model-summary-subtitle {
                color: #334155 !important;
            }

            .performance-card {
                background: #FFFFFF !important;
                color: #0F172A !important;
                border: 1px solid #E2E8F0 !important;
                box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08) !important;
            }

            .performance-card-title {
                color: #475569 !important;
            }

            .performance-card-value {
                color: #064E3B !important;
            }

            .performance-card-note {
                color: #64748B !important;
            }

            .section-label {
                color: #0F172A !important;
            }

            /* Prediction result boxes stay readable */
            .normal-box h3,
            .normal-box p,
            .normal-box b {
                color: #14532D !important;
            }

            .warning-box h3,
            .warning-box p,
            .warning-box b {
                color: #78350F !important;
            }

            .severe-box h3,
            .severe-box p,
            .severe-box b {
                color: #7F1D1D !important;
            }

            /* Tables */
            [data-testid="stDataFrame"] {
                background: #FFFFFF !important;
                border-radius: 16px !important;
                box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06) !important;
            }

            /* Alerts */
            .stAlert {
                border-radius: 14px !important;
                color: #0F172A !important;
            }

            /* Lines */
            hr {
                border-color: #E2E8F0 !important;
            }

            /* Toggle area on top-right */
            [data-testid="stToggle"] label {
                color: #064E3B !important;
                font-weight: 800 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_dataset():
    if DATASET_PATH.exists():
        df = pd.read_csv(DATASET_PATH)

        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            df["Year"] = df["Date"].dt.year

        return df

    return pd.DataFrame()


# -----------------------------
# Header
# -----------------------------
def render_header():
    st.markdown(
        """
        <div class="hero-section">
            <div class="hero-badge">Southern Somalia Drought Intelligence System</div>
            <div class="main-title">Drought Risk Prediction System</div>
            <div class="subtitle">
                A machine learning-based decision-support prototype for predicting drought risk
                using NDVI, rainfall, temperature, soil moisture, and historical lag indicators
                across Southern Somalia from 2000 to 2025.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# -----------------------------
# Home Page
# -----------------------------
def render_home(df):
    render_header()

    st.markdown(
        """
        <div class="info-card">
        This web application is a research-based decision-support prototype developed
        to present drought risk predictions in an accessible and structured manner.
        The system connects trained machine learning models with a user-friendly interface
        to classify drought risk into <b>Normal</b>, <b>Moderate</b>, or <b>Severe</b>.
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            '<div class="metric-card"><h3>6</h3><p>Regions</p></div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            '<div class="metric-card"><h3>29</h3><p>Districts</p></div>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            '<div class="metric-card"><h3>2000–2025</h3><p>Study Period</p></div>',
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            '<div class="metric-card"><h3>SVM</h3><p>Final Model</p></div>',
            unsafe_allow_html=True
        )

    st.subheader("Study Area")
    st.write(
        "The system focuses on Southern Somalia, specifically Bay, Bakool, Gedo, "
        "Lower Shabelle, Middle Juba, and Lower Juba."
    )

    st.subheader("Drought Indicators Used")
    st.write(
        "The model uses drought-related indicators including NDVI, rainfall, temperature, "
        "soil moisture, and their lag features."
    )

    if not df.empty:
        st.subheader("Dataset Preview")
        st.dataframe(df.head(10), use_container_width=True)
    else:
        st.warning("Dataset file was not found in the data folder.")


# -----------------------------
# Environmental Warning Logic
# -----------------------------
def get_environmental_warning(input_data):
    """
    Rule-based drought stress warning.
    This does not replace the machine learning prediction.
    It gives extra interpretation when environmental indicators show dangerous drought stress.
    """

    rainfall = input_data["Rainfall"]
    rainfall_lag1 = input_data["Rainfall_lag1"]
    rainfall_lag2 = input_data["Rainfall_lag2"]

    ndvi = input_data["NDVI"]
    ndvi_lag1 = input_data["NDVI_lag1"]
    ndvi_lag2 = input_data["NDVI_lag2"]

    soil = input_data["Soil_Moisture"]
    soil_lag1 = input_data["Soil_Moisture_lag1"]
    soil_lag2 = input_data["Soil_Moisture_lag2"]

    temperature = input_data["Temperature"]

    warnings = []

    # Three-month rainfall shortage
    if rainfall == 0 and rainfall_lag1 == 0 and rainfall_lag2 == 0:
        warnings.append(
            "Rainfall has been zero for three consecutive months."
        )

    # Very low vegetation condition
    if ndvi <= 0.15 and ndvi_lag1 <= 0.15 and ndvi_lag2 <= 0.15:
        warnings.append(
            "NDVI values are very low, indicating weak vegetation condition."
        )

    # Very low soil moisture
    if soil <= 0.03 and soil_lag1 <= 0.03 and soil_lag2 <= 0.03:
        warnings.append(
            "Soil moisture values are very low, indicating dry land surface conditions."
        )

    # High temperature
    if temperature >= 32:
        warnings.append(
            "Temperature is high, which can increase drought stress."
        )

    # Decide warning level
    if len(warnings) >= 3:
        return {
            "level": "High",
            "title": "High Environmental Drought Stress Detected",
            "message": (
                "Although the machine learning model provides the final predicted class, "
                "the input indicators show strong drought-stress conditions. "
                "This case should be treated with serious attention."
            ),
            "details": warnings
        }

    elif len(warnings) == 2:
        return {
            "level": "Medium",
            "title": "Moderate Environmental Drought Stress Detected",
            "message": (
                "Some drought-related indicators show stress conditions. "
                "Monitoring is recommended."
            ),
            "details": warnings
        }

    elif len(warnings) == 1:
        return {
            "level": "Low",
            "title": "Early Environmental Warning",
            "message": (
                "One drought-related indicator shows possible stress. "
                "Further monitoring is recommended."
            ),
            "details": warnings
        }

    else:
        return None
# -----------------------------
# Prediction Box Style
# -----------------------------
def get_prediction_box_class(prediction):
    if prediction == "Normal":
        return "normal-box"
    elif prediction == "Moderate":
        return "warning-box"
    elif prediction == "Severe":
        return "severe-box"
    else:
        return "info-card"
# -----------------------------
# Placeholder Pages
# -----------------------------
def render_predict_page(df):
    render_header()

    st.subheader("Manual Drought Risk Prediction")

    st.markdown(
        """
        <div class="info-card">
        This page allows users to manually enter drought-related indicator values and predict
        the drought risk class using one of the trained machine learning models. The final
        recommended model is <b>SVM + Class Weight Balanced</b>, but Random Forest and XGBoost
        are also available for comparison.
        </div>
        """,
        unsafe_allow_html=True
    )

    available_models = get_available_models()

    if len(available_models) == 0:
        st.error("No trained model files were found in the models folder.")
        return

    selected_model_name = st.selectbox(
        "Select Model for Prediction",
        available_models,
        index=0
    )

    if selected_model_name == "SVM + Class Weight Balanced (Final Selected Model)":
        st.success(
            "This is the final selected model because it achieved the best drought-class recall "
            "for Moderate and Severe drought."
        )
    else:
        st.info(
            "This model is included for comparison because it was part of the experimental evaluation."
        )

    model = load_model(selected_model_name)
    label_encoder = load_label_encoder()

    if not df.empty:
        regions = sorted(df["Region"].unique().tolist())
    else:
        regions = ["Bay", "Bakool", "Gedo", "Lower Shabelle", "Middle Juba", "Lower Juba"]

    st.markdown("---")
    st.markdown("---")
    st.subheader("Location and Time Selection")

    loc_col1, loc_col2, loc_col3 = st.columns(3)

    with loc_col1:
        month = st.selectbox(
            "Month",
            list(range(1, 13)),
            key="manual_month"
        )

    with loc_col2:
        region = st.selectbox(
            "Region",
            regions,
            key="manual_region"
        )

    if not df.empty:
        districts = sorted(
            df[df["Region"] == region]["District"].unique().tolist()
        )
    else:
        districts = []

    with loc_col3:
        district = st.selectbox(
            "District",
            districts,
            key=f"manual_district_{region}"
        )
    with st.form("manual_prediction_form"):
        st.subheader("Input Drought Indicators")

        col1, col2, col3,col4 = st.columns(4)

        with col1:
            ndvi = st.number_input("NDVI", min_value=0.0, max_value=1.0, value=0.35, step=0.01)
            ndvi_lag1 = st.number_input("NDVI Lag 1", min_value=0.0, max_value=1.0, value=0.35, step=0.01)
            ndvi_lag2 = st.number_input("NDVI Lag 2", min_value=0.0, max_value=1.0, value=0.35, step=0.01)

        with col2:
            soil_moisture = st.number_input("Soil Moisture", min_value=0.0, max_value=1.0, value=0.15, step=0.01)
            soil_moisture_lag1 = st.number_input("Soil Moisture Lag 1", min_value=0.0, max_value=1.0, value=0.15, step=0.01)
            soil_moisture_lag2 = st.number_input("Soil Moisture Lag 2", min_value=0.0, max_value=1.0, value=0.15, step=0.01)

        with col3:
            temperature = st.number_input("Temperature (°C)", min_value=10.0, max_value=50.0, value=29.0, step=0.1)
            temperature_lag1 = st.number_input("Temperature Lag 1 (°C)", min_value=10.0, max_value=50.0, value=29.0, step=0.1)
            temperature_lag2 = st.number_input("Temperature Lag 2 (°C)", min_value=10.0, max_value=50.0, value=29.0, step=0.1)
        with col4:
            rainfall = st.number_input("Rainfall (mm)", min_value=0.0, max_value=1000.0, value=20.0, step=1.0)
            rainfall_lag1 = st.number_input("Rainfall Lag 1 (mm)", min_value=0.0, max_value=1000.0, value=20.0, step=1.0)
            rainfall_lag2 = st.number_input("Rainfall Lag 2 (mm)", min_value=0.0, max_value=1000.0, value=20.0, step=1.0)

        button_col1, button_col2, button_col3 = st.columns([2, 1, 2])
 
        with button_col2:
         submitted = st.form_submit_button(
        "Predict Drought Risk",
        use_container_width=True
    )

    if submitted:
        input_data = {
            "Month": month,
            "Region": region,
            "District": district,
            "NDVI": ndvi,
            "NDVI_lag1": ndvi_lag1,
            "NDVI_lag2": ndvi_lag2,
            "Soil_Moisture": soil_moisture,
            "Soil_Moisture_lag1": soil_moisture_lag1,
            "Soil_Moisture_lag2": soil_moisture_lag2,
            "Temperature": temperature,
            "Temperature_lag1": temperature_lag1,
            "Temperature_lag2": temperature_lag2,
            "Rainfall": rainfall,
            "Rainfall_lag1": rainfall_lag1,
            "Rainfall_lag2": rainfall_lag2,
        }

        environmental_warning = get_environmental_warning(input_data)

        try:
            result = predict_single(
                model=model,
                label_encoder=label_encoder,
                input_data=input_data
            )

            prediction = result["prediction"]
            message_data = get_prediction_message(prediction)
            box_class = get_prediction_box_class(prediction)

            st.markdown("---")
            st.subheader("Prediction Result")

            st.markdown(
                f"""
                <div class="{box_class}">
                    <h3>Predicted Drought Risk: {prediction}</h3>
                    <p><b>Risk Level:</b> {message_data["risk_level"]}</p>
                    <p>{message_data["message"]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if environmental_warning is not None:
                if environmental_warning["level"] == "High":
                    warning_color = "#C62828"
                    warning_bg = "#FFEBEE"
                elif environmental_warning["level"] == "Medium":
                    warning_color = "#F57F17"
                    warning_bg = "#FFF8E1"
                else:
                    warning_color = "#1565C0"
                    warning_bg = "#E3F2FD"

                warning_details = "".join(
                    [f"<li>{item}</li>" for item in environmental_warning["details"]]
                )

                st.markdown(
                    f"""
                    <div style="
                        background: {warning_bg};
                        color: {warning_color};
                        padding: 18px;
                        border-radius: 14px;
                        border-left: 6px solid {warning_color};
                        margin-top: 15px;
                    ">
                        <h4>{environmental_warning["title"]}</h4>
                        <p>{environmental_warning["message"]}</p>
                        <ul>
                            {warning_details}
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            if result["confidence"] is not None:
                st.metric(
                    "Prediction Confidence",
                    f"{result['confidence'] * 100:.2f}%"
                )

            if result["probabilities"]:
                probability_df = pd.DataFrame({
                    "Class": list(result["probabilities"].keys()),
                    "Probability": list(result["probabilities"].values())
                })

                fig = px.bar(
                    probability_df,
                    x="Class",
                    y="Probability",
                    color="Class",
                    color_discrete_map=CLASS_COLORS,
                    title="Prediction Probability by Drought Class"
                )

                fig.update_layout(
                    yaxis_tickformat=".0%",
                    height=420
                )

                st.plotly_chart(fig, use_container_width=True)

            with st.expander("View Input Values Used for Prediction"):
                st.dataframe(pd.DataFrame([input_data]), use_container_width=True)

        except Exception as error:
            st.error(f"Prediction failed: {error}")


def render_batch_page(df):
    render_header()

    st.subheader("Batch Drought Risk Prediction")

    st.markdown(
        """
        <div class="info-card">
        This page allows users to upload a CSV file containing drought-related indicator values.
        The selected machine learning model will predict drought risk classes for all uploaded records.
        </div>
        """,
        unsafe_allow_html=True
    )

    available_models = get_available_models()

    if len(available_models) == 0:
        st.error("No trained model files were found in the models folder.")
        return

    selected_model_name = st.selectbox(
        "Select Model for Batch Prediction",
        available_models,
        index=0
    )

    if selected_model_name == "SVM + Class Weight Balanced (Final Selected Model)":
        st.success(
            "This is the final selected model recommended for drought risk prediction."
        )
    else:
        st.info(
            "This model is available for comparison because it was included in the experimental evaluation."
        )

    model = load_model(selected_model_name)
    label_encoder = load_label_encoder()

    st.markdown("---")

    st.subheader("Required CSV Columns")

    st.write(
        "Your uploaded CSV file must contain the following input columns:"
    )

    required_columns = [
        "Month",
        "Region",
        "District",
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

    st.dataframe(
        pd.DataFrame({"Required Columns": required_columns}),
        use_container_width=True
    )

    template_df = pd.DataFrame(columns=required_columns)
    template_csv = template_df.to_csv(index=False)

    st.download_button(
        label="Download CSV Template",
        data=template_csv,
        file_name="drought_prediction_template.csv",
        mime="text/csv"
    )

    uploaded_file = st.file_uploader(
        "Upload CSV File for Batch Prediction",
        type=["csv"]
    )

    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)

            st.subheader("Uploaded File Preview")
            st.dataframe(uploaded_df.head(10), use_container_width=True)

            if st.button("Run Batch Prediction"):
                from backend.predictor import predict_batch

                result_df = predict_batch(
                    model=model,
                    label_encoder=label_encoder,
                    uploaded_df=uploaded_df
                )

                st.success("Batch prediction completed successfully.")

                st.subheader("Prediction Results")
                st.dataframe(result_df, use_container_width=True)

                if "Predicted_Drought_Risk" in result_df.columns:
                    prediction_counts = (
                        result_df["Predicted_Drought_Risk"]
                        .value_counts()
                        .reset_index()
                    )

                    prediction_counts.columns = ["Drought Risk Class", "Count"]

                    fig = px.bar(
                        prediction_counts,
                        x="Drought Risk Class",
                        y="Count",
                        color="Drought Risk Class",
                        color_discrete_map=CLASS_COLORS,
                        title="Batch Prediction Result Distribution"
                    )

                    st.plotly_chart(fig, use_container_width=True)

                csv_output = result_df.to_csv(index=False)

                st.download_button(
                    label="Download Prediction Results",
                    data=csv_output,
                    file_name="batch_drought_prediction_results.csv",
                    mime="text/csv"
                )

        except Exception as error:
            st.error(f"Batch prediction failed: {error}")


def render_dashboard_page(df):
    render_header()

    st.subheader("Data Dashboard")

    st.markdown(
        """
        <div class="info-card">
        This dashboard presents visual summaries of drought-related indicators and drought risk
        classes in Southern Somalia. It helps users understand patterns in rainfall, NDVI,
        temperature, soil moisture, and predicted drought classes.
        </div>
        """,
        unsafe_allow_html=True
    )

    if df.empty:
        st.warning("Dataset file was not found in the data folder.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Records", f"{len(df):,}")

    with col2:
        st.metric("Regions", df["Region"].nunique())

    with col3:
        st.metric("Districts", df["District"].nunique())

    st.markdown("---")

    if "Drought_Risk_Class" in df.columns:
        st.subheader("Drought Risk Class Distribution")

        class_counts = df["Drought_Risk_Class"].value_counts().reset_index()
        class_counts.columns = ["Drought Risk Class", "Count"]

        fig_class = px.pie(
            class_counts,
            names="Drought Risk Class",
            values="Count",
            color="Drought Risk Class",
            color_discrete_map=CLASS_COLORS,
            title="Distribution of Drought Risk Classes"
        )

        st.plotly_chart(fig_class, use_container_width=True)

    st.markdown("---")

    st.subheader("Annual Indicator Trend")

    if "Year" not in df.columns and "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df["Year"] = df["Date"].dt.year

    yearly_summary = df.groupby("Year").agg(
        Rainfall=("Rainfall", "mean"),
        NDVI=("NDVI", "mean"),
        Temperature=("Temperature", "mean"),
        Soil_Moisture=("Soil_Moisture", "mean")
    ).reset_index()

    selected_indicator = st.selectbox(
        "Select indicator for annual trend",
        ["Rainfall", "NDVI", "Temperature", "Soil_Moisture"]
    )

    fig_trend = px.line(
        yearly_summary,
        x="Year",
        y=selected_indicator,
        markers=True,
        title=f"Annual Trend of {selected_indicator}"
    )

    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")

    st.subheader("Regional Indicator Comparison")

    regional_summary = df.groupby("Region").agg(
        Rainfall=("Rainfall", "mean"),
        NDVI=("NDVI", "mean"),
        Temperature=("Temperature", "mean"),
        Soil_Moisture=("Soil_Moisture", "mean")
    ).reset_index()

    selected_regional_indicator = st.selectbox(
        "Select indicator for regional comparison",
        ["Rainfall", "NDVI", "Temperature", "Soil_Moisture"],
        key="regional_indicator_select"
    )

    fig_region = px.bar(
        regional_summary,
        x="Region",
        y=selected_regional_indicator,
        title=f"Regional Comparison of {selected_regional_indicator}"
    )

    st.plotly_chart(fig_region, use_container_width=True)

    with st.expander("View Regional Summary Table"):
        st.dataframe(regional_summary, use_container_width=True)


def render_model_info_page():
    render_header()

    st.subheader("Model Information")

    st.markdown(
        """
        <div class="info-card">
        This page presents the performance of the trained machine learning models used in the drought
        risk prediction system. Random Forest, XGBoost, and SVM were trained and evaluated. The final
        recommended model is <b>SVM + Class Weight Balanced</b> because it achieved the strongest recall
        for Moderate and Severe drought classes.
        </div>
        """,
        unsafe_allow_html=True
    )

    metadata = load_metadata()
    performance = metadata.get("performance", {})

    if not performance:
        st.warning("Model performance metadata was not found.")
        return

    st.subheader("Select Model to View Performance")

    model_names = list(performance.keys())

    selected_model = st.selectbox(
        "Choose a trained model",
        model_names,
        index=model_names.index("SVM + Class Weight Balanced") if "SVM + Class Weight Balanced" in model_names else 0
    )

    selected_perf = performance[selected_model]

    accuracy = selected_perf.get("Accuracy", 0)
    weighted_precision = selected_perf.get("Weighted_Precision", 0)
    weighted_recall = selected_perf.get("Weighted_Recall", 0)
    weighted_f1 = selected_perf.get("Weighted_F1", 0)
    macro_f1 = selected_perf.get("Macro_F1", 0)
    moderate_recall = selected_perf.get("Moderate_Recall", 0)
    severe_recall = selected_perf.get("Severe_Recall", 0)

    if selected_model == "SVM + Class Weight Balanced":
        badge_html = '<div class="final-badge">FINAL SELECTED MODEL</div>'
        subtitle = (
            "This model is recommended for deployment because it produced the strongest detection "
            "of Moderate and Severe drought classes."
        )
    else:
        badge_html = '<div class="compare-badge">COMPARISON MODEL</div>'
        subtitle = (
            "This model is included for comparison because it was part of the experimental evaluation. "
            "The final recommended model remains SVM + Class Weight Balanced."
        )

    st.markdown(
        f"""
        <div class="model-summary-card">
            {badge_html}
            <div class="model-summary-title">{selected_model}</div>
            <div class="model-summary-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-label">Overall Model Performance</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="performance-card" style="border-top: 5px solid #22C55E;">
                <div class="performance-card-title">Accuracy</div>
                <div class="performance-card-value">{accuracy * 100:.2f}%</div>
                <div class="performance-card-note">Overall correct predictions</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="performance-card" style="border-top: 5px solid #3B82F6;">
                <div class="performance-card-title">Weighted F1</div>
                <div class="performance-card-value">{weighted_f1 * 100:.2f}%</div>
                <div class="performance-card-note">Balanced precision and recall</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="performance-card" style="border-top: 5px solid #A855F7;">
                <div class="performance-card-title">Weighted Precision</div>
                <div class="performance-card-value">{weighted_precision * 100:.2f}%</div>
                <div class="performance-card-note">Correctness of positive predictions</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="performance-card" style="border-top: 5px solid #06B6D4;">
                <div class="performance-card-title">Weighted Recall</div>
                <div class="performance-card-value">{weighted_recall * 100:.2f}%</div>
                <div class="performance-card-note">Overall class detection ability</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div class="section-label">Drought-Class Detection Performance</div>', unsafe_allow_html=True)

    col5, col6, col7 = st.columns(3)

    with col5:
        st.markdown(
            f"""
            <div class="performance-card" style="border-top: 5px solid #F59E0B;">
                <div class="performance-card-title">Macro F1</div>
                <div class="performance-card-value">{macro_f1 * 100:.2f}%</div>
                <div class="performance-card-note">Treats all classes equally</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col6:
        st.markdown(
            f"""
            <div class="performance-card" style="border-top: 5px solid #F97316;">
                <div class="performance-card-title">Moderate Recall</div>
                <div class="performance-card-value">{moderate_recall * 100:.2f}%</div>
                <div class="performance-card-note">Ability to detect Moderate drought</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col7:
        st.markdown(
            f"""
            <div class="performance-card" style="border-top: 5px solid #EF4444;">
                <div class="performance-card-title">Severe Recall</div>
                <div class="performance-card-value">{severe_recall * 100:.2f}%</div>
                <div class="performance-card-note">Ability to detect Severe drought</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.subheader("Performance Comparison Table")

    comparison_rows = []

    for model_name, values in performance.items():
        comparison_rows.append({
            "Model": model_name,
            "Accuracy": values.get("Accuracy", None),
            "Weighted Precision": values.get("Weighted_Precision", None),
            "Weighted Recall": values.get("Weighted_Recall", None),
            "Weighted F1": values.get("Weighted_F1", None),
            "Macro F1": values.get("Macro_F1", None),
            "Moderate Recall": values.get("Moderate_Recall", None),
            "Severe Recall": values.get("Severe_Recall", None),
        })

    comparison_df = pd.DataFrame(comparison_rows)

    st.dataframe(
        comparison_df,
        use_container_width=True
    )

    st.subheader("Model Comparison Chart")

    chart_df = comparison_df.melt(
        id_vars="Model",
        value_vars=[
            "Accuracy",
            "Weighted F1",
            "Macro F1",
            "Moderate Recall",
            "Severe Recall"
        ],
        var_name="Metric",
        value_name="Score"
    )

    fig = px.bar(
        chart_df,
        x="Model",
        y="Score",
        color="Metric",
        barmode="group",
        title="Comparison of Trained Models"
    )

    fig.update_layout(
        yaxis_tickformat=".0%",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

   

    st.subheader("Input Features Used by the Models")

    feature_list = metadata.get(
        "features",
        [
            "Month", "Region", "District",
            "NDVI", "NDVI_lag1", "NDVI_lag2",
            "Soil_Moisture", "Soil_Moisture_lag1", "Soil_Moisture_lag2",
            "Temperature", "Temperature_lag1", "Temperature_lag2",
            "Rainfall", "Rainfall_lag1", "Rainfall_lag2"
        ]
    )

    st.dataframe(
        pd.DataFrame({"Model Input Features": feature_list}),
        use_container_width=True
    )




# -----------------------------
# Main App
# -----------------------------
def main():
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True

    top_left, top_right = st.columns([6, 1])

    with top_right:
        mode_label = "🌙 Dark Mode" if st.session_state.dark_mode else "☀️ Light Mode"

        dark_mode = st.toggle(
            mode_label,
            value=st.session_state.dark_mode
        )

    st.session_state.dark_mode = dark_mode

    load_css(dark_mode=dark_mode)
    df = load_dataset()

    load_css(dark_mode=dark_mode)
    df = load_dataset()

    st.sidebar.markdown(
    """
    <div style="padding: 10px 0 20px 0;">
        <h2 style="color: #F8FAFC; margin-bottom: 0;">🌾 Drought System</h2>
        <p style="color: #BBF7D0; font-size: 14px; margin-top: 6px;">
            ML-based drought risk prediction
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

    page = st.sidebar.radio(
        "Navigation Menu",
        [
            "Home",
            "Predict Drought Risk",
            "Batch Prediction",
            "Data Dashboard",
            "Model Information",
           
        ]
    )

    if page == "Home":
        render_home(df)

    elif page == "Predict Drought Risk":
       render_predict_page(df)


    elif page == "Batch Prediction":
        render_batch_page(df)

    elif page == "Data Dashboard":
        render_dashboard_page(df)

    elif page == "Model Information":
        render_model_info_page()

    


if __name__ == "__main__":
    main()