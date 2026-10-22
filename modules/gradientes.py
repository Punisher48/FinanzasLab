"""Valor presente de gradientes aritméticos y geométricos vencidos."""

import math

import pandas as pd
import plotly.express as px
import streamlit as st


MAX_PERIODOS = 1000


def calcular_gradiente_aritmetico(
    primer_pago: float,
    incremento: float,
    tasa_descuento_porcentaje: float,
    periodos: int,
) -> tuple[list[float], float]:
    """Construye los pagos y suma su valor presente; los importes deben ser no negativos."""
    primer_pago = _no_negativo(primer_pago, "El primer pago")
    incremento = _finito(incremento, "El incremento")
    tasa = _tasa_descuento(tasa_descuento_porcentaje)
    periodos = _validar_periodos(periodos)

    pagos = [primer_pago + periodo * incremento for periodo in range(periodos)]
    if any(not math.isfinite(pago) or pago < 0 for pago in pagos):
        raise ValueError("El incremento produce pagos negativos o fuera del rango numérico.")
    return pagos, _valor_presente(pagos, tasa)


def calcular_gradiente_geometrico(
    primer_pago: float,
    crecimiento_porcentaje: float,
    tasa_descuento_porcentaje: float,
    periodos: int,
) -> tuple[list[float], float]:
    """Construye pagos con crecimiento geométrico y suma su valor presente."""
    primer_pago = _no_negativo(primer_pago, "El primer pago")
    crecimiento = _finito(crecimiento_porcentaje, "La tasa de crecimiento") / 100
    if crecimiento < -1:
        raise ValueError("La tasa de crecimiento debe ser mayor o igual que −100% para mantener pagos no negativos.")
    tasa = _tasa_descuento(tasa_descuento_porcentaje)
    periodos = _validar_periodos(periodos)

    pagos = [primer_pago * (1 + crecimiento) ** periodo for periodo in range(periodos)]
    if any(not math.isfinite(pago) or pago < 0 for pago in pagos):
        raise ValueError("La tasa de crecimiento produce pagos fuera del rango numérico.")
    return pagos, _valor_presente(pagos, tasa)


def _valor_presente(pagos: list[float], tasa: float) -> float:
    try:
        descontados = [pago / (1 + tasa) ** periodo for periodo, pago in enumerate(pagos, start=1)]
    except OverflowError as error:
        raise ValueError("El valor presente excede el rango numérico disponible.") from error
    if not all(math.isfinite(valor) for valor in descontados):
        raise ValueError("El valor presente excede el rango numérico disponible.")
    presente = math.fsum(descontados)
    if not math.isfinite(presente):
        raise ValueError("El valor presente excede el rango numérico disponible.")
    return presente


def _validar_periodos(periodos: int) -> int:
    if isinstance(periodos, bool) or not isinstance(periodos, int) or not 1 <= periodos <= MAX_PERIODOS:
        raise ValueError(f"El número de períodos debe ser un entero entre 1 y {MAX_PERIODOS}.")
    return periodos


def _finito(valor: float, nombre: str) -> float:
    try:
        numero = float(valor)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{nombre} debe ser un número válido.") from error
    if not math.isfinite(numero):
        raise ValueError(f"{nombre} debe ser un valor finito.")
    return numero


def _no_negativo(valor: float, nombre: str) -> float:
    numero = _finito(valor, nombre)
    if numero < 0:
        raise ValueError(f"{nombre} no puede ser negativo.")
    return numero


def _tasa_descuento(porcentaje: float) -> float:
    tasa = _finito(porcentaje, "La tasa efectiva de descuento") / 100
    if tasa <= -1:
        raise ValueError("La tasa efectiva de descuento debe ser mayor que −100%.")
    return tasa


def _cop(valor: float) -> str:
    return f"${valor:,.2f} COP".replace(",", "X").replace(".", ",").replace("X", ".")


