import json
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de la página en formato ancho
st.set_page_config(
    page_title="Control Diario - Fitness & Gym", page_icon="💪", layout="wide"
)

# Estilos visuales modernos
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2129; padding: 15px; border-radius: 10px; border: 1px solid #2d3139; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("💪 Sistema de Control Diario: Definición & Gym")
st.markdown(
    "Registro granular de peso, pasos, nutrición (macros) y sobrecarga"
    " progresiva en el gimnasio."
)

ARCHIVO_DATOS = "historial_diario.json"


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

# Pestañas principales de la aplicación
tab1, tab2, tab3 = st.tabs(
    [
        "📝 Registro Diario",
        "📊 Dashboard y Gráficas",
        "🏋️‍♂️ Historial de Fuerza (Gym)",
    ]
)

# ================= TAB 1: REGISTRO DIARIO =================
with tab1:
  st.subheader("Registrar Datos del Día")

  with st.form("form_diario", clear_on_submit=False):
    col_f, col_p, col_pas = st.columns(3)
    with col_f:
      fecha = st.date_input("Fecha del registro")
    with col_p:
      peso = st.number_input(
          "Peso en ayunas (kg)", min_value=30.0, max_value=200.0, format="%.2f"
      )
    with col_pas:
      pasos = st.number_input(
          "Pasos totales del día", min_value=0, max_value=50000, step=100
      )

    st.markdown("---")
    st.subheader("🍽️ Control Nutricional (Macros)")
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
      calorias = st.number_input("Calorías (kcal)", min_value=0, step=50)
    with col_m2:
      proteina = st.number_input("Proteína (g)", min_value=0, step=5)
    with col_m3:
      carbos = st.number_input("Carbohidratos (g)", min_value=0, step=5)
    with col_m4:
      grasas = st.number_input("Grasas (g)", min_value=0, step=5)

    st.markdown("---")
    st.subheader("💪 Entrenamiento de Fuerza (Gym del Día)")
    st.markdown(
        "Ingresa los ejercicios principales de tu sesión (Torso o Pierna):"
    )

    # Espacios para registrar hasta 4 ejercicios clave del día
    ejercicios_ingresados = []
    for i in range(1, 5):
      with st.expander(f"Ejercicio {i} (Opcional)"):
        col_e1, col_e2, col_e3, col_e4 = st.columns(4)
        with col_e1:
          nombre_ej = st.text_input(
              f"Nombre Ejercicio {i}", key=f"nombre_{i}"
          )
        with col_e2:
          series = st.number_input(
              f"Series {i}", min_value=0, max_value=10, value=0, key=f"ser_{i}"
          )
        with col_e3:
          reps = st.text_input(
              f"Reps (ej: 10,10,8)", value="", key=f"rep_{i}"
          )
        with col_e4:
          peso_ej = st.number_input(
              f"Peso usado (kg) {i}",
              min_value=0.0,
              format="%.1f",
              key=f"pes_ej_{i}",
          )

        if nombre_ej and series > 0:
          ejercicios_ingresados.append({
              "ejercicio": nombre_ej,
              "series": series,
              "reps": reps,
              "peso_kg": peso_ej,
          })

    submit_btn = st.form_submit_button(
        "Guardar Registro Diario", use_container_width=True
    )

  if submit_btn:
    fecha_str = str(fecha)
    # Reemplazar si ya existe la fecha
    db["registros"] = [r for r in db["registros"] if r["fecha"] != fecha_str]

    nuevo_registro = {
        "fecha": fecha_str,
        "peso": peso,
        "pasos": pasos,
        "calorias": calorias,
        "proteina": proteina,
        "carbos": carbos,
        "grasas": grasas,
        "ejercicios": ejercicios_ingresados,
    }

    db["registros"].append(nuevo_registro)
    # Ordenar por fecha cronológica
    db["registros"] = sorted(db["registros"], key=lambda x: x["fecha"])
    guardar_datos(db)
    st.success(
        f"¡Registro del día {fecha_str} guardado exitosamente en la base de"
        " datos!"
    )

