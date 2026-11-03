"""Pantalla C: ¿Cuánto debo ahorrar para mi meta?"""

import plotly.graph_objects as go
import streamlit as st

from modules.ui import COLORES, GRIS, aplicar_estilo, aviso_datos_ejemplo, campos_fuente, parametros, tabla_cop, texto_dinero
from motor.datos_ejemplo import CASO_C, PLAN_ARITMETICO, PLAN_GEOMETRICO, PLANES
from motor.decisiones import PERIODICIDADES_TASA, evaluar_caso_c
from motor.formato import formato_cop
from motor.tasas import TIPOS_TASA


def _entradas() -> None:
    st.markdown("#### 🎛️ Tu meta")
    st.number_input("Meta (valor futuro, COP)", min_value=1.0, step=1_000_000.0, format="%.2f", key="c_meta")
    st.number_input("Plazo (meses)", min_value=1, max_value=600, step=6, key="c_meses")
    st.number_input("Capital inicial (COP, opcional)", min_value=0.0, step=500_000.0, format="%.2f", key="c_capital")
    st.number_input("Tasa de rentabilidad (%)", min_value=0.0, step=0.25, format="%.4f", key="c_tasa")
    st.selectbox("Tipo de tasa", TIPOS_TASA, key="c_tipo")
    st.selectbox("Periodicidad de la tasa", list(PERIODICIDADES_TASA), key="c_periodicidad")
    plan = st.selectbox("Tipo de plan", PLANES, key="c_plan")
    if plan == PLAN_GEOMETRICO:
        st.number_input("Crecimiento anual de la cuota (%)", min_value=-50.0, step=0.5, format="%.2f", key="c_crecimiento_pct")
    elif plan == PLAN_ARITMETICO:
        st.number_input("Aumento anual de la cuota (COP)", step=10_000.0, format="%.2f", key="c_crecimiento_cop")
    st.caption("Los aportes son mensuales y vencidos. La cuota se mantiene 12 meses y sube al empezar cada año.")


def _resultados(r: dict, p: dict) -> None:
    st.markdown("#### ✅ Tu plan")
    st.success(texto_dinero(r["recomendacion"]))
    k1, k2 = st.columns(2)
    k3, k4 = st.columns(2)
    k1.metric("Cuota inicial", formato_cop(r["cuota_inicial"]))
    k2.metric("Cuota final", formato_cop(r["cuota_final"]))
    k3.metric("Total aportado", formato_cop(r["total_aportado"]))
    k4.metric("Intereses ganados", formato_cop(r["intereses"]))

    mensaje = f"Saldo final: {formato_cop(r['saldo_final'])}, meta: {formato_cop(p['c_meta'])}"
    if r["ok_meta"]:
        st.success(texto_dinero(f"✅ {mensaje} (el calendario llega a la meta)"))
    else:
        st.error(texto_dinero(f"❌ {mensaje} (el calendario no llega a la meta)"))

    calendario = r["calendario"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=calendario["Mes"], y=calendario["Aporte (COP)"], name="Aporte del mes", marker=dict(color=COLORES[0], line=dict(color="white", width=1))))
    st.plotly_chart(aplicar_estilo(fig, "Flujo de aportes mensuales", "Mes", "Aporte (COP)", 280), width="stretch")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=calendario["Mes"], y=calendario["Saldo Acumulado (COP)"], mode="lines", name="Valor acumulado", line=dict(color=COLORES[0], width=3)))
    fig.add_trace(go.Scatter(x=[calendario["Mes"].iloc[0], calendario["Mes"].iloc[-1]], y=[p["c_meta"]] * 2, mode="lines", name="Meta", line=dict(color=GRIS, width=2, dash="dash")))
    st.plotly_chart(aplicar_estilo(fig, "Valor acumulado hacia la meta", "Mes", "Valor acumulado (COP)", 320), width="stretch")


def render() -> None:
    st.title("🎯 ¿Cuánto debo ahorrar para mi meta?")
    st.write("Calcula la cuota necesaria con un plan uniforme o con cuotas que crecen cada año.")
    aviso_datos_ejemplo()

    col_entradas, col_resultados = st.columns([0.32, 0.68], gap="large")
    with col_entradas:
        _entradas()
    with col_resultados:
        try:
            p = parametros(CASO_C)
            r = evaluar_caso_c(p)
            _resultados(r, p)
        except ValueError as e:
            r = None
            st.error(f"Revisa los datos: {e}")

    if r is not None:
        st.markdown("##### 📅 Calendario de aportes")
        columnas = ["Aporte (COP)", "Interés Ganado (COP)", "Saldo Acumulado (COP)"]
        st.dataframe(tabla_cop(r["calendario"], columnas), width="stretch", hide_index=True)

        with st.expander("📐 Fórmulas usadas"):
            st.latex(r"\text{Uniforme: } C_t = A_1 \qquad \text{Aritmético: } C_t = A_1 + G \cdot a_t \qquad \text{Geométrico: } C_t = A_1 (1 + g)^{a_t}")
            st.latex(r"A_1 = \frac{\text{Meta} - K (1 + i)^n - G \cdot F_G}{F_A}")
            st.latex(r"F_A = \sum_{t=1}^{n} w_t (1 + i)^{n - t} \qquad F_G = \sum_{t=1}^{n} a_t (1 + i)^{n - t}")
            st.caption("a_t: años completos transcurridos antes del mes t; w_t: 1, o (1 + g)^a_t en el plan geométrico; K: capital inicial; i: tasa mensual; n: meses.")
    campos_fuente("c_")
