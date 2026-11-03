"""Pantalla B: ¿Me conviene este crédito?"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.ui import (
    COLORES,
    aplicar_estilo,
    aviso_datos_ejemplo,
    campos_fuente,
    mostrar_verificacion,
    parametros,
    tabla_cop,
    texto_dinero,
)
from motor.amortizacion import (
    FORMAS_PAGO,
    MAX_CUOTAS,
    PERIODICIDADES_AMORT,
    SISTEMAS,
    efecto_abono_extra,
    puntos_saldo,
)
from motor.datos_ejemplo import CASO_B
from motor.decisiones import PERIODICIDADES_TASA, evaluar_caso_b
from motor.formato import formato_cop
from motor.tasas import TIPOS_TASA

COLUMNAS_COP = ["Saldo Inicial (COP)", "Cuota (COP)", "Interés (COP)", "Abono a Capital (COP)", "Abono Extra (COP)", "Saldo Final (COP)"]


def _entradas_oferta(letra: str) -> None:
    prefijo = f"b_{letra}_"
    st.markdown(f"**Oferta {letra.upper()}**")
    c1, c2 = st.columns(2)
    c1.number_input("Capital (COP)", min_value=1.0, step=1_000_000.0, format="%.2f", key=f"{prefijo}capital")
    c2.number_input("Tasa (%)", min_value=0.0, step=0.25, format="%.4f", key=f"{prefijo}tasa")
    c3, c4 = st.columns(2)
    c3.selectbox("Tipo de tasa", TIPOS_TASA, key=f"{prefijo}tipo")
    c4.selectbox("Periodicidad de la tasa", list(PERIODICIDADES_TASA), key=f"{prefijo}periodicidad_tasa")
    c4, c5, c6 = st.columns(3)
    c4.number_input("Plazo (meses)", min_value=1, max_value=MAX_CUOTAS, step=6, key=f"{prefijo}meses")
    c5.selectbox("Periodicidad de pago", list(PERIODICIDADES_AMORT), key=f"{prefijo}periodicidad_pago")
    c6.selectbox("Forma de pago", FORMAS_PAGO, key=f"{prefijo}pago", help="Vencida: al final de cada periodo. Anticipada: al inicio, con el primer pago en el periodo 0.")


def _columna_oferta(oferta: dict, sistema: str) -> None:
    r = oferta["sistemas"][sistema]
    st.markdown(f"#### Oferta {oferta['nombre']}")
    k1, k2 = st.columns(2)
    k1.metric("Tasa EA", f"{oferta['ea']:.4f}%")
    k2.metric(f"Tasa por periodo ({oferta['n']} pagos)", f"{oferta['tasa_periodica'] * 100:.4f}%")
    k3, k4 = st.columns(2)
    k3.metric("Primera cuota", formato_cop(r["cuota_inicial"]))
    k4.metric("Última cuota", formato_cop(r["cuota_final"]))
    k5, k6 = st.columns(2)
    k5.metric("Intereses totales", formato_cop(r["intereses"]))
    k6.metric("Total pagado", formato_cop(r["total_pagado"]))


def _graficos(a: dict, b: dict, sistema: str) -> None:
    fig = go.Figure()
    for oferta, color in zip((a, b), COLORES):
        x, y = puntos_saldo(oferta["sistemas"][sistema]["tabla"], oferta["capital"])
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", marker=dict(size=5), name=f"Oferta {oferta['nombre']}", line=dict(color=color, width=2)))
    st.plotly_chart(aplicar_estilo(fig, f"Saldo del crédito después de cada pago: {sistema}", "Periodo de pago", "Saldo (COP)"), width="stretch")

    columnas = st.columns(2)
    for columna, oferta in zip(columnas, (a, b)):
        tabla = oferta["sistemas"][sistema]["tabla"]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=tabla["Período"], y=tabla["Abono a Capital (COP)"], name="Capital", marker=dict(color=COLORES[0], line=dict(color="white", width=1))))
        fig.add_trace(go.Bar(x=tabla["Período"], y=tabla["Interés (COP)"], name="Intereses", marker=dict(color=COLORES[1], line=dict(color="white", width=1))))
        fig.update_layout(barmode="stack")
        columna.plotly_chart(aplicar_estilo(fig, f"Composición de la cuota: oferta {oferta['nombre']}", "Periodo de pago", "Pago por periodo (COP)"), width="stretch")


def _comparacion_sistemas(a: dict, b: dict) -> None:
    st.markdown("##### ⚖️ Cuota fija frente a abono constante")
    filas = []
    for oferta in (a, b):
        for sistema in SISTEMAS:
            r = oferta["sistemas"][sistema]
            filas.append({
                "Oferta": oferta["nombre"],
                "Sistema": sistema,
                "Tasa EA": f"{oferta['ea']:.2f}%",
                "Primera cuota": formato_cop(r["cuota_inicial"]),
                "Última cuota": formato_cop(r["cuota_final"]),
                "Intereses totales": formato_cop(r["intereses"]),
                "Total pagado": formato_cop(r["total_pagado"]),
            })
    st.dataframe(pd.DataFrame(filas), width="stretch", hide_index=True)
    st.caption(
        "Dentro de una misma oferta, ambos sistemas tienen el mismo costo efectivo (misma EA). "
        "El abono constante paga menos intereses en pesos porque devuelve el capital más rápido, no porque sea una tasa menor."
    )


def _tablas(a: dict, b: dict) -> None:
    st.markdown("##### 📋 Tablas de amortización")
    for oferta in (a, b):
        for sistema in SISTEMAS:
            r = oferta["sistemas"][sistema]
            with st.expander(f"Oferta {oferta['nombre']}: {sistema}"):
                mostrar_verificacion(r["verificacion"])
                st.dataframe(tabla_cop(r["tabla"], COLUMNAS_COP), width="stretch", hide_index=True)


def _abono_extra(a: dict, b: dict, p: dict) -> None:
    st.subheader("💪 ¿Y si abonas extra a capital?")
    extra = st.number_input("Abono extra en cada pago (COP)", min_value=0.0, step=50_000.0, format="%.2f", key="b_extra")
    if extra <= 0:
        st.caption("Escribe un valor mayor que cero para ver cuánto ahorras.")
        return
    sistema = p["b_sistema"]
    columnas = st.columns(2)
    for columna, oferta in zip(columnas, (a, b)):
        efecto = efecto_abono_extra(oferta["capital"], oferta["tasa_periodica"], oferta["n"], sistema, oferta["pago"], extra)
        with columna:
            st.markdown(f"**Oferta {oferta['nombre']}**")
            k1, k2 = st.columns(2)
            k1.metric("Intereses que ahorras", formato_cop(efecto["intereses_ahorrados"]))
            k2.metric("Pagos que te ahorras", f"{efecto['cuotas_menos']}", delta=f"{efecto['cuotas_con_extra']} en vez de {efecto['cuotas_sin_extra']}", delta_color="off", delta_arrow="off")


def render() -> None:
    st.title("🏦 ¿Me conviene este crédito?")
    st.write("Pon dos ofertas lado a lado. Cada tasa se convierte a EA para compararlas en igualdad de condiciones.")
    aviso_datos_ejemplo()

    st.subheader("🎛️ Las ofertas")
    col_a, col_b = st.columns(2, gap="medium")
    with col_a.container(border=True):
        _entradas_oferta("a")
    with col_b.container(border=True):
        _entradas_oferta("b")
    c1, c2 = st.columns(2)
    c1.selectbox("Sistema para comparar", SISTEMAS, key="b_sistema")
    c2.number_input(
        "Tasa de descuento (% EA)", min_value=0.0, step=0.5, format="%.2f", key="b_descuento",
        help="Lo que rendiría tu dinero en otra parte. Sirve para expresar los pagos futuros en pesos de hoy.",
    )

    try:
        p = parametros(CASO_B)
        r = evaluar_caso_b(p)
        a, b, sistema = r["a"], r["b"], p["b_sistema"]

        st.subheader("✅ Veredicto")
        st.success(texto_dinero(r["veredicto"]["texto"]))
        for aviso in r["veredicto"]["avisos"]:
            st.warning(texto_dinero(aviso))

        col_a, col_b = st.columns(2, gap="large")
        with col_a:
            _columna_oferta(a, sistema)
        with col_b:
            _columna_oferta(b, sistema)

        _graficos(a, b, sistema)
        _comparacion_sistemas(a, b)
        _tablas(a, b)
        _abono_extra(a, b, p)

        with st.expander("📐 Fórmulas usadas"):
            st.latex(r"\text{Anticipada a vencida: } i_v = \frac{i_a}{1 - i_a} \qquad EA = (1 + i_v)^m - 1 \qquad i_{pago} = (1 + EA)^{1/m_p} - 1")
            st.latex(r"\text{Cuota fija vencida: } A = P \frac{i}{1 - (1 + i)^{-n}} \qquad \text{anticipada: } A = \frac{P}{\frac{1 - (1 + i)^{-n}}{i}(1 + i)}")
            st.latex(r"\text{Abono constante: } K = \frac{P}{n} \qquad \text{Cuota}_t = K + S_{t-1} \cdot i")
            st.latex(r"\text{Costo en pesos de hoy} = \sum_t \frac{\text{Pago}_t}{(1 + d)^{t / m_p}} - P")
    except ValueError as e:
        st.error(f"Revisa los datos: {e}")
    campos_fuente("b_")
