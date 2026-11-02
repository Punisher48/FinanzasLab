"""Cálculos y comparaciones de interés simple e interés compuesto."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from motor.formato import formato_cop
from motor.interes import *  # noqa: F401,F403


# ------------------ RENDER STREAMLIT ------------------

def render():
    st.title("Interés Simple y Compuesto")
    st.write(
        "Panel interactivo para cálculo y despeje de variables en regímenes simple y compuesto, "
        "con soporte para convenciones de días y comparación gráfica simultánea del crecimiento del capital."
    )

    tab_simple, tab_compuesto, tab_comparacion, tab_verificacion = st.tabs([
        "💰 Interés Simple",
        "📈 Interés Compuesto",
        "⚖️ Comparación Simultánea",
        "✅ Supuestos y Verificación",
    ])

    # ---------------- TAB 1: INTERÉS SIMPLE ----------------
    with tab_simple:
        col_ctrl, col_view = st.columns([0.38, 0.62], gap="large")

        with col_ctrl:
            st.markdown("#### 🎛️ Parámetros de Simulación")
            accion_simple = st.selectbox(
                "Variable a calcular",
                [
                    "Valor Futuro (Monto final) e Interés",
                    "Valor Presente (Capital inicial)",
                    "Tasa de interés periódica",
                    "Plazo o tiempo transcurrido",
                ],
                key="simple_accion",
            )
            convencion = st.selectbox(
                "Convención de días",
                ["Comercial (360 días)", "Exacto (365 días)"],
                key="simple_convencion",
            )
            unidad_tiempo = st.selectbox(
                "Unidad del plazo",
                ["Años", "Meses", "Días"],
                key="simple_unidad",
            )

            with st.form("form_interes_simple"):
                if accion_simple == "Valor Futuro (Monto final) e Interés":
                    c_in = st.number_input("Capital inicial - VP (COP)", min_value=0.0, value=5_000_000.0, step=500_000.0, format="%.2f")
                    tasa_in = st.number_input(f"Tasa de interés por {unidad_tiempo.lower()[:-1] if unidad_tiempo.endswith('s') else unidad_tiempo} (%)", min_value=0.0, value=2.0, step=0.25, format="%.4f")
                    plazo_in = st.number_input(f"Plazo ({unidad_tiempo})", min_value=1.0, value=12.0, step=1.0, format="%.2f")
                elif accion_simple == "Valor Presente (Capital inicial)":
                    m_in = st.number_input("Valor Futuro objetivo - VF (COP)", min_value=0.0, value=6_200_000.0, step=500_000.0, format="%.2f")
                    tasa_in = st.number_input(f"Tasa de interés por {unidad_tiempo.lower()[:-1] if unidad_tiempo.endswith('s') else unidad_tiempo} (%)", min_value=0.0, value=2.0, step=0.25, format="%.4f")
                    plazo_in = st.number_input(f"Plazo ({unidad_tiempo})", min_value=1.0, value=12.0, step=1.0, format="%.2f")
                elif accion_simple == "Tasa de interés periódica":
                    c_in = st.number_input("Capital inicial - VP (COP)", min_value=0.0, value=5_000_000.0, step=500_000.0, format="%.2f")
                    m_in = st.number_input("Valor Futuro final - VF (COP)", min_value=0.0, value=6_200_000.0, step=500_000.0, format="%.2f")
                    plazo_in = st.number_input(f"Plazo ({unidad_tiempo})", min_value=1.0, value=12.0, step=1.0, format="%.2f")
                else:
                    c_in = st.number_input("Capital inicial - VP (COP)", min_value=0.0, value=5_000_000.0, step=500_000.0, format="%.2f")
                    m_in = st.number_input("Valor Futuro final - VF (COP)", min_value=0.0, value=6_200_000.0, step=500_000.0, format="%.2f")
                    tasa_in = st.number_input(f"Tasa de interés por {unidad_tiempo.lower()[:-1] if unidad_tiempo.endswith('s') else unidad_tiempo} (%)", min_value=0.001, value=2.0, step=0.25, format="%.4f")

                btn_simple = st.form_submit_button("Recalcular Interés Simple", type="primary")

        with col_view:
            st.markdown("#### 📊 Resultados y Visualización en Vivo")
            try:
                if accion_simple == "Valor Futuro (Monto final) e Interés":
                    interes_calc, monto_calc = calcular_monto_interes_simple(c_in, tasa_in, plazo_in)
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Capital Inicial (C)", formato_cop(c_in))
                    m2.metric("Interés Total (I)", formato_cop(interes_calc))
                    m3.metric("Monto Final (M)", formato_cop(monto_calc))

                    # Gráfico de área sombreada con spline
                    n_steps = int(max(1, min(int(plazo_in), 200)))
                    saldos = [c_in * (1 + (tasa_in / 100.0) * p) for p in range(n_steps + 1)]
                    df_s = pd.DataFrame({"Período": range(n_steps + 1), "Saldo Acumulado": saldos})

                    fig_s = go.Figure()
                    fig_s.add_trace(go.Scatter(
                        x=df_s["Período"],
                        y=df_s["Saldo Acumulado"],
                        mode="lines+markers",
                        name="Interés Simple",
                        line=dict(color="#2563eb", width=3, shape="spline"),
                        fill="tozeroy",
                        fillcolor="rgba(37, 99, 235, 0.08)",
                    ))
                    fig_s.update_layout(
                        title=f"Evolución del Valor Acumulado ({convencion})",
                        xaxis_title=f"Período ({unidad_tiempo})",
                        yaxis_title="Monto (COP)",
                        template="plotly_white",
                        margin=dict(l=20, r=20, t=40, b=20),
                        height=290,
                    )
                    st.plotly_chart(fig_s, use_container_width=True)

                    st.markdown("##### Sustento Matemático y Fórmulas")
                    st.latex(
                        rf"""
                        \begin{{aligned}}
                        M &= C \cdot (1 + i \cdot t) \\
                        M &= {c_in:,.2f} \cdot (1 + {tasa_in/100:.6g} \cdot {plazo_in}) = {monto_calc:,.2f}\text{{ COP}}
                        \end{{aligned}}
                        """
                    )
                    st.latex(rf"I = C \cdot i \cdot t = {interes_calc:,.2f}\text{{ COP}}")

                elif accion_simple == "Valor Presente (Capital inicial)":
                    vp_calc, int_calc = calcular_vp_interes_simple(m_in, tasa_in, plazo_in)
                    m1, m2 = st.columns(2)
                    m1.metric("Valor Presente Requerido (C)", formato_cop(vp_calc))
                    m2.metric("Intereses a devengar", formato_cop(int_calc))
                    st.latex(
                        rf"""
                        \begin{{aligned}}
                        C &= \frac{{M}}{{1 + i \cdot t}} \\
                        C &= \frac{{{m_in:,.2f}}}{{1 + ({tasa_in/100:.6g} \cdot {plazo_in})}} = {vp_calc:,.2f}\text{{ COP}}
                        \end{{aligned}}
                        """
                    )

                elif accion_simple == "Tasa de interés periódica":
                    tasa_res = despejar_tasa_interes_simple(c_in, m_in, plazo_in)
                    st.metric(f"Tasa Despejada por {unidad_tiempo.lower()[:-1]}", f"{tasa_res:.4f}%")
                    st.latex(
                        rf"""
                        \begin{{aligned}}
                        i &= \frac{{M - C}}{{C \cdot t}} \\
                        i &= \frac{{{m_in:,.2f} - {c_in:,.2f}}}{{{c_in:,.2f} \cdot {plazo_in}}} = {tasa_res/100:.6g} \implies {tasa_res:.4f}\%
                        \end{{aligned}}
                        """
                    )

                else:
                    t_res = despejar_tiempo_interes_simple(c_in, m_in, tasa_in)
                    st.metric(f"Plazo Despejado en {unidad_tiempo}", f"{t_res:.2f} {unidad_tiempo}")
                    st.latex(
                        rf"""
                        \begin{{aligned}}
                        t &= \frac{{M - C}}{{C \cdot i}} \\
                        t &= \frac{{{m_in:,.2f} - {c_in:,.2f}}}{{{c_in:,.2f} \cdot {tasa_in/100:.6g}}} = {t_res:.2f}\text{{ {unidad_tiempo.lower()}}}
                        \end{{aligned}}
                        """
                    )

            except Exception as e:
                st.error(f"Error en el cálculo: {e}")

    # ---------------- TAB 2: INTERÉS COMPUESTO ----------------
    with tab_compuesto:
        col_ctrl_c, col_view_c = st.columns([0.38, 0.62], gap="large")

        with col_ctrl_c:
            st.markdown("#### 🎛️ Parámetros de Interés Compuesto")
            accion_compuesto = st.selectbox(
                "Variable a calcular",
                [
                    "Valor Futuro (VF) e Interés Total",
                    "Valor Presente (VP)",
                    "Tasa periódica efectiva (i)",
                    "Número de períodos (n)",
                ],
                key="compuesto_accion",
            )

            with st.form("form_interes_compuesto"):
                if accion_compuesto == "Valor Futuro (VF) e Interés Total":
                    vp_in = st.number_input("Valor Presente - VP (COP)", min_value=0.0, value=5_000_000.0, step=500_000.0, format="%.2f", key="comp_vp_1")
                    tasa_in = st.number_input("Tasa periódica efectiva i (%)", value=2.0, step=0.25, format="%.4f", key="comp_tasa_1")
                    n_in = st.number_input("Número de períodos (n)", min_value=1.0, value=12.0, step=1.0, format="%.2f", key="comp_n_1")
                elif accion_compuesto == "Valor Presente (VP)":
                    vf_in = st.number_input("Valor Futuro objetivo - VF (COP)", min_value=0.0, value=6_341_208.97, step=500_000.0, format="%.2f", key="comp_vf_2")
                    tasa_in = st.number_input("Tasa periódica efectiva i (%)", value=2.0, step=0.25, format="%.4f", key="comp_tasa_2")
                    n_in = st.number_input("Número de períodos (n)", min_value=1.0, value=12.0, step=1.0, format="%.2f", key="comp_n_2")
                elif accion_compuesto == "Tasa periódica efectiva (i)":
                    vp_in = st.number_input("Valor Presente - VP (COP)", min_value=0.0, value=5_000_000.0, step=500_000.0, format="%.2f", key="comp_vp_3")
                    vf_in = st.number_input("Valor Futuro final - VF (COP)", min_value=0.0, value=6_341_208.97, step=500_000.0, format="%.2f", key="comp_vf_3")
                    n_in = st.number_input("Número de períodos (n)", min_value=1.0, value=12.0, step=1.0, format="%.2f", key="comp_n_3")
                else:
                    vp_in = st.number_input("Valor Presente - VP (COP)", min_value=0.0, value=5_000_000.0, step=500_000.0, format="%.2f", key="comp_vp_4")
                    vf_in = st.number_input("Valor Futuro final - VF (COP)", min_value=0.0, value=6_341_208.97, step=500_000.0, format="%.2f", key="comp_vf_4")
                    tasa_in = st.number_input("Tasa periódica efectiva i (%)", min_value=0.001, value=2.0, step=0.25, format="%.4f", key="comp_tasa_4")

                btn_compuesto = st.form_submit_button("Recalcular Interés Compuesto", type="primary")

        with col_view_c:
            st.markdown("#### 📊 Crecimiento Exponencial por Capitalización")
            try:
                if accion_compuesto == "Valor Futuro (VF) e Interés Total":
                    int_c, vf_c = calcular_monto_interes_compuesto(vp_in, tasa_in, n_in)
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Valor Presente (VP)", formato_cop(vp_in))
                    m2.metric("Interés Total (I)", formato_cop(int_c))
                    m3.metric("Valor Futuro (VF)", formato_cop(vf_c))

                    n_int = int(max(1, min(int(n_in), 200)))
                    saldos_c = calcular_saldos_compuesto(vp_in, tasa_in, n_int)
                    df_c = pd.DataFrame({"Período": range(n_int + 1), "Saldo Acumulado": saldos_c})

                    fig_c = go.Figure()
                    fig_c.add_trace(go.Scatter(
                        x=df_c["Período"],
                        y=df_c["Saldo Acumulado"],
                        mode="lines+markers",
                        name="Interés Compuesto",
                        line=dict(color="#1d4ed8", width=3, shape="spline"),
                        fill="tozeroy",
                        fillcolor="rgba(29, 78, 216, 0.08)",
                    ))
                    fig_c.update_layout(
                        title="Trayectoria Exponencial del Capital",
                        xaxis_title="Período",
                        yaxis_title="Monto (COP)",
                        template="plotly_white",
                        margin=dict(l=20, r=20, t=40, b=20),
                        height=290,
                    )
                    st.plotly_chart(fig_c, use_container_width=True)

                    st.markdown("##### Sustento Matemático y Fórmulas")
                    st.latex(
                        rf"""
                        \begin{{aligned}}
                        VF &= VP \cdot (1 + i)^n \\
                        VF &= {vp_in:,.2f} \cdot (1 + {tasa_in/100:.6g})^{{{n_in}}} = {vf_c:,.2f}\text{{ COP}}
                        \end{{aligned}}
                        """
                    )
                    st.latex(rf"I = VF - VP = {vf_c:,.2f} - {vp_in:,.2f} = {int_c:,.2f}\text{{ COP}}")

                elif accion_compuesto == "Valor Presente (VP)":
                    vp_calc, int_calc = calcular_vp_interes_compuesto(vf_in, tasa_in, n_in)
                    m1, m2 = st.columns(2)
                    m1.metric("Valor Presente Requerido (VP)", formato_cop(vp_calc))
                    m2.metric("Intereses totales del plazo", formato_cop(int_calc))
                    st.latex(
                        rf"""
                        \begin{{aligned}}
                        VP &= \frac{{VF}}{{(1 + i)^n}} \\
                        VP &= \frac{{{vf_in:,.2f}}}{{(1 + {tasa_in/100:.6g})^{{{n_in}}}}} = {vp_calc:,.2f}\text{{ COP}}
                        \end{{aligned}}
                        """
                    )

                elif accion_compuesto == "Tasa periódica efectiva (i)":
                    tasa_calc = despejar_tasa_interes_compuesto(vp_in, vf_in, n_in)
                    st.metric("Tasa Periódica Despejada (i)", f"{tasa_calc:.4f}%")
                    st.latex(
                        rf"""
                        \begin{{aligned}}
                        i &= \left(\frac{{VF}}{{VP}}\right)^{{\frac{{1}}{{n}}}} - 1 \\
                        i &= \left(\frac{{{vf_in:,.2f}}}{{{vp_in:,.2f}}}\right)^{{\frac{{1}}{{{n_in}}}}} - 1 = {tasa_calc/100:.6g} \implies {tasa_calc:.4f}\%
                        \end{{aligned}}
                        """
                    )

                else:
                    n_calc = despejar_periodos_interes_compuesto(vp_in, vf_in, tasa_in)
                    st.metric("Número de Períodos Despejado (n)", f"{n_calc:.2f} períodos")
                    st.latex(
                        rf"""
                        \begin{{aligned}}
                        n &= \frac{{\ln(VF / VP)}}{{\ln(1 + i)}} \\
                        n &= \frac{{\ln({vf_in:,.2f} / {vp_in:,.2f})}}{{\ln(1 + {tasa_in/100:.6g})}} = {n_calc:.2f}\text{{ períodos}}
                        \end{{aligned}}
                        """
                    )

            except Exception as e:
                st.error(f"Error en el cálculo: {e}")

    # ---------------- TAB 3: COMPARACIÓN SIMULTÁNEA ----------------
    with tab_comparacion:
        st.subheader("Comparación Gráfica Simultánea: Interés Simple vs. Compuesto")
        col_c_p, col_c_g = st.columns([0.35, 0.65], gap="large")

        with col_c_p:
            st.markdown("#### 🎛️ Parámetros Comunes")
            with st.form("form_comparacion_interes"):
                comp_capital = st.number_input("Capital Inicial (COP)", min_value=0.0, value=10_000_000.0, step=1_000_000.0, format="%.2f", key="comp_cap")
                comp_tasa = st.number_input("Tasa Periódica Común (%)", min_value=0.0, value=2.0, step=0.25, format="%.4f", key="comp_tasa")
                comp_n = st.number_input("Número de Períodos (n)", min_value=1, max_value=120, value=24, step=1, key="comp_per")
                btn_compare = st.form_submit_button("Comparar Regímenes", type="primary")

        saldos_s = calcular_saldos_simple(comp_capital, comp_tasa, comp_n)
        saldos_c = calcular_saldos_compuesto(comp_capital, comp_tasa, comp_n)
        diferencias = [c - s for s, c in zip(saldos_s, saldos_c)]

        m_final_simple = saldos_s[-1]
        m_final_compuesto = saldos_c[-1]
        brecha_final = m_final_compuesto - m_final_simple

        with col_c_g:
            k1, k2, k3 = st.columns(3)
            k1.metric("Valor Final Simple", formato_cop(m_final_simple))
            k2.metric("Valor Final Compuesto", formato_cop(m_final_compuesto))
            k3.metric("Brecha a Favor de Compuesto", formato_cop(brecha_final), delta=f"+{((m_final_compuesto/m_final_simple)-1)*100:.2f}%")

            df_comp = pd.DataFrame({
                "Período": list(range(comp_n + 1)),
                "Interés Simple": saldos_s,
                "Interés Compuesto": saldos_c,
                "Diferencia (Brecha)": diferencias,
            })

            fig_comp = go.Figure()
            fig_comp.add_trace(go.Scatter(
                x=df_comp["Período"], y=df_comp["Interés Simple"],
                mode="lines+markers", name="Interés Simple (Lineal)",
                line=dict(color="#f59e0b", width=2.5, dash="dash")
            ))
            fig_comp.add_trace(go.Scatter(
                x=df_comp["Período"], y=df_comp["Interés Compuesto"],
                mode="lines+markers", name="Interés Compuesto (Exponencial)",
                line=dict(color="#2563eb", width=3, shape="spline"),
                fill="tonexty",
                fillcolor="rgba(37, 99, 235, 0.08)",
            ))
            fig_comp.update_layout(
                title=f"Crecimiento Comparado con Capital {formato_cop(comp_capital)}",
                xaxis_title="Período",
                yaxis_title="Monto Acumulado (COP)",
                template="plotly_white",
                hovermode="x unified",
                margin=dict(l=20, r=20, t=40, b=20),
                height=300,
            )
            st.plotly_chart(fig_comp, use_container_width=True)

        st.markdown("##### 📈 Desglose de la Brecha de Capitalización (Intereses sobre Intereses)")
        fig_brecha = go.Figure()
        fig_brecha.add_trace(go.Bar(
            x=df_comp["Período"], y=df_comp["Diferencia (Brecha)"],
            name="Intereses sobre Intereses (Brecha)",
            marker=dict(color="#60a5fa", line=dict(color="#2563eb", width=1))
        ))
        fig_brecha.update_layout(
            title="Magnitud Monetaria de la Brecha Acumulada Período a Período",
            xaxis_title="Período",
            yaxis_title="Diferencia en COP",
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20),
            height=250,
        )
        st.plotly_chart(fig_brecha, use_container_width=True)

        tabla_presentar = df_comp.copy()
        for col in ["Interés Simple", "Interés Compuesto", "Diferencia (Brecha)"]:
            tabla_presentar[col] = tabla_presentar[col].map(formato_cop)
        st.dataframe(tabla_presentar, use_container_width=True, hide_index=True)

    # ---------------- TAB 4: SUPUESTOS Y VERIFICACIÓN ----------------
    with tab_verificacion:
        st.subheader("Supuestos Técnicos y Verificación Matemática")
        col_sup, col_calc = st.columns(2, gap="large")

        with col_sup:
            st.markdown(
                """
                #### Supuestos Técnicos del Módulo:
                1. **Convención de días**:
                   - **Comercial (360 días)**: Asume meses uniformes de 30 días. Es el estándar bancario colombiano.
                   - **Exacto (365 días)**: Utiliza los días calendario reales transcurridos.
                2. **Homogeneidad temporal**: La tasa periódica y el plazo deben expresar la misma unidad temporal.
                3. **Base de cálculo**:
                   - Simple: $I_t = C \\cdot i$ permanece constante.
                   - Compuesto: $I_t = S_{t-1} \\cdot i$, aumentando período a período.
                """
            )

        with col_calc:
            st.markdown("#### Comprobación de Cálculo Manual (Paso a Paso):")
            st.latex(r"C = 1{.}000{.}000\text{ COP}, \quad i = 10\%\text{ periódico } (0{,}10), \quad n = 3\text{ períodos}")
            st.latex(
                r"""
                \begin{aligned}
                M &= C \cdot (1 + i \cdot t) = 1{.}000{.}000 \cdot (1 + 0{,}10 \cdot 3) = 1{.}300{.}000\text{ COP} \quad \text{✅} \\
                VF &= VP \cdot (1 + i)^n = 1{.}000{.}000 \cdot (1 + 0{,}10)^3 = 1{.}331{.}000\text{ COP} \quad \text{✅} \\
                \Delta &= 1{.}331{.}000 - 1{.}300{.}000 = 31{.}000\text{ COP} \quad \text{✅ Verificado}
                \end{aligned}
                """
            )
