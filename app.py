import json
import os
import streamlit as st

# Configuración de la página del proyecto
st.set_page_config(
    page_title="Gestor de Progreso Físico", page_icon="🏋️‍♂️", layout="centered"
)

st.title("🏋️‍♂️ Motor de Progreso Físico y Nutrición")
st.markdown(
    "Sistema automatizado independiente para tu etapa de definición y"
    " control de rendimiento."
)

# Archivo JSON local exclusivo para este proyecto
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

# Formulario de entrada de datos semanales
with st.form("form_nuevo_registro", clear_on_submit=False):
  st.subheader("📝 Registrar Datos de la Semana")

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

  submit_button = st.form_submit_button("Guardar Registro Semanal")

if submit_button:
  datos["historial"] = [h for h in datos["historial"] if h["semana"] != sem]
  datos["historial"].append({"semana": sem, "peso": peso, "pasos": pasos})
  datos["historial"] = sorted(datos["historial"], key=lambda x: x["semana"])
  guardar_datos(datos)
  st.success(f"¡Semana {sem} registrada y guardada en la base de datos local!")

# Sección de Análisis y Evaluación Automática
historial = datos["historial"]

if len(historial) >= 2:
  st.divider()
  st.subheader("📊 Evaluación Automática del Rendimiento")

  actual = historial[-1]
  anterior = historial[-2]

  cambio_peso = actual["peso"] - anterior["peso"]
  pct_cambio = (cambio_peso / anterior["peso"]) * 100

  st.metric(
      label=f"Comparativa: Semana {anterior['semana']} ➔ Semana {actual['semana']}",
      value=f"{actual['peso']} kg",
      delta=f"{cambio_peso:+.2f} kg ({pct_cambio:+.2f}%)",
  )

  if -1.0 <= pct_cambio <= -0.5:
    st.success(
        "🚀 **ESTADO: ÓPTIMO**\n\nEl sistema opera perfectamente. Mantener"
        " calorías y esquema actual de entrenamiento."
    )
  elif pct_cambio > 0 or pct_cambio > -0.3:
    st.warning(
        "⚠️ **ALERTA: ESTANCAMIENTO DETECTADO**\n\n**ACCIÓN AUTOMÁTICA:**"
        " Incrementar 1,500 pasos diarios o reducir 150 kcal en la dieta."
    )
  elif pct_cambio < -1.2:
    st.error(
        "🔥 **ALERTA: PÉRDIDA MUY AGRESIVA**\n\n**ACCIÓN AUTOMÁTICA:** Aumentar"
        " 150 kcal para proteger tu masa muscular magra."
    )
  else:
    st.info(
        "📈 **ESTADO: PROGRESO MODERADO**\n\nEl ritmo es aceptable. Continuar"
        " monitoreando la tendencia la próxima semana."
    )

  st.divider()
  st.subheader("📋 Historial de Registros Guardados")
  st.dataframe(historial, use_container_width=True)

else:
  st.divider()
  st.info(
      "ℹ️ **Primeros pasos:** Registra al menos **2 semanas** de datos usando el"
      " formulario de arriba para que el motor empiece a calcular las"
      " tendencias y alertas automáticas."
  )
