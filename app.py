import json
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de página profesional en ancho completo
st.set_page_config(
    page_title="Elite Coaching Dashboard", page_icon="⚡", layout="wide"
)

# Estilos CSS avanzados para un diseño minimalista oscuro de alta gama
st.markdown(
    """
    <style>
    .main { background-color: #0b0f19; color: #f3f4f6; }
    .stMetric { background-color: #111827; padding: 18px; border-radius: 12px; border: 1px solid #1f2937; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .stTab { font-size: 16px; font-weight: 600; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("⚡ ELITE COACHING & PERFORMANCE SYSTEM")
st.markdown(
    "Plataforma avanzada de control corporal, nutrición de precisión y"
    " sobrecarga progresiva."
)

ARCHIVO_DATOS = "historial_elite.json"


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

# Pestañas de la plataforma
tab1, tab2, tab3, tab4 = st.tabs([
    "📥 Registro Diario",
    "📊 Dashboard Ejecutivo",
    "🏋️‍♂️ Análisis de Fuerza & Tonnage",
    "🍽️ Control Nutricional",
])

# ================= TAB 1: REGISTRO DIARIO =================
with tab1:
  st.subheader("📝 Bitácora Diaria del Atleta")

  with st.form("form_elite", clear_on_submit=False):
    col_f, col_p, col_pas = st.columns(3)
    with col_f:
      fecha = st.date_input("Fecha del registro")
    with col_p:
      peso = st.number_input(
          "Peso en ayunas (kg)", min_value=30.0, max_value=200.0, format="%.2f"
      )
    with col_pas:
      pasos = st.number_input(
          "Pasos diarios (NEAT)", min_value=0, max_value=50000, step=100
      )

    st.markdown("---")
    st.subheader("🍽️ Macronutrientes & Calorías")
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
      calorias = st.number_input("Calorías Totales (kcal)", min_value=0, step=50)
    with col_m2:
      proteina = st.number_input(
          "Proteína (g) [Clave para preservar músculo]", min_value=0, step=5
      )
    with col_m3:
      carbos = st.number_input("Carbohidratos (g)", min_value=0, step=5)
    with col_m4:
      grasas = st.number_input("Grasas (g)", min_value=0, step=5)

    st.markdown("---")
    st.subheader("💪 Bloque de Entrenamiento (Fuerza & Intensidad)")
    st.markdown(
        "Registra tus ejercicios clave aplicando control de peso y RIR (Reps"
        " en Reserva)."
    )

    ejercicios_ingresados = []
    for i in range(1, 5):
      with st.expander(f"Ejercicio Principal #{i}"):
        col_e1, col_e2, col_e3, col_e4, col_e5 = st.columns(5)
        with col_e1:
          nombre_ej = st.text_input(f"Nombre Ejercicio {i}", key=f"nom_{i}")
        with col_e2:
          series = st.number_input(
              f"Series {i}", min_value=0, max_value=10, value=0, key=f"ser_{i}"
          )
        with col_e3:
          reps = st.number_input(
              f"Reps Promedio {i}", min_value=0, max_value=30, value=0, key=f"rep_{i}"
          )
        with col_e4:
          peso_ej = st.number_input(
              f"Peso (kg) {i}", min_value=0.0, format="%.1f", key=f"pes_{i}"
          )
        with col_e5:
          rir = st.slider(
              f"RIR (Margen al fallo) {i}",
              min_value=0,
              max_value=5,
              value=2,
              key=f"rir_{i}",
          )

        if nombre_ej and series > 0:
          # Cálculo del Tonnage (Volumen total de carga de este ejercicio)
          tonnage_ejercicio = series * reps * peso_ej
          ejercicios_ingresados.append({
              "ejercicio": nombre_ej,
              "series": series,
              "reps": reps,
              "peso_kg": peso_ej,
              "rir": rir,
              "tonnage": tonnage_ejercicio,
          })

    submit_btn = st.form_submit_button(
        "💾 Guardar Bitácora en el Sistema", use_container_width=True
    )

  if submit_btn:
    fecha_str = str(fecha)
    db["registros"] = [r for r in db["registros"] if r["fecha"] != fecha_str]

    # Calcular tonnage total de la sesión de gym
    tonnage_total_sesion = sum(
        [e["tonnage"] for e in ejercicios_ingresados]
    )

    nuevo_registro = {
        "fecha": fecha_str,
        "peso": peso,
        "pasos": pasos,
        "calorias": calorias,
        "proteina": proteina,
        "carbos": carbos,
        "grasas": grasas,
        "ejercicios": ejercicios_ingresados,
        "tonnage_total": tonnage_total_sesion,
    }

    db["registros"].append(nuevo_registro)
    db["registros"] = sorted(db["registros"], key=lambda x: x["fecha"])
    guardar_datos(db)
    st.success(
        f"✅ ¡Bitácora del día {fecha_str} procesada y guardada con éxito!"
    )

# Preparar DataFrame global si hay datos
if registros:
  df = pd.DataFrame(registros)
  df["fecha"] = pd.to_datetime(df["fecha"])
  # Calcular promedio móvil de peso (suavizar retención de líquidos)
  df["peso_promedio_movil"] = df["peso"].rolling(window=3, min_periods=1).mean()

# ================= TAB 2: DASHBOARD EJECUTIVO =================
with tab2:
  st.subheader("📊 Panel de Control y Tendencias Físicas")

  if len(registros) >= 1:
    ultimo = registros[-1]
    penultimo = registros[-2] if len(registros) >= 2 else ultimo
    delta_peso = ultimo["peso"] - penultimo["peso"]

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
      st.metric(
          "Peso Actual",
          f"{ultimo['peso']} kg",
          delta=f"{delta_peso:+.2f} kg",
          delta_color="inverse",
      )
    with col_m2:
      st.metric("Promedio Pasos (NEAT)", f"{ultimo['pasos']} pasos")
    with col_m3:
      st.metric("Calorías Ingresadas", f"{ultimo['calorias']} kcal")
    with col_m4:
      st.metric("Proteína Diaria", f"{ultimo['proteina']} g")

    st.divider()

    # Gráfica de Tendencia de Peso vs Promedio Móvil
    fig_peso = px.line(
        df,
        x="fecha",
        y=["peso", "peso_promedio_movil"],
        markers=True,
        title="Tendencia de Peso Corporal (Curva Real vs Promedio Móvil)",
        labels={
            "value": "Peso (kg)",
            "fecha": "Fecha",
            "variable": "Métrica",
        },
    )
    fig_peso.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        legend_title_text="Indicador",
    )
    st.plotly_chart(fig_peso, use_container_width=True)

    # Gráfica de NEAT (Pasos)
    fig_pasos = px.bar(
        df,
        x="fecha",
        y="pasos",
        title="Control Diario de Pasos (Actividad No Ejercicio)",
        labels={"fecha": "Fecha", "pasos": "Pasos Totales"},
    )
    fig_pasos.update_traces(marker_color="#3b82f6")
    fig_pasos.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
    )
    st.plotly_chart(fig_pasos, use_container_width=True)
  else:
    st.info("ℹ️ Registra al menos un día de datos para desplegar el dashboard.")

# ================= TAB 3: ANÁLISIS DE FUERZA & TONNAGE =================
with tab3:
  st.subheader("🏋️‍♂️ Análisis de Carga Mecánica y Sobrecarga Progresiva")

  # Gráfica de Tonnage Total por Sesión
  if len(registros) >= 1:
    fig_ton = px.area(
        df,
        x="fecha",
        y="tonnage_total",
        title="Volumen Total de Carga por Sesión de Entrenamiento (Tonnage)",
        labels={"fecha": "Fecha", "tonnage_total": "Tonnage Total (kg)"},
    )
    fig_ton.update_traces(line_color="#10b981", fillcolor="rgba(16, 185, 129, 0.2)")
    fig_ton.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
    )
    st.plotly_chart(fig_ton, use_container_width=True)

    st.divider()

    # Aplanar ejercicios para análisis específico
    lista_ej = []
    for reg in registros:
      for ej in reg.get("ejercicios", []):
        lista_ej.append({
            "fecha": reg["fecha"],
            "ejercicio": ej["ejercicio"],
            "peso_kg": ej["peso_kg"],
            "reps": ej["reps"],
            "rir": ej["rir"],
            "tonnage": ej["tonnage"],
        })

    if lista_ej:
      df_ej = pd.DataFrame(lista_ej)
      ej_seleccionado = st.selectbox(
          "Selecciona un ejercicio específico para analizar su evolución:",
          df_ej["ejercicio"].unique(),
      )

      df_filtrado = df_ej[df_ej["ejercicio"] == ej_seleccionado]

      fig_ind = px.line(
          df_filtrado,
          x="fecha",
          y="peso_kg",
          markers=True,
          title=f"Evolución de Carga Efectiva en: {ej_seleccionado}",
          labels={"fecha": "Fecha", "peso_kg": "Peso utilizado (kg)"},
      )
      fig_ind.update_traces(
          line=dict(color="#f59e0b", width=3), marker=dict(size=10)
      )
      fig_ind.update_layout(
          plot_bgcolor="rgba(0,0,0,0)",
          paper_bgcolor="rgba(0,0,0,0)",
          font_color="white",
      )
      st.plotly_chart(fig_ind, use_container_width=True)
    else:
      st.info("ℹ️ No hay ejercicios registrados en las bitácoras todavía.")

# ================= TAB 4: CONTROL NUTRICIONAL =================
with tab4:
  st.subheader("🍽️ Monitoreo de Calorías y Macronutrientes")
  if len(registros) >= 1:
    fig_macro = px.line(
        df,
        x="fecha",
        y=["proteina", "carbos", "grasas"],
        markers=True,
        title="Evolución Diaria de Macros (Proteína, Carbos, Grasas)",
        labels={
            "value": "Gramos (g)",
            "fecha": "Fecha",
            "variable": "Macronutriente",
        },
    )
    fig_macro.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
    )
    st.plotly_chart(fig_macro, use_container_width=True)

    st.subheader("📋 Base de Datos General")
    st.dataframe(df, use_container_width=True)
  else:
    st.info("ℹ️ Aún no hay registros guardados.")
