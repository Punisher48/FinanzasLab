"""Aplicación principal de FinanzasLab - Tablero de Visualización de Ingeniería Financiera."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules import (
    amortizacion,
    casos_aplicados,
    gradientes,
    interes,
    series_uniformes,
    supuestos_verificacion,
    tasas,
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
    <style>
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
            font-size: 1.55rem !important;
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

MODULOS = {
    "🏠 Inicio (Panel Síntesis)": None,
    "💰 Interés Simple y Compuesto": interes,
    "📈 Tasas y Rentabilidad": tasas,
    "🔁 Series Uniformes": series_uniformes,
    "📉 Gradientes (Aritmético/Geom.)": gradientes,
    "🧾 Tablas de Amortización": amortizacion,
    "🏦 Casos Financieros Aplicados": casos_aplicados,
    "📋 Supuestos y Verificación": supuestos_verificacion,
}

# Integrantes fijos
integrante_1 = "Santiago Izef"
integrante_2 = "Miguel Arboleda"
integrante_3 = "Andrés Rojas"

with st.sidebar:
    st.markdown("## 📊 FinanzasLab")
    st.caption("Tablero Interactivo de Ingeniería Financiera")
    st.caption("**Docente**: Adriana Arango L. | UPB")
    st.divider()

    seccion = st.radio(
        "Navegación del Tablero",
        options=list(MODULOS.keys()),
        label_visibility="collapsed",
    )
    st.divider()

    st.markdown("### 👥 Integrantes del Equipo")
    st.markdown(
        f"""
        - 🎓 **{integrante_1}**
        - 🎓 **{integrante_2}**
        - 🎓 **{integrante_3}**
        """
    )
    st.divider()
    st.caption("✨ UPB · Escuela de Ingenierías")

# ---------------- CONTENIDO DEL PANEL PRINCIPAL (INICIO) ----------------
if seccion == "🏠 Inicio (Panel Síntesis)":
    # Banner Hero Académico
    st.markdown(
        f"""
        <section class="hero">
            <h1>FinanzasLab — Tablero de Ingeniería Financiera</h1>
            <p>Laboratorio interactivo de síntesis: interés simple, interés compuesto, equivalencia de tasas, series uniformes, gradientes y tablas de amortización.</p>
            <div class="team-container">
                <span class="team-pill">🎓 {integrante_1}</span>
                <span class="team-pill">🎓 {integrante_2}</span>
                <span class="team-pill">🎓 {integrante_3}</span>
                <span class="team-pill">🏛️ UPB — Escuela de Ingenierías</span>
                <span class="team-pill">📅 Octubre 2026</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # Indicadores Clave del Tablero (Consolidado Ejecutivo)
    st.subheader("📌 Indicadores Clave Consolidados")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(label="Rendimiento Máximo Evaluado", value="12.00% EA", delta="Cajita Nu Bank (Caso 1)")
    with k2:
        st.metric(label="Cuota Crédito Vehículo (Francés)", value="$1.116.488 COP", delta="Davivienda 48m (Caso 2)")
    with k3:
        st.metric(label="Ahorro Intereses con Sist. Alemán", value="$1.666.667 COP", delta="-12.3% vs. Francés")
    with k4:
        st.metric(label="Meta Vivienda Ahorro Acumulado", value="$30.000.000 COP", delta="Fondo Crecer (Caso 3)")

    st.markdown("<br>", unsafe_allow_html=True)

    # Sección en 2 columnas: Resumen ejecutivo a la izquierda + Gráfico comparativo a la derecha
    col_izq, col_der = st.columns([1.1, 0.9], gap="large")

    with col_izq:
        st.subheader("📑 Casos Financieros Reales (Mercado Colombiano)")
        st.write("Síntesis comparativa de decisiones sobre productos verificados a Octubre 2026:")

        resumen_casos_df = pd.DataFrame({
            "Caso / Decisión": [
                "1. CDT vs Cajita Nu",
                "2. Crédito Vehículo",
                "3. Ahorro Vivienda",
            ],
            "Tasa (TEA)": [
                "Nu 12.00% (Neta 11.51%)",
                "16.08% EA (1.25% mes)",
                "8.50% EA (0.682% mes)",
            ],
            "Impacto Económico": [
                "+$863.078 COP netos",
                "Ahorro Alemán: $1.666.667",
                "Rendimientos: $3.528.304",
            ],
            "Decisión Recomendada": [
                "✅ Nu: Mayor TEA y liquidez diaria.",
                "✅ Alemán: Cuotas decrecientes.",
                "✅ Gradiente: Cuota inicial menor.",
            ],
        })
        st.dataframe(resumen_casos_df, use_container_width=True, hide_index=True)

    with col_der:
        st.subheader("📊 Comparación Visual de Rendimientos y Costos")
        fig_home = go.Figure()
        categorias = ["Nu (Inversión)", "CDT Bancolombia", "Fondo Vivienda", "Crédito Vehículo (Costo)"]
        tasas_ea = [12.00, 10.25, 8.50, 16.08]
        colores = ["#2563eb", "#60a5fa", "#38bdf8", "#f59e0b"]

        fig_home.add_trace(go.Bar(
            x=categorias,
            y=tasas_ea,
            text=[f"{t:.2f}%" for t in tasas_ea],
            textposition="auto",
            marker=dict(color=colores, line=dict(color="#1e3a8a", width=1.5)),
            name="Tasa Efectiva Anual (EA)",
        ))
        fig_home.update_layout(
            title="Tasas Efectivas Anuales Evaluadas en el Tablero (%)",
            yaxis_title="Tasa Efectiva Anual (% EA)",
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20),
            height=280,
        )
        st.plotly_chart(fig_home, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Navegación hacia cada módulo
    st.subheader("🧭 Exploración por Módulos Temáticos")
    tarjetas = [
        ("💰", "Interés Simple y Compuesto", "Cálculos, despejes de variables (C, M, i, t), convención de días y comparación gráfica simultánea de la brecha exponencial."),
        ("📈", "Tasas y Rentabilidad", "Conversión de tasas vencidas/anticipadas, nominales/efectivas, tasas combinadas (Fisher), retención en la fuente y tabla de equivalencias."),
        ("🔁", "Series Uniformes", "Anualidades vencidas y anticipadas. Cálculo de VP, VF y cuotas con gráficos combinados de flujo y saldo."),
        ("📉", "Gradientes Financieros", "Series con gradientes aritméticos y geométricos. Cálculo de VP, VF, Cuota Uniforme Equivalente y flujos."),
        ("🧾", "Tablas de Amortización", "Simulador completo para Sistemas Francés y Alemán. Verificación de suma de capital, saldo cero y comparador simultáneo."),
        ("🏦", "Casos Financieros Aplicados", "Tres decisiones financieras con datos reales bancarios de Colombia, respondiendo las 4 preguntas de la rúbrica."),
        ("📋", "Supuestos y Verificación", "Documentación formal de convenciones de días, tipos de tasas, compendio de fórmulas y matriz de comprobación."),
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
