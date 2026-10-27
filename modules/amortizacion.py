"""Tablas de amortización de préstamos: Sistema Francés (Cuota Fija) y Alemán (Abono Constante a Capital)."""

import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.tasas import periodica_desde_efectiva_anual


def formato_cop(valor: float) -> str:
    """Formatea un valor en pesos colombianos para presentación."""
    if not math.isfinite(valor):
        return "N/A"
    return f"${valor:,.2f} COP".replace(",", "X").replace(".", ",").replace("X", ".")


MAX_CUOTAS = 600

PERIODICIDADES_AMORT = {
    "Mensual": 12,
    "Bimestral": 6,
    "Trimestral": 4,
    "Semestral": 2,
    "Anual": 1,
}


def calcular_tasa_periodica(tasa_valor: float, tipo_tasa: str, periodicidad: str) -> float:
    """Convierte la tasa ingresada a tasa efectiva periódica según la frecuencia."""
    m = PERIODICIDADES_AMORT.get(periodicidad, 12)
    if tipo_tasa == "Efectiva Periódica":
        return tasa_valor / 100.0
    elif tipo_tasa == "Efectiva Anual (EA)":
        return periodica_desde_efectiva_anual(tasa_valor, m) / 100.0
    elif tipo_tasa == "Nominal Anual Vencida":
        return (tasa_valor / 100.0) / m
    return tasa_valor / 100.0


# ------------------ SISTEMA FRANCÉS (CUOTA FIJA) ------------------

def amortizacion_frances(prestamo: float, tasa_periodica: float, n_cuotas: int) -> pd.DataFrame:
    """Genera la tabla de amortización por el sistema francés (cuota fija)."""
    if prestamo <= 0 or n_cuotas < 1:
        raise ValueError("El préstamo debe ser > 0 y el número de cuotas >= 1.")

    if tasa_periodica == 0:
        cuota_fija = prestamo / n_cuotas
    else:
        cuota_fija = prestamo * (tasa_periodica / (1.0 - (1.0 + tasa_periodica) ** (-n_cuotas)))

    filas = []
    saldo = prestamo
    for p in range(1, n_cuotas + 1):
        saldo_inicial = saldo
        interes = saldo_inicial * tasa_periodica
        if p == n_cuotas:
            abono = saldo_inicial
            cuota = abono + interes
            saldo_final = 0.0
        else:
            abono = cuota_fija - interes
            cuota = cuota_fija
            saldo_final = saldo_inicial - abono

        filas.append({
            "Período": p,
            "Saldo Inicial (COP)": saldo_inicial,
            "Cuota (COP)": cuota,
            "Interés (COP)": interes,
            "Abono a Capital (COP)": abono,
            "Saldo Final (COP)": max(0.0, saldo_final),
        })
        saldo = saldo_final

    return pd.DataFrame(filas)


# ------------------ SISTEMA ALEMÁN (ABONO CONSTANTE) ------------------

def amortizacion_aleman(prestamo: float, tasa_periodica: float, n_cuotas: int) -> pd.DataFrame:
    """Genera la tabla de amortización por el sistema alemán (abono constante a capital)."""
    if prestamo <= 0 or n_cuotas < 1:
        raise ValueError("El préstamo debe ser > 0 y el número de cuotas >= 1.")

    abono_fijo = prestamo / n_cuotas
    filas = []
    saldo = prestamo
    for p in range(1, n_cuotas + 1):
        saldo_inicial = saldo
        interes = saldo_inicial * tasa_periodica
        abono = abono_fijo
        cuota = abono + interes
        saldo_final = saldo_inicial - abono
        if p == n_cuotas or abs(saldo_final) < 1e-4:
            saldo_final = 0.0

        filas.append({
            "Período": p,
            "Saldo Inicial (COP)": saldo_inicial,
            "Cuota (COP)": cuota,
            "Interés (COP)": interes,
            "Abono a Capital (COP)": abono,
            "Saldo Final (COP)": max(0.0, saldo_final),
        })
        saldo = saldo_final

    return pd.DataFrame(filas)


