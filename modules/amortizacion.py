"""Tablas de amortización de préstamos: Sistema Francés (Cuota Fija) y Alemán (Abono Constante a Capital)."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.ui import mostrar_verificacion
from motor.formato import formato_cop, variacion_pct
from motor.tasas import TIPOS_TASA
from motor.amortizacion import (
    MAX_CUOTAS,
    PERIODICIDADES_AMORT,
    amortizacion_aleman,
    CUOTA_FIJA,
    FORMAS_PAGO,
    SISTEMAS,
    amortizacion_frances,
    puntos_saldo,
    tabla_amortizacion,
    verificar_amortizacion,
    calcular_tasa_periodica,
)


# ------------------ RENDER STREAMLIT ------------------

def render():
    st.title("Tablas de Amortización de Créditos")
    st.write(
        "Módulo integral para simular créditos en los sistemas **Francés (Cuota Fija)** y **Alemán (Abono Constante a Capital)**. "
        "Permite parametrizar el tipo de tasa, la periodicidad de pago y realizar una comparación simultánea entre ambos sistemas."
    )

    tab_simulador, tab_comparativa, tab_verif = st.tabs([
        "🧾 Simulador de Tabla",
        "⚖️ Comparación Francés vs. Alemán",
        "✅ Supuestos y Verificación",
    ])

    with tab_simulador:
        col_ctrl, col_view = st.columns([0.35, 0.65], gap="large")

        with col_ctrl:
            st.markdown("#### 🎛️ Parámetros del Crédito")
            prestamo = st.number_input("Monto del Préstamo (COP)", min_value=100_000.0, value=20_000_000.0, step=1_000_000.0, format="%.2f")
            sistema = st.selectbox("Sistema de Amortización", SISTEMAS)
            tasa_val = st.number_input("Valor de la Tasa (%)", min_value=0.0, value=18.0, step=0.5, format="%.4f")
            tipo_tasa = st.selectbox("Tipo de Tasa", TIPOS_TASA)
            periodicidad = st.selectbox("Periodicidad de Pago", list(PERIODICIDADES_AMORT.keys()))
            forma_pago = st.selectbox("Forma de Pago", FORMAS_PAGO, help="Vencida: al final de cada periodo. Anticipada: al inicio, con el primer pago en el periodo 0.")
            n_cuotas = st.number_input("Número de Cuotas (Plazo)", min_value=1, max_value=MAX_CUOTAS, value=24, step=1)

        tasa_per = calcular_tasa_periodica(tasa_val, tipo_tasa, periodicidad)
        is_frances = sistema == CUOTA_FIJA
        df_tabla = tabla_amortizacion(prestamo, tasa_per, int(n_cuotas), sistema, forma_pago)

        total_cuotas = float(df_tabla["Cuota (COP)"].sum())
        total_intereses = float(df_tabla["Interés (COP)"].sum())

        with col_view:
            st.markdown("#### 📊 Métricas Clave del Crédito")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Tasa Periódica", f"{tasa_per * 100:.4f}% {periodicidad.lower()}")
            k2.metric("Primera Cuota", formato_cop(df_tabla["Cuota (COP)"].iloc[0]))
            k3.metric("Total Intereses", formato_cop(total_intereses))
            k4.metric("Costo Total", formato_cop(total_cuotas))

            mostrar_verificacion(verificar_amortizacion(df_tabla, prestamo))

            # Gráficos
            g1, g2 = st.columns(2)
            with g1:
                fig_saldo = go.Figure()
                periodos_plot, saldos_plot = puntos_saldo(df_tabla, prestamo)
                fig_saldo.add_trace(go.Scatter(
                    x=periodos_plot,
                    y=saldos_plot,
                    mode="lines+markers",
                    name="Saldo Pendiente",
                    line=dict(color="#1d4ed8", width=3, shape="spline"),
                    fill="tozeroy",
                    fillcolor="rgba(29, 78, 216, 0.08)",
                ))
                fig_saldo.update_layout(
                    title="Evolución del Saldo Pendiente",
                    xaxis_title="Período",
                    yaxis_title="Saldo (COP)",
                    template="plotly_white",
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=260,
                )
                st.plotly_chart(fig_saldo, use_container_width=True)

            with g2:
                fig_comp = go.Figure()
                fig_comp.add_trace(go.Bar(x=df_tabla["Período"], y=df_tabla["Abono a Capital (COP)"], name="Abono a Capital", marker_color="#60a5fa"))
                fig_comp.add_trace(go.Bar(x=df_tabla["Período"], y=df_tabla["Interés (COP)"], name="Interés", marker_color="#f59e0b"))
                fig_comp.update_layout(
                    title="Composición de la Cuota por Período",
                    barmode="stack",
                    xaxis_title="Período",
                    yaxis_title="Monto (COP)",
                    template="plotly_white",
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=260,
                    legend=dict(orientation="h", y=1.1, x=0.1),
                )
                st.plotly_chart(fig_comp, use_container_width=True)

            st.markdown("##### Fórmulas Matemáticas y Sustitución")
            cuota_0 = df_tabla["Cuota (COP)"].iloc[0]
            cuota_n = df_tabla["Cuota (COP)"].iloc[-1]
            n_int = int(n_cuotas)
            if is_frances and forma_pago == "Vencida":
                st.latex(rf"A = P \cdot \frac{{i}}{{1 - (1+i)^{{-n}}}} = {prestamo:,.2f} \cdot \frac{{{tasa_per:.6g}}}{{1 - (1 + {tasa_per:.6g})^{{-{n_int}}}}} = {cuota_0:,.2f}\text{{ COP}}")
            elif is_frances:
                st.latex(rf"A = \frac{{P}}{{\left[\frac{{1 - (1+i)^{{-n}}}}{{i}}\right](1+i)}} = {cuota_0:,.2f}\text{{ COP (primera cuota en el periodo 0)}}")
            else:
                abono_c = prestamo / n_int
                st.latex(rf"K = \frac{{P}}{{n}} = \frac{{{prestamo:,.2f}}}{{{n_int}}} = {abono_c:,.2f}\text{{ COP}}, \qquad A_t = K + S_{{t-1}} \cdot i")
                st.latex(rf"\text{{Primera cuota}} = {cuota_0:,.2f}\text{{ COP}}, \qquad \text{{Última cuota}} = {cuota_n:,.2f}\text{{ COP}}")

        st.markdown("##### 📋 Tabla Completa de Amortización")
        df_most = df_tabla.copy()
        for c in ["Saldo Inicial (COP)", "Cuota (COP)", "Interés (COP)", "Abono a Capital (COP)", "Saldo Final (COP)"]:
            df_most[c] = df_most[c].map(formato_cop)
        st.dataframe(df_most, use_container_width=True, hide_index=True)

    with tab_comparativa:
        st.subheader("Comparación Simultánea: Sistema Francés vs. Sistema Alemán")
        col_comp_ctrl, col_comp_view = st.columns([0.35, 0.65], gap="large")

        with col_comp_ctrl:
            st.markdown("#### 🎛️ Parámetros Comunes")
            comp_prestamo = st.number_input("Monto del Crédito (COP)", min_value=100_000.0, value=30_000_000.0, step=1_000_000.0, format="%.2f", key="comp_prestamo")
            comp_tasa_ea = st.number_input("Tasa Efectiva Anual EA (%)", min_value=0.0, value=20.0, step=0.5, format="%.4f", key="comp_tasa_ea")
            comp_plazo = st.number_input("Plazo en Meses", min_value=1, max_value=MAX_CUOTAS, value=36, step=1, key="comp_plazo")

        tasa_mes = calcular_tasa_periodica(comp_tasa_ea, "Efectiva Anual (EA)", "Mensual")
        df_f = amortizacion_frances(comp_prestamo, tasa_mes, int(comp_plazo))
        df_a = amortizacion_aleman(comp_prestamo, tasa_mes, int(comp_plazo))

        int_f = float(df_f["Interés (COP)"].sum())
        int_a = float(df_a["Interés (COP)"].sum())
        total_f = float(df_f["Cuota (COP)"].sum())
        total_a = float(df_a["Cuota (COP)"].sum())
        ahorro_intereses = int_f - int_a

        with col_comp_view:
            st.markdown("#### 📊 Análisis Comparativo Directo")
            m1, m2, m3 = st.columns(3)
            m1.metric("Intereses Francés", formato_cop(int_f))
            m2.metric("Intereses Alemán", formato_cop(int_a))
            m3.metric("Ahorro con Sist. Alemán", formato_cop(ahorro_intereses), delta=f"-{variacion_pct(ahorro_intereses, int_f):.2f}% de intereses")

            c_ini_f, c_fin_f = df_f["Cuota (COP)"].iloc[0], df_f["Cuota (COP)"].iloc[-1]
            c_ini_a, c_fin_a = df_a["Cuota (COP)"].iloc[0], df_a["Cuota (COP)"].iloc[-1]

            fig_cuotas = go.Figure()
            fig_cuotas.add_trace(go.Scatter(x=df_f["Período"], y=df_f["Cuota (COP)"], mode="lines+markers", name="Cuota Francés (Constante)", line=dict(color="#f59e0b", width=3)))
            fig_cuotas.add_trace(go.Scatter(x=df_a["Período"], y=df_a["Cuota (COP)"], mode="lines+markers", name="Cuota Alemán (Decreciente)", line=dict(color="#2563eb", width=3, shape="spline")))
            fig_cuotas.update_layout(
                title="Comparación de Cuotas Mensuales: Francés vs. Alemán",
                xaxis_title="Mes",
                yaxis_title="Cuota (COP)",
                template="plotly_white",
                margin=dict(l=20, r=20, t=40, b=20),
                height=280,
                legend=dict(orientation="h", y=1.1, x=0.2),
            )
            st.plotly_chart(fig_cuotas, use_container_width=True)

        st.markdown("##### 📑 Cuadro Resumen Comparativo")
        df_resumen = pd.DataFrame({
            "Sistema de Amortización": ["Francés (Cuota Fija)", "Alemán (Abono Constante)", "Diferencia"],
            "Cuota Inicial (Mes 1)": [formato_cop(c_ini_f), formato_cop(c_ini_a), formato_cop(c_ini_a - c_ini_f) + " (Alemán inicial más alta)"],
            "Cuota Final (Último Mes)": [formato_cop(c_fin_f), formato_cop(c_fin_a), formato_cop(c_fin_f - c_fin_a) + " (Alemán final más baja)"],
            "Total Intereses": [formato_cop(int_f), formato_cop(int_a), f"-{formato_cop(ahorro_intereses)} a favor del Alemán"],
            "Desembolso Total Pagado": [formato_cop(total_f), formato_cop(total_a), f"-{formato_cop(ahorro_intereses)}"],
        })
        st.dataframe(df_resumen, use_container_width=True, hide_index=True)

    with tab_verif:
        st.subheader("Supuestos Técnicos y Verificación de Amortización")
        col_s, col_v = st.columns(2, gap="large")
        with col_s:
            st.markdown(
                r"""
                #### Supuestos Técnicos:
                1. **Sistema Francés**: Cuotas periódicas uniformes ($A$). Los primeros períodos amortizan menor capital y liquidan mayor proporción de intereses.
                2. **Sistema Alemán**: Abono a capital constante en cada período ($K = P / n$). Las cuotas son decrecientes en el tiempo, pagando menores intereses acumulados que el sistema francés.
                3. **Condición de Cierre**: El saldo final al término del plazo $n$ debe ser estrictamente cero ($S_n = 0$) y la sumatoria de abonos a capital debe igualar con exactitud el capital prestado ($\sum K_t = P$).
                """
            )

        with col_v:
            st.markdown("#### Comprobación de Cálculo Manual (Paso a Paso)")
            st.latex(r"P = 1{.}000{.}000\text{ COP}, \quad i = 10\%\text{ periódico } (0{,}10), \quad n = 2\text{ cuotas}")
            st.latex(
                r"""
                \begin{aligned}
                \text{Francés: } A &= 1{.}000{.}000 \cdot \frac{0{,}10}{1 - (1{,}10)^{-2}} = 576{.}190{,}48\text{ COP} \\
                \text{Alemán: } K &= \frac{1{.}000{.}000}{2} = 500{.}000\text{ COP}, \quad A_1 = 600{.}000, \quad A_2 = 550{.}000\text{ COP} \\
                \text{Ahorro: } \Delta &= 152{.}380{,}95 - 150{.}000{,}00 = 2{.}380{,}95\text{ COP} \quad \text{✅ Verificado}
                \end{aligned}
                """
            )
