"""Tabla de amortización de préstamos con sistema francés."""

import math

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.series_uniformes import cuota_para_prestamo


MAX_CUOTAS = 1000


def generar_tabla_amortizacion(prestamo: float, tasa_porcentaje: float, numero_cuotas: int) -> pd.DataFrame:
    """Construye una tabla francesa conservando la precisión hasta su presentación."""
    prestamo = _finito(prestamo, "El monto del préstamo")
    if prestamo <= 0:
        raise ValueError("El monto del préstamo debe ser mayor que cero.")
    tasa_pct = _finito(tasa_porcentaje, "La tasa efectiva por período")
    if tasa_pct <= -100:
        raise ValueError("La tasa efectiva por período debe ser mayor que −100%.")
    if (
        isinstance(numero_cuotas, bool)
        or not isinstance(numero_cuotas, int)
        or not 1 <= numero_cuotas <= MAX_CUOTAS
    ):
        raise ValueError(f"El número de cuotas debe ser un entero entre 1 y {MAX_CUOTAS}.")

    tasa = tasa_pct / 100
    try:
        cuota_fija = cuota_para_prestamo(prestamo, tasa_pct, numero_cuotas)
    except OverflowError as error:
        raise ValueError("La cuota calculada excede el rango numérico disponible.") from error
    if not math.isfinite(cuota_fija):
        raise ValueError("La cuota calculada excede el rango numérico disponible.")

    filas = []
    saldo = prestamo
    intereses_totales = 0.0
    for periodo in range(1, numero_cuotas + 1):
        saldo_inicial = saldo
        interes = saldo_inicial * tasa
        abono = cuota_fija - interes
        cuota_periodo = cuota_fija
        saldo_final = saldo_inicial - abono

        if periodo == numero_cuotas:
            residuo = saldo_final
            tolerancia = max(0.01, prestamo * 1e-10)
            if abs(residuo) > tolerancia:
                raise ValueError(
                    "La tabla deja un saldo final significativo; revise la tasa y el número de cuotas."
                )
            # Ajuste limitado al residuo de coma flotante en la última cuota.
            cuota_periodo = saldo_inicial + interes
            abono = saldo_inicial
            saldo_final = 0.0

        valores = [saldo_inicial, cuota_periodo, interes, abono, saldo_final]
        if not all(math.isfinite(valor) for valor in valores):
            raise ValueError("La tabla excede el rango numérico disponible.")
        filas.append({
            "Período": periodo,
            "Saldo inicial (COP)": saldo_inicial,
            "Cuota (COP)": cuota_periodo,
            "Interés (COP)": interes,
            "Abono a capital (COP)": abono,
            "Saldo final (COP)": saldo_final,
        })
        saldo = saldo_final
        intereses_totales += interes

    if not math.isfinite(intereses_totales):
        raise ValueError("El total de intereses excede el rango numérico disponible.")
    return pd.DataFrame(filas)


def _finito(valor: float, nombre: str) -> float:
    try:
        numero = float(valor)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{nombre} debe ser un número válido.") from error
    if not math.isfinite(numero):
        raise ValueError(f"{nombre} debe ser un valor finito.")
    return numero


def _cop(valor: float) -> str:
    return f"${valor:,.2f} COP".replace(",", "X").replace(".", ",").replace("X", ".")


