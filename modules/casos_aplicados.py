"""Casos Financieros Aplicados con datos del mercado financiero colombiano."""

import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.amortizacion import amortizacion_frances, amortizacion_aleman
from modules.gradientes import calcular_gradiente_geometrico
from modules.series_uniformes import valor_futuro_serie, cuota_para_valor_futuro
from modules.tasas import (
    periodica_desde_efectiva_anual,
    efectiva_anual_desde_periodica,
    rentabilidad_con_retencion,
)


def formato_cop(valor: float) -> str:
    """Formatea un valor en pesos colombianos para presentación."""
    if not math.isfinite(valor):
        return "N/A"
    return f"${valor:,.2f} COP".replace(",", "X").replace(".", ",").replace("X", ".")


def render():
    st.title("Casos Financieros Aplicados")
    st.write(
        "Análisis de decisiones financieras estratégicas con **productos reales de entidades bancarias colombianas**, "
        "con fuentes verificables, fechas de consulta e interacción dinámica de parámetros. "
        "En conjunto, estos tres casos integran los seis temas fundamentales del curso de Ingeniería Financiera."
    )

    tab_caso1, tab_caso2, tab_caso3 = st.tabs([
        "🏦 Caso 1: Inversión CDT vs. Cuenta de Rendimientos",
        "🚗 Caso 2: Financiación de Vehículo (Francés vs. Alemán)",
        "🏠 Caso 3: Ahorro Cuota Inicial con Gradiente Creciente",
    ])

    # =========================================================================
    # CASO 1: CDT BANCOLOMBIA VS. CUENTA NU
    # =========================================================================
    with tab_caso1:
        st.subheader("Caso 1: Comparación de Inversión — CDT Digital Bancolombia vs. Cajita Nu Colombia")
        st.info(
            "**Temas integrados**: Interés simple, interés compuesto, equivalencia de tasas, "
            "retención en la fuente y rentabilidad efectiva neta.\n\n"
            "**Fuentes**: Simulador CDT Digital Bancolombia (10.25% EA a 180 días) | "
            "Tarifario Oficial 'Cajitas de Ahorro' Nu Bank Colombia (12.00% EA capitalización diaria). "
            "**Fecha de consulta**: 24 de Octubre de 2026."
        )

        col1_c, col1_v = st.columns([0.36, 0.64], gap="large")

        with col1_c:
            st.markdown("#### 🎛️ Parámetros de Inversión")
            with st.form("form_caso_1"):
                inv_capital = st.number_input("Capital a Invertir (COP)", min_value=1_000_000.0, value=15_000_000.0, step=1_000_000.0, format="%.2f", key="c1_cap")
                inv_plazo_dias = st.number_input("Plazo de Inversión (Días)", min_value=30.0, max_value=720.0, value=180.0, step=30.0, key="c1_plazo")
                tasa_cdt_ea = st.number_input("Tasa CDT Bancolombia (% EA)", min_value=0.0, value=10.25, step=0.25, format="%.4f", key="c1_tasa_cdt")
                tasa_nu_ea = st.number_input("Tasa Cuenta Nu (% EA)", min_value=0.0, value=12.00, step=0.25, format="%.4f", key="c1_tasa_nu")
                retefuente_pct = st.slider("Retención en la Fuente sobre rendimientos (%)", min_value=0.0, max_value=10.0, value=4.0, step=0.5, key="c1_rete")
                btn_caso1 = st.form_submit_button("Simular y Comparar", type="primary")

        factor_plazo = inv_plazo_dias / 360.0
        tasa_per_cdt = ((1.0 + (tasa_cdt_ea / 100.0)) ** factor_plazo) - 1.0
        vf_bruto_cdt = inv_capital * (1.0 + tasa_per_cdt)
        res_cdt = rentabilidad_con_retencion(inv_capital, vf_bruto_cdt, retefuente_pct, inv_plazo_dias)

        tasa_diaria_nu = ((1.0 + (tasa_nu_ea / 100.0)) ** (1.0 / 360.0)) - 1.0
        vf_bruto_nu = inv_capital * ((1.0 + tasa_diaria_nu) ** inv_plazo_dias)
        res_nu = rentabilidad_con_retencion(inv_capital, vf_bruto_nu, retefuente_pct, inv_plazo_dias)
        diferencia_neta = res_nu["rendimiento_neto"] - res_cdt["rendimiento_neto"]

        with col1_v:
            st.markdown("#### 📊 Comparativa de Rentabilidad Neta Real")
            col_k1, col_k2, col_k3 = st.columns(3)
            col_k1.metric("Neto CDT Bancolombia", formato_cop(inv_capital + res_cdt["rendimiento_neto"]), delta=f"TEA Neta: {res_cdt['ea_neta']:.2f}%")
            col_k2.metric("Neto Cuenta Nu", formato_cop(inv_capital + res_nu["rendimiento_neto"]), delta=f"TEA Neta: {res_nu['ea_neta']:.2f}%")
            col_k3.metric("Ventaja a favor de Nu", formato_cop(diferencia_neta), delta=f"+{((res_nu['rendimiento_neto']/res_cdt['rendimiento_neto'])-1)*100:.1f}%")

            # Gráfico de barras comparativas
            fig_c1 = go.Figure()
            fig_c1.add_trace(go.Bar(
                name="Rendimiento Bruto",
                x=["CDT Bancolombia", "Cajita Nu"],
                y=[res_cdt["rendimiento_bruto"], res_nu["rendimiento_bruto"]],
                marker_color="#93c5fd"
            ))
            fig_c1.add_trace(go.Bar(
                name="Retención en la Fuente",
                x=["CDT Bancolombia", "Cajita Nu"],
                y=[res_cdt["retencion_valor"], res_nu["retencion_valor"]],
                marker_color="#f59e0b"
            ))
            fig_c1.add_trace(go.Bar(
                name="Rendimiento Neto a Recibir",
                x=["CDT Bancolombia", "Cajita Nu"],
                y=[res_cdt["rendimiento_neto"], res_nu["rendimiento_neto"]],
                marker_color="#2563eb"
            ))
            fig_c1.update_layout(
                title="Desglose: Rendimiento Bruto vs. Retención vs. Rendimiento Neto",
                barmode="group",
                template="plotly_white",
                margin=dict(l=20, r=20, t=40, b=20),
                height=260,
                legend=dict(orientation="h", y=1.1, x=0.1),
            )
            st.plotly_chart(fig_c1, use_container_width=True)

        st.markdown("##### 📑 Cuadro Comparativo Detallado")
        df_c1 = pd.DataFrame({
            "Variable / Métrica": [
                "Tasa Bruta Ofrecida",
                "Rendimiento Financiero Bruto",
                f"Deducción Retención ({retefuente_pct}%)",
                "Intereses Netos Recibidos",
                "Monto Total al Cierre",
                "Tasa Efectiva Anual Neta (TEA Real)",
            ],
            "CDT Digital Bancolombia": [
                f"{tasa_cdt_ea:.2f}% EA",
                formato_cop(res_cdt["rendimiento_bruto"]),
                f"-{formato_cop(res_cdt['retencion_valor'])}",
                formato_cop(res_cdt["rendimiento_neto"]),
                formato_cop(inv_capital + res_cdt["rendimiento_neto"]),
                f"{res_cdt['ea_neta']:.4f}% EA",
            ],
            "Cuenta Cajitas Nu Colombia": [
                f"{tasa_nu_ea:.2f}% EA",
                formato_cop(res_nu["rendimiento_bruto"]),
                f"-{formato_cop(res_nu['retencion_valor'])}",
                formato_cop(res_nu["rendimiento_neto"]),
                formato_cop(inv_capital + res_nu["rendimiento_neto"]),
                f"{res_nu['ea_neta']:.4f}% EA",
            ],
        })
        st.dataframe(df_c1, use_container_width=True, hide_index=True)

        st.markdown("#### 🎯 Respuestas a las Preguntas de Decisión (Rúbrica)")
        st.markdown(
            f"""
            1. **¿Cuál es el costo o la rentabilidad real del producto?**
               - El CDT Bancolombia genera una rentabilidad bruta de **{tasa_cdt_ea:.2f}% EA**, pero tras la retención en la fuente del {retefuente_pct}% su rentabilidad neta real desciende a **{res_cdt['ea_neta']:.2f}% EA**.
               - La cuenta Nu ofrece una rentabilidad bruta de **{tasa_nu_ea:.2f}% EA**, logrando una rentabilidad neta real de **{res_nu['ea_neta']:.2f}% EA**.
            2. **¿Cuánto se paga o se recibe en total y qué parte corresponde a intereses?**
               - En el CDT se reciben en total **{formato_cop(inv_capital + res_cdt['rendimiento_neto'])}**, de los cuales **{formato_cop(res_cdt['rendimiento_neto'])}** corresponden a intereses netos.
               - En Nu se reciben en total **{formato_cop(inv_capital + res_nu['rendimiento_neto'])}**, de los cuales **{formato_cop(res_nu['rendimiento_neto'])}** son intereses netos.
            3. **¿Cómo cambia el resultado si varían la tasa, el plazo o la retención?**
               - Al alargar el plazo, el efecto de capitalización diaria de Nu genera una brecha proporcionalmente mayor a su favor.
            4. **¿Qué alternativa o decisión se recomienda y con qué argumentos?**
               - **Decisión recomendada**: Se recomienda invertir en la **Cuenta de Rendimientos Nu Colombia**.
               - **Argumentos técnicos**: Produce un beneficio monetario superior de **{formato_cop(diferencia_neta)}** adicionales en el plazo evaluado, con la ventaja de ofrecer **liquidez inmediata** (retiro de fondos diario sin penalidad ni permanencia mínima obligatoria).
            """
        )

    # =========================================================================
    # CASO 2: CRÉDITO VEHÍCULO DAVIVIENDA (FRANCÉS VS. ALEMÁN)
    # =========================================================================
    with tab_caso2:
        st.subheader("Caso 2: Financiación de Vehículo — Crédito Banco Davivienda (Cuota Fija vs. Abono a Capital)")
        st.info(
            "**Temas integrados**: Conversión de tasas de interés (Nominal/Periódica a EA), series uniformes, "
            "construcción de tablas de amortización completas y comparación simultánea entre sistemas.\n\n"
            "**Fuente**: Simulador de Crédito de Vehículo Banco Davivienda Colombia (1.25% mes vencido = 16.08% EA). "
            "**Fecha de consulta**: 25 de Octubre de 2026."
        )

        col2_c, col2_v = st.columns([0.36, 0.64], gap="large")

        with col2_c:
            st.markdown("#### 🎛️ Parámetros del Crédito")
            with st.form("form_caso_2"):
                prestamo_auto = st.number_input("Valor a Financiar (COP)", min_value=5_000_000.0, value=40_000_000.0, step=2_000_000.0, format="%.2f", key="c2_prestamo")
                tasa_auto_mes = st.number_input("Tasa Mensual Vencida (%)", min_value=0.0, value=1.25, step=0.05, format="%.4f", key="c2_tasa")
                plazo_auto_meses = st.number_input("Plazo del Crédito (Meses)", min_value=6, max_value=84, value=48, step=6, key="c2_plazo")
                btn_caso2 = st.form_submit_button("Evaluar Sistemas de Amortización", type="primary")

        tasa_auto_ea = efectiva_anual_desde_periodica(tasa_auto_mes, 12)
        df_frances = amortizacion_frances(prestamo_auto, tasa_auto_mes / 100.0, int(plazo_auto_meses))
        df_aleman = amortizacion_aleman(prestamo_auto, tasa_auto_mes / 100.0, int(plazo_auto_meses))

        tot_pag_f = float(df_frances["Cuota (COP)"].sum())
        tot_int_f = float(df_frances["Interés (COP)"].sum())
        cuota_f = float(df_frances["Cuota (COP)"].iloc[0])

        tot_pag_a = float(df_aleman["Cuota (COP)"].sum())
        tot_int_a = float(df_aleman["Interés (COP)"].sum())
        cuota_a_ini = float(df_aleman["Cuota (COP)"].iloc[0])
        cuota_a_fin = float(df_aleman["Cuota (COP)"].iloc[-1])
        ahorro_int = tot_int_f - tot_int_a

        with col2_v:
            st.markdown("#### 📊 Comparativa de Costos y Cuotas")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Costo Real (TEA)", f"{tasa_auto_ea:.2f}% EA")
            m2.metric("Intereses Francés", formato_cop(tot_int_f))
            m3.metric("Intereses Alemán", formato_cop(tot_int_a))
            m4.metric("Ahorro Alemán", formato_cop(ahorro_int), delta=f"-{(ahorro_int/tot_int_f)*100:.1f}%")

            fig_auto = go.Figure()
            fig_auto.add_trace(go.Scatter(x=df_frances["Período"], y=df_frances["Cuota (COP)"], mode="lines+markers", name="Sistema Francés (Cuota Fija)", line=dict(color="#f59e0b", width=3)))
            fig_auto.add_trace(go.Scatter(x=df_aleman["Período"], y=df_aleman["Cuota (COP)"], mode="lines+markers", name="Sistema Alemán (Cuota Decreciente)", line=dict(color="#2563eb", width=3, shape="spline")))
            fig_auto.update_layout(
                title="Trayectoria de Cuotas Mensuales: Cuota Fija vs. Abono Constante",
                xaxis_title="Mes",
                yaxis_title="Cuota (COP)",
                template="plotly_white",
                margin=dict(l=20, r=20, t=40, b=20),
                height=260,
                legend=dict(orientation="h", y=1.1, x=0.2),
            )
            st.plotly_chart(fig_auto, use_container_width=True)

        st.markdown("#### 🎯 Respuestas a las Preguntas de Decisión (Rúbrica)")
        st.markdown(
            f"""
            1. **¿Cuál es el costo real del producto?**
               - La tasa pactada del **{tasa_auto_mes:.2f}% mes vencido** equivale a un costo efectivo anual real del **{tasa_auto_ea:.2f}% EA** (Tasa Nominal Anual del {tasa_auto_mes*12:.2f}% MV).
            2. **¿Cuánto se paga en total y qué parte corresponde a intereses?**
               - **Sistema Francés**: Se pagan en total **{formato_cop(tot_pag_f)}**, de los cuales **{formato_cop(tot_int_f)}** corresponden a intereses ({((tot_int_f/tot_pag_f)*100):.1f}% del desembolso total).
               - **Sistema Alemán**: Se pagan en total **{formato_cop(tot_pag_a)}**, de los cuales **{formato_cop(tot_int_a)}** son intereses.
            3. **¿Cómo cambia el resultado si varían la tasa o el plazo?**
               - Al incrementar el plazo de 48 a 60 o 72 meses, el total de intereses se dispara dramáticamente en el sistema francés. El sistema alemán amortiza el principal más rápido, preservando el ahorro financiero.
            4. **¿Qué alternativa o decisión se recomienda y con qué argumentos?**
               - **Decisión recomendada**: Se recomienda el **Sistema Alemán (Abono Constante a Capital)** si la capacidad de pago inicial del deudor lo permite.
               - **Argumentos técnicos**: Genera un ahorro neto de **{formato_cop(ahorro_int)}** en intereses totales. Aunque la primera cuota inicia en {formato_cop(cuota_a_ini)} (superior a la fija de {formato_cop(cuota_f)}), decrece rápidamente cada mes hasta terminar en {formato_cop(cuota_a_fin)}, liberando flujo de caja progresivamente.
            """
        )

    # =========================================================================
    # CASO 3: AHORRO CON GRADIENTE GEOMÉTRICO (CUOTA INICIAL VIVIENDA)
    # =========================================================================
    with tab_caso3:
        st.subheader("Caso 3: Plan de Ahorro para Cuota Inicial — Fondo Crecer Bancolombia (Cuota Fija vs. Gradiente Creciente)")
        st.info(
            "**Temas integrados**: Series uniformes, gradiente geométrico, valor futuro de gradientes y cuota uniforme equivalente.\n\n"
            "**Fuente**: Fondo de Inversión Colectiva / Plan Ahorro Vivienda Bancolombia (Rentabilidad histórica esperada: 8.50% EA = 0.682% mensual). "
            "**Fecha de consulta**: 24 de Octubre de 2026."
        )

        col3_c, col3_v = st.columns([0.36, 0.64], gap="large")

        with col3_c:
            st.markdown("#### 🎛️ Parámetros de la Meta de Ahorro")
            with st.form("form_caso_3"):
                meta_vivienda = st.number_input("Meta de Cuota Inicial (COP)", min_value=5_000_000.0, value=30_000_000.0, step=1_000_000.0, format="%.2f", key="c3_meta")
                rentabilidad_fondo_ea = st.number_input("Rentabilidad del Fondo (% EA)", min_value=0.0, value=8.50, step=0.25, format="%.4f", key="c3_ea")
                plazo_ahorro_meses = st.number_input("Plazo de Ahorro (Meses)", min_value=6, max_value=60, value=36, step=6, key="c3_plazo")
                g_mensual_pct = st.slider("Crecimiento de cuota mensual por gradiente (%)", min_value=0.1, max_value=2.0, value=0.5, step=0.1, key="c3_g")
                btn_caso3 = st.form_submit_button("Evaluar Esquemas de Ahorro", type="primary")

        tasa_fondo_mes = periodica_desde_efectiva_anual(rentabilidad_fondo_ea, 12)
        n_meses = int(plazo_ahorro_meses)

        cuota_fija_ahorro = cuota_para_valor_futuro(meta_vivienda, tasa_fondo_mes, n_meses, "Vencida")
        total_aportes_fijos = cuota_fija_ahorro * n_meses
        intereses_fijos = meta_vivienda - total_aportes_fijos

        i_dec = tasa_fondo_mes / 100.0
        g_dec = g_mensual_pct / 100.0

        if abs(i_dec - g_dec) < 1e-9:
            factor_vf_grad = n_meses * ((1.0 + i_dec) ** (n_meses - 1))
        else:
            factor_vf_grad = (((1.0 + i_dec) ** n_meses) - ((1.0 + g_dec) ** n_meses)) / (i_dec - g_dec)

        primer_pago_grad = meta_vivienda / factor_vf_grad
        resultado_grad = calcular_gradiente_geometrico(primer_pago_grad, g_mensual_pct, tasa_fondo_mes, n_meses)
        pagos_grad = resultado_grad["pagos"]
        total_aportes_grad = sum(pagos_grad)
        intereses_grad = meta_vivienda - total_aportes_grad

        with col3_v:
            st.markdown("#### 📊 Esfuerzo de Ahorro y Rentabilidad Acumulada")
            m1, m2, m3 = st.columns(3)
            m1.metric("Cuota Fija Requerida", formato_cop(cuota_fija_ahorro))
            m2.metric("Primera Cuota Gradiente (A₁)", formato_cop(primer_pago_grad), delta=f"-{formato_cop(cuota_fija_ahorro - primer_pago_grad)} al inicio")
            m3.metric("Última Cuota Gradiente (A₃₆)", formato_cop(pagos_grad[-1]))

            fig_grad = go.Figure()
            fig_grad.add_trace(go.Scatter(x=list(range(1, n_meses + 1)), y=[cuota_fija_ahorro] * n_meses, mode="lines", name="Aporte Fijo Uniforme", line=dict(color="#f59e0b", width=3, dash="dash")))
            fig_grad.add_trace(go.Scatter(
                x=list(range(1, n_meses + 1)),
                y=pagos_grad,
                mode="lines+markers",
                name="Aporte con Gradiente Creciente",
                line=dict(color="#2563eb", width=3, shape="spline"),
                fill="tozeroy",
                fillcolor="rgba(37, 99, 235, 0.08)",
            ))
            fig_grad.update_layout(
                title="Esquemas de Ahorro: Cuota Fija vs. Gradiente Creciente",
                xaxis_title="Mes",
                yaxis_title="Aporte Mensual (COP)",
                template="plotly_white",
                margin=dict(l=20, r=20, t=40, b=20),
                height=260,
                legend=dict(orientation="h", y=1.1, x=0.2),
            )
            st.plotly_chart(fig_grad, use_container_width=True)

        st.markdown("#### 🎯 Respuestas a las Preguntas de Decisión (Rúbrica)")
        st.markdown(
            f"""
            1. **¿Cuál es la rentabilidad real del producto?**
               - El fondo fiduciario renta a una tasa efectiva del **{rentabilidad_fondo_ea:.2f}% EA**, lo que equivale a un **{tasa_fondo_mes:.4f}% mes vencido**.
            2. **¿Cuánto se paga o se recibe en total y qué parte corresponde a intereses?**
               - En la meta de **{formato_cop(meta_vivienda)}**:
                 - Con cuota fija: El ahorrador aporta **{formato_cop(total_aportes_fijos)}** y los intereses ganados son **{formato_cop(intereses_fijos)}**.
                 - Con gradiente: El ahorrador aporta **{formato_cop(total_aportes_grad)}** y los intereses ganados son **{formato_cop(intereses_grad)}**.
            3. **¿Cómo cambia el resultado si varían la tasa o el gradiente?**
               - Un mayor porcentaje de gradiente permite empezar con cuotas iniciales aún más bajas, facilitando el enganche al plan de ahorro para familias cuyos ingresos se proyectan al alza con los incrementos salariales anuales.
            4. **¿Qué alternativa o decisión se recomienda y con qué argumentos?**
               - **Decisión recomendada**: Se recomienda el **Plan con Gradiente Geométrico Creciente**.
               - **Argumentos técnicos**: Reduce el esfuerzo financiero inicial de **{formato_cop(cuota_fija_ahorro)}** a **{formato_cop(primer_pago_grad)}** al mes (ahorrando liquidez en los primeros 18 meses), haciendo viable el proyecto de vivienda para jóvenes profesionales que anticipan ascensos o aumentos salariales periódicos.
            """
        )
