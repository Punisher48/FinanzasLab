"""Conversiones de tasas, equivalencias, tasas combinadas y retención: fórmulas puras."""

import numbers

import pandas as pd


def vencida_a_anticipada(tasa_vencida_porcentaje: float) -> float:
    """Convierte tasa periódica vencida a tasa periódica anticipada: ia = iv / (1 + iv)."""
    i_v = tasa_vencida_porcentaje / 100.0
    if i_v <= -1.0:
        raise ValueError("La tasa periódica vencida debe ser mayor que -100%.")
    i_a = i_v / (1.0 + i_v)
    return i_a * 100.0


def anticipada_a_vencida(tasa_anticipada_porcentaje: float) -> float:
    """Convierte tasa periódica anticipada a tasa periódica vencida: iv = ia / (1 - ia)."""
    i_a = tasa_anticipada_porcentaje / 100.0
    if i_a >= 1.0:
        raise ValueError("La tasa periódica anticipada debe ser menor que 100%.")
    i_v = i_a / (1.0 - i_a)
    return i_v * 100.0


def efectiva_anual_desde_periodica(tasa_periodica_porcentaje: float, periodos_por_anio: int) -> float:
    """Convierte una tasa efectiva periódica vencida (en %) a efectiva anual (en %)."""
    _validar_periodos(periodos_por_anio)
    i = tasa_periodica_porcentaje / 100.0
    if i <= -1.0:
        raise ValueError("La tasa periódica debe ser mayor que -100%.")
    ea = ((1.0 + i) ** periodos_por_anio) - 1.0
    return ea * 100.0


def periodica_desde_efectiva_anual(tasa_anual_porcentaje: float, periodos_por_anio: int) -> float:
    """Convierte una tasa efectiva anual (en %) a efectiva periódica vencida (en %)."""
    _validar_periodos(periodos_por_anio)
    ea = tasa_anual_porcentaje / 100.0
    if ea <= -1.0:
        raise ValueError("La tasa efectiva anual debe ser mayor que -100%.")
    i = ((1.0 + ea) ** (1.0 / periodos_por_anio)) - 1.0
    return i * 100.0


def efectiva_anual_desde_nominal(tasa_nominal_porcentaje: float, periodos_por_anio: int, anticipada: bool = False) -> float:
    """Convierte una tasa nominal anual a efectiva anual (en %)."""
    _validar_periodos(periodos_por_anio)
    j = tasa_nominal_porcentaje / 100.0
    i_periodica = j / periodos_por_anio
    if anticipada:
        if i_periodica >= 1.0:
            raise ValueError("La tasa periódica anticipada (j/m) debe ser menor a 100%.")
        i_vencida = i_periodica / (1.0 - i_periodica)
    else:
        i_vencida = i_periodica

    if i_vencida <= -1.0:
        raise ValueError("La tasa periódica resultante debe ser mayor que -100%.")
    ea = ((1.0 + i_vencida) ** periodos_por_anio) - 1.0
    return ea * 100.0


def nominal_desde_efectiva_anual(ea_porcentaje: float, periodos_por_anio: int, anticipada: bool = False) -> float:
    """Calcula la tasa nominal anual a partir de la efectiva anual."""
    i_v = periodica_desde_efectiva_anual(ea_porcentaje, periodos_por_anio) / 100.0
    if anticipada:
        i_p = i_v / (1.0 + i_v)
    else:
        i_p = i_v
    return (i_p * periodos_por_anio) * 100.0


# ------------------ TASAS COMBINADAS (FISHER) ------------------

def tasa_combinada(tasa_base_pct: float, spread_pct: float) -> float:
    """Calcula la tasa combinada (Fisher): (1 + it) = (1 + i_base) * (1 + spread)."""
    i1 = tasa_base_pct / 100.0
    i2 = spread_pct / 100.0
    it = ((1.0 + i1) * (1.0 + i2)) - 1.0
    return it * 100.0


def tasa_real_fisher(tasa_aparente_pct: float, tasa_inflacion_pct: float) -> float:
    """Despeja la tasa real deflactada: (1 + i_real) = (1 + i_aparente) / (1 + inflacion)."""
    ia = tasa_aparente_pct / 100.0
    inf = tasa_inflacion_pct / 100.0
    if inf <= -1.0:
        raise ValueError("La inflación debe ser mayor a -100%.")
    ir = ((1.0 + ia) / (1.0 + inf)) - 1.0
    return ir * 100.0


# ------------------ RENTABILIDAD CON RETENCIÓN EN LA FUENTE ------------------

