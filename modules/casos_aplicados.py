"""Casos financieros ilustrativos basados en las funciones de FinanzasLab."""

import math

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.amortizacion import MAX_CUOTAS, generar_tabla_amortizacion
from modules.series_uniformes import valor_futuro_serie


def calcular_vpn(inversion_inicial: float, flujos_futuros: list[float], tasa_porcentaje: float) -> tuple[float, list[float]]:
    """Calcula VPN = suma de flujos futuros descontados menos inversión inicial."""
    inversion = _finito(inversion_inicial, "La inversión inicial")
    tasa_pct = _finito(tasa_porcentaje, "La tasa de descuento")
    if inversion <= 0:
        raise ValueError("La inversión inicial debe ser mayor que cero.")
    if tasa_pct <= -100:
        raise ValueError("La tasa efectiva de descuento debe ser mayor que −100%.")
    if not isinstance(flujos_futuros, (list, tuple)) or not 1 <= len(flujos_futuros) <= MAX_CUOTAS:
        raise ValueError(f"Debe ingresar entre 1 y {MAX_CUOTAS} flujos futuros.")

    tasa = tasa_pct / 100
    flujos = []
    try:
        for flujo in flujos_futuros:
            valor = _finito(flujo, "Cada ingreso futuro")
            if valor < 0:
                raise ValueError("Los ingresos futuros no pueden ser negativos en este caso.")
            flujos.append(valor)
        valores_presentes = [flujo / (1 + tasa) ** periodo for periodo, flujo in enumerate(flujos, start=1)]
    except OverflowError as error:
        raise ValueError("El valor presente neto excede el rango numérico disponible.") from error

    if not all(math.isfinite(valor) for valor in valores_presentes):
        raise ValueError("El valor presente neto excede el rango numérico disponible.")
    vpn = math.fsum(valores_presentes) - inversion
    if not math.isfinite(vpn):
        raise ValueError("El valor presente neto excede el rango numérico disponible.")
    return vpn, valores_presentes


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


def _tasa_valida(tasa_porcentaje: float) -> tuple[float, float]:
    tasa_pct = _finito(tasa_porcentaje, "La tasa efectiva por período")
    if tasa_pct <= -100:
        raise ValueError("La tasa efectiva por período debe ser mayor que −100%.")
    return tasa_pct, tasa_pct / 100


def _mostrar_sustitucion(texto: str) -> None:
    st.markdown("#### Sustitución numérica")
    st.latex(texto)
    st.caption("Los importes de la sustitución se expresan en pesos colombianos (COP).")


def _graficar(datos: pd.DataFrame, x: str, y: str, titulo: str):
    grafica = px.line(datos, x=x, y=y, markers=True, title=titulo, template="plotly_dark")
    grafica.update_layout(hovermode="x unified", margin={"l": 20, "r": 20, "t": 55, "b": 20})
    return grafica


