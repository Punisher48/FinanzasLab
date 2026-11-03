"""Aplicación principal de FinanzasLab - Tablero de Visualización de Ingeniería Financiera."""

import streamlit as st

from modules import (
    amortizacion,
    decision_ahorro,
    decision_credito,
    decision_inversion,
    gradientes,
    inicio,
    interes,
    series_uniformes,
    supuestos_verificacion,
    tasas,
    ui,
)

st.set_page_config(
    page_title="FinanzasLab — Tablero de Ingeniería Financiera",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS Personalizados: Estética Pastel Blue & Academic Slate con Profundidad
st.markdown(
    """
    <meta name="google" content="notranslate">
    <meta name="googlebot" content="notranslate">
    <style>
        /* Prevención de errores de React causados por Google Translate */
        html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"], .main {
            -webkit-translate: no !important;
            translate: no !important;
        }
        .notranslate {
            -webkit-translate: no !important;
            translate: no !important;
        }

        /* Contenedor general */
        .block-container { 
            padding-top: 1.5rem; 
            padding-bottom: 3.5rem; 
            max-width: 96%;
        }

        /* Banner Hero Principal */
        .hero {
            padding: clamp(1.8rem, 3.5vw, 2.5rem);
            border-radius: 1.25rem;
            background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 60%, #93c5fd 100%);
            color: #ffffff;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.18), 0 8px 10px -6px rgba(37, 99, 235, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.25);
        }
        .hero h1 { 
            color: #ffffff; 
            font-size: 2.3rem; 
            font-weight: 700; 
            margin-bottom: 0.35rem; 
            letter-spacing: -0.02em;
        }
        .hero p { 
            color: #e0f2fe; 
            font-size: 1.05rem; 
            margin-bottom: 0.8rem; 
            line-height: 1.5;
        }
        .team-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }
        .team-pill {
            display: inline-flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(8px);
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            font-size: 0.88rem;
            font-weight: 500;
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        /* Panel de Parámetros (Columna Izquierda) */
        .control-panel-header {
            background: linear-gradient(90deg, #1e3a8a, #2563eb);
            color: white;
            padding: 0.75rem 1rem;
            border-radius: 0.85rem 0.85rem 0 0;
            font-weight: 600;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* Tarjetas de Navegación */
        .section-card {
            border: 1px solid #cbd5e1;
            border-left: 5px solid #2563eb;
            border-radius: 1rem;
            padding: 1.25rem 1.35rem;
            min-height: 140px;
            background: linear-gradient(180deg, #ffffff 0%, #f8faff 100%);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.04);
            transition: all 0.25s ease-in-out;
        }
        .section-card:hover {
            border-color: #60a5fa;
            border-left-color: #1e3a8a;
            box-shadow: 0 10px 20px -3px rgba(37, 99, 235, 0.14);
            transform: translateY(-3px);
        }
        .section-card h3 { 
            margin-top: 0; 
            font-size: 1.1rem; 
            font-weight: 600;
            color: #1e3a8a; 
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .section-card p { 
            margin-bottom: 0; 
            color: #475569; 
            font-size: 0.92rem; 
            line-height: 1.45;
        }

        /* Tarjeta de Fórmula / Sustento */
        .formula-callout {
            background: #f0f7ff;
            border: 1px solid #bfdbfe;
            border-left: 4px solid #2563eb;
            border-radius: 0.85rem;
            padding: 1rem 1.25rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.03);
        }

        /* Tarjetas de Métricas (KPIs) */
        [data-testid="stMetric"] {
            background: linear-gradient(180deg, #ffffff 0%, #f8faff 100%);
            border: 1px solid #bfdbfe;
            border-top: 3px solid #2563eb;
            border-radius: 0.85rem;
            padding: 0.95rem 1.15rem;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.05);
        }
        [data-testid="stMetricLabel"] {
            color: #475569 !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
        }
        [data-testid="stMetricValue"] {
            color: #1e3a8a !important;
            font-weight: 700 !important;
            font-size: 1.2rem !important;
        }
        [data-testid="stMetricValue"], [data-testid="stMetricValue"] *,
        [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }

        /* Formularios y Botones */
        div[data-testid="stForm"] {
            background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
            border: 1px solid #dbeafe;
            border-radius: 1rem;
            padding: 1.35rem;
            box-shadow: 0 4px 12px -2px rgba(37, 99, 235, 0.05);
        }
        .stButton > button[type="primary"] {
            background-color: #2563eb;
            color: #ffffff;
            font-weight: 600;
            border-radius: 0.65rem;
            border: none;
            padding: 0.6rem 1.35rem;
            width: 100%;
            transition: all 0.2s ease;
            box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
        }
        .stButton > button[type="primary"]:hover {
            background-color: #1d4ed8;
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
            transform: translateY(-1px);
        }

        /* Pestañas (Tabs) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
            margin-bottom: 0.75rem;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 0.6rem 0.6rem 0 0;
            padding: 0.55rem 1.15rem;
            font-weight: 600;
            color: #475569;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-bottom: none;
        }
        .stTabs [aria-selected="true"] {
            background-color: #e0f2fe !important;
            color: #1e40af !important;
            border-color: #93c5fd !important;
            border-bottom: 2px solid #2563eb !important;
        }

        /* Barra Lateral */
        [data-testid="stSidebar"] {
            background-color: #f1f6fc;
            border-right: 1px solid #cbd5e1;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

ui.iniciar_estado()

MODULOS = {
    "🏠 Inicio (Panel Síntesis)": inicio,
    "💸 ¿Dónde pongo mi plata?": decision_inversion,
    "🏦 ¿Me conviene este crédito?": decision_credito,
    "🎯 ¿Cuánto debo ahorrar para mi meta?": decision_ahorro,
    "💰 Interés Simple y Compuesto": interes,
    "📈 Tasas y Rentabilidad": tasas,
    "🔁 Series Uniformes": series_uniformes,
    "📉 Gradientes (Aritmético/Geom.)": gradientes,
    "🧾 Tablas de Amortización": amortizacion,
    "📋 Supuestos y Fórmulas": supuestos_verificacion,
}

INICIO = "🏠 Inicio (Panel Síntesis)"
INTEGRANTES = ["Santiago Izef", "Miguel Arboleda", "Andrés Rojas"]

with st.sidebar:
    st.markdown("## 📊 FinanzasLab")
    st.caption("Tablero Interactivo de Ingeniería Financiera")
    st.caption("**Docente**: Adriana Arango L. | UPB")
    st.divider()

    seccion = st.radio(
        "Navegación del Tablero",
        options=list(MODULOS.keys()),
        label_visibility="collapsed",
        key="nav",
    )
    st.divider()

    st.markdown("### 👥 Integrantes del Equipo")
    st.markdown("\n".join(f"- 🎓 **{nombre}**" for nombre in INTEGRANTES))
    st.divider()
    st.caption("✨ UPB · Escuela de Ingenierías")

if seccion == INICIO:
    inicio.render(INTEGRANTES, [nombre for nombre in list(MODULOS)[4:]])
else:
    MODULOS[seccion].render()
