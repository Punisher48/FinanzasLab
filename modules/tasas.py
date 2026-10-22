"""Conversiones de tasas financieras y cálculo de rentabilidad."""

import math

import streamlit as st


def efectiva_anual_desde_periodica(tasa_periodica_porcentaje: float, periodos_por_anio: int) -> float:
    """Convierte una tasa efectiva periódica (en %) a efectiva anual (en %)."""
    _validar_periodos(periodos_por_anio)
    tasa = _tasa_decimal_valida(tasa_periodica_porcentaje, "La tasa periódica")
    if tasa <= -1:
        raise ValueError("La tasa efectiva periódica debe ser mayor que -100%.")
    return _porcentaje_finito((_potencia(1 + tasa, periodos_por_anio) - 1) * 100)


def periodica_desde_efectiva_anual(tasa_anual_porcentaje: float, periodos_por_anio: int) -> float:
    """Convierte una tasa efectiva anual (en %) a efectiva periódica (en %)."""
    _validar_periodos(periodos_por_anio)
    tasa = _tasa_decimal_valida(tasa_anual_porcentaje, "La tasa efectiva anual")
    if tasa <= -1:
        raise ValueError("La tasa efectiva anual debe ser mayor que -100%.")
    return _porcentaje_finito((_potencia(1 + tasa, 1 / periodos_por_anio) - 1) * 100)


def efectiva_anual_desde_nominal(tasa_nominal_porcentaje: float, periodos_por_anio: int) -> float:
    """Convierte una tasa nominal anual convertible m veces al año a EA, en %."""
    _validar_periodos(periodos_por_anio)
    nominal = _tasa_decimal_valida(tasa_nominal_porcentaje, "La tasa nominal anual")
    tasa_periodica = nominal / periodos_por_anio
    if tasa_periodica <= -1:
        raise ValueError(
            "La tasa nominal no es coherente: la tasa periódica j/m debe ser mayor que -100%."
        )
    return _porcentaje_finito((_potencia(1 + tasa_periodica, periodos_por_anio) - 1) * 100)


def rentabilidad_porcentual(valor_inicial: float, valor_final: float) -> float:
    """Calcula la rentabilidad del período como porcentaje."""
    inicial = _valor_finito(valor_inicial, "El valor inicial")
    final = _valor_finito(valor_final, "El valor final")
    if inicial <= 0:
        raise ValueError("El valor inicial debe ser mayor que cero para calcular la rentabilidad.")
    if final < 0:
        raise ValueError("El valor final no puede ser negativo.")
    return (final - inicial) / inicial * 100


def _valor_finito(valor: float, nombre: str) -> float:
    try:
        numero = float(valor)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{nombre} debe ser un número válido.") from error
    if not math.isfinite(numero):
        raise ValueError(f"{nombre} debe ser un número finito.")
    return numero


def _tasa_decimal_valida(porcentaje: float, nombre: str) -> float:
    return _valor_finito(porcentaje, nombre) / 100


def _porcentaje_finito(resultado: float) -> float:
    if not math.isfinite(resultado):
        raise ValueError("El resultado excede el rango numérico disponible.")
    return resultado


def _potencia(base: float, exponente: float) -> float:
    try:
        return base ** exponente
    except OverflowError as error:
        raise ValueError("El resultado excede el rango numérico disponible.") from error


def _validar_periodos(periodos_por_anio: int) -> None:
    if isinstance(periodos_por_anio, bool) or not isinstance(periodos_por_anio, int) or periodos_por_anio < 1:
        raise ValueError("La cantidad de períodos por año debe ser un entero positivo.")


def _mostrar_resultado(etiqueta: str, resultado: float, formula: str, variables: str) -> None:
    st.metric(etiqueta, f"{resultado:,.6f}%")
    st.latex(formula)
    st.caption(variables)


def render():
    st.title("Tasas y rentabilidad")
    st.write(
        "Convierte tasas financieras y calcula la rentabilidad de una inversión. "
        "Las tasas introducidas se expresan en porcentaje y se convierten a decimal antes del cálculo."
    )
    st.info(
        "Las tasas deben ser financieramente coherentes con la conversión elegida: "
        "las tasas efectivas no pueden ser menores o iguales a −100%, y para una tasa nominal "
        "la tasa periódica j/m debe ser mayor que −100%."
    )

    conversion_periodos = st.number_input(
        "Períodos por año (m)", min_value=1, max_value=3650, value=12, step=1,
        key="tasas_periodos_anio",
    )
    m = int(conversion_periodos)

    tab_periodica, tab_anual, tab_nominal, tab_rentabilidad = st.tabs(
        ["Periódica → anual", "Anual → periódica", "Nominal → efectiva anual", "Rentabilidad"]
    )

    with tab_periodica:
        with st.form("form_tasa_periodica_anual"):
            tasa = st.number_input("Tasa efectiva periódica (%)", value=1.0, step=0.1, format="%.6f")
            enviar = st.form_submit_button("Convertir")
        if enviar:
            try:
                resultado = efectiva_anual_desde_periodica(tasa, m)
                _mostrar_resultado(
                    "Tasa efectiva anual",
                    resultado,
                    r"EA = (1 + i)^{m} - 1",
                    "i: tasa efectiva periódica en decimal · m: períodos por año · EA: tasa efectiva anual en decimal.",
                )
            except ValueError as error:
                st.error(str(error))

    with tab_anual:
        with st.form("form_tasa_anual_periodica"):
            tasa = st.number_input("Tasa efectiva anual (%)", value=12.0, step=0.5, format="%.6f")
            enviar = st.form_submit_button("Convertir")
        if enviar:
            try:
                resultado = periodica_desde_efectiva_anual(tasa, m)
                _mostrar_resultado(
                    "Tasa efectiva periódica",
                    resultado,
                    r"i = (1 + EA)^{\frac{1}{m}} - 1",
                    "EA: tasa efectiva anual en decimal · m: períodos por año · i: tasa efectiva por período en decimal.",
                )
            except ValueError as error:
                st.error(str(error))

    with tab_nominal:
        with st.form("form_tasa_nominal_efectiva"):
            tasa = st.number_input("Tasa nominal anual (%)", value=12.0, step=0.5, format="%.6f")
            enviar = st.form_submit_button("Convertir")
        if enviar:
            try:
                resultado = efectiva_anual_desde_nominal(tasa, m)
                _mostrar_resultado(
                    "Tasa efectiva anual",
                    resultado,
                    r"EA = \left(1 + \frac{j}{m}\right)^{m} - 1",
                    "j: tasa nominal anual en decimal · m: períodos de capitalización por año · EA: tasa efectiva anual en decimal.",
                )
            except ValueError as error:
                st.error(str(error))

    with tab_rentabilidad:
        with st.form("form_rentabilidad"):
            columna_inicial, columna_final = st.columns(2)
            with columna_inicial:
                valor_inicial = st.number_input("Valor inicial de la inversión", min_value=0.0, value=1_000_000.0, step=100_000.0)
            with columna_final:
                valor_final = st.number_input("Valor final de la inversión", min_value=0.0, value=1_120_000.0, step=100_000.0)
            enviar = st.form_submit_button("Calcular rentabilidad")
        if enviar:
            try:
                resultado = rentabilidad_porcentual(valor_inicial, valor_final)
                _mostrar_resultado(
                    "Rentabilidad del período",
                    resultado,
                    r"R = \frac{V_f - V_i}{V_i}",
                    "Vᵢ: valor inicial · V𝒻: valor final · R: rentabilidad del período en decimal.",
                )
            except ValueError as error:
                st.error(str(error))
