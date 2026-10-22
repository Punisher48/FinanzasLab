"""Cálculos de series uniformes vencidas."""

import math

import pandas as pd
import plotly.express as px
import streamlit as st


def valor_futuro_serie(cuota: float, tasa_porcentaje: float, periodos: int) -> float:
    """Valor futuro de una serie uniforme vencida."""
    cuota, tasa, periodos = _validar_serie(cuota, tasa_porcentaje, periodos)
    if tasa == 0:
        return cuota * periodos
    return cuota * (((1 + tasa) ** periodos - 1) / tasa)


def valor_presente_serie(cuota: float, tasa_porcentaje: float, periodos: int) -> float:
    """Valor presente de una serie uniforme vencida."""
    cuota, tasa, periodos = _validar_serie(cuota, tasa_porcentaje, periodos)
    if tasa == 0:
        return cuota * periodos
    return cuota * ((1 - (1 + tasa) ** (-periodos)) / tasa)


def cuota_para_valor_futuro(valor_futuro: float, tasa_porcentaje: float, periodos: int) -> float:
    """Cuota vencida necesaria para alcanzar un valor futuro objetivo."""
    objetivo = _valor_no_negativo(valor_futuro, "El valor futuro")
    tasa, periodos = _validar_tasa_periodos(tasa_porcentaje, periodos)
    if tasa == 0:
        return objetivo / periodos
    return objetivo * tasa / ((1 + tasa) ** periodos - 1)


def cuota_para_prestamo(valor_presente: float, tasa_porcentaje: float, periodos: int) -> float:
    """Cuota vencida constante para amortizar un préstamo."""
    principal = _valor_no_negativo(valor_presente, "El valor presente")
    tasa, periodos = _validar_tasa_periodos(tasa_porcentaje, periodos)
    if tasa == 0:
        return principal / periodos
    return principal * tasa / (1 - (1 + tasa) ** (-periodos))


def _validar_serie(cuota: float, tasa_porcentaje: float, periodos: int):
    importe = _valor_no_negativo(cuota, "La cuota")
    tasa, periodos = _validar_tasa_periodos(tasa_porcentaje, periodos)
    return importe, tasa, periodos


def _validar_tasa_periodos(tasa_porcentaje: float, periodos: int):
    tasa_pct = _valor_finito(tasa_porcentaje, "La tasa")
    tasa = tasa_pct / 100
    if tasa <= -1:
        raise ValueError("La tasa efectiva por período debe ser mayor que −100%.")
    if isinstance(periodos, bool) or not isinstance(periodos, int) or periodos < 1:
        raise ValueError("El número de períodos debe ser un entero igual o mayor que uno.")
    return tasa, periodos


def _valor_no_negativo(valor: float, nombre: str) -> float:
    numero = _valor_finito(valor, nombre)
    if numero < 0:
        raise ValueError(f"{nombre} no puede ser negativo.")
    return numero


def _valor_finito(valor: float, nombre: str) -> float:
    try:
        numero = float(valor)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{nombre} debe ser un número válido.") from error
    if not math.isfinite(numero):
        raise ValueError(f"{nombre} debe ser un valor finito.")
    return numero


def _cop(valor: float) -> str:
    return f"${valor:,.2f} COP".replace(",", "X").replace(".", ",").replace("X", ".")


def _verificar_resultados(valores):
    if not all(math.isfinite(valor) for valor in valores):
        raise ValueError("El resultado excede el rango numérico disponible.")


def _datos_flujo(operacion: str, cuota: float, tasa: float, periodos: int, saldo_inicial: float = 0.0):
    """Construye filas sin redondeo para el flujo y su saldo acumulado."""
    filas = [{"Período": 0, "Flujo (COP)": 0.0, "Interés (COP)": 0.0, "Saldo (COP)": saldo_inicial}]
    saldo = saldo_inicial
    for periodo in range(1, periodos + 1):
        interes = saldo * tasa
        if operacion == "préstamo":
            saldo = saldo + interes - cuota
            flujo = -cuota
        elif operacion == "presente":
            saldo += cuota / (1 + tasa) ** periodo
            interes = 0.0
            flujo = cuota
        else:
            saldo = saldo * (1 + tasa) + cuota
            flujo = cuota
        if abs(saldo) < 1e-8:
            saldo = 0.0
        filas.append({"Período": periodo, "Flujo (COP)": flujo, "Interés (COP)": interes, "Saldo (COP)": saldo})
    return pd.DataFrame(filas)


