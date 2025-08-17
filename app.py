import streamlit as st
import numpy as np
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import io
import datetime
from PIL import Image as PILImage

# ===================== FUNCIONES DE CUATERNIONES =====================
def suma(q1, q2):
    res = np.array(q1) + np.array(q2)
    explicacion = f"Suma componente a componente:\nq1: {q1}\nq2: {q2}\nResultado: {res}"
    return res, explicacion

def resta(q1, q2):
    res = np.array(q1) - np.array(q2)
    explicacion = f"Resta componente a componente:\nq1: {q1}\nq2: {q2}\nResultado: {res}"
    return res, explicacion

def multiplicacion(q1, q2):
    w1,x1,y1,z1 = q1
    w2,x2,y2,z2 = q2
    res = np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2
    ])
    explicacion = (f"Multiplicación según fórmula:\n"
                   f"({w1},{x1},{y1},{z1}) * ({w2},{x2},{y2},{z2}) = {res}")
    return res, explicacion

def conjugado(q):
    res = np.array([q[0], -q[1], -q[2], -q[3]])
    explicacion = f"Conjugado: cambiar signo de las partes imaginarias\nq: {q}\nResultado: {res}"
    return res, explicacion

def norma(q):
    res = np.linalg.norm(q)
    explicacion = f"Norma calculada como sqrt(sum(q_i^2))\nq: {q}\nResultado: {res}"
    return res, explicacion

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
def generar_pdf(q1, q2, resultado, operacion, explicacion, fig_bytes, logo_bytes):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Logo en memoria
    story.append(Image(logo_bytes, width=200, height=70))
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
    story.append(Paragraph(explicacion.replace("\n","<br/>"), styles["Normal"]))
    story.append(Spacer(1, 12))

    # Imagen 3D en memoria
    story.append(Paragraph("<b>Visualización 3D:</b>", styles["Heading2"]))
    story.append(Image(fig_bytes, width=400, height=300))
    story.append(Spacer(1, 20))

    # Sección educativa
    story.append(Paragraph("<b>Qué es un cuaternión:</b>", styles["Heading2"]))
    story.append(Paragraph("Un cuaternión es una extensión de los números complejos con cuatro componentes: uno real y tres imaginarios. Se utilizan en gráficos 3D y robótica para representar rotaciones.", styles["Normal"]))
    story.append(Paragraph("<b>Aplicaciones:</b>", styles["Heading2"]))
    story.append(Paragraph("En videojuegos, robótica y simulaciones físicas, los cuaterniones permiten representar rotaciones sin sufrir gimbal lock.", styles["Normal"]))

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
        resultado, explicacion = suma(q1, q2)
    elif operacion == "Resta":
        resultado, explicacion = resta(q1, q2)
    elif operacion == "Multiplicación":
        resultado, explicacion = multiplicacion(q1, q2)
    elif operacion == "Conjugado q1":
        resultado, explicacion = conjugado(q1)
    elif operacion == "Norma q1":
        resultado, explicacion = norma(q1)

    st.success(f"Resultado: {resultado}")

    with st.expander("📖 Paso a paso"):
        st.info(explicacion)

    # Mostrar gráfica
    if isinstance(resultado, (list, np.ndarray)) and len(resultado) >= 4:
        fig = plot_quaternion(resultado)
        st.plotly_chart(fig)

        # Guardar figura en memoria para PDF
        fig_bytes_io = io.BytesIO()
        fig.write_image(fig_bytes_io, format="PNG")
        fig_bytes_io.seek(0)

        # Logo en memoria
        logo_image = PILImage.open("ulsa_logo.png")
        logo_bytes_io = io.BytesIO()
        logo_image.save(logo_bytes_io, format="PNG")
        logo_bytes_io.seek(0)

        # Descargar PDF
        pdf_buffer = generar_pdf(q1, q2, resultado, operacion, explicacion, fig_bytes_io, logo_bytes_io)
        st.download_button("📄 Descargar PDF", data=pdf_buffer, file_name="reporte_cuaterniones.pdf", mime="application/pdf")