# Compatibilidad
def generar_tabla_amortizacion(prestamo: float, tasa_porcentaje: float, numero_cuotas: int) -> pd.DataFrame:
    tasa_p = tasa_porcentaje / 100.0
    return amortizacion_frances(prestamo, tasa_p, numero_cuotas)


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
            with st.form("form_amortizacion_single"):
                prestamo = st.number_input("Monto del Préstamo (COP)", min_value=100_000.0, value=20_000_000.0, step=1_000_000.0, format="%.2f")
                sistema = st.selectbox("Sistema de Amortización", ["Francés (Cuota Fija)", "Alemán (Abono Constante a Capital)"])
                tasa_val = st.number_input("Valor de la Tasa (%)", min_value=0.0, value=18.0, step=0.5, format="%.4f")
                tipo_tasa = st.selectbox("Tipo de Tasa", ["Efectiva Anual (EA)", "Nominal Anual Vencida", "Efectiva Periódica"])
                periodicidad = st.selectbox("Periodicidad de Pago", list(PERIODICIDADES_AMORT.keys()))
                n_cuotas = st.number_input("Número de Cuotas (Plazo)", min_value=1, max_value=MAX_CUOTAS, value=24, step=1)
                btn_simular = st.form_submit_button("Generar Tabla de Amortización", type="primary")

        tasa_per = calcular_tasa_periodica(tasa_val, tipo_tasa, periodicidad)
        is_frances = "Francés" in sistema
        if is_frances:
            df_tabla = amortizacion_frances(prestamo, tasa_per, int(n_cuotas))
        else:
            df_tabla = amortizacion_aleman(prestamo, tasa_per, int(n_cuotas))

        total_cuotas = float(df_tabla["Cuota (COP)"].sum())
        total_intereses = float(df_tabla["Interés (COP)"].sum())
        total_abonos = float(df_tabla["Abono a Capital (COP)"].sum())
        saldo_cierre = float(df_tabla["Saldo Final (COP)"].iloc[-1])

        with col_view:
            st.markdown("#### 📊 Métricas Clave del Crédito")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Tasa Periódica", f"{tasa_per * 100:.4f}% {periodicidad.lower()}")
            k2.metric("Primera Cuota", formato_cop(df_tabla["Cuota (COP)"].iloc[0]))
            k3.metric("Total Intereses", formato_cop(total_intereses))
            k4.metric("Costo Total", formato_cop(total_cuotas))

            col_v1, col_v2 = st.columns(2)
            check_abonos = abs(total_abonos - prestamo) < 1.0
            check_saldo = abs(saldo_cierre) < 0.01

            with col_v1:
                st.success(f"✅ Suma de abonos ({formato_cop(total_abonos)}) = Préstamo" if check_abonos else "❌ Discrepancia")
            with col_v2:
                st.success(f"✅ Saldo final: {formato_cop(saldo_cierre)} (Cierre en cero)" if check_saldo else "❌ No cerró en cero")

            # Gráficos
            g1, g2 = st.columns(2)
            with g1:
                fig_saldo = go.Figure()
                saldos_plot = [prestamo] + df_tabla["Saldo Final (COP)"].tolist()
                fig_saldo.add_trace(go.Scatter(
                    x=list(range(len(saldos_plot))),
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
            if is_frances:
                cuota_0 = df_tabla["Cuota (COP)"].iloc[0]
                st.latex(
                    rf"""
                    \begin{{aligned}}
                    A &= P \cdot \left[\frac{{i}}{{1 - (1+i)^{{-n}}}}\right] \\
                    A &= {prestamo:,.2f} \cdot \left[\frac{{{tasa_per:.6g}}}{{1 - (1 + {tasa_per:.6g})^{{-{int(n_cuotas)}}}}}\right] = {cuota_0:,.2f}\text{{ COP (Cuota Fija)}}
                    \end{{aligned}}
                    """
                )
            else:
                abono_c = prestamo / int(n_cuotas)
                c_ini = df_tabla['Cuota (COP)'].iloc[0]
                c_fin = df_tabla['Cuota (COP)'].iloc[-1]
                st.latex(
                    rf"""
                    \begin{{aligned}}
                    K &= \frac{{P}}{{n}} = \frac{{{prestamo:,.2f}}}{{{int(n_cuotas)}}} = {abono_c:,.2f}\text{{ COP (Abono Constante)}} \\
                    A_1 &= K + (P \cdot i) = {abono_c:,.2f} + ({prestamo:,.2f} \cdot {tasa_per:.6g}) = {c_ini:,.2f}\text{{ COP}} \\
                    A_n &= K + (K \cdot i) = {abono_c:,.2f} + ({abono_c:,.2f} \cdot {tasa_per:.6g}) = {c_fin:,.2f}\text{{ COP}}
                    \end{{aligned}}
                    """
                )

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
            with st.form("form_comparativa_sistemas"):
                comp_prestamo = st.number_input("Monto del Crédito (COP)", min_value=100_000.0, value=30_000_000.0, step=1_000_000.0, format="%.2f", key="comp_prestamo")
                comp_tasa_ea = st.number_input("Tasa Efectiva Anual EA (%)", min_value=0.0, value=20.0, step=0.5, format="%.4f", key="comp_tasa_ea")
                comp_plazo = st.number_input("Plazo en Meses", min_value=1, max_value=MAX_CUOTAS, value=36, step=1, key="comp_plazo")
                btn_compare = st.form_submit_button("Comparar Ambos Sistemas", type="primary")

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
            m3.metric("Ahorro con Sist. Alemán", formato_cop(ahorro_intereses), delta=f"-{(ahorro_intereses / int_f) * 100:.2f}% de intereses")

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
