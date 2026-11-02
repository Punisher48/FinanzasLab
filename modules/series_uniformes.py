"""Cálculos y análisis de series uniformes (anualidades) vencidas y anticipadas."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from motor.formato import formato_cop
from motor.series import *  # noqa: F401,F403


# ------------------ RENDER STREAMLIT ------------------

def render():
    st.title("Series Uniformes (Anualidades)")
    st.write(
        "Herramienta integral para cálculo de series uniformes **vencidas** y **anticipadas**. "
        "Permite hallar Valor Presente, Valor Futuro y Cuota Periódica, con visualización combinada del flujo de pagos y saldo acumulado."
    )

    tab_calc, tab_verif = st.tabs(["🔁 Calculadora de Anualidades", "✅ Supuestos y Verificación"])

    with tab_calc:
        col_ctrl, col_view = st.columns([0.38, 0.62], gap="large")

        with col_ctrl:
            st.markdown("#### 🎛️ Parámetros de la Anualidad")
            modalidad = st.radio("Modalidad de la serie", ["Vencida", "Anticipada"], horizontal=True, key="serie_modalidad")
            operacion = st.selectbox(
                "Objetivo del cálculo",
                [
                    "Valor Futuro de la serie (Ahorro)",
                    "Valor Presente de la serie (Préstamo / Inversión)",
                    "Cuota requerida para meta de Valor Futuro",
                    "Cuota requerida para amortizar Préstamo (Valor Presente)",
                ],
                key="serie_operacion",
            )

            with st.form("form_series"):
                if operacion in ("Valor Futuro de la serie (Ahorro)", "Valor Presente de la serie (Préstamo / Inversión)"):
                    importe = st.number_input("Cuota periódica constante A (COP)", min_value=0.0, value=500_000.0, step=50_000.0, format="%.2f")
                elif operacion == "Cuota requerida para meta de Valor Futuro":
                    importe = st.number_input("Monto objetivo futuro VF (COP)", min_value=0.0, value=20_000_000.0, step=1_000_000.0, format="%.2f")
                else:
                    importe = st.number_input("Monto del préstamo VP (COP)", min_value=0.0, value=20_000_000.0, step=1_000_000.0, format="%.2f")

                tasa_pct = st.number_input("Tasa periódica efectiva i (%)", min_value=0.0, value=1.5, step=0.1, format="%.4f")
                n_periodos = st.number_input("Número de pagos / períodos (n)", min_value=1, max_value=360, value=24, step=1)
                btn_calcular = st.form_submit_button("Recalcular Serie Uniforme", type="primary")

        with col_view:
            st.markdown("#### 📊 Proyección del Flujo y Acumulación")
            try:
                if operacion == "Valor Futuro de la serie (Ahorro)":
                    cuota_val = importe
                    resultado = valor_futuro_serie(cuota_val, tasa_pct, n_periodos, modalidad)
                    etiqueta = "Valor Futuro Acumulado (VF)"
                    formula = r"VF_v = A \cdot \left[\frac{(1+i)^n - 1}{i}\right]" if modalidad == "Vencida" else r"VF_a = A \cdot \left[\frac{(1+i)^n - 1}{i}\right] \cdot (1+i)"
                    df_flujo = generar_flujo_serie("Ahorro", cuota_val, tasa_pct, n_periodos, modalidad)

                elif operacion == "Valor Presente de la serie (Préstamo / Inversión)":
                    cuota_val = importe
                    resultado = valor_presente_serie(cuota_val, tasa_pct, n_periodos, modalidad)
                    etiqueta = "Valor Presente Equivalente (VP)"
                    formula = r"VP_v = A \cdot \left[\frac{1-(1+i)^{-n}}{i}\right]" if modalidad == "Vencida" else r"VP_a = A \cdot \left[\frac{1-(1+i)^{-n}}{i}\right] \cdot (1+i)"
                    df_flujo = generar_flujo_serie("Préstamo", cuota_val, tasa_pct, n_periodos, modalidad, monto_base=resultado)

                elif operacion == "Cuota requerida para meta de Valor Futuro":
                    resultado = cuota_para_valor_futuro(importe, tasa_pct, n_periodos, modalidad)
                    cuota_val = resultado
                    etiqueta = "Cuota Periódica a Depositar (A)"
                    formula = r"A_v = VF \cdot \left[\frac{i}{(1+i)^n - 1}\right]" if modalidad == "Vencida" else r"A_a = \frac{VF}{(1+i) \cdot \left[\frac{(1+i)^n - 1}{i}\right]}"
                    df_flujo = generar_flujo_serie("Ahorro", cuota_val, tasa_pct, n_periodos, modalidad)

                else:
                    resultado = cuota_para_prestamo(importe, tasa_pct, n_periodos, modalidad)
                    cuota_val = resultado
                    etiqueta = "Cuota Periódica del Préstamo (A)"
                    formula = r"A_v = VP \cdot \left[\frac{i}{1-(1+i)^{-n}}\right]" if modalidad == "Vencida" else r"A_a = \frac{VP}{(1+i) \cdot \left[\frac{1-(1+i)^{-n}}{i}\right]}"
                    df_flujo = generar_flujo_serie("Préstamo", cuota_val, tasa_pct, n_periodos, modalidad, monto_base=importe)

                m1, m2, m3 = st.columns(3)
                m1.metric("Modalidad", modalidad)
                m2.metric(etiqueta, formato_cop(resultado))
                m3.metric("Total Aportado en Cuotas", formato_cop(cuota_val * n_periodos))

                # Gráfico combinado
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(
                    go.Bar(
                        x=df_flujo["Período"],
                        y=df_flujo["Flujo Pago (COP)"].abs(),
                        name="Cuota Periódica",
                        marker=dict(color="#93c5fd", line=dict(color="#2563eb", width=1)),
                        opacity=0.85,
                    ),
                    secondary_y=False,
                )
                fig.add_trace(
                    go.Scatter(
                        x=df_flujo["Período"],
                        y=df_flujo["Saldo Acumulado (COP)"],
                        mode="lines+markers",
                        name="Saldo Acumulado",
                        line=dict(color="#1e40af", width=3, shape="spline"),
                        fill="tozeroy",
                        fillcolor="rgba(30, 64, 175, 0.08)",
                    ),
                    secondary_y=True,
                )
                fig.update_layout(
                    title=f"Flujo y Saldo Acumulado ({modalidad})",
                    xaxis_title="Período",
                    template="plotly_white",
                    legend=dict(orientation="h", y=1.1, x=0.2),
                    margin=dict(l=20, r=20, t=50, b=20),
                    height=290,
                )
                fig.update_yaxes(title_text="Cuota (COP)", secondary_y=False)
                fig.update_yaxes(title_text="Saldo (COP)", secondary_y=True)
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("##### Sustento Matemático y Fórmulas")
                st.latex(formula)
                t_dec = tasa_pct / 100.0
                if operacion == "Valor Futuro de la serie (Ahorro)":
                    st.latex(rf"VF = {cuota_val:,.2f} \cdot \left[\frac{{(1 + {t_dec:.6g})^{{{n_periodos}}} - 1}}{{{t_dec:.6g}}}\right] = {resultado:,.2f}\text{{ COP}}")
                elif operacion == "Valor Presente de la serie (Préstamo / Inversión)":
                    st.latex(rf"VP = {cuota_val:,.2f} \cdot \left[\frac{{1 - (1 + {t_dec:.6g})^{{-{n_periodos}}}}}{{{t_dec:.6g}}}\right] = {resultado:,.2f}\text{{ COP}}")
                elif operacion == "Cuota requerida para meta de Valor Futuro":
                    st.latex(rf"A = {importe:,.2f} \cdot \left[\frac{{{t_dec:.6g}}}{{(1 + {t_dec:.6g})^{{{n_periodos}}} - 1}}\right] = {resultado:,.2f}\text{{ COP}}")
                else:
                    st.latex(rf"A = {importe:,.2f} \cdot \left[\frac{{{t_dec:.6g}}}{{1 - (1 + {t_dec:.6g})^{{-{n_periodos}}}}}\right] = {resultado:,.2f}\text{{ COP}}")

            except Exception as e:
                st.error(f"Error en el cálculo: {e}")

        st.markdown("##### 📋 Flujo Período a Período")
        df_mostrar = df_flujo.copy()
        for col in ["Flujo Pago (COP)", "Interés Ganado (COP)", "Saldo Acumulado (COP)"]:
            df_mostrar[col] = df_mostrar[col].map(formato_cop)
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

    with tab_verif:
        st.subheader("Supuestos Técnicos y Verificación de Series Uniformes")
        col_s, col_v = st.columns(2, gap="large")
        with col_s:
            st.markdown(
                """
                #### Supuestos Técnicos:
                1. **Pagos Iguales y Periódicos**: Todas las cuotas $A$ son constantes y ocurren a intervalos de tiempo idénticos.
                2. **Tasa de Interés Homogénea**: La tasa periódica $i$ permanece constante a lo largo de los $n$ períodos.
                3. **Relación Vencida vs Anticipada**: Cada pago de una serie anticipada se realiza al inicio del período, capitalizando un período adicional de intereses frente a la modalidad vencida.
                """
            )
            st.latex(r"VP_{\text{anticipada}} = VP_{\text{vencida}} \cdot (1 + i) \quad \text{y} \quad VF_{\text{anticipada}} = VF_{\text{vencida}} \cdot (1 + i)")

        with col_v:
            st.markdown("#### Comprobación de Cálculo Manual (Paso a Paso)")
            st.latex(r"A = 100{.}000\text{ COP}, \quad i = 10\%\text{ periódico } (0{,}10), \quad n = 3\text{ períodos}")
            st.latex(
                r"""
                \begin{aligned}
                VF_v &= 100{.}000 \cdot \frac{(1{,}10)^3 - 1}{0{,}10} = 331{.}000\text{ COP} \quad \text{✅} \\
                VF_a &= 331{.}000 \cdot (1 + 0{,}10) = 364{.}100\text{ COP} \quad \text{✅} \\
                VP_v &= 100{.}000 \cdot \frac{1 - (1{,}10)^{-3}}{0{,}10} = 248{.}685{,}20\text{ COP} \quad \text{✅} \\
                VP_a &= 248{.}685{,}20 \cdot (1 + 0{,}10) = 273{.}553{,}72\text{ COP} \quad \text{✅ Verificado}
                \end{aligned}
                """
            )
