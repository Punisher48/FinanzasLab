"""Tablas de amortización: cuota fija (francés) y abono constante (alemán)."""

import pandas as pd

from motor.tasas import periodica_desde_efectiva_anual


MAX_CUOTAS = 600

PERIODICIDADES_AMORT = {
    "Mensual": 12,
    "Bimestral": 6,
    "Trimestral": 4,
    "Semestral": 2,
    "Anual": 1,
}


def calcular_tasa_periodica(tasa_valor: float, tipo_tasa: str, periodicidad: str) -> float:
    """Convierte la tasa ingresada a tasa efectiva periódica según la frecuencia."""
    m = PERIODICIDADES_AMORT.get(periodicidad, 12)
    if tipo_tasa == "Efectiva Periódica":
        return tasa_valor / 100.0
    elif tipo_tasa == "Efectiva Anual (EA)":
        return periodica_desde_efectiva_anual(tasa_valor, m) / 100.0
    elif tipo_tasa == "Nominal Anual Vencida":
        return (tasa_valor / 100.0) / m
    return tasa_valor / 100.0


# ------------------ SISTEMA FRANCÉS (CUOTA FIJA) ------------------

def amortizacion_frances(prestamo: float, tasa_periodica: float, n_cuotas: int) -> pd.DataFrame:
    """Genera la tabla de amortización por el sistema francés (cuota fija)."""
    if prestamo <= 0 or n_cuotas < 1:
        raise ValueError("El préstamo debe ser > 0 y el número de cuotas >= 1.")

    if tasa_periodica == 0:
        cuota_fija = prestamo / n_cuotas
    else:
        cuota_fija = prestamo * (tasa_periodica / (1.0 - (1.0 + tasa_periodica) ** (-n_cuotas)))

    filas = []
    saldo = prestamo
    for p in range(1, n_cuotas + 1):
        saldo_inicial = saldo
        interes = saldo_inicial * tasa_periodica
        if p == n_cuotas:
            abono = saldo_inicial
            cuota = abono + interes
            saldo_final = 0.0
        else:
            abono = cuota_fija - interes
            cuota = cuota_fija
            saldo_final = saldo_inicial - abono

        filas.append({
            "Período": p,
            "Saldo Inicial (COP)": saldo_inicial,
            "Cuota (COP)": cuota,
            "Interés (COP)": interes,
            "Abono a Capital (COP)": abono,
            "Saldo Final (COP)": max(0.0, saldo_final),
        })
        saldo = saldo_final

    return pd.DataFrame(filas)


# ------------------ SISTEMA ALEMÁN (ABONO CONSTANTE) ------------------

def amortizacion_aleman(prestamo: float, tasa_periodica: float, n_cuotas: int) -> pd.DataFrame:
    """Genera la tabla de amortización por el sistema alemán (abono constante a capital)."""
    if prestamo <= 0 or n_cuotas < 1:
        raise ValueError("El préstamo debe ser > 0 y el número de cuotas >= 1.")

    abono_fijo = prestamo / n_cuotas
    filas = []
    saldo = prestamo
    for p in range(1, n_cuotas + 1):
        saldo_inicial = saldo
        interes = saldo_inicial * tasa_periodica
        abono = abono_fijo
        cuota = abono + interes
        saldo_final = saldo_inicial - abono
        if p == n_cuotas or abs(saldo_final) < 1e-4:
            saldo_final = 0.0

        filas.append({
            "Período": p,
            "Saldo Inicial (COP)": saldo_inicial,
            "Cuota (COP)": cuota,
            "Interés (COP)": interes,
            "Abono a Capital (COP)": abono,
            "Saldo Final (COP)": max(0.0, saldo_final),
        })
        saldo = saldo_final

    return pd.DataFrame(filas)


# Compatibilidad
def generar_tabla_amortizacion(prestamo: float, tasa_porcentaje: float, numero_cuotas: int) -> pd.DataFrame:
    tasa_p = tasa_porcentaje / 100.0
    return amortizacion_frances(prestamo, tasa_p, numero_cuotas)
