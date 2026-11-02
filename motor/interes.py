"""Interés simple e interés compuesto: fórmulas puras.

Las tasas se reciben en porcentaje (2.0 significa 2 %). La tasa y el tiempo
deben estar en la misma unidad; `tiempo_en_unidad_de_tasa` hace esa conversión.
"""

import math

DIAS_POR_CONVENCION = {"Comercial (360 días)": 360.0, "Exacto (365 días)": 365.0}


def _validar_capital(valor: float, nombre: str = "El capital") -> None:
    if valor < 0:
        raise ValueError(f"{nombre} no puede ser negativo.")


def _validar_tasa(tasa_porcentaje: float) -> None:
    if tasa_porcentaje <= -100:
        raise ValueError("La tasa debe ser mayor que -100%.")


def calcular_tiempo_fraccionario(plazo: float, unidad: str, convencion: str) -> float:
    """Convierte el plazo a años. Solo los plazos en días dependen de la convención."""
    if unidad == "Años":
        return plazo
    if unidad == "Meses":
        return plazo / 12.0
    if unidad == "Días":
        return plazo / DIAS_POR_CONVENCION[convencion]
    raise ValueError(f"Unidad de plazo desconocida: {unidad}")


def tiempo_en_unidad_de_tasa(plazo: float, unidad_plazo: str, unidad_tasa: str, convencion: str) -> float:
    """Expresa el plazo en la unidad de la tasa ("Año" o "Mes"), para poder calcular i * t."""
    anios = calcular_tiempo_fraccionario(plazo, unidad_plazo, convencion)
    if unidad_tasa == "Año":
        return anios
    if unidad_tasa == "Mes":
        return anios * 12.0
    raise ValueError(f"Unidad de tasa desconocida: {unidad_tasa}")


# ------------------ INTERÉS SIMPLE ------------------

def calcular_monto_interes_simple(capital: float, tasa_porcentaje: float, tiempo: float) -> tuple[float, float]:
    """Calcula el interés y monto final en interés simple: M = C * (1 + i * t)."""
    _validar_capital(capital)
    _validar_tasa(tasa_porcentaje)
    tasa = tasa_porcentaje / 100.0
    interes = capital * tasa * tiempo
    monto = capital + interes
    return interes, monto


def calcular_vp_interes_simple(monto_futuro: float, tasa_porcentaje: float, tiempo: float) -> tuple[float, float]:
    """Calcula el valor presente en interés simple: C = M / (1 + i * t)."""
    _validar_capital(monto_futuro, "El monto futuro")
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
    if monto_futuro < capital:
        raise ValueError("Con tasa positiva, el monto futuro no puede ser menor que el capital.")
    return (monto_futuro - capital) / (capital * tasa)


def calcular_saldos_simple(capital: float, tasa_porcentaje: float, periodos: int) -> list[float]:
    """Devuelve los saldos período a período para interés simple."""
    _validar_capital(capital)
    _validar_tasa(tasa_porcentaje)
    tasa = tasa_porcentaje / 100.0
    return [capital * (1.0 + tasa * p) for p in range(periodos + 1)]


def evolucion_interes_simple(
    capital: float, tasa_porcentaje: float, plazo: float, tiempo_por_unidad: float, puntos: int = 60
) -> tuple[list[float], list[float]]:
    """Da los puntos (plazo, saldo) de la recta M(x) = C * (1 + i * t(x)), de 0 hasta el plazo."""
    _validar_capital(capital)
    tasa = tasa_porcentaje / 100.0
    x = [plazo * k / puntos for k in range(puntos + 1)]
    return x, [capital * (1.0 + tasa * valor * tiempo_por_unidad) for valor in x]


# ------------------ INTERÉS COMPUESTO ------------------

def calcular_monto_interes_compuesto(capital: float, tasa_porcentaje: float, periodos: float) -> tuple[float, float]:
    """Calcula el valor futuro e interés en interés compuesto: VF = VP * (1 + i)^n."""
    _validar_capital(capital)
    _validar_tasa(tasa_porcentaje)
    tasa = tasa_porcentaje / 100.0
    monto = capital * ((1.0 + tasa) ** periodos)
    interes = monto - capital
    return interes, monto


def calcular_vp_interes_compuesto(monto_futuro: float, tasa_porcentaje: float, periodos: float) -> tuple[float, float]:
    """Calcula el valor presente en interés compuesto: VP = VF / (1 + i)^n."""
    _validar_capital(monto_futuro, "El monto futuro")
    _validar_tasa(tasa_porcentaje)
    tasa = tasa_porcentaje / 100.0
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
    _validar_capital(capital)
    _validar_tasa(tasa_porcentaje)
    tasa = tasa_porcentaje / 100.0
    return [capital * ((1.0 + tasa) ** p) for p in range(periodos + 1)]


def calcular_saldos(capital: float, tasa_porcentaje: float, periodos: int, tipo: str) -> list[float]:
    """Compatibilidad: elige el régimen por nombre."""
    if tipo == "Interés simple":
        return calcular_saldos_simple(capital, tasa_porcentaje, periodos)
    return calcular_saldos_compuesto(capital, tasa_porcentaje, periodos)
