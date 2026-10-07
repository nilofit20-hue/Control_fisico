import json
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Control Diario de Gym & Pasos", page_icon="🏋️‍♂️", layout="wide"
)

# Estilos visuales limpios en modo oscuro
st.markdown(
    """
    <style>
    .main { background-color: #0b0f19; color: #f3f4f6; }
    .stMetric { background-color: #111827; padding: 15px; border-radius: 10px; border: 1px solid #1f2937; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🏋️‍♂️ Bitácora de Gym & Pasos")
st.markdown("Control directo de tu peso, actividad diaria y cargas en el gimnasio.")

ARCHIVO_DATOS = "historial_simple.json"


def cargar_datos():
  if os.path.exists(ARCHIVO_DATOS):
    with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
      return json.load(f)
  return {"registros": []}


def guardar_datos(datos):
  with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
    json.dump(datos, f, indent=4, ensure_ascii=False)


db = cargar_datos()
registros = db["registros"]

# Pestañas principales
tab1, tab2 = st.tabs(["📝 Registrar Día", "📈 Ver Progreso y Cargas"])

# ================= TAB 1: REGISTRAR DÍA =================
with tab1
