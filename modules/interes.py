"""Herramientas para calcular interés simple y compuesto."""

import math

import pandas as pd
import plotly.express as px
import streamlit as st


def calcular_saldos(capital: float, tasa_porcentaje: float, periodos: int, tipo: str):
    """Devuelve los saldos desde el período cero hasta el período final."""
    tasa = tasa_porcentaje / 100
    if tipo == "Interés simple":
        return [capital * (1 + tasa * periodo) for periodo in range(periodos + 1)]
    return [capital * (1 + tasa) ** periodo for periodo in range(periodos + 1)]


def formato_cop(valor: float) -> str:
    """Formatea un valor en pesos colombianos para presentación."""
    return f"${valor:,.2f} COP".replace(",", "X").replace(".", ",").replace("X", ".")


def render():
    st.title("Interés simple y compuesto")
    st.write(
        "Calcula cómo evoluciona un capital con una tasa constante. "
        "La tasa y el número de períodos deben usar la misma unidad temporal "
        "(por ejemplo, tasa mensual y períodos en meses)."
    )

    tipo = st.radio(
        "Tipo de interés",
        ["Interés simple", "Interés compuesto"],
        horizontal=True,
        key="interes_tipo",
    )
    with st.form("formulario_interes"):
        columna_capital, columna_tasa, columna_periodos = st.columns(3)
        with columna_capital:
            capital = st.number_input(
                "Capital inicial (COP)", min_value=0.0, value=1_000_000.0,
                step=100_000.0, format="%.2f", key="interes_capital",
            )
        with columna_tasa:
            tasa = st.number_input(
                "Tasa por período (%)", min_value=0.0, value=5.0,
                step=0.5, format="%.4f", key="interes_tasa",
            )
        with columna_periodos:
            periodos = st.number_input(
                "Número de períodos", min_value=1, max_value=10000, value=12,
                step=1, format="%d", key="interes_periodos",
            )
        calcular = st.form_submit_button("Calcular", type="primary")

    if not calcular:
        st.caption("Ingresa los datos y selecciona Calcular para ver la proyección.")
        return

    if not math.isfinite(capital) or capital < 0:
        st.error("El capital inicial debe ser un valor finito igual o mayor que cero.")
        return
    if not math.isfinite(tasa) or tasa < 0:
        st.error("La tasa debe ser un valor finito igual o mayor que cero.")
        return
    if isinstance(periodos, bool) or int(periodos) != periodos or periodos < 1:
        st.error("El número de períodos debe ser un entero positivo.")
        return

    periodos = int(periodos)
    try:
        saldos = calcular_saldos(capital, tasa, periodos, tipo)
    except OverflowError:
        st.error("Con estos valores, el monto excede el rango numérico disponible.")
        return
    if not all(math.isfinite(saldo) for saldo in saldos):
        st.error("Con estos valores, el monto excede el rango numérico disponible.")
        return
    monto_final = saldos[-1]
    interes_generado = monto_final - capital

    resultado_1, resultado_2 = st.columns(2)
    resultado_1.metric("Monto final", formato_cop(monto_final))
    resultado_2.metric("Interés generado", formato_cop(interes_generado))

    formula = r"M = C \times (1 + i \times n)" if tipo == "Interés simple" else r"M = C \times (1 + i)^{n}"
    st.markdown("#### Fórmula utilizada")
    st.latex(formula)
    st.caption(
        "C: capital inicial · i: tasa por período en decimal · "
        "n: número de períodos · M: monto final. "
        f"La tasa aplicada es {tasa / 100:.8g} en decimal. "
        "El interés generado es M − C."
    )

    datos = pd.DataFrame({"Período": range(periodos + 1), "Saldo (COP)": saldos})
    st.markdown("#### Evolución del capital")
    grafica = px.line(
        datos,
        x="Período",
        y="Saldo (COP)",
        markers=True,
        title=f"{tipo}: saldo al final de cada período",
        labels={"Saldo (COP)": "Saldo (COP)"},
        template="plotly_dark",
    )
    grafica.update_traces(hovertemplate="Período %{x}<br>Saldo: $%{y:,.2f} COP<extra></extra>")
    grafica.update_layout(hovermode="x unified", margin={"l": 20, "r": 20, "t": 55, "b": 20})
    st.plotly_chart(grafica, use_container_width=True)

    st.markdown("#### Saldo por período")
    tabla = datos.copy()
    tabla["Saldo (COP)"] = tabla["Saldo (COP)"].map(formato_cop)
    st.dataframe(tabla, use_container_width=True, hide_index=True)