def render():
    st.title("Series uniformes")
    st.write(
        "Calcula equivalencias y cuotas para una serie de pagos iguales realizados al final de cada período. "
        "Estas fórmulas corresponden a series vencidas; las series anticipadas no están incluidas."
    )

    frecuencia = st.selectbox(
        "Frecuencia de los pagos",
        ["Mensual", "Bimestral", "Trimestral", "Cuatrimestral", "Semestral", "Anual", "Otra frecuencia"],
        key="series_frecuencia",
    )
    if frecuencia == "Otra frecuencia":
        frecuencia = st.text_input("Describe la frecuencia", value="Por período")
    st.caption(
        f"Frecuencia seleccionada: {frecuencia}. La tasa ingresada debe ser efectiva por período y "
        "el número de períodos debe contar pagos en esa misma frecuencia."
    )

    operacion = st.selectbox(
        "Cálculo",
        [
            "Valor futuro de una serie",
            "Valor presente de una serie",
            "Cuota para alcanzar un valor futuro",
            "Cuota para pagar un préstamo",
        ],
        key="series_operacion",
    )

    with st.form("formulario_series_uniformes"):
        columna_1, columna_2, columna_3 = st.columns(3)
        with columna_1:
            if operacion in ("Valor futuro de una serie", "Valor presente de una serie"):
                importe = st.number_input("Cuota periódica (COP)", min_value=0.0, value=100_000.0, step=10_000.0, format="%.2f")
            else:
                importe = st.number_input(
                    "Valor futuro objetivo (COP)" if operacion == "Cuota para alcanzar un valor futuro" else "Valor presente del préstamo (COP)",
                    min_value=0.0, value=1_000_000.0, step=100_000.0, format="%.2f",
                )
        with columna_2:
            tasa_pct = st.number_input("Tasa efectiva por período (%)", value=1.0, step=0.25, format="%.6f")
        with columna_3:
            periodos = st.number_input("Número de períodos (n)", min_value=1, max_value=10000, value=12, step=1, format="%d")
        enviar = st.form_submit_button("Calcular", type="primary")

    if not enviar:
        return

    try:
        if isinstance(periodos, bool) or int(periodos) != periodos or periodos < 1:
            raise ValueError("El número de períodos debe ser un entero igual o mayor que uno.")
        periodos = int(periodos)
        tasa_pct = _valor_finito(tasa_pct, "La tasa")
        tasa = tasa_pct / 100
        if tasa <= -1:
            raise ValueError("La tasa efectiva por período debe ser mayor que −100%.")
        importe = _valor_no_negativo(importe, "El importe")

        if operacion == "Valor futuro de una serie":
            cuota = importe
            resultado = valor_futuro_serie(cuota, tasa_pct, periodos)
            etiqueta = "Valor futuro"
            formula = r"VF = A \times \frac{(1+i)^{n}-1}{i}"
            explicacion = "A: cuota por período · i: tasa efectiva por período en decimal · n: número de pagos · VF: valor acumulado al final del período n."
            flujo_tipo, saldo_inicial = "ahorro", 0.0
        elif operacion == "Valor presente de una serie":
            cuota = importe
            resultado = valor_presente_serie(cuota, tasa_pct, periodos)
            etiqueta = "Valor presente"
            formula = r"VP = A \times \frac{1-(1+i)^{-n}}{i}"
            explicacion = "A: cuota por período · i: tasa efectiva por período en decimal · n: número de pagos · VP: valor equivalente en el período cero."
            flujo_tipo, saldo_inicial = "presente", 0.0
        elif operacion == "Cuota para alcanzar un valor futuro":
            resultado = cuota_para_valor_futuro(importe, tasa_pct, periodos)
            cuota = resultado
            etiqueta = "Cuota periódica requerida"
            formula = r"A = VF \times \frac{i}{(1+i)^{n}-1}"
            explicacion = "VF: valor futuro objetivo · A: cuota al final de cada período · i: tasa efectiva por período en decimal · n: número de pagos."
            flujo_tipo, saldo_inicial = "ahorro", 0.0
        else:
            resultado = cuota_para_prestamo(importe, tasa_pct, periodos)
            cuota = resultado
            etiqueta = "Cuota periódica del préstamo"
            formula = r"A = VP \times \frac{i}{1-(1+i)^{-n}}"
            explicacion = "VP: valor presente del préstamo · A: cuota al final de cada período · i: tasa efectiva por período en decimal · n: número de cuotas."
            flujo_tipo, saldo_inicial = "préstamo", importe

        _verificar_resultados([resultado, cuota])
        datos = _datos_flujo(flujo_tipo, cuota, tasa, periodos, saldo_inicial)
        _verificar_resultados(datos["Saldo (COP)"].tolist())
    except (ValueError, OverflowError) as error:
        st.error(str(error) or "El resultado excede el rango numérico disponible.")
        return

    st.markdown("#### Datos ingresados")
    nombre_importe = {
        "Valor futuro de una serie": "Cuota periódica",
        "Valor presente de una serie": "Cuota periódica",
        "Cuota para alcanzar un valor futuro": "Valor futuro objetivo",
        "Cuota para pagar un préstamo": "Valor presente del préstamo",
    }[operacion]
    datos_fila_1 = st.columns(3)
    datos_fila_1[0].metric("Operación", operacion)
    datos_fila_1[1].metric(nombre_importe, _cop(importe))
    datos_fila_1[2].metric("Frecuencia", frecuencia)
    datos_fila_2 = st.columns(2)
    datos_fila_2[0].metric("Tasa efectiva por período", f"{tasa_pct:.6f}% ({tasa:.8g} decimal)")
    datos_fila_2[1].metric("Número de períodos", str(periodos))
    st.metric(etiqueta, _cop(resultado))
    st.markdown("#### Fórmula utilizada")
    st.latex(formula)
    st.caption(explicacion + (" Cuando i = 0 se utilizan los límites: VF = A·n, VP = A·n y A = VF/n o VP/n.") )

    st.markdown("#### Flujo y saldo por período")
    st.caption("El saldo mostrado se acumula período a período; en préstamos representa el saldo pendiente después de cada cuota.")
    st.dataframe(datos.style.format({col: _cop for col in ["Flujo (COP)", "Interés (COP)", "Saldo (COP)"]}), width="stretch", hide_index=True)

    titulo = {
        "ahorro": "Saldo del ahorro por período",
        "presente": "Valor presente acumulado por período",
        "préstamo": "Saldo pendiente del préstamo",
    }[flujo_tipo]
    grafica = px.line(
        datos,
        x="Período",
        y="Saldo (COP)",
        markers=True,
        title=titulo,
        template="plotly_dark",
    )
    grafica.update_traces(hovertemplate="Período %{x}<br>Saldo: $%{y:,.2f} COP<extra></extra>")
    grafica.update_layout(hovermode="x unified", margin={"l": 20, "r": 20, "t": 55, "b": 20})
    st.plotly_chart(grafica, width="stretch")