def render():
    st.title("Gradientes")
    st.write(
        "Calcula el valor presente de flujos que cambian por un incremento fijo o una tasa de crecimiento. "
        "Los pagos ocurren al final de cada período: el primer pago es en t=1."
    )

    tipo = st.radio(
        "Tipo de gradiente",
        ["Aritmético", "Geométrico"],
        horizontal=True,
        key="gradientes_tipo",
    )
    clave_cambio = (
        "gradientes_incremento_aritmetico"
        if tipo == "Aritmético"
        else "gradientes_crecimiento_geometrico"
    )
    with st.form("formulario_gradientes"):
        columna_pago, columna_cambio, columna_tasa, columna_periodos = st.columns(4)
        with columna_pago:
            primer_pago = st.number_input(
                "Primer pago (COP)", min_value=0.0, value=100_000.0,
                step=10_000.0, format="%.2f", key="gradientes_primer_pago",
            )
        with columna_cambio:
            cambio = st.number_input(
                "Incremento fijo por período (COP)" if tipo == "Aritmético" else "Crecimiento de los pagos (%)",
                value=10_000.0 if tipo == "Aritmético" else 2.0,
                step=1_000.0 if tipo == "Aritmético" else 0.5,
                format="%.4f",
                key=clave_cambio,
            )
        with columna_tasa:
            tasa_pct = st.number_input(
                "Tasa efectiva de descuento por período (%)",
                value=1.0, step=0.25, format="%.6f", key="gradientes_tasa",
            )
        with columna_periodos:
            periodos = st.number_input(
                "Número de períodos", min_value=1, max_value=MAX_PERIODOS,
                value=12, step=1, format="%d", key="gradientes_periodos",
            )
        calcular = st.form_submit_button("Calcular valor presente", type="primary")

    st.caption(
        "La tasa de descuento y el número de períodos deben usar la misma unidad temporal. "
        "En el gradiente aritmético, el incremento se aplica a partir del segundo pago. "
        "Se aceptan únicamente flujos de pago no negativos."
    )
    if not calcular:
        return

    try:
        if isinstance(periodos, bool) or int(periodos) != periodos:
            raise ValueError(f"El número de períodos debe ser un entero entre 1 y {MAX_PERIODOS}.")
        periodos = _validar_periodos(int(periodos))
        if tipo == "Aritmético":
            pagos, valor_presente = calcular_gradiente_aritmetico(primer_pago, cambio, tasa_pct, periodos)
            formula_pago = r"\displaystyle P_t = A_1 + (t - 1)G"
            etiqueta_cambio = "Incremento fijo G"
            valor_cambio = _cop(cambio)
        else:
            pagos, valor_presente = calcular_gradiente_geometrico(primer_pago, cambio, tasa_pct, periodos)
            formula_pago = r"\displaystyle P_t = A_1(1+g)^{t-1}"
            etiqueta_cambio = "Crecimiento g"
            valor_cambio = f"{cambio:.6f}% por período"

        tasa = tasa_pct / 100
        flujos = [pago / (1 + tasa) ** periodo for periodo, pago in enumerate(pagos, start=1)]
        if not all(math.isfinite(flujo) for flujo in flujos):
            raise ValueError("Los flujos descontados exceden el rango numérico disponible.")
        datos = pd.DataFrame({
            "Período": range(1, periodos + 1),
            "Pago (COP)": pagos,
            "Factor de descuento": [(1 + tasa) ** -periodo for periodo in range(1, periodos + 1)],
            "Valor presente del pago (COP)": flujos,
        })
    except (ValueError, OverflowError) as error:
        st.error(str(error) or "El resultado excede el rango numérico disponible.")
        return

    st.markdown("#### Datos ingresados")
    datos_fila_1 = st.columns(3)
    datos_fila_1[0].metric("Tipo de gradiente", tipo)
    datos_fila_1[1].metric("Primer pago A₁", _cop(primer_pago))
    datos_fila_1[2].metric(etiqueta_cambio, valor_cambio)
    datos_fila_2 = st.columns(2)
    datos_fila_2[0].metric("Tasa efectiva de descuento i", f"{tasa_pct:.6f}%")
    datos_fila_2[1].metric("Número de períodos n", str(periodos))
    st.metric("Valor presente de los flujos", _cop(valor_presente))

    st.markdown("#### Fórmulas utilizadas")
    st.latex(formula_pago)
    st.latex(r"\displaystyle VP = \sum_{t=1}^{n} \frac{P_t}{\left(1+i\right)^{t}}")
    st.caption(
        "Pₜ: pago en el período t · A₁: primer pago · G: incremento fijo · g: crecimiento por período en decimal · "
        "i: tasa efectiva de descuento por período en decimal · n: número de períodos. "
        "El VP se obtiene sumando cada pago descontado, también cuando i = 0."
    )

    st.markdown("#### Pagos y valores presentes por período")
    st.dataframe(
        datos.style.format({
            "Pago (COP)": _cop,
            "Factor de descuento": "{:.8f}",
            "Valor presente del pago (COP)": _cop,
        }),
        width="stretch",
        hide_index=True,
    )

    grafica = px.line(
        datos,
        x="Período",
        y="Pago (COP)",
        markers=True,
        title=f"Flujos del gradiente {tipo.lower()}",
        template="plotly_dark",
    )
    grafica.update_traces(hovertemplate="Período %{x}<br>Pago: $%{y:,.2f} COP<extra></extra>")
    grafica.update_layout(hovermode="x unified", margin={"l": 20, "r": 20, "t": 55, "b": 20})
    st.plotly_chart(grafica, width="stretch")
