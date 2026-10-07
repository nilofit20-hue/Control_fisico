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
with tab1:
  st.subheader("Registrar Actividad Diaria")

  with st.form("form_simple", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
      fecha = st.date_input("Fecha")
    with col2:
      peso = st.number_input(
          "Peso en ayunas (kg)", min_value=30.0, max_value=200.0, format="%.2f"
      )

    pasos = st.number_input(
        "Pasos totales del día", min_value=0, max_value=50000, step=100
    )

    st.markdown("---")
    st.subheader("💪 Ejercicios de Hoy")
    st.markdown("Anota los ejercicios que hiciste, cuántas series, repeticiones y el peso con el que trabajaste.")

    # Permitir registrar hasta 6 ejercicios de forma limpia
    ejercicios_dia = []
    for i in range(1, 7):
      with st.expander(f"Ejercicio #{i} (Opcional)"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
          nombre = st.text_input(f"Nombre Ejercicio {i}", key=f"nom_{i}")
        with c2:
          series = st.number_input(
              f"Series {i}", min_value=0, max_value=10, value=0, key=f"ser_{i}"
          )
        with c3:
          reps = st.text_input(f"Reps (ej: 10,10,8)", value="", key=f"rep_{i}")
        with c4:
          peso_ej = st.number_input(
              f"Peso (kg) {i}", min_value=0.0, format="%.1f", key=f"pes_{i}"
          )

        if nombre and series > 0:
          ejercicios_dia.append({
              "ejercicio": nombre,
              "series": series,
              "reps": reps,
              "peso_kg": peso_ej,
          })

    guardar_btn = st.form_submit_button(
        "💾 Guardar Día", use_container_width=True
    )

  if guardar_btn:
    fecha_str = str(fecha)
    # Reemplazar si ya existe la fecha
    db["registros"] = [r for r in db["registros"] if r["fecha"] != fecha_str]

    nuevo_reg = {
        "fecha": fecha_str,
        "peso": peso,
        "pasos": pasos,
        "ejercicios": ejercicios_dia,
    }

    db["registros"].append(nuevo_reg)
    db["registros"] = sorted(db["registros"], key=lambda x: x["fecha"])
    guardar_datos(db)
    st.success(f"¡Registro del {fecha_str} guardado con éxito!")

# ================= TAB 2: VER PROGRESO =================
with tab2:
  st.subheader("📈 Historial y Evolución de Cargas")

  if registros:
    df_general = pd.DataFrame(registros)

    # Gráfica rápida de peso y pasos
    col_g1, col_g2 = st.columns(2)
    with col_g1:
      fig_p = px.line(
          df_general,
          x="fecha",
          y="peso",
          markers=True,
          title="Evolución del Peso (kg)",
          labels={"fecha": "Fecha", "peso": "Peso (kg)"},
      )
      fig_p.update_traces(
          line=dict(color="#00E676", width=3), marker=dict(size=8)
      )
      fig_p.update_layout(
          plot_bgcolor="rgba(0,0,0,0)",
          paper_bgcolor="rgba(0,0,0,0)",
          font_color="white",
      )
      st.plotly_chart(fig_p, use_container_width=True)

    with col_g2:
      fig_pas = px.bar(
          df_general,
          x="fecha",
          y="pasos",
          title="Registro de Pasos Diario",
          labels={"fecha": "Fecha", "pasos": "Pasos"},
      )
      fig_pas.update_traces(marker_color="#29B6F6")
      fig_pas.update_layout(
          plot_bgcolor="rgba(0,0,0,0)",
          paper_bgcolor="rgba(0,0,0,0)",
          font_color="white",
      )
      st.plotly_chart(fig_pas, use_container_width=True)

    st.divider()

    # Extraer los ejercicios para ver la evolución de las cargas
    lista_ej_plana = []
    for reg in registros:
      for ej in reg.get("ejercicios", []):
        lista_ej_plana.append({
            "fecha": reg["fecha"],
            "ejercicio": ej["ejercicio"],
            "series": ej["series"],
            "reps": ej["reps"],
            "peso_kg": ej["peso_kg"],
        })

    if lista_ej_plana:
      df_ej = pd.DataFrame(lista_ej_plana)
      st.subheader("💪 Evolución de Peso en el Gimnasio por Ejercicio")

      ej_
