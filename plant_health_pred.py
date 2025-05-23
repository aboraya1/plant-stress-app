import streamlit as st
import numpy as np
import pandas as pd
import joblib
import plotly.express as px

# 🗾️ إعداد الواجهة
st.set_page_config(page_title="🌿 Plant Health Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center; color: green;'>🌿 Plant Stress Detection Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# 🧪 الشريط الجانبي
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2900/2900583.png", width=120)
st.sidebar.markdown("👋 Welcome! This app predicts plant health status based on soil, weather & nutrients.")
menu = st.sidebar.radio("📍 Navigate", ["📋 Predict", "📊 Visualizations"])

# 📦 تحميل النموذج والمقياس
@st.cache_resource
def load_resources():
    model = joblib.load("plant_model_balanced.pkl")
    scaler = joblib.load("plant_scaler.pkl")
    return model, scaler

model, scaler = load_resources()

@st.cache_data
def load_data():
    return pd.read_csv("updated_plant_health_data.csv")

data = load_data()

# 🔄 تهيئة حالة الجلسة
if "step" not in st.session_state:
    st.session_state.step = 1

if "plant_type" not in st.session_state:
    st.session_state.plant_type = None

def reset_prediction():
    st.session_state.step = 1
    st.session_state.plant_type = None

if menu == "📋 Predict":
    if st.session_state.step == 1:
        st.subheader("🏜️ Step 1: Choose Environment Type")

        with st.form("type_form"):
            plant_env_type = st.selectbox("Select the Plant Environment Type", ["Desert", "Agricultural", "Shade"])
            next_step = st.form_submit_button("➡ Next")

        if next_step:
            st.session_state.plant_type = plant_env_type
            st.session_state.step = 2
            st.rerun()

    elif st.session_state.step == 2:
        st.subheader(f"🧪 Step 2: Enter Features for {st.session_state.plant_type} Area")

        with st.form("feature_form"):
            col1, col2 = st.columns(2)
            with col1:
                soil_moisture = st.slider("Soil Moisture", 0.0, 100.0, 25.0)
                ambient_temp = st.slider("Ambient Temperature", 0.0, 50.0, 25.0)
                soil_temp = st.slider("Soil Temperature", 0.0, 50.0, 25.0)
                humidity = st.slider("Humidity", 0.0, 100.0, 50.0)
                light_intensity = st.slider("Light Intensity", 0.0, 1000.0, 400.0)

            with col2:
                soil_ph = st.slider("Soil pH", 3.0, 9.0, 6.5)
                nitrogen = st.slider("Nitrogen Level", 0.0, 50.0, 15.0)
                phosphorus = st.slider("Phosphorus Level", 0.0, 50.0, 15.0)
                potassium = st.slider("Potassium Level", 0.0, 50.0, 15.0)
                chlorophyll = st.slider("Chlorophyll Content", 0.0, 100.0, 30.0)
                electro_signal = st.slider("Electrochemical Signal", 0.0, 2.0, 1.0)

            back = st.form_submit_button("🔙 Back")
            submit = st.form_submit_button("🌿 Predict")

        if back:
            reset_prediction()
            st.rerun()

        if submit:
            type_mapping = {"Desert": 0, "Agricultural": 1, "Shade": 2}
            type_encoded = type_mapping[st.session_state.plant_type]

            input_data = np.array([[soil_moisture, ambient_temp, soil_temp, humidity, light_intensity,
                                    soil_ph, nitrogen, phosphorus, potassium, chlorophyll, electro_signal, type_encoded]])

            input_scaled = scaler.transform(input_data)
            prediction = model.predict(input_scaled)[0]

            status_map = {
                0: "✅ Healthy Plant",
                1: "⚠ Moderate Stress",
                2: "🚨 High Stress"
            }

            st.success(f"**Prediction Result ({st.session_state.plant_type} Area):** {status_map[prediction]}")

            if prediction in [1, 2]:
                st.warning("🧺 Recommended Actions to Improve Plant Health:")
                if soil_moisture < 30:
                    st.info("💧 Increase watering: Soil moisture is too low.")
                if nitrogen < 10:
                    st.info("🌱 Apply nitrogen-rich fertilizer: Nitrogen level is insufficient.")
                if soil_ph < 5.5 or soil_ph > 7.5:
                    st.info("🧪 Adjust soil pH: Ideal range is 5.5 to 7.5.")
                if light_intensity < 300:
                    st.info("🔆 Increase light exposure: Light intensity is lower than optimal.")
                if ambient_temp < 15 or ambient_temp > 35:
                    st.info("🌡️ Temperature adjustment: Keep ambient temperature between 15°C and 35°C.")

            st.button("🔄 Start Over", on_click=reset_prediction)

elif menu == "📊 Visualizations":
    st.subheader("📊 Explore Key Feature Impact on Plant Health")

    @st.cache_resource
    def plot_feature_relation(x_feature):
        data_numeric = data.copy()
        mapping = {"Healthy": 0, "Moderate Stress": 1, "High Stress": 2}
        if data_numeric["Plant_Health_Status"].dtype == object:
            data_numeric["Plant_Health_Status"] = data_numeric["Plant_Health_Status"].map(mapping)

        avg_values = data_numeric.groupby("Plant_Health_Status")[x_feature].mean().reset_index()

        fig = px.bar(avg_values, x="Plant_Health_Status", y=x_feature,
                     labels={"Plant_Health_Status": "Health Status", x_feature: f"Avg {x_feature}"},
                     title=f"Average {x_feature} per Plant Health Status",
                     color_discrete_sequence=["#4CAF50"])

        fig.update_layout(xaxis=dict(
            tickmode="array",
            tickvals=[0, 1, 2],
            ticktext=["Healthy", "Moderate", "High Stress"]
        ))

        return fig

    important_features = ["Soil_Moisture", "Nitrogen_Level"]
    selected_feature = st.sidebar.selectbox("📌 Choose Feature", important_features)
    plot = plot_feature_relation(selected_feature)
    st.plotly_chart(plot, use_container_width=True)

    notes = {
        "Soil_Moisture": "💧 Dry soil often indicates high stress.",
        "Nitrogen_Level": "🌱 Low nitrogen = weak growth."
    }

    st.info(notes[selected_feature])