def rentabilidad_con_retencion(
    inversion_inicial: float,
    valor_final: float,
    retencion_pct: float,
    dias_plazo: float = 360.0,
    base_dias: float = 360.0,
) -> dict[str, float]:
    """Calcula la rentabilidad bruta y neta con deducción de retención en la fuente."""
    if inversion_inicial <= 0:
        raise ValueError("La inversión inicial debe ser mayor que cero.")
    if valor_final < inversion_inicial:
        raise ValueError("El valor final debe ser mayor o igual a la inversión inicial.")
    if dias_plazo <= 0 or base_dias <= 0:
        raise ValueError("El plazo y la base de días deben ser mayores que cero.")
    if retencion_pct < 0 or retencion_pct > 100:
        raise ValueError("El porcentaje de retención debe estar entre 0% y 100%.")

    rendimiento_bruto = valor_final - inversion_inicial
    retencion_valor = rendimiento_bruto * (retencion_pct / 100.0)
    rendimiento_neto = rendimiento_bruto - retencion_valor

    rentabilidad_periodo_bruta = (rendimiento_bruto / inversion_inicial) * 100.0
    rentabilidad_periodo_neta = (rendimiento_neto / inversion_inicial) * 100.0

    factor_anual = base_dias / dias_plazo
    ea_bruta = (((1.0 + (rentabilidad_periodo_bruta / 100.0)) ** factor_anual) - 1.0) * 100.0
    ea_neta = (((1.0 + (rentabilidad_periodo_neta / 100.0)) ** factor_anual) - 1.0) * 100.0

    return {
        "rendimiento_bruto": rendimiento_bruto,
        "retencion_valor": retencion_valor,
        "rendimiento_neto": rendimiento_neto,
        "rentabilidad_periodo_bruta": rentabilidad_periodo_bruta,
        "rentabilidad_periodo_neta": rentabilidad_periodo_neta,
        "ea_bruta": ea_bruta,
        "ea_neta": ea_neta,
    }


def rentabilidad_porcentual(valor_inicial: float, valor_final: float) -> float:
    if valor_inicial <= 0:
        raise ValueError("El valor inicial debe ser mayor que cero.")
    if valor_final < 0:
        raise ValueError("El valor final no puede ser negativo.")
    return ((valor_final - valor_inicial) / valor_inicial) * 100.0


PERIODICIDADES = [
    ("Diaria", 360),
    ("Mensual", 12),
    ("Bimestral", 6),
    ("Trimestral", 4),
    ("Cuatrimestral", 3),
    ("Semestral", 2),
    ("Anual", 1),
]


TIPOS_TASA = [
    "Efectiva Anual (EA)",
    "Efectiva Periódica Vencida",
    "Efectiva Periódica Anticipada",
    "Nominal Anual Vencida",
    "Nominal Anual Anticipada",
]


def a_efectiva_anual(tasa_pct: float, tipo: str, periodos_por_anio: int = 12) -> float:
    """Convierte cualquier tipo de tasa a efectiva anual (EA), en porcentaje."""
    if tipo == "Efectiva Anual (EA)":
        return tasa_pct
    if tipo == "Efectiva Periódica Vencida":
        return efectiva_anual_desde_periodica(tasa_pct, periodos_por_anio)
    if tipo == "Efectiva Periódica Anticipada":
        return efectiva_anual_desde_periodica(anticipada_a_vencida(tasa_pct), periodos_por_anio)
    if tipo == "Nominal Anual Vencida":
        return efectiva_anual_desde_nominal(tasa_pct, periodos_por_anio, anticipada=False)
    if tipo == "Nominal Anual Anticipada":
        return efectiva_anual_desde_nominal(tasa_pct, periodos_por_anio, anticipada=True)
    raise ValueError(f"Tipo de tasa desconocido: {tipo}")


def generar_tabla_equivalencias(tasa_origen_pct: float, tipo_origen: str, periodos_origen: int = 12) -> pd.DataFrame:
    """Genera la matriz completa de equivalencias a partir de cualquier tasa de entrada."""
    ea = a_efectiva_anual(tasa_origen_pct, tipo_origen, periodos_origen)

    filas = []
    for nombre, m in PERIODICIDADES:
        i_v = periodica_desde_efectiva_anual(ea, m)
        i_a = vencida_a_anticipada(i_v)
        j_v = i_v * m
        j_a = i_a * m

        filas.append({
            "Periodicidad": nombre,
            "Períodos m": m,
            "Periódica Vencida (ip)": f"{i_v:.4f}%",
            "Periódica Anticipada (ia)": f"{i_a:.4f}%",
            "Nominal Vencida (j)": f"{j_v:.4f}%",
            "Nominal Anticipada (ja)": f"{j_a:.4f}%",
            "Efectiva Anual (EA)": f"{ea:.4f}%",
        })

    return pd.DataFrame(filas)


def _validar_periodos(periodos_por_anio: int) -> None:
    if isinstance(periodos_por_anio, bool) or not isinstance(periodos_por_anio, numbers.Integral) or periodos_por_anio < 1:
        raise ValueError("La cantidad de períodos por año debe ser un entero positivo.")
