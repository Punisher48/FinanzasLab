"""Interés simple e interés compuesto: fórmulas puras."""

import math


def calcular_tiempo_fraccionario(plazo: float, unidad: str, convencion: str) -> float:
    """Convierte el plazo a períodos anuales o acordes a la convención."""
    dias_anio = 360.0 if convencion == "Comercial (360 días)" else 365.0
    if unidad == "Años":
        return plazo
    elif unidad == "Meses":
        return plazo / 12.0
    elif unidad == "Días":
        return plazo / dias_anio
    return plazo


# ------------------ INTERÉS SIMPLE ------------------

def calcular_monto_interes_simple(capital: float, tasa_porcentaje: float, tiempo: float) -> tuple[float, float]:
    """Calcula el interés y monto final en interés simple: M = C * (1 + i * t)."""
    tasa = tasa_porcentaje / 100.0
    interes = capital * tasa * tiempo
    monto = capital + interes
    return interes, monto


def calcular_vp_interes_simple(monto_futuro: float, tasa_porcentaje: float, tiempo: float) -> tuple[float, float]:
    """Calcula el valor presente en interés simple: C = M / (1 + i * t)."""
    tasa = tasa_porcentaje / 100.0
    divisor = 1.0 + tasa * tiempo
    if divisor <= 0:
        raise ValueError("El factor (1 + i*t) debe ser estrictamente positivo.")
    capital = monto_futuro / divisor
    interes = monto_futuro - capital
    return capital, interes


def despejar_tasa_interes_simple(capital: float, monto_futuro: float, tiempo: float) -> float:
    """Despeja la tasa en interés simple: i = (M - C) / (C * t) expresada en porcentaje."""
    if capital <= 0 or tiempo <= 0:
        raise ValueError("El capital y el tiempo deben ser mayores que cero.")
    tasa = (monto_futuro - capital) / (capital * tiempo)
    return tasa * 100.0


def despejar_tiempo_interes_simple(capital: float, monto_futuro: float, tasa_porcentaje: float) -> float:
    """Despeja el tiempo en interés simple: t = (M - C) / (C * i)."""
    tasa = tasa_porcentaje / 100.0
    if capital <= 0 or tasa <= 0:
        raise ValueError("El capital y la tasa deben ser mayores que cero.")
    return (monto_futuro - capital) / (capital * tasa)


def calcular_saldos_simple(capital: float, tasa_porcentaje: float, periodos: int) -> list[float]:
    """Devuelve los saldos período a período para interés simple."""
    tasa = tasa_porcentaje / 100.0
    return [capital * (1.0 + tasa * p) for p in range(periodos + 1)]


# ------------------ INTERÉS COMPUESTO ------------------

def calcular_monto_interes_compuesto(capital: float, tasa_porcentaje: float, periodos: float) -> tuple[float, float]:
    """Calcula el valor futuro e interés en interés compuesto: VF = VP * (1 + i)^n."""
    tasa = tasa_porcentaje / 100.0
    if tasa <= -1:
        raise ValueError("La tasa periódica debe ser mayor al -100%.")
    monto = capital * ((1.0 + tasa) ** periodos)
    interes = monto - capital
    return interes, monto


def calcular_vp_interes_compuesto(monto_futuro: float, tasa_porcentaje: float, periodos: float) -> tuple[float, float]:
    """Calcula el valor presente en interés compuesto: VP = VF / (1 + i)^n."""
    tasa = tasa_porcentaje / 100.0
    if tasa <= -1:
        raise ValueError("La tasa periódica debe ser mayor al -100%.")
    capital = monto_futuro / ((1.0 + tasa) ** periodos)
    interes = monto_futuro - capital
    return capital, interes


def despejar_tasa_interes_compuesto(capital: float, monto_futuro: float, periodos: float) -> float:
    """Despeja la tasa periódica en interés compuesto: i = (VF / VP)^(1/n) - 1 en porcentaje."""
    if capital <= 0 or periodos <= 0 or monto_futuro <= 0:
        raise ValueError("El capital, monto futuro y períodos deben ser mayores que cero.")
    tasa = ((monto_futuro / capital) ** (1.0 / periodos)) - 1.0
    return tasa * 100.0


def despejar_periodos_interes_compuesto(capital: float, monto_futuro: float, tasa_porcentaje: float) -> float:
    """Despeja el número de períodos en interés compuesto: n = ln(VF / VP) / ln(1 + i)."""
    tasa = tasa_porcentaje / 100.0
    if capital <= 0 or monto_futuro <= 0 or tasa <= 0:
        raise ValueError("El capital, monto y tasa deben ser mayores que cero.")
    if monto_futuro < capital:
        raise ValueError("El monto futuro debe ser mayor o igual al capital inicial.")
    return math.log(monto_futuro / capital) / math.log(1.0 + tasa)


def calcular_saldos_compuesto(capital: float, tasa_porcentaje: float, periodos: int) -> list[float]:
    """Devuelve los saldos período a período para interés compuesto."""
    tasa = tasa_porcentaje / 100.0
    return [capital * ((1.0 + tasa) ** p) for p in range(periodos + 1)]


# Compatibilidad hacia atrás con tests existentes
def calcular_saldos(capital: float, tasa_porcentaje: float, periodos: int, tipo: str) -> list[float]:
    if tipo == "Interés simple":
        return calcular_saldos_simple(capital, tasa_porcentaje, periodos)
    return calcular_saldos_compuesto(capital, tasa_porcentaje, periodos)
