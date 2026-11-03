"""Cálculos y análisis de gradientes aritméticos y geométricos."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from motor.formato import formato_cop
from motor.gradientes import (
    calcular_gradiente_aritmetico,
    calcular_gradiente_geometrico,
)


# ------------------ RENDER STREAMLIT ------------------

def render():
    st.title("Gradientes Financieros (Aritméticos y Geométricos)")
    st.write(
        "Panel interactivo para evaluar series con pagos variables crecientes y decrecientes. "
        "Calcula el **Valor Presente (VP)**, **Valor Futuro (VF)** y la **Cuota Uniforme Equivalente (Aeq)**."
    )

    tab_calc, tab_verif = st.tabs(["📉 Calculadora de Gradientes", "✅ Supuestos y Verificación"])

    with tab_calc:
        col_ctrl, col_view = st.columns([0.38, 0.62], gap="large")

        with col_ctrl:
            st.markdown("#### 🎛️ Parámetros del Gradiente")
            tipo_gradiente = st.radio(
                "Tipo de Gradiente",
                ["Aritmético (Variación en pesos $)", "Geométrico (Variación porcentual %)"],
                horizontal=False,
                key="grad_tipo",
            )

            primer_pago = st.number_input("Primer pago / cuota A₁ (COP)", min_value=0.0, value=1_000_000.0, step=100_000.0, format="%.2f")
            if "Aritmético" in tipo_gradiente:
                variacion = st.number_input("Gradiente constante G (COP/período)", value=50_000.0, step=10_000.0, format="%.2f", help="Positivo para creciente, negativo para decreciente")
            else:
                variacion = st.number_input("Tasa de crecimiento g (%/período)", value=3.0, step=0.5, format="%.4f", help="Positiva para creciente, negativa para decreciente")

            tasa_desc = st.number_input("Tasa de descuento / interés i (%)", min_value=0.0, value=1.5, step=0.25, format="%.4f")
            n_periodos = st.number_input("Número de períodos (n)", min_value=1, max_value=360, value=12, step=1)

        with col_view:
            st.markdown("#### 📊 Resultados de la Serie Gradiente")
            try:
                is_aritmetico = "Aritmético" in tipo_gradiente
                if is_aritmetico:
                    resultado = calcular_gradiente_aritmetico(primer_pago, variacion, tasa_desc, int(n_periodos))
                    formula_pago = r"P_t = A_1 + (t - 1) \cdot G"
                    formula_vp = r"VP = A_1 \cdot \left[\frac{1-(1+i)^{-n}}{i}\right] + \frac{G}{i}\cdot\left[\frac{1-(1+i)^{-n}}{i} - \frac{n}{(1+i)^n}\right]"
                else:
                    resultado = calcular_gradiente_geometrico(primer_pago, variacion, tasa_desc, int(n_periodos))
                    formula_pago = r"P_t = A_1 \cdot (1 + g)^{t - 1}"
                    formula_vp = r"VP = A_1 \cdot \left[\frac{1 - \left(\frac{1+g}{1+i}\right)^n}{i - g}\right] \quad (i \neq g)"

                m1, m2, m3 = st.columns(3)
                m1.metric("Valor Presente (VP)", formato_cop(resultado["valor_presente"]))
                m2.metric("Valor Futuro (VF)", formato_cop(resultado["valor_futuro"]))
                m3.metric("Cuota Equiv. (Aeq)", formato_cop(resultado["cuota_equivalente"]))

                tasa_dec = tasa_desc / 100.0
                pagos = resultado["pagos"]
                vp_pagos = [p / ((1.0 + tasa_dec) ** (t + 1)) for t, p in enumerate(pagos)]

                saldo_acum = []
                s = 0.0
                for p in pagos:
                    s = s * (1.0 + tasa_dec) + p
                    saldo_acum.append(s)

                df_grad = pd.DataFrame({
                    "Período": list(range(1, int(n_periodos) + 1)),
                    "Pago Cuota Pt (COP)": pagos,
                    "Factor Descuento": [1.0 / ((1.0 + tasa_dec) ** t) for t in range(1, int(n_periodos) + 1)],
                    "Valor Presente del Pago": vp_pagos,
                    "Saldo Acumulado Futuro": saldo_acum,
                })

                nombre_grad = "aritmético" if is_aritmetico else "geométrico"
                g_flujo, g_saldo = st.columns(2)
                fig_flujo = go.Figure(go.Bar(x=df_grad["Período"], y=df_grad["Pago Cuota Pt (COP)"], name="Pago", marker_color="#2a78d6"))
                fig_flujo.update_layout(title=f"Flujo de pagos del gradiente {nombre_grad}", xaxis_title="Período", yaxis_title="Pago (COP)", template="plotly_white", margin=dict(l=20, r=20, t=50, b=20), height=290)
                g_flujo.plotly_chart(fig_flujo, width="stretch")
                fig_saldo = go.Figure(go.Scatter(x=df_grad["Período"], y=df_grad["Saldo Acumulado Futuro"], mode="lines+markers", name="Acumulado", line=dict(color="#2a78d6", width=2)))
                fig_saldo.update_layout(title="Valor acumulado de los pagos", xaxis_title="Período", yaxis_title="Valor acumulado (COP)", template="plotly_white", margin=dict(l=20, r=20, t=50, b=20), height=290)
                g_saldo.plotly_chart(fig_saldo, width="stretch")

                st.markdown("##### Fórmulas Matemáticas y Sustitución")
                st.latex(formula_pago)
                st.latex(formula_vp)
                st.latex(
                    rf"""
                    \begin{{aligned}}
                    VP &= {resultado['valor_presente']:,.2f}\text{{ COP}} \\
                    VF &= {resultado['valor_presente']:,.2f} \cdot (1 + {tasa_dec:.6g})^{{{int(n_periodos)}}} = {resultado['valor_futuro']:,.2f}\text{{ COP}} \\
                    A_{{eq}} &= {resultado['valor_presente']:,.2f} \cdot \left[\frac{{{tasa_dec:.6g}}}{{1 - (1 + {tasa_dec:.6g})^{{-{int(n_periodos)}}}}}\right] = {resultado['cuota_equivalente']:,.2f}\text{{ COP}}
                    \end{{aligned}}
                    """
                )

                st.markdown("##### 📋 Detalle de Pagos Período a Período")
                df_most = df_grad.copy()
                for c in ["Pago Cuota Pt (COP)", "Valor Presente del Pago", "Saldo Acumulado Futuro"]:
                    df_most[c] = df_most[c].map(formato_cop)
                df_most["Factor Descuento"] = df_most["Factor Descuento"].map(lambda x: f"{x:.6f}")
                st.dataframe(df_most, width="stretch", hide_index=True)

            except Exception as e:
                st.error(f"Error en el cálculo: {e}")

    with tab_verif:
        st.subheader("Supuestos Técnicos y Verificación de Gradientes")
        col_s, col_v = st.columns(2, gap="large")
        with col_s:
            st.markdown(
                """
                #### Supuestos Técnicos:
                1. **Gradiente Aritmético**: Cada cuota varía en una suma monetaria constante $G$ respecto a la anterior ($P_t = A_1 + (t-1)G$).
                2. **Gradiente Geométrico**: Cada cuota varía en un porcentaje constante $g$ respecto a la anterior ($P_t = A_1(1+g)^{t-1}$).
                3. **Cuota Uniforme Equivalente ($A_{eq}$)**: Anualidad fija que, a la misma tasa $i$ y plazo $n$, produce exactamente el mismo Valor Presente ($VP$).
                """
            )

        with col_v:
            st.markdown("#### Comprobación de Cálculo Manual (Paso a Paso)")
            st.latex(r"A_1 = 100{.}000\text{ COP}, \quad G = 20{.}000\text{ COP}, \quad i = 10\%\text{ periódico } (0{,}10), \quad n = 3\text{ períodos}")
            st.latex(
                r"""
                \begin{aligned}
                P_1 &= 100{.}000, \quad P_2 = 120{.}000, \quad P_3 = 140{.}000\text{ COP} \\
                VP &= \frac{100{.}000}{1{,}10} + \frac{120{.}000}{(1{,}10)^2} + \frac{140{.}000}{(1{,}10)^3} = 295{.}266{,}72\text{ COP} \quad \text{✅} \\
                VF &= 295{.}266{,}72 \cdot (1{,}10)^3 = 393{.}000{,}00\text{ COP} \quad \text{✅} \\
                A_{eq} &= 295{.}266{,}72 \cdot \frac{0{,}10}{1 - (1{,}10)^{-3}} = 118{.}731{,}12\text{ COP} \quad \text{✅ Verificado}
                \end{aligned}
                """
            )
