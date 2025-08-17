import streamlit as st
import numpy as np
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import plotly.io as pio

# Configuración de Kaleido para exportar imágenes
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 600
pio.kaleido.scope.default_height = 600

# ----------------- Funciones de cuaterniones -----------------
class Quaternion:
    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __add__(self, other):
        return Quaternion(self.a+other.a, self.b+other.b, self.c+other.c, self.d+other.d)

    def __sub__(self, other):
        return Quaternion(self.a-other.a, self.b-other.b, self.c-other.c, self.d-other.d)

    def __mul__(self, other):
        a1,b1,c1,d1 = self.a,self.b,self.c,self.d
        a2,b2,c2,d2 = other.a,other.b,other.c,other.d
        return Quaternion(
            a1*a2 - b1*b2 - c1*c2 - d1*d2,
            a1*b2 + b1*a2 + c1*d2 - d1*c2,
            a1*c2 - b1*d2 + c1*a2 + d1*b2,
            a1*d2 + b1*c2 - c1*b2 + d1*a2
        )

    def conjugate(self):
        return Quaternion(self.a, -self.b, -self.c, -self.d)

    def norm(self):
        return np.sqrt(self.a**2 + self.b**2 + self.c**2 + self.d**2)

    def normalize(self):
        n = self.norm()
        return Quaternion(self.a/n, self.b/n, self.c/n, self.d/n)

    def to_vector(self):
        return np.array([self.b, self.c, self.d])

def rotate_vector(v, q: Quaternion):
    q = q.normalize()
    q_vec = Quaternion(0,*v)
    q_rot = q * q_vec * q.conjugate()
    return q_rot.to_vector()

# ----------------- Interfaz Streamlit -----------------
st.title("📐 Calculadora de Cuaterniones")

st.subheader("Ingresa los valores del primer cuaternión")
q1_vals = [st.number_input(f"q1_{x}", value=0.0) for x in ["a","b","c","d"]]
q1 = Quaternion(*q1_vals)

st.subheader("Ingresa los valores del segundo cuaternión")
q2_vals = [st.number_input(f"q2_{x}", value=0.0) for x in ["a","b","c","d"]]
q2 = Quaternion(*q2_vals)

operacion = st.selectbox("Selecciona la operación", ["Suma","Resta","Multiplicación","Conjugado","Norma","Rotar Vector"])

if operacion == "Suma":
    resultado = q1 + q2
elif operacion == "Resta":
    resultado = q1 - q2
elif operacion == "Multiplicación":
    resultado = q1 * q2
elif operacion == "Conjugado":
    resultado = q1.conjugate()
elif operacion == "Norma":
    resultado = q1.norm()
elif operacion == "Rotar Vector":
    st.subheader("Vector a rotar")
    v = [st.number_input(f"v_{x}", value=0.0) for x in ["x","y","z"]]
    resultado = rotate_vector(v, q1)
else:
    resultado = "Operación no seleccionada"

st.write("**Resultado:**", resultado)

# ----------------- Visualización 3D -----------------
if operacion == "Rotar Vector":
    fig = go.Figure()
    fig.add_trace(go.Cone(x=[0], y=[0], z=[0], u=[v[0]], v=[v[1]], w=[v[2]], colorscale='reds', sizemode="absolute", sizeref=2, name="Original"))
    fig.add_trace(go.Cone(x=[0], y=[0], z=[0], u=[resultado[0]], v=[resultado[1]], w=[resultado[2]], colorscale='blues', sizemode="absolute", sizeref=2, name="Rotado"))
    fig.update_layout(scene=dict(xaxis=dict(range=[-10,10]), yaxis=dict(range=[-10,10]), zaxis=dict(range=[-10,10])))
    st.plotly_chart(fig)

    # Botón para guardar imagen
    if st.button("Guardar gráfico como PNG"):
        fig_path = "vector_rotado.png"
        fig.write_image(fig_path)
        st.success(f"Gráfico guardado en {fig_path}")

# ----------------- Exportar PDF -----------------
if st.button("Generar PDF del resultado"):
    c = canvas.Canvas("resultado.pdf", pagesize=letter)
    c.drawString(100, 750, f"Operación: {operacion}")
    c.drawString(100, 730, f"Resultado: {resultado}")
    c.save()
    st.success("PDF generado correctamente")
