"""Pantalla A: ¿Dónde pongo mi plata?"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.ui import COLORES, GRIS, aplicar_estilo, aviso_datos_ejemplo, campos_fuente, parametros
from motor.datos_ejemplo import CASO_A, INTERES_REINVERTIDO, INTERES_RETIRADO
from motor.decisiones import PERIODICIDADES_TASA, evaluar_caso_a
from motor.formato import formato_cop
from motor.interes import DIAS_POR_CONVENCION
from motor.tasas import TIPOS_TASA, tasa_combinada


def _entradas_tasa(prefijo: str) -> None:
    st.number_input("Tasa (%)", min_value=0.0, step=0.25, format="%.4f", key=f"{prefijo}tasa")
    st.selectbox("Tipo de tasa", TIPOS_TASA, key=f"{prefijo}tipo")
    st.selectbox("Periodicidad de la tasa", list(PERIODICIDADES_TASA), key=f"{prefijo}periodicidad")


def _entradas() -> None:
    st.subheader("🎛️ Tus datos")
    c1, c2, c3, c4 = st.columns(4)
    c1.number_input("Monto a invertir (COP)", min_value=1.0, step=500_000.0, format="%.2f", key="a_monto")
    c2.number_input("Plazo (días)", min_value=1, max_value=3650, step=30, key="a_dias")
    c3.selectbox("Convención de días", list(DIAS_POR_CONVENCION), key="a_convencion")
    c4.number_input("Inflación esperada (% EA)", min_value=-50.0, step=0.1, format="%.2f", key="a_inflacion")

    col_cdt, col_ahorro, col_combinada = st.columns(3, gap="medium")
    with col_cdt.container(border=True):
        st.markdown("**CDT**")
        _entradas_tasa("a_cdt_")
        st.selectbox("Intereses", [INTERES_RETIRADO, INTERES_REINVERTIDO], key="a_cdt_intereses")
        st.number_input("Retención en la fuente (%)", min_value=0.0, max_value=100.0, step=0.5, format="%.2f", key="a_cdt_retencion")
    with col_ahorro.container(border=True):
        st.markdown("**Cuenta de ahorros**")
        _entradas_tasa("a_ahorro_")
        st.number_input("Retención en la fuente (%)", min_value=0.0, max_value=100.0, step=0.5, format="%.2f", key="a_ahorro_retencion")
    with col_combinada.container(border=True):
        st.markdown("**Alternativa a tasa combinada**")
        st.number_input("Puntos sobre la inflación (%)", min_value=0.0, step=0.25, format="%.2f", key="a_comb_puntos")
        ea = tasa_combinada(st.session_state["a_inflacion"], st.session_state["a_comb_puntos"])
        st.caption(f"Tasa combinada: (1 + inflación) × (1 + puntos) − 1 = **{ea:.4f}% EA**")
        st.number_input("Retención en la fuente (%)", min_value=0.0, max_value=100.0, step=0.5, format="%.2f", key="a_comb_retencion")


def _resultados(r: dict, p: dict) -> None:
    st.subheader("✅ Recomendación")
    st.success(r["recomendacion"])
    st.caption("La recomendación compara solo el dinero final: no incluye liquidez, riesgo ni condiciones de cada producto.")

    mejor = r["mejor"]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(f"EA neta: {mejor['nombre']}", f"{mejor['ea_neta']:.2f}%", delta=f"bruta {mejor['ea_bruta']:.2f}%", delta_color="off")
    k2.metric("Valor final neto", formato_cop(mejor["vf_neto"]))
    k3.metric("Intereses ganados netos", formato_cop(mejor["intereses_netos"]))
    k4.metric("Ganancia real", formato_cop(mejor["ganancia_real"]), delta=f"{mejor['tasa_real']:.2f}% real", delta_color="off")

    fig = go.Figure()
    for producto, color in zip(r["productos"], COLORES):
        fig.add_trace(go.Scatter(x=producto["dias"], y=producto["saldos"], mode="lines", name=producto["nombre"], line=dict(color=color, width=3)))
    fig.add_trace(go.Scatter(
        x=r["dias"], y=r["poder_adquisitivo"], mode="lines", name="Monto ajustado por inflación (referencia)",
        line=dict(color=GRIS, width=2, dash="dash"),
    ))
    st.plotly_chart(aplicar_estilo(fig, "Evolución del dinero en cada opción, neto de retención", "Días desde la inversión", "Valor acumulado (COP)", 380), use_container_width=True)

    st.markdown("##### 📑 Comparación completa")
    st.dataframe(pd.DataFrame([
        {
            "Producto": x["nombre"],
            "EA ofrecida": f"{x['ea_ofrecida']:.2f}%",
            "EA bruta obtenida": f"{x['ea_bruta']:.2f}%",
            "EA neta": f"{x['ea_neta']:.2f}%",
            "Retención": formato_cop(x["retencion"]),
            "Intereses netos": formato_cop(x["intereses_netos"]),
            "Valor final neto": formato_cop(x["vf_neto"]),
            "Ganancia real": formato_cop(x["ganancia_real"]),
            "Tasa real": f"{x['tasa_real']:.2f}%",
        }
        for x in r["productos"]
    ]), use_container_width=True, hide_index=True)
    if p["a_cdt_intereses"] == INTERES_RETIRADO:
        st.caption("El CDT retira sus intereses sin reinvertirlos (interés simple), por eso su EA bruta obtenida es menor que la EA ofrecida.")

    with st.expander("📐 Fórmulas usadas"):
        st.latex(r"\text{Compuesto: } VF = C (1 + EA)^{d / B} \qquad \text{Simple: } VF = C (1 + i_p \cdot t)")
        st.latex(r"\text{Retención} = (VF - C) \cdot r \qquad VF_{neto} = VF - \text{Retención}")
        st.latex(r"EA_{neta} = \left(\frac{VF_{neto}}{C}\right)^{B / d} - 1 \qquad i_{real} = \frac{1 + EA_{neta}}{1 + \pi} - 1")
        st.latex(r"\text{Ganancia real} = \frac{VF_{neto}}{(1 + \pi)^{d / B}} - C")
        st.caption("C: monto; d: días; B: base de días (360 o 365); r: retención; π: inflación; i_p: tasa del periodo; t: número de periodos.")


def render() -> None:
    st.title("💸 ¿Dónde pongo mi plata?")
    st.write("Compara un CDT, una cuenta de ahorros y una alternativa a tasa combinada (inflación + puntos).")
    aviso_datos_ejemplo()
    _entradas()
    try:
        p = parametros(CASO_A)
        _resultados(evaluar_caso_a(p), p)
    except ValueError as e:
        st.error(f"Revisa los datos: {e}")
    campos_fuente("a_")
