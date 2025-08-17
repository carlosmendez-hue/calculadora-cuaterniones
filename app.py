import streamlit as st
import numpy as np
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import io
import datetime
import matplotlib.pyplot as plt

# ===================== FUNCIONES DE CUATERNIONES =====================
def suma(q1, q2):
    return q1 + q2, f"Suma componente a componente: {q1} + {q2}"

def resta(q1, q2):
    return q1 - q2, f"Resta componente a componente: {q1} - {q2}"

def multiplicacion(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    resultado = np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2
    ])
    explicacion = (f"Multiplicación según la fórmula:\n"
                   f"(w1,w2) - (x1x2 + y1y2 + z1z2), etc.\n"
                   f"Resultado: {resultado}")
    return resultado, explicacion

def conjugado(q):
    return np.array([q[0], -q[1], -q[2], -q[3]]), f"Se cambia el signo de las partes imaginarias: {q}"

def norma(q):
    return np.linalg.norm(q), f"Norma calculada como sqrt(w² + x² + y² + z²)"

# ===================== VISUALIZACIÓN 3D =====================
def plot_quaternion(q):
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=[0, q[1]], y=[0, q[2]], z=[0, q[3]],
        marker=dict(size=4),
        line=dict(color="green", width=6)
    ))
    fig.update_layout(scene=dict(
        xaxis_title='X', yaxis_title='Y', zaxis_title='Z'
    ))
    return fig

# ===================== PDF EXPORTACIÓN =====================
def generar_pdf(q1, q2, resultado, operacion, explicacion, fig_path, logo_path):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Logo ULSA
    story.append(Image(logo_path, width=200, height=70))
    story.append(Spacer(1, 20))

    # Encabezado
    story.append(Paragraph("<b><font size=16 color='green'>Calculadora de Cuaterniones - ULSA</font></b>", styles["Title"]))
    story.append(Paragraph(f"Fecha: {datetime.date.today()}", styles["Normal"]))
    story.append(Spacer(1, 20))

    # Datos de entrada
    story.append(Paragraph(f"<b>q1:</b> {q1}", styles["Normal"]))
    story.append(Paragraph(f"<b>q2:</b> {q2}", styles["Normal"]))
    story.append(Paragraph(f"<b>Operación:</b> {operacion}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Resultado
    story.append(Paragraph(f"<b>Resultado:</b> {resultado}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Explicación paso a paso
    story.append(Paragraph("<b>Explicación paso a paso:</b>", styles["Heading2"]))
    story.append(Paragraph(explicacion, styles["Normal"]))
    story.append(Spacer(1, 12))

    # Imagen 3D
    story.append(Paragraph("<b>Visualización 3D:</b>", styles["Heading2"]))
    story.append(Image(fig_path, width=400, height=300))
    story.append(Spacer(1, 20))

    # Sección educativa
    story.append(Paragraph("<b>Qué es un cuaternión:</b>", styles["Heading2"]))
    story.append(Paragraph("Un cuaternión es una extensión de los números complejos con cuatro componentes: "
                           "uno real y tres imaginarios. Se utilizan en gráficos 3D y robótica para representar rotaciones.", styles["Normal"]))
    story.append(Paragraph("<b>Aplicaciones:</b>", styles["Heading2"]))
    story.append(Paragraph("En videojuegos, robótica y simulaciones físicas, los cuaterniones permiten representar rotaciones "
                           "sin sufrir gimbal lock.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ===================== INTERFAZ STREAMLIT =====================
st.sidebar.title("Menú")
st.sidebar.info("Calculadora de Cuaterniones - ULSA")
operacion = st.sidebar.selectbox("Selecciona la operación", ["Suma", "Resta", "Multiplicación", "Conjugado q1", "Norma q1"])

st.title("🧮 Calculadora de Cuaterniones - ULSA")
st.write("Explora las operaciones con cuaterniones y aprende paso a paso cómo se realizan.")

q1 = [st.number_input("q1 - parte real", value=1.0),
      st.number_input("q1 - i", value=0.0),
      st.number_input("q1 - j", value=0.0),
      st.number_input("q1 - k", value=0.0)]

q2 = [st.number_input("q2 - parte real", value=1.0),
      st.number_input("q2 - i", value=0.0),
      st.number_input("q2 - j", value=0.0),
      st.number_input("q2 - k", value=0.0)]

resultado, explicacion = None, ""
if st.button("Calcular"):
    if operacion == "Suma":
        resultado, explicacion = suma(np.array(q1), np.array(q2))
    elif operacion == "Resta":
        resultado, explicacion = resta(np.array(q1), np.array(q2))
    elif operacion == "Multiplicación":
        resultado, explicacion = multiplicacion(np.array(q1), np.array(q2))
    elif operacion == "Conjugado q1":
        resultado, explicacion = conjugado(np.array(q1))
    elif operacion == "Norma q1":
        resultado, explicacion = norma(np.array(q1))

    st.success(f"Resultado: {resultado}")
    st.info(explicacion)

    # Mostrar gráfica
    fig = plot_quaternion(resultado if isinstance(resultado, np.ndarray) else [resultado,0,0,0])
    st.plotly_chart(fig)

    # Guardar figura temporal
    fig_path = "temp.png"
    fig.write_image(fig_path)

    # Botón PDF
    logo_path = "ulsa_logo.png"  # asegúrate de tener esta imagen en tu carpeta
    pdf_buffer = generar_pdf(q1, q2, resultado, operacion, explicacion, fig_path, logo_path)
    st.download_button("📄 Descargar PDF", data=pdf_buffer, file_name="reporte_cuaterniones.pdf", mime="application/pdf")