def render():
    st.title("Casos financieros aplicados")
    st.write(
        "Explora tres situaciones académicas con valores modificables. Los datos iniciales son ilustrativos; "
        "no representan tasas de mercado ni constituyen asesoría financiera."
    )

    caso_ahorro, caso_compra, caso_inversion = st.tabs(
        ["Ahorro para una meta", "Compra financiada", "Evaluación de una inversión"]
    )

    with caso_ahorro:
        st.subheader("Ahorro para una meta")
        st.write("Proyecta depósitos iguales realizados al final de cada período y compáralos con una meta.")
        with st.form("caso_ahorro_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                deposito = st.number_input("Depósito periódico (COP)", min_value=0.0, value=250_000.0, step=25_000.0, format="%.2f", key="caso_ahorro_deposito")
            with c2:
                meta = st.number_input("Meta de ahorro (COP)", min_value=0.01, value=6_000_000.0, step=250_000.0, format="%.2f", key="caso_ahorro_meta")
            with c3:
                tasa_ahorro_input = st.number_input("Tasa efectiva por período (%)", value=0.5, step=0.1, format="%.6f", key="caso_ahorro_tasa")
            frecuencia_ahorro = st.selectbox("Frecuencia de los depósitos", ["Mensual", "Bimestral", "Trimestral", "Semestral", "Anual"], key="caso_ahorro_frecuencia")
            periodos_ahorro = st.number_input("Número de depósitos", min_value=1, max_value=MAX_CUOTAS, value=24, step=1, key="caso_ahorro_periodos")
            calcular_ahorro = st.form_submit_button("Evaluar ahorro", type="primary")

        st.caption("Se supone que cada depósito se realiza al final del período y gana la tasa efectiva indicada desde el siguiente período.")
        if calcular_ahorro:
            try:
                deposito = _finito(deposito, "El depósito periódico")
                meta = _finito(meta, "La meta de ahorro")
                if deposito < 0 or meta <= 0:
                    raise ValueError("El depósito no puede ser negativo y la meta debe ser mayor que cero.")
                tasa_pct, tasa = _tasa_valida(tasa_ahorro_input)
                if isinstance(periodos_ahorro, bool) or int(periodos_ahorro) != periodos_ahorro:
                    raise ValueError("El número de depósitos debe ser un entero positivo.")
                periodos_ahorro = int(periodos_ahorro)
                saldo_final = valor_futuro_serie(deposito, tasa_pct, periodos_ahorro)
                saldos = [valor_futuro_serie(deposito, tasa_pct, t) for t in range(1, periodos_ahorro + 1)]
                if not math.isfinite(saldo_final) or not all(math.isfinite(saldo) for saldo in saldos):
                    raise ValueError("El monto acumulado excede el rango numérico disponible.")
            except (ValueError, OverflowError) as error:
                st.error(str(error))
            else:
                diferencia = saldo_final - meta
                st.markdown("#### Datos ingresados")
                datos = st.columns(4)
                datos[0].metric("Depósito periódico", _cop(deposito))
                datos[1].metric("Meta", _cop(meta))
                datos[2].metric("Frecuencia", frecuencia_ahorro)
                datos[3].metric("Tasa / períodos", f"{tasa_pct:.4f}% · {periodos_ahorro}")
                st.latex(r"VF = A \times \frac{(1+i)^n-1}{i}")
                st.caption("A: depósito por período · i: tasa efectiva por período en decimal · n: número de depósitos · VF: monto acumulado.")
                if tasa == 0:
                    sustitucion = rf"VF = {deposito:.2f} \times {periodos_ahorro} = {saldo_final:.2f}"
                else:
                    sustitucion = rf"VF = {deposito:.2f} \times \frac{{(1+{tasa:.8g})^{{{periodos_ahorro}}}-1}}{{{tasa:.8g}}} = {saldo_final:.2f}"
                _mostrar_sustitucion(sustitucion)
                m1, m2 = st.columns(2)
                m1.metric("Ahorro acumulado", _cop(saldo_final))
                m2.metric("Diferencia frente a la meta", _cop(diferencia))
                st.info("Con estos supuestos, la meta se alcanza o supera." if diferencia >= 0 else "Con estos supuestos, el ahorro proyectado queda por debajo de la meta.")
                tabla_ahorro = pd.DataFrame({"Período": range(1, periodos_ahorro + 1), "Depósito (COP)": [deposito] * periodos_ahorro, "Saldo acumulado (COP)": saldos})
                st.dataframe(tabla_ahorro.style.format({"Depósito (COP)": _cop, "Saldo acumulado (COP)": _cop}), width="stretch", hide_index=True)
                st.plotly_chart(_graficar(tabla_ahorro, "Período", "Saldo acumulado (COP)", "Evolución del ahorro"), width="stretch")

    with caso_compra:
        st.subheader("Compra financiada")
        st.write("Estima la cuota fija y observa cómo se distribuye entre intereses y abono a capital.")
        with st.form("caso_compra_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                monto_compra = st.number_input("Monto financiado (COP)", min_value=0.01, value=24_000_000.0, step=500_000.0, format="%.2f", key="caso_compra_monto")
            with c2:
                tasa_compra_input = st.number_input("Tasa efectiva por cuota (%)", value=1.2, step=0.1, format="%.6f", key="caso_compra_tasa")
            with c3:
                cuotas_compra = st.number_input("Número de cuotas", min_value=1, max_value=MAX_CUOTAS, value=24, step=1, key="caso_compra_cuotas")
            frecuencia_compra = st.selectbox("Frecuencia de pago", ["Mensual", "Bimestral", "Trimestral", "Semestral", "Anual"], key="caso_compra_frecuencia")
            calcular_compra = st.form_submit_button("Analizar financiación", type="primary")

        st.caption("Sistema francés: tasa efectiva por cuota y pagos al final de cada período. El ejemplo no incorpora seguros, comisiones ni otros cargos.")
        if calcular_compra:
            try:
                tabla_prestamo = generar_tabla_amortizacion(monto_compra, tasa_compra_input, int(cuotas_compra))
                if int(cuotas_compra) != cuotas_compra:
                    raise ValueError("El número de cuotas debe ser un entero positivo.")
            except (ValueError, OverflowError) as error:
                st.error(str(error))
            else:
                total_pagado = float(tabla_prestamo["Cuota (COP)"].sum())
                total_intereses = float(tabla_prestamo["Interés (COP)"].sum())
                cuota = float(tabla_prestamo["Cuota (COP)"].iloc[0])
                st.markdown("#### Datos ingresados")
                datos = st.columns(4)
                datos[0].metric("Monto financiado", _cop(monto_compra))
                datos[1].metric("Frecuencia", frecuencia_compra)
                datos[2].metric("Tasa efectiva por cuota", f"{tasa_compra_input:.4f}%")
                datos[3].metric("Número de cuotas", str(int(cuotas_compra)))
                tasa_compra = tasa_compra_input / 100
                if tasa_compra == 0:
                    st.latex(r"A = P/n")
                    sustitucion = rf"A = {monto_compra:.2f}/{int(cuotas_compra)} = {cuota:.2f}"
                else:
                    st.latex(r"A = P \times \frac{i}{1-(1+i)^{-n}}")
                    sustitucion = rf"A = {monto_compra:.2f} \times \frac{{{tasa_compra:.8g}}}{{1-(1+{tasa_compra:.8g})^{{-{int(cuotas_compra)}}}}} = {cuota:.2f}"
                st.caption("P: monto financiado · i: tasa efectiva por cuota en decimal · n: número de cuotas · A: cuota fija vencida.")
                _mostrar_sustitucion(sustitucion)
                m1, m2, m3 = st.columns(3)
                m1.metric("Cuota periódica", _cop(cuota))
                m2.metric("Total pagado", _cop(total_pagado))
                m3.metric("Total de intereses", _cop(total_intereses))
                st.dataframe(tabla_prestamo.style.format({col: _cop for col in tabla_prestamo.columns if col != "Período"}), width="stretch", hide_index=True)
                st.plotly_chart(_graficar(tabla_prestamo, "Período", "Saldo final (COP)", "Saldo pendiente de la financiación"), width="stretch")

    with caso_inversion:
        st.subheader("Evaluación de una inversión")
        st.write("Compara una inversión inicial con los ingresos futuros descontados a una tasa elegida.")
        with st.form("caso_inversion_form"):
            inversion = st.number_input("Desembolso inicial (COP)", min_value=0.01, value=10_000_000.0, step=500_000.0, format="%.2f", key="caso_inversion_inicial")
            tasa_vpn_input = st.number_input("Tasa efectiva de descuento por período (%)", value=1.0, step=0.1, format="%.6f", key="caso_inversion_tasa")
            frecuencia_vpn = st.selectbox("Frecuencia de los flujos", ["Mensual", "Bimestral", "Trimestral", "Semestral", "Anual"], key="caso_inversion_frecuencia")
            numero_flujos = st.number_input("Número de ingresos futuros", min_value=1, max_value=20, value=4, step=1, key="caso_inversion_numero_flujos")
            ingresos = []
            columnas_ingresos = st.columns(2)
            for periodo in range(1, int(numero_flujos) + 1):
                with columnas_ingresos[(periodo - 1) % 2]:
                    ingresos.append(st.number_input(
                        f"Ingreso del período {periodo} (COP)", min_value=0.0,
                        value=3_000_000.0, step=250_000.0, format="%.2f",
                        key=f"caso_inversion_flujo_{periodo}",
                    ))
            calcular_inversion = st.form_submit_button("Calcular VPN", type="primary")

        st.caption("Convención de signos: el desembolso inicial se resta y los ingresos futuros se suman después de descontarlos. Se supone que cada ingreso ocurre al final de su período; la tasa debe corresponder a esa frecuencia.")
        if calcular_inversion:
            try:
                if int(numero_flujos) != numero_flujos:
                    raise ValueError("El número de ingresos futuros debe ser un entero positivo.")
                tasa_vpn_pct, tasa_vpn = _tasa_valida(tasa_vpn_input)
                vpn, valores_presentes = calcular_vpn(inversion, ingresos, tasa_vpn_pct)
                tabla_vpn = pd.DataFrame({
                    "Período": range(1, len(ingresos) + 1),
                    "Ingreso (COP)": ingresos,
                    "Factor de descuento": [(1 + tasa_vpn) ** -periodo for periodo in range(1, len(ingresos) + 1)],
                    "Valor presente (COP)": valores_presentes,
                })
            except (ValueError, OverflowError) as error:
                st.error(str(error))
            else:
                st.markdown("#### Datos ingresados")
                datos = st.columns(4)
                datos[0].metric("Desembolso inicial", _cop(inversion))
                datos[1].metric("Tasa de descuento", f"{tasa_vpn_pct:.4f}%")
                datos[2].metric("Frecuencia", frecuencia_vpn)
                datos[3].metric("Períodos", str(len(ingresos)))
                st.latex(r"VPN = -I_0 + \sum_{t=1}^{n} \frac{F_t}{(1+i)^t}")
                st.caption("I₀: desembolso inicial positivo, que se resta · Fₜ: ingreso futuro del período t · i: tasa efectiva por período en decimal · n: número de períodos.")
                terminos = " + ".join(
                    rf"\frac{{{flujo:.2f}}}{{(1+{tasa_vpn:.8g})^{{{periodo}}}}}"
                    for periodo, flujo in enumerate(ingresos, start=1)
                )
                _mostrar_sustitucion(rf"VPN = -{inversion:.2f} + {terminos} = {vpn:.2f}")
                st.metric("Valor presente neto (VPN)", _cop(vpn))
                st.info("Con los flujos y la tasa seleccionados, el VPN es positivo." if vpn > 0 else "Con estos supuestos, el VPN es negativo." if vpn < 0 else "Con estos supuestos, el VPN es cero.")
                st.dataframe(tabla_vpn.style.format({"Ingreso (COP)": _cop, "Factor de descuento": "{:.8f}", "Valor presente (COP)": _cop}), width="stretch", hide_index=True)
                st.plotly_chart(_graficar(tabla_vpn, "Período", "Valor presente (COP)", "Ingresos futuros descontados"), width="stretch")