def render():
    st.title("Tablas de amortización")
    st.write(
        "Calcula el pago de un préstamo mediante el sistema francés, con cuotas periódicas constantes. "
        "Se supone una tasa efectiva por período y pagos al final de cada período."
    )

    frecuencia = st.selectbox(
        "Frecuencia de pago",
        ["Mensual", "Bimestral", "Trimestral", "Cuatrimestral", "Semestral", "Anual", "Otra frecuencia"],
        key="amortizacion_frecuencia",
    )
    if frecuencia == "Otra frecuencia":
        frecuencia = st.text_input("Describe la frecuencia", value="Por período")
    st.caption("La tasa efectiva por período y el número de cuotas deben corresponder a la frecuencia seleccionada.")

    with st.form("formulario_amortizacion"):
        columna_prestamo, columna_tasa, columna_cuotas = st.columns(3)
        with columna_prestamo:
            prestamo = st.number_input(
                "Monto del préstamo (COP)", min_value=0.01, value=10_000_000.0,
                step=500_000.0, format="%.2f", key="amortizacion_prestamo",
            )
        with columna_tasa:
            tasa_pct = st.number_input(
                "Tasa efectiva por período (%)", value=1.0, step=0.25,
                format="%.6f", key="amortizacion_tasa",
            )
        with columna_cuotas:
            numero_cuotas = st.number_input(
                "Número de cuotas", min_value=1, max_value=MAX_CUOTAS,
                value=12, step=1, format="%d", key="amortizacion_numero_cuotas",
            )
        calcular = st.form_submit_button("Generar tabla", type="primary")

    if not calcular:
        return

    try:
        if isinstance(numero_cuotas, bool) or int(numero_cuotas) != numero_cuotas:
            raise ValueError(f"El número de cuotas debe ser un entero entre 1 y {MAX_CUOTAS}.")
        numero_cuotas = int(numero_cuotas)
        datos = generar_tabla_amortizacion(prestamo, tasa_pct, numero_cuotas)
    except (ValueError, OverflowError) as error:
        st.error(str(error) or "No fue posible calcular la amortización con esos datos.")
        return

    tasa = tasa_pct / 100
    cuota_fija = cuota_para_prestamo(prestamo, tasa_pct, numero_cuotas)
    total_pagado = float(datos["Cuota (COP)"].sum())
    total_intereses = float(datos["Interés (COP)"].sum())
    saldo_pendiente = float(datos["Saldo final (COP)"].iloc[-1])

    st.markdown("#### Datos del préstamo")
    datos_fila_1 = st.columns(3)
    datos_fila_1[0].metric("Monto del préstamo", _cop(prestamo))
    datos_fila_1[1].metric("Frecuencia", frecuencia)
    datos_fila_1[2].metric("Tasa efectiva por período", f"{tasa_pct:.6f}% ({tasa:.8g} decimal)")
    datos_fila_2 = st.columns(2)
    datos_fila_2[0].metric("Número de cuotas", str(numero_cuotas))
    datos_fila_2[1].metric("Cuota fija calculada", _cop(cuota_fija))
    metrica_pagado, metrica_intereses, metrica_saldo = st.columns(3)
    metrica_pagado.metric("Total pagado", _cop(total_pagado))
    metrica_intereses.metric("Total de intereses", _cop(total_intereses))
    metrica_saldo.metric("Saldo pendiente", _cop(saldo_pendiente))

    st.markdown("#### Fórmulas utilizadas")
    if tasa == 0:
        st.latex(r"A = \frac{P}{n}")
        st.caption("Como i = 0, la cuota es el préstamo dividido entre el número de cuotas.")
    else:
        st.latex(r"A = P \times \frac{i}{1-(1+i)^{-n}}")
    st.latex(r"I_t = S_{t-1} \times i")
    st.latex(r"K_t = A - I_t")
    st.latex(r"S_t = S_{t-1} - K_t")
    st.caption(
        "P: préstamo inicial · i: tasa efectiva por período en decimal · n: número de cuotas · "
        "A: cuota · Iₜ: interés del período · Kₜ: abono a capital · Sₜ: saldo al final del período t."
    )

    st.markdown("#### Tabla de amortización")
    st.dataframe(
        datos.style.format({col: _cop for col in datos.columns if col != "Período"}),
        width="stretch",
        hide_index=True,
    )

    saldo_plot = pd.concat([
        pd.DataFrame({"Período": [0], "Saldo (COP)": [prestamo]}),
        datos[["Período", "Saldo final (COP)"]].rename(columns={"Saldo final (COP)": "Saldo (COP)"}),
    ], ignore_index=True)
    grafica_saldo = px.line(
        saldo_plot,
        x="Período",
        y="Saldo (COP)",
        markers=True,
        title="Evolución del saldo pendiente",
        template="plotly_dark",
    )
    grafica_saldo.update_traces(hovertemplate="Período %{x}<br>Saldo: $%{y:,.2f} COP<extra></extra>")
    grafica_saldo.update_layout(hovermode="x unified", margin={"l": 20, "r": 20, "t": 55, "b": 20})
    st.plotly_chart(grafica_saldo, width="stretch")

    comparacion = datos.melt(
        id_vars="Período",
        value_vars=["Abono a capital (COP)", "Interés (COP)"],
        var_name="Componente",
        value_name="Monto (COP)",
    )
    grafica_componentes = px.bar(
        comparacion,
        x="Período",
        y="Monto (COP)",
        color="Componente",
        barmode="group",
        title="Composición de cada cuota",
        template="plotly_dark",
    )
    grafica_componentes.update_traces(hovertemplate="Período %{x}<br>%{fullData.name}: $%{y:,.2f} COP<extra></extra>")
    grafica_componentes.update_layout(margin={"l": 20, "r": 20, "t": 55, "b": 20})
    st.plotly_chart(grafica_componentes, width="stretch")
