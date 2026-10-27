"""Cálculos y análisis de gradientes aritméticos y geométricos."""

import math
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def formato_cop(valor: float) -> str:
    """Formatea un valor en pesos colombianos para presentación."""
    if not math.isfinite(valor):
        return "N/A"
    return f"${valor:,.2f} COP".replace(",", "X").replace(".", ",").replace("X", ".")


# ------------------ FUNCIONES MATEMÁTICAS ------------------

def calcular_gradiente_aritmetico(
    primer_pago: float,
    incremento_g: float,
    tasa_pct: float,
    periodos: int,
) -> dict[str, any]:
    """Calcula VP, VF, Cuota Uniforme Equivalente y flujos para gradiente aritmético."""
    if primer_pago < 0:
        raise ValueError("El primer pago no puede ser negativo.")
    if periodos < 1:
        raise ValueError("El número de períodos debe ser al menos 1.")
    tasa = tasa_pct / 100.0

    pagos = [primer_pago + (t * incremento_g) for t in range(periodos)]
    if any(p < 0 for p in pagos):
        raise ValueError("El incremento negativo (gradiente decreciente) produce pagos negativos en el plazo.")

    if tasa == 0:
        vp = sum(pagos)
        vf = vp
        a_eq = vp / periodos
    else:
        factor_anualidad = (1.0 - (1.0 + tasa) ** (-periodos)) / tasa
        factor_gradiente = (factor_anualidad - (periodos / ((1.0 + tasa) ** periodos))) / tasa
        vp = (primer_pago * factor_anualidad) + (incremento_g * factor_gradiente)
        vf = vp * ((1.0 + tasa) ** periodos)
        a_eq = vp * (tasa / (1.0 - (1.0 + tasa) ** (-periodos)))

    return {
        "pagos": pagos,
        "valor_presente": vp,
        "valor_futuro": vf,
        "cuota_equivalente": a_eq,
    }


def calcular_gradiente_geometrico(
    primer_pago: float,
    crecimiento_pct: float,
    tasa_pct: float,
    periodos: int,
) -> dict[str, any]:
    """Calcula VP, VF, Cuota Uniforme Equivalente y flujos para gradiente geométrico."""
    if primer_pago < 0:
        raise ValueError("El primer pago no puede ser negativo.")
    if periodos < 1:
        raise ValueError("El número de períodos debe ser al menos 1.")

    g = crecimiento_pct / 100.0
    tasa = tasa_pct / 100.0

    if g < -1.0:
        raise ValueError("La tasa de decrecimiento no puede ser menor a -100%.")

    pagos = [primer_pago * ((1.0 + g) ** t) for t in range(periodos)]

    if abs(tasa - g) < 1e-9:
        vp = (periodos * primer_pago) / (1.0 + tasa)
        vf = periodos * primer_pago * ((1.0 + tasa) ** (periodos - 1))
    else:
        vp = primer_pago * ((1.0 - ((1.0 + g) / (1.0 + tasa)) ** periodos) / (tasa - g))
        vf = vp * ((1.0 + tasa) ** periodos)

    if tasa == 0:
        a_eq = vp / periodos
    else:
        a_eq = vp * (tasa / (1.0 - (1.0 + tasa) ** (-periodos)))

    return {
        "pagos": pagos,
        "valor_presente": vp,
        "valor_futuro": vf,
        "cuota_equivalente": a_eq,
    }


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

            with st.form("form_gradientes"):
                primer_pago = st.number_input("Primer pago / cuota A₁ (COP)", min_value=0.0, value=1_000_000.0, step=100_000.0, format="%.2f")
                if "Aritmético" in tipo_gradiente:
                    variacion = st.number_input("Gradiente constante G (COP/período)", value=50_000.0, step=10_000.0, format="%.2f", help="Positivo para creciente, negativo para decreciente")
                else:
                    variacion = st.number_input("Tasa de crecimiento g (%/período)", value=3.0, step=0.5, format="%.4f", help="Positiva para creciente, negativa para decreciente")

                tasa_desc = st.number_input("Tasa de descuento / interés i (%)", min_value=0.0, value=1.5, step=0.25, format="%.4f")
                n_periodos = st.number_input("Número de períodos (n)", min_value=1, max_value=360, value=12, step=1)
                btn_grad = st.form_submit_button("Recalcular Gradiente", type="primary")

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

                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(
                    go.Bar(
                        x=df_grad["Período"],
                        y=df_grad["Pago Cuota Pt (COP)"],
                        name="Pago del Período (Pt)",
                        marker=dict(color="#93c5fd", line=dict(color="#2563eb", width=1)),
                    ),
                    secondary_y=False,
                )
                fig.add_trace(
                    go.Scatter(
                        x=df_grad["Período"],
                        y=df_grad["Saldo Acumulado Futuro"],
                        name="Valor Acumulado",
                        mode="lines+markers",
                        line=dict(color="#1e3a8a", width=3, shape="spline"),
                        fill="tozeroy",
                        fillcolor="rgba(30, 58, 138, 0.08)",
                    ),
                    secondary_y=True,
                )
                fig.update_layout(
                    title=f"Flujo y Acumulación en Gradiente {('Aritmético' if is_aritmetico else 'Geométrico')}",
                    xaxis_title="Período",
                    template="plotly_white",
                    margin=dict(l=20, r=20, t=50, b=20),
                    legend=dict(orientation="h", y=1.1, x=0.2),
                    height=290,
                )
                fig.update_yaxes(title_text="Pago Cuota (COP)", secondary_y=False)
                fig.update_yaxes(title_text="Saldo Acumulado (COP)", secondary_y=True)
                st.plotly_chart(fig, use_container_width=True)

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

            except Exception as e:
                st.error(f"Error en el cálculo: {e}")

        st.markdown("##### 📋 Detalle de Pagos Período a Período")
        df_most = df_grad.copy()
        for c in ["Pago Cuota Pt (COP)", "Valor Presente del Pago", "Saldo Acumulado Futuro"]:
            df_most[c] = df_most[c].map(formato_cop)
        df_most["Factor Descuento"] = df_most["Factor Descuento"].map(lambda x: f"{x:.6f}")
        st.dataframe(df_most, use_container_width=True, hide_index=True)

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
                A_{eq} &= 295{.}266{,}72 \cdot \frac{0{,}10}{1 - (1{,}10)^{-3}} = 118{.}731{,}18\text{ COP} \quad \text{✅ Verificado}
                \end{aligned}
                """
            )
