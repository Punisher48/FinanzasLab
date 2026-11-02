"""Tablas de amortización: cuota fija (francés) y abono constante a capital (alemán).

Forma de pago:
- Vencida: los pagos ocurren en los periodos 1, 2, ..., n.
- Anticipada: los pagos ocurren en los periodos 0, 1, ..., n-1. El primero no
  lleva intereses, porque todavía no ha transcurrido tiempo.

El saldo final se calcula con la operación normal de cada fila y nunca se fuerza
a cero: por eso `verificar_amortizacion` es una comprobación real.
"""

import pandas as pd

from motor.series import cuota_para_prestamo
from motor.tasas import a_efectiva_anual, periodica_desde_efectiva_anual

MAX_CUOTAS = 600

PERIODICIDADES_AMORT = {
    "Mensual": 12,
    "Bimestral": 6,
    "Trimestral": 4,
    "Semestral": 2,
    "Anual": 1,
}

CUOTA_FIJA = "Cuota fija (francés)"
ABONO_CONSTANTE = "Abono constante a capital (alemán)"
SISTEMAS = [CUOTA_FIJA, ABONO_CONSTANTE]
FORMAS_PAGO = ["Vencida", "Anticipada"]
TOLERANCIA_COP = 0.01


def calcular_tasa_periodica(tasa_valor: float, tipo_tasa: str, periodicidad: str) -> float:
    """Convierte la tasa ingresada a tasa efectiva periódica vencida, según la periodicidad de pago."""
    if periodicidad not in PERIODICIDADES_AMORT:
        raise ValueError(f"Periodicidad desconocida: {periodicidad}")
    m = PERIODICIDADES_AMORT[periodicidad]
    if tipo_tasa == "Efectiva Periódica":
        tipo_tasa = "Efectiva Periódica Vencida"
    return periodica_desde_efectiva_anual(a_efectiva_anual(tasa_valor, tipo_tasa, m), m) / 100.0


def _validar_credito(prestamo: float, tasa_periodica: float, n_cuotas: int) -> None:
    if prestamo <= 0 or n_cuotas < 1:
        raise ValueError("El préstamo debe ser > 0 y el número de cuotas >= 1.")
    if tasa_periodica < 0:
        raise ValueError("La tasa de un crédito no puede ser negativa.")


def tabla_amortizacion(
    prestamo: float,
    tasa_periodica: float,
    n_cuotas: int,
    sistema: str = CUOTA_FIJA,
    pago: str = "Vencida",
    abono_extra: float = 0.0,
) -> pd.DataFrame:
    """Construye la tabla período a período. `tasa_periodica` es decimal (0.015 = 1.5 %)."""
    _validar_credito(prestamo, tasa_periodica, n_cuotas)
    if sistema not in SISTEMAS:
        raise ValueError(f"Sistema desconocido: {sistema}")
    if pago not in FORMAS_PAGO:
        raise ValueError(f"Forma de pago desconocida: {pago}")
    if abono_extra < 0:
        raise ValueError("El abono extra no puede ser negativo.")

    cuota_fija = cuota_para_prestamo(prestamo, tasa_periodica * 100.0, n_cuotas, pago)
    abono_constante = prestamo / n_cuotas
    primer_periodo = 1 if pago == "Vencida" else 0

    filas = []
    saldo = prestamo
    for periodo in range(primer_periodo, primer_periodo + n_cuotas):
        interes = 0.0 if periodo == 0 else saldo * tasa_periodica
        abono = cuota_fija - interes if sistema == CUOTA_FIJA else abono_constante
        extra = abono_extra
        es_ultimo_pago = False

        # Con abonos extra el crédito termina antes: el último pago solo cubre lo que falta.
        if abono_extra > 0 and abono + extra >= saldo:
            abono = min(abono, saldo)
            extra = saldo - abono
            es_ultimo_pago = True

        fila = {
            "Período": periodo,
            "Saldo Inicial (COP)": saldo,
            "Cuota (COP)": interes + abono + extra,
            "Interés (COP)": interes,
            "Abono a Capital (COP)": abono,
            "Saldo Final (COP)": saldo - abono - extra,
        }
        if abono_extra > 0:
            fila["Abono Extra (COP)"] = extra
        filas.append(fila)
        saldo -= abono + extra
        if es_ultimo_pago:
            break

    return pd.DataFrame(filas)


def amortizacion_frances(prestamo: float, tasa_periodica: float, n_cuotas: int) -> pd.DataFrame:
    """Tabla con cuota fija y pago vencido."""
    return tabla_amortizacion(prestamo, tasa_periodica, n_cuotas, CUOTA_FIJA)


def amortizacion_aleman(prestamo: float, tasa_periodica: float, n_cuotas: int) -> pd.DataFrame:
    """Tabla con abono constante a capital y pago vencido."""
    return tabla_amortizacion(prestamo, tasa_periodica, n_cuotas, ABONO_CONSTANTE)


def generar_tabla_amortizacion(prestamo: float, tasa_porcentaje: float, numero_cuotas: int) -> pd.DataFrame:
    """Compatibilidad: cuota fija con la tasa en porcentaje."""
    return amortizacion_frances(prestamo, tasa_porcentaje / 100.0, numero_cuotas)


def puntos_saldo(tabla: pd.DataFrame, capital: float) -> tuple[list[int], list[float]]:
    """Da los puntos (periodo, saldo) para graficar. Con pago vencido arranca en el capital."""
    periodos = tabla["Período"].tolist()
    saldos = tabla["Saldo Final (COP)"].tolist()
    if periodos[0] == 1:
        return [0] + periodos, [capital] + saldos
    return periodos, saldos


def verificar_amortizacion(tabla: pd.DataFrame, capital: float) -> dict:
    """Comprueba el cierre de la tabla: saldo final cero, abonos = capital y pagos = capital + intereses."""
    saldo_final = float(tabla["Saldo Final (COP)"].iloc[-1])
    suma_abonos = float(tabla["Abono a Capital (COP)"].sum())
    if "Abono Extra (COP)" in tabla:
        suma_abonos += float(tabla["Abono Extra (COP)"].sum())
    total_pagado = float(tabla["Cuota (COP)"].sum())
    total_intereses = float(tabla["Interés (COP)"].sum())
    return {
        "saldo_final": saldo_final,
        "suma_abonos": suma_abonos,
        "total_pagado": total_pagado,
        "total_intereses": total_intereses,
        "ok_saldo": abs(saldo_final) < TOLERANCIA_COP,
        "ok_abonos": abs(suma_abonos - capital) < TOLERANCIA_COP,
        "ok_total": abs(total_pagado - capital - total_intereses) < TOLERANCIA_COP,
    }


def efecto_abono_extra(
    prestamo: float, tasa_periodica: float, n_cuotas: int, sistema: str, pago: str, abono_extra: float
) -> dict:
    """Compara el crédito con y sin abono extra: intereses ahorrados y periodos que se acorta."""
    base = tabla_amortizacion(prestamo, tasa_periodica, n_cuotas, sistema, pago)
    con_extra = tabla_amortizacion(prestamo, tasa_periodica, n_cuotas, sistema, pago, abono_extra)
    intereses_base = float(base["Interés (COP)"].sum())
    intereses_con_extra = float(con_extra["Interés (COP)"].sum())
    return {
        "tabla": con_extra,
        "intereses_sin_extra": intereses_base,
        "intereses_con_extra": intereses_con_extra,
        "intereses_ahorrados": intereses_base - intereses_con_extra,
        "cuotas_sin_extra": len(base),
        "cuotas_con_extra": len(con_extra),
        "cuotas_menos": len(base) - len(con_extra),
    }