# ================= TAB 2: DASHBOARD Y GRÁFICAS =================
with tab2:
  st.subheader("📊 Evolución y Tendencias Diarias")

  if len(registros) >= 1:
    df = pd.DataFrame(registros)

    # Métricas rápidas del último registro
    ultimo = registros[-1]
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
      st.metric("Último Peso", f"{ultimo['peso']} kg")
    with col_m2:
      st.metric("Pasos Recientes", f"{ultimo['pasos']} pasos")
    with col_m3:
      st.metric("Calorías Recientes", f"{ultimo['calorias']} kcal")
    with col_m4:
      st.metric("Proteína Reciente", f"{ultimo['proteina']} g")

    st.divider()

    # Gráfica de Peso Corporal
    fig_peso = px.line(
        df,
        x="fecha",
        y="peso",
        markers=True,
        title="Tendencia Diaria del Peso Corporal",
        labels={"fecha": "Fecha", "peso": "Peso (kg)"},
    )
    fig_peso.update_traces(
        line=dict(color="#00E676", width=3), marker=dict(size=8)
    )
    fig_peso.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
    )
    st.plotly_chart(fig_peso, use_container_width=True)

    # Gráfica de Pasos y Calorías
    col_g1, col_g2 = st.columns(2)
    with col_g1:
      fig_pasos = px.bar(
          df,
          x="fecha",
          y="pasos",
          title="Registro Diario de Pasos (NEAT)",
          labels={"fecha": "Fecha", "pasos": "Pasos"},
      )
      fig_pasos.update_layout(
          plot_bgcolor="rgba(0,0,0,0)",
          paper_bgcolor="rgba(0,0,0,0)",
          font_color="white",
      )
      st.plotly_chart(fig_pasos, use_container_width=True)

    with col_g2:
      fig_cal = px.line(
          df,
          x="fecha",
          y="calorias",
          markers=True,
          title="Calorías Consumidas Diarias",
          labels={"fecha": "Fecha", "calorias": "kcal"},
      )
      fig_cal.update_traces(
          line=dict(color="#FF9800", width=3), marker=dict(size=8)
      )
      fig_cal.update_layout(
          plot_bgcolor="rgba(0,0,0,0)",
          paper_bgcolor="rgba(0,0,0,0)",
          font_color="white",
      )
      st.plotly_chart(fig_cal, use_container_width=True)

    st.divider()
    st.subheader("📋 Tabla General de Registros")
    st.dataframe(df[["fecha", "peso", "pasos", "calorias", "proteina", "carbos", "grasas"]], use_container_width=True)
  else:
    st.warning("⚠️ No hay suficientes registros diarios cargados todavía.")

# ================= TAB 3: HISTORIAL DE FUERZA =================
with tab3:
  st.subheader("🏋️‍♂️ Progreso de Ejercicios en el Gimnasio")
  
  # Aplanar los datos de ejercicios para ver la sobrecarga progresiva
  lista_ejercicios_plana = []
  for reg in registros:
    fecha_reg = reg["fecha"]
    for ej in reg.get("ejercicios", []):
      lista_ejercicios_plana.append({
          "fecha": fecha_reg,
          "ejercicio": ej["ejercicio"],
          "series": ej["series"],
          "reps": ej["reps"],
          "peso_kg": ej["peso_kg"]
      })

  if lista_ejercicios_plana:
    df_gym = pd.DataFrame(lista_ejercicios_plana)
    
    # Filtro por ejercicio para ver su evolución específica
    ejercicios_unicos = df_gym["ejercicio"].unique()
    ejercicio_seleccionado = st.selectbox("Selecciona un ejercicio para ver su evolución de carga:", ejercicios_unicos)
    
    df_filtrado = df_gym[df_gym["ejercicio"] == ejercicio_seleccionado]
    
    # Gráfica de evolución de peso en el ejercicio
    fig_gym = px.line(
        df_filtrado,
        x="fecha",
        y="peso_kg",
        markers=True,
        title=f"Evolución de Carga en: {ejercicio_seleccionado}",
        labels={"fecha": "Fecha", "peso_kg": "Peso Usado (kg)"}
    )
    fig_gym.update_traces(line=dict(color="#29B6F6", width=3), marker=dict(size=10))
    fig_gym.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig_gym, use_container_width=True)

    st.subheader("Historial Detallado de Entrenamientos")
    st.dataframe(df_gym, use_container_width=True)
  else:
    st.info("ℹ️ Aún no has registrado ejercicios con pesas en los formularios diarios. Rellena los campos de los expansores de ejercicios en la pestaña 'Registro Diario'.")
