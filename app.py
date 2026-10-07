import json
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de la página en formato ancho para aprovechar mejor el espacio
st.set_page_config(
    page_title="Motor de Progreso Físico", page_icon="🏋️‍♂️", layout="wide"
)

# Estilos visuales modernos para tarjetas y contenedores
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2129;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2d3139;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🏋️‍♂️ Motor de Progreso Físico y Nutrición")
st.markdown(
    "Sistema automatizado avanzado para control de peso, pasos y"
    " optimización de definición."
)

ARCHIVO_DATOS = "historial_fitness.json"


def cargar_datos():
  if os.path.exists(ARCHIVO_DATOS):
    with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
      return json.load(f)
  return {"historial": []}


def guardar_datos(datos):
  with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
    json.dump(datos, f, indent=4, ensure_ascii=False)


datos = cargar_datos()
historial = datos["historial"]

# Organización mediante Pestañas Profesionales (Tabs)
tab1, tab2, tab3 = st.tabs(
    ["📊 Dashboard Principal", "📝 Registrar Semana", "📈 Gráficas de Tendencia"]
)

# ================= TAB 1: DASHBOARD =================
with tab1:
  st.subheader("Estado Actual del Sistema")

  if len(historial) >= 2:
    actual = historial[-1]
    anterior = historial[-2]
    cambio_peso = actual["peso"] - anterior["peso"]
    pct_cambio = (cambio_peso / anterior["peso"]) * 100

    # Tarjetas de métricas visuales superiores
    col1, col2, col3, col4 = st.columns(4)
    with col1:
      st.metric(
          label="Peso Actual",
          value=f"{actual['peso']} kg",
          delta=f"{cambio_peso:+.2f} kg",
      )
    with col2:
      st.metric(label="Pasos Promedio", value=f"{actual['pasos']} pasos")
    with col3:
      st.metric(label="Semana Activa", value=f"Semana {actual['semana']}")
    with col4:
      st.metric(label="Variación Relativa", value=f"{pct_cambio:+.2f}%")

    st.divider()

    # Evaluación automatizada con alertas visuales de colores
    if -1.0 <= pct_cambio <= -0.5:
      st.success(
          "🚀 **ESTADO: ÓPTIMO** — El sistema opera perfectamente. Mantener"
          " calorías y esquema actual de entrenamiento."
      )
    elif pct_cambio > 0 or pct_cambio > -0.3:
      st.warning(
          "⚠️ **ALERTA: ESTANCAMIENTO DETECTADO** — **ACCIÓN AUTOMÁTICA:**"
          " Incrementar 1,500 pasos diarios o reducir 150 kcal en la dieta."
      )
    elif pct_cambio < -1.2:
      st.error(
          "🔥 **ALERTA: PÉRDIDA MUY AGRESIVA** — **ACCIÓN AUTOMÁTICA:** Aumentar"
          " 150 kcal para proteger masa muscular magra."
      )
    else:
      st.info(
          "📈 **ESTADO: PROGRESO MODERADO** — Ritmo aceptable. Continuar"
          " monitoreando la tendencia."
      )

    st.divider()
    st.subheader("📋 Historial Completo de Registros")
    st.dataframe(historial, use_container_width=True)
  else:
    st.info(
        "ℹ️ **Primeros pasos:** Registra al menos **2 semanas** de datos en la"
        " pestaña de 'Registrar Semana' para activar el dashboard analítico."
    )

# ================= TAB 2: REGISTRO =================
with tab2:
  st.subheader("Ingreso de Datos Semanales")
  with st.form("form_nuevo_registro", clear_on_submit=False):
    col1, col2, col3 = st.columns(3)
    with col1:
      sem = st.number_input("Número de semana", min_value=1, step=1, value=1)
    with col2:
      peso = st.number_input(
          "Peso promedio (kg)", min_value=30.0, max_value=200.0, format="%.2f"
      )
    with col3:
      pasos = st.number_input(
          "Pasos diarios promedio", min_value=0, max_value=50000, step=100
      )

    submit_button = st.form_submit_button(
        "Guardar Registro en el Sistema", use_container_width=True
    )

  if submit_button:
    datos["historial"] = [h for h in datos["historial"] if h["semana"] != sem]
    datos["historial"].append({"semana": sem, "peso": peso, "pasos": pasos})
    datos["historial"] = sorted(datos["historial"], key=lambda x: x["semana"])
    guardar_datos(datos)
    st.success(
        f"¡Semana {sem} registrada exitosamente! Ve a la pestaña 'Dashboard"
        " Principal' para ver las métricas actualizadas."
    )

# ================= TAB 3: GRÁFICAS =================
with tab3:
  st.subheader("📈 Análisis Gráfico de Tendencias")
  if len(historial) >= 1:
    df = pd.DataFrame(historial)

    # Gráfica interactiva de peso con Plotly
    fig = px.line(
        df,
        x="semana",
        y="peso",
        markers=True,
        title="Evolución del Peso Corporal por Semana",
        labels={"semana": "Semana", "peso": "Peso Promedio (kg)"},
    )
    fig.update_traces(
        line=dict(color="#00E676", width=3), marker=dict(size=8)
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
    )
    st.plotly_chart(fig, use_container_width=True)
  else:
    st.warning("⚠️ No hay suficientes datos registrados para generar la gráfica.")
