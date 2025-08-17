import streamlit as st
import numpy as np
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import plotly.io as pio

# Configuración de Kaleido
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 600
pio.kaleido.scope.default_height = 600

# ----------------- Clases y funciones de cuaterniones -----------------
class Quaternion:
    def __init__(self, a, b, c, d):
        self.a, self.b, self.c, self.d = a, b, c, d

    def __str__(self):
        return f"{self.a} + {self.b}i + {self.c}j + {self.d}k"

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
        if n == 0:
            return Quaternion(0,0,0,0)
        return Quaternion(self.a/n, self.b/n, self.c/n, self.d/n)

    def to_vector(self):
        return np.array([self.b, self.c, self.d])

def rotate_vector(v, q: Quaternion):
    q = q.normalize()
    q_vec = Quaternion(0,*v)
    q_rot = q * q_vec * q.conjugate()
    return q_rot.to_vector()

# ----------------- Interfaz educativa -----------------
st.set_page_config(page_title="Simulador Educativo de Cuaterniones", layout="wide")
st.title("🔬 Mini-Lab Interactivo de Cuaterniones")

st.markdown("""
Bienvenido al **simulador educativo de cuaterniones**.  
- Observa cómo los cuaterniones rotan vectores en 3D.  
- Realiza operaciones paso a paso.  
- Descarga resultados y gráficos en PDF.
""")

# Entradas de cuaterniones
col1, col2 = st.columns(2)
with col1:
    st.subheader("Primer cuaternión")
    q1_vals = [st.number_input(f"q1_{x}", value=0.0) for x in ["a","b","c","d"]]
    q1 = Quaternion(*q1_vals)
with col2:
    st.subheader("Segundo cuaternión")
    q2_vals = [st.number_input(f"q2_{x}", value=0.0) for x in ["a","b","c","d"]]
    q2 = Quaternion(*q2_vals)

operacion = st.selectbox("Selecciona la operación", ["Suma","Resta","Multiplicación","Conjugado","Norma","Rotar Vector"])

# ----------------- Ejecutar operación -----------------
resultado = None
fig_path = None

if operacion == "Suma":
    resultado = q1 + q2
    st.markdown(f"**Resultado paso a paso:**\n\n`({q1}) + ({q2}) = {resultado}`")

elif operacion == "Resta":
    resultado = q1 - q2
    st.markdown(f"**Resultado paso a paso:**\n\n`({q1}) - ({q2}) = {resultado}`")

elif operacion == "Multiplicación":
    resultado = q1 * q2
    st.markdown(f"**Resultado paso a paso:**\n\n`({q1}) * ({q2}) = {resultado}`")

elif operacion == "Conjugado":
    resultado = q1.conjugate()
    st.markdown(f"**Conjugado de {q1}:** `{resultado}`")

elif operacion == "Norma":
    resultado = q1.norm()
    st.markdown(f"**Norma de {q1}:** `{resultado}`")

elif operacion == "Rotar Vector":
    st.subheader("Vector a rotar")
    v = [st.number_input(f"v_{x}", value=1.0 if x=="x" else 0.0) for x in ["x","y","z"]]
    resultado = rotate_vector(v, q1)
    st.markdown(f"**Vector original:** `{v}`\n\n**Vector rotado con {q1}:** `{resultado}`")

    # ----------------- Visualización 3D animada -----------------
    fig = go.Figure()
    fig.add_trace(go.Cone(x=[0], y=[0], z=[0], u=[v[0]], v=[v[1]], w=[v[2]], colorscale='reds', sizemode="absolute", sizeref=2, name="Original"))
    fig.add_trace(go.Cone(x=[0], y=[0], z=[0], u=[resultado[0]], v=[resultado[1]], w=[resultado[2]], colorscale='blues', sizemode="absolute", sizeref=2, name="Rotado"))
    fig.update_layout(scene=dict(xaxis=dict(range=[-10,10]), yaxis=dict(range=[-10,10]), zaxis=dict(range=[-10,10])),
                      title="Animación interactiva de vectores")
    st.plotly_chart(fig)
    fig_path = "vector_rotado.png"
    fig.write_image(fig_path)

# ----------------- Exportar PDF completo -----------------
if st.button("📄 Generar PDF Educativo Final"):
    pdf_path = "resultado_simulador.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(70, 750, "🔬 Mini-Lab Educativo de Cuaterniones")
    c.setFont("Helvetica", 12)
    c.drawString(70, 720, f"Operación: {operacion}")
    c.drawString(70, 700, f"Primer cuaternión: {q1}")
    if operacion in ["Suma","Resta","Multiplicación"]:
        c.drawString(70, 680, f"Segundo cuaternión: {q2}")
    c.drawString(70, 660, f"Resultado: {resultado}")

    # Incluir gráfico si existe
    if fig_path:
        c.drawImage(fig_path, 70, 350, width=450, height=300)

    c.save()
    st.success(f"✅ PDF generado con resultados y gráficos en {pdf_path}")
    st.markdown(f"[Descargar PDF]({pdf_path})")
