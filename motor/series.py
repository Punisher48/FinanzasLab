"""Series uniformes (anualidades) vencidas y anticipadas: fórmulas puras."""

import pandas as pd


def valor_futuro_serie(cuota: float, tasa_porcentaje: float, periodos: int, modalidad: str = "Vencida") -> float:
    """Calcula el Valor Futuro (VF) de una serie uniforme vencida o anticipada."""
    cuota, tasa, periodos = _validar_entradas(cuota, tasa_porcentaje, periodos)
    if tasa == 0:
        return cuota * periodos
    vf_vencido = cuota * (((1.0 + tasa) ** periodos - 1.0) / tasa)
    if modalidad == "Anticipada":
        return vf_vencido * (1.0 + tasa)
    return vf_vencido


def valor_presente_serie(cuota: float, tasa_porcentaje: float, periodos: int, modalidad: str = "Vencida") -> float:
    """Calcula el Valor Presente (VP) de una serie uniforme vencida o anticipada."""
    cuota, tasa, periodos = _validar_entradas(cuota, tasa_porcentaje, periodos)
    if tasa == 0:
        return cuota * periodos
    vp_vencido = cuota * ((1.0 - (1.0 + tasa) ** (-periodos)) / tasa)
    if modalidad == "Anticipada":
        return vp_vencido * (1.0 + tasa)
    return vp_vencido


def cuota_para_valor_futuro(valor_futuro: float, tasa_porcentaje: float, periodos: int, modalidad: str = "Vencida") -> float:
    """Calcula la cuota periódica para acumular un fondo futuro."""
    if valor_futuro < 0:
        raise ValueError("El valor futuro no puede ser negativo.")
    _, tasa, periodos = _validar_entradas(0.0, tasa_porcentaje, periodos)
    if tasa == 0:
        return valor_futuro / periodos
    factor = ((1.0 + tasa) ** periodos - 1.0) / tasa
    if modalidad == "Anticipada":
        factor *= (1.0 + tasa)
    return valor_futuro / factor


def cuota_para_prestamo(valor_presente: float, tasa_porcentaje: float, periodos: int, modalidad: str = "Vencida") -> float:
    """Calcula la cuota periódica requerida para amortizar un préstamo."""
    if valor_presente < 0:
        raise ValueError("El valor presente no puede ser negativo.")
    _, tasa, periodos = _validar_entradas(0.0, tasa_porcentaje, periodos)
    if tasa == 0:
        return valor_presente / periodos
    factor = (1.0 - (1.0 + tasa) ** (-periodos)) / tasa
    if modalidad == "Anticipada":
        factor *= (1.0 + tasa)
    return valor_presente / factor


def generar_flujo_serie(
    operacion_tipo: str,
    cuota: float,
    tasa_pct: float,
    periodos: int,
    modalidad: str = "Vencida",
    monto_base: float = 0.0
) -> pd.DataFrame:
    """Genera la tabla período a período con el flujo de pago y el saldo acumulado."""
    tasa = tasa_pct / 100.0
    filas = []

    if "Ahorro" in operacion_tipo or "Futuro" in operacion_tipo:
        saldo = 0.0
        if modalidad == "Anticipada":
            saldo = cuota
            filas.append({"Período": 0, "Flujo Pago (COP)": cuota, "Interés Ganado (COP)": 0.0, "Saldo Acumulado (COP)": saldo})
            for p in range(1, periodos):
                interes = saldo * tasa
                saldo = saldo + interes + cuota
                filas.append({"Período": p, "Flujo Pago (COP)": cuota, "Interés Ganado (COP)": interes, "Saldo Acumulado (COP)": saldo})
            interes_final = saldo * tasa
            saldo_final = saldo + interes_final
            filas.append({"Período": periodos, "Flujo Pago (COP)": 0.0, "Interés Ganado (COP)": interes_final, "Saldo Acumulado (COP)": saldo_final})
        else:
            filas.append({"Período": 0, "Flujo Pago (COP)": 0.0, "Interés Ganado (COP)": 0.0, "Saldo Acumulado (COP)": 0.0})
            saldo = 0.0
            for p in range(1, periodos + 1):
                interes = saldo * tasa
                saldo = saldo + interes + cuota
                filas.append({"Período": p, "Flujo Pago (COP)": cuota, "Interés Ganado (COP)": interes, "Saldo Acumulado (COP)": saldo})
    else:
        saldo = monto_base
        if modalidad == "Anticipada":
            abono_0 = cuota
            saldo -= abono_0
            filas.append({"Período": 0, "Flujo Pago (COP)": -cuota, "Interés Ganado (COP)": 0.0, "Saldo Acumulado (COP)": saldo})
            for p in range(1, periodos):
                interes = saldo * tasa
                abono = cuota - interes
                saldo -= abono
                filas.append({"Período": p, "Flujo Pago (COP)": -cuota, "Interés Ganado (COP)": interes, "Saldo Acumulado (COP)": max(0.0, saldo)})
        else:
            filas.append({"Período": 0, "Flujo Pago (COP)": 0.0, "Interés Ganado (COP)": 0.0, "Saldo Acumulado (COP)": saldo})
            for p in range(1, periodos + 1):
                interes = saldo * tasa
                abono = cuota - interes
                saldo -= abono
                filas.append({"Período": p, "Flujo Pago (COP)": -cuota, "Interés Ganado (COP)": interes, "Saldo Acumulado (COP)": max(0.0, saldo)})

    return pd.DataFrame(filas)


def _validar_entradas(cuota: float, tasa_porcentaje: float, periodos: int):
    c = float(cuota)
    t = float(tasa_porcentaje) / 100.0
    p = int(periodos)
    if c < 0:
        raise ValueError("La cuota no puede ser negativa.")
    if t <= -1.0:
        raise ValueError("La tasa periódica debe ser mayor que -100%.")
    if p < 1:
        raise ValueError("El número de períodos debe ser mayor o igual a 1.")
    return c, t, p
