"""Conversiones de tasas financieras, equivalencias, tasas combinadas y rentabilidad con retención."""

import streamlit as st

from motor.tasas import *  # noqa: F401,F403


# ------------------ RENDER STREAMLIT ------------------

def render():
    st.title("Rentabilidad y Equivalencia de Tasas")
    st.write(
        "Panel integral para conversión entre familias de tasas financieras, "
        "tasas compuestas (Fisher), impacto tributario de retención en la fuente y matriz dinámica de equivalencias."
    )

    tab_conv, tab_tabla, tab_combinadas, tab_retencion, tab_verif = st.tabs([
        "🔄 Conversión de Tasas",
        "📊 Tabla de Equivalencias",
        "➕ Tasas Combinadas (Fisher)",
        "🏛️ Rentabilidad y Retención",
        "✅ Supuestos y Verificación",
    ])

    with tab_conv:
        col_ctrl, col_view = st.columns([0.4, 0.6], gap="large")

        with col_ctrl:
            st.markdown("#### 🎛️ Operación de Conversión")
            tipo_conversion = st.selectbox(
                "Tipo de conversión",
                [
                    "Periódica Vencida ↔ Periódica Anticipada",
                    "Efectiva Periódica → Efectiva Anual (EA)",
                    "Efectiva Anual (EA) → Efectiva Periódica",
                    "Nominal Anual (Vencida / Anticipada) → Efectiva Anual (EA)",
                    "Efectiva Anual (EA) → Nominal Anual (Vencida / Anticipada)",
                ],
                key="tasas_tipo_conv",
            )

            with st.form("form_conversion_tasas"):
                if tipo_conversion == "Periódica Vencida ↔ Periódica Anticipada":
                    direccion = st.radio("Dirección", ["Vencida a Anticipada", "Anticipada a Vencida"], horizontal=True)
                    tasa_in = st.number_input("Tasa periódica de entrada (%)", value=2.0, step=0.1, format="%.6f")
                    m_in = 12
                elif tipo_conversion in ("Efectiva Periódica → Efectiva Anual (EA)", "Efectiva Anual (EA) → Efectiva Periódica"):
                    tasa_in = st.number_input("Tasa de entrada (%)", value=12.0, step=0.5, format="%.6f")
                    m_in = st.number_input("Períodos por año (m) [Mensual=12, Trimestral=4]", min_value=1, max_value=365, value=12, step=1)
                    direccion = None
                elif tipo_conversion == "Nominal Anual (Vencida / Anticipada) → Efectiva Anual (EA)":
                    tasa_in = st.number_input("Tasa Nominal Anual (%)", value=24.0, step=0.5, format="%.6f")
                    m_in = st.number_input("Períodos por año (m)", min_value=1, max_value=365, value=12, step=1)
                    direccion = st.selectbox("Modalidad", ["Vencida", "Anticipada"])
                else:
                    tasa_in = st.number_input("Tasa Efectiva Anual (%)", value=26.8242, step=0.5, format="%.6f")
                    m_in = st.number_input("Períodos por año (m)", min_value=1, max_value=365, value=12, step=1)
                    direccion = st.selectbox("Modalidad deseada", ["Vencida", "Anticipada"])

                btn_conv = st.form_submit_button("Realizar Conversión", type="primary")

        with col_view:
            st.markdown("#### 📊 Tasa Equivalente Resultante")
            try:
                if tipo_conversion == "Periódica Vencida ↔ Periódica Anticipada":
                    if direccion == "Vencida a Anticipada":
                        res = vencida_a_anticipada(tasa_in)
                        st.metric("Tasa Periódica Anticipada (ia)", f"{res:.6f}%")
                        st.markdown("##### Ecuación de Equivalencia")
                        st.latex(rf"i_a = \frac{{i_v}}{{1 + i_v}} = \frac{{{tasa_in/100:.6g}}}{{1 + {tasa_in/100:.6g}}} = {res/100:.6g} \implies {res:.4f}\%")
                    else:
                        res = anticipada_a_vencida(tasa_in)
                        st.metric("Tasa Periódica Vencida (iv)", f"{res:.6f}%")
                        st.markdown("##### Ecuación de Equivalencia")
                        st.latex(rf"i_v = \frac{{i_a}}{{1 - i_a}} = \frac{{{tasa_in/100:.6g}}}{{1 - {tasa_in/100:.6g}}} = {res/100:.6g} \implies {res:.4f}\%")

                elif tipo_conversion == "Efectiva Periódica → Efectiva Anual (EA)":
                    res = efectiva_anual_desde_periodica(tasa_in, int(m_in))
                    st.metric("Tasa Efectiva Anual (EA)", f"{res:.6f}%")
                    st.markdown("##### Ecuación de Equivalencia")
                    st.latex(rf"EA = (1 + i_p)^m - 1 = (1 + {tasa_in/100:.6g})^{{{int(m_in)}}} - 1 = {res/100:.6g} \implies {res:.4f}\%")

                elif tipo_conversion == "Efectiva Anual (EA) → Efectiva Periódica":
                    res = periodica_desde_efectiva_anual(tasa_in, int(m_in))
                    st.metric("Tasa Periódica Efectiva (ip)", f"{res:.6f}%")
                    st.markdown("##### Ecuación de Equivalencia")
                    st.latex(rf"i_p = (1 + EA)^{{\frac{{1}}{{m}}}} - 1 = (1 + {tasa_in/100:.6g})^{{\frac{{1}}{{{int(m_in)}}}}} - 1 = {res/100:.6g} \implies {res:.4f}\%")

                elif tipo_conversion == "Nominal Anual (Vencida / Anticipada) → Efectiva Anual (EA)":
                    is_ant = (direccion == "Anticipada")
                    res = efectiva_anual_desde_nominal(tasa_in, int(m_in), is_ant)
                    st.metric("Tasa Efectiva Anual (EA)", f"{res:.6f}%")
                    st.markdown("##### Ecuación de Equivalencia")
                    if is_ant:
                        st.latex(r"i_a = \frac{j}{m}, \quad i_v = \frac{i_a}{1 - i_a}, \quad EA = (1 + i_v)^m - 1")
                    else:
                        st.latex(rf"EA = \left(1 + \frac{{{tasa_in/100:.6g}}}{{{int(m_in)}}}\right)^{{{int(m_in)}}} - 1 = {res:.4f}\%")

                else:
                    is_ant = (direccion == "Anticipada")
                    res = nominal_desde_efectiva_anual(tasa_in, int(m_in), is_ant)
                    st.metric(f"Tasa Nominal Anual ({direccion})", f"{res:.6f}%")
                    st.markdown("##### Ecuación de Equivalencia")
                    st.latex(r"i_v = (1 + EA)^{\frac{1}{m}} - 1, \quad j = m \times i")

            except Exception as e:
                st.error(f"Error en la conversión: {e}")

    with tab_tabla:
        st.subheader("Matriz Dinámica de Equivalencias de Tasas")
        col_t_in, col_t_mat = st.columns([0.35, 0.65], gap="large")

        with col_t_in:
            st.markdown("#### 🎛️ Tasa Base de Referencia")
            tasa_ref = st.number_input("Valor de la tasa (%)", value=12.0, step=0.5, format="%.4f", key="tabla_tasa_ref")
            tipo_ref = st.selectbox(
                "Tipo de tasa",
                [
                    "Efectiva Anual (EA)",
                    "Efectiva Periódica Vencida",
                    "Efectiva Periódica Anticipada",
                    "Nominal Anual Vencida",
                    "Nominal Anual Anticipada",
                ],
                key="tabla_tipo_ref",
            )
            m_ref = st.number_input("Períodos/año (m) si es periódica o nominal", min_value=1, max_value=365, value=12, step=1, key="tabla_m_ref")

        with col_t_mat:
            st.markdown("#### 📑 Matriz Completa de Tasas Equivalentes")
            try:
                df_equivalencias = generar_tabla_equivalencias(tasa_ref, tipo_ref, int(m_ref))
                st.dataframe(df_equivalencias, use_container_width=True, hide_index=True)
                st.caption("Todas las tasas en cada fila generan idéntico rendimiento compuesto al cabo de 360 días.")
            except Exception as e:
                st.error(f"Error: {e}")

    with tab_combinadas:
        st.subheader("Tasas Combinadas y Ecuación de Fisher")
        col_f_in, col_f_res = st.columns([0.4, 0.6], gap="large")

        with col_f_in:
            modo_combinada = st.radio(
                "Modelo a evaluar",
                ["Tasa Combinada (Inflación + Tasa Real / DTF + Spread)", "Despejar Tasa Real Deflactada"],
                key="combo_modo",
            )
            with st.form("form_tasas_combinadas"):
                if "Combinada" in modo_combinada:
                    tasa_base = st.number_input("Tasa base / Inflación (%)", value=5.5, step=0.25, format="%.4f")
                    spread = st.number_input("Puntos adicionales / Tasa real (%)", value=4.0, step=0.25, format="%.4f")
                else:
                    tasa_aparente = st.number_input("Tasa aparente o corriente (%)", value=12.0, step=0.25, format="%.4f")
                    inflacion = st.number_input("Tasa de inflación del período (%)", value=6.0, step=0.25, format="%.4f")

                btn_comb = st.form_submit_button("Calcular Tasa", type="primary")

        with col_f_res:
            st.markdown("#### 📊 Resultado")
            try:
                if "Combinada" in modo_combinada:
                    total_comb = tasa_combinada(tasa_base, spread)
                    st.metric("Tasa Combinada Resultante (EA)", f"{total_comb:.4f}%")
                    st.latex(r"(1 + i_{\text{total}}) = (1 + i_{\text{base}}) \times (1 + \text{spread})")
                    st.latex(rf"i_{{\text{{total}}}} = {tasa_base:.4f}\% + {spread:.4f}\% + ({tasa_base/100:.6g} \cdot {spread/100:.6g}) = {total_comb:.4f}\%")
                else:
                    real = tasa_real_fisher(tasa_aparente, inflacion)
                    st.metric("Tasa Real Neta de Inflación", f"{real:.4f}%")
                    st.latex(r"1 + i_{\text{real}} = \frac{1 + i_{\text{aparente}}}{1 + \text{inflación}}")
                    st.latex(rf"i_{{\text{{real}}}} = \frac{{1 + {tasa_aparente/100:.6g}}}{{1 + {inflacion/100:.6g}}} - 1 = {real:.4f}\%")
            except Exception as e:
                st.error(str(e))

    with tab_retencion:
        st.subheader("Rentabilidad Neta con Retención en la Fuente")
        col_r_in, col_r_res = st.columns([0.4, 0.6], gap="large")

        with col_r_in:
            with st.form("form_retencion"):
                inv_inicial = st.number_input("Monto invertido (COP)", min_value=1.0, value=10_000_000.0, step=1_000_000.0, format="%.2f")
                dias_plazo = st.number_input("Plazo de la inversión (días)", min_value=1.0, value=180.0, step=30.0)
                v_final_bruto = st.number_input("Valor final bruto esperado (COP)", min_value=1.0, value=10_600_000.0, step=100_000.0, format="%.2f")
                tasa_retefuente = st.number_input("Retención en la fuente (%)", min_value=0.0, max_value=100.0, value=4.0, step=1.0, format="%.2f")
                btn_ret = st.form_submit_button("Calcular Impacto Tributario", type="primary")

        res_ret = rentabilidad_con_retencion(inv_inicial, v_final_bruto, tasa_retefuente, dias_plazo)

        with col_r_res:
            col_k1, col_k2, col_k3 = st.columns(3)
            col_k1.metric("Intereses Brutos", f"${res_ret['rendimiento_bruto']:,.2f} COP")
            col_k2.metric(f"Retención ({tasa_retefuente}%)", f"-${res_ret['retencion_valor']:,.2f} COP", delta="-Deducción fiscal")
            col_k3.metric("Intereses Netos", f"${res_ret['rendimiento_neto']:,.2f} COP")

            col_t1, col_t2 = st.columns(2)
            col_t1.metric("TEA Bruta", f"{res_ret['ea_bruta']:.4f}%")
            col_t2.metric("TEA Neta Real", f"{res_ret['ea_neta']:.4f}%", delta=f"{res_ret['ea_neta'] - res_ret['ea_bruta']:.4f}%")

            st.markdown("##### Procedimiento Tributario")
            st.latex(r"\text{Retención} = \text{Rendimiento Bruto} \times \text{Tasa Retefuente}")
            st.latex(r"EA_{\text{neta}} = \left(1 + \frac{\text{Rendimiento Neto}}{V_0}\right)^{\frac{360}{\text{Días}}} - 1")

    with tab_verif:
        st.subheader("Supuestos Técnicos y Verificación de Tasas")
        col_s, col_v = st.columns(2, gap="large")
        with col_s:
            st.markdown(
                """
                #### Supuestos Técnicos:
                1. **Tasa Efectiva**: Considera la reinversión de intereses en cada período de liquidación.
                2. **Tasa Nominal**: Es una tasa de referencia anual pactada que se divide directamente entre $m$ ($i_p = j / m$).
                3. **Retención en la Fuente**: Aplica únicamente sobre los rendimientos generados ($V_f - V_0$), no sobre el capital base (Art. 395 E.T. de Colombia).
                """
            )

        with col_v:
            st.markdown("#### Comprobación de Equivalencia Manual (Paso a Paso)")
            st.markdown("**Parámetro:** Tasa Nominal del 24% MV ($m=12$).")
            st.latex(
                r"""
                \begin{aligned}
                i_m &= \frac{24\%}{12} = 2{,}0000\%\text{ mensual vencido} \quad \text{✅} \\
                EA &= (1 + 0{,}02)^{12} - 1 = 26{,}8242\%\text{ EA} \quad \text{✅} \\
                i_a &= \frac{0{,}02}{1 + 0{,}02} = 1{,}9608\%\text{ mensual anticipado} \quad \text{✅ Verificado}
                \end{aligned}
                """
            )
