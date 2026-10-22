"""Aplicación principal de FinanzasLab."""

import streamlit as st

from modules import (
    amortizacion,
    casos_aplicados,
    gradientes,
    interes,
    series_uniformes,
    tasas,
)

st.set_page_config(
    page_title="FinanzasLab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos de presentación para mantener una interfaz limpia y adaptable.
st.markdown(
    """
    <style>
        .block-container { padding-top: 2.2rem; padding-bottom: 3rem; }
        .hero {
            padding: clamp(1.5rem, 5vw, 3rem);
            border-radius: 1.25rem;
            background: linear-gradient(120deg, #102a43 0%, #176b68 100%);
            color: white;
            margin-bottom: 1.5rem;
        }
        .hero h1 { color: white; margin-bottom: .5rem; }
        .hero p { color: #e4f2f1; font-size: 1.05rem; margin-bottom: 0; }
        .section-card {
            border: 1px solid rgba(128, 150, 170, .28);
            border-radius: 1rem;
            padding: 1.1rem 1.2rem;
            min-height: 130px;
            background: rgba(128, 150, 170, .06);
        }
        .section-card h3 { margin-top: 0; font-size: 1.05rem; }
        .section-card p { margin-bottom: 0; color: #788797; }
        [data-testid="stSidebar"] { border-right: 1px solid rgba(128, 150, 170, .2); }
        @media (max-width: 640px) {
            .block-container { padding-top: 1.2rem; }
            .section-card { min-height: auto; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

MODULOS = {
    "Inicio": None,
    "Interés simple y compuesto": interes,
    "Tasas y rentabilidad": tasas,
    "Series uniformes": series_uniformes,
    "Gradientes": gradientes,
    "Tablas de amortización": amortizacion,
    "Casos financieros aplicados": casos_aplicados,
}

with st.sidebar:
    st.markdown("## 📊 FinanzasLab")
    st.caption("Herramientas para Ingeniería Financiera")
    st.divider()
    seccion = st.radio(
        "Navegación",
        options=list(MODULOS),
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Proyecto académico · Versión inicial")

if seccion == "Inicio":
    st.markdown(
        """
        <section class="hero">
            <h1>FinanzasLab</h1>
            <p>Un espacio claro para explorar conceptos y herramientas de Ingeniería Financiera.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.subheader("Explora los módulos")
    st.write("Selecciona una sección en el menú lateral para comenzar.")

    tarjetas = [
        ("💰", "Interés simple y compuesto", "Calcula montos e intereses y consulta la evolución del capital por período."),
        ("📈", "Tasas y rentabilidad", "Convierte tasas efectivas y nominales, y calcula la rentabilidad de una inversión."),
        ("🔁", "Series uniformes", "Calcula valores presentes y futuros, cuotas y flujos de pagos iguales."),
        ("📉", "Gradientes", "Analiza flujos con pagos que cambian según un gradiente aritmético o geométrico."),
        ("🧾", "Tablas de amortización", "Consulta cuotas, intereses, abonos a capital y saldos de un préstamo."),
        ("🏦", "Casos financieros aplicados", "Explora casos de ahorro, financiación e inversión con resultados y flujos."),
    ]
    for fila in range(0, len(tarjetas), 3):
        columnas = st.columns(3, gap="medium")
        for columna, (icono, titulo, descripcion) in zip(columnas, tarjetas[fila:fila + 3]):
            with columna:
                st.markdown(
                    f'<div class="section-card"><h3>{icono} {titulo}</h3>'
                    f'<p>{descripcion}</p></div>',
                    unsafe_allow_html=True,
                )
else:
    MODULOS[seccion].render()
