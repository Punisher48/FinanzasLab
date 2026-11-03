"""Gradientes aritméticos y geométricos: fórmulas puras."""

def calcular_gradiente_aritmetico(
    primer_pago: float,
    incremento_g: float,
    tasa_pct: float,
    periodos: int,
) -> dict:
    """Calcula VP, VF, Cuota Uniforme Equivalente y flujos para gradiente aritmético."""
    if primer_pago < 0:
        raise ValueError("El primer pago no puede ser negativo.")
    if periodos < 1:
        raise ValueError("El número de períodos debe ser al menos 1.")
    if tasa_pct <= -100:
        raise ValueError("La tasa debe ser mayor que -100%.")
    tasa = tasa_pct / 100.0

    pagos = [primer_pago + (t * incremento_g) for t in range(periodos)]
    if any(p < 0 for p in pagos):
        raise ValueError("El incremento negativo (gradiente decreciente) produce pagos negativos en el plazo.")

    if tasa == 0:
        vp = sum(pagos)
        vf = vp
        a_eq = vp / periodos
    else:
        factor_anualidad = (1.0 - (1.0 + tasa) ** (-periodos)) / tasa
        factor_gradiente = (factor_anualidad - (periodos / ((1.0 + tasa) ** periodos))) / tasa
        vp = (primer_pago * factor_anualidad) + (incremento_g * factor_gradiente)
        vf = vp * ((1.0 + tasa) ** periodos)
        a_eq = vp * (tasa / (1.0 - (1.0 + tasa) ** (-periodos)))

    return {
        "pagos": pagos,
        "valor_presente": vp,
        "valor_futuro": vf,
        "cuota_equivalente": a_eq,
    }


def calcular_gradiente_geometrico(
    primer_pago: float,
    crecimiento_pct: float,
    tasa_pct: float,
    periodos: int,
) -> dict:
    """Calcula VP, VF, Cuota Uniforme Equivalente y flujos para gradiente geométrico."""
    if primer_pago < 0:
        raise ValueError("El primer pago no puede ser negativo.")
    if periodos < 1:
        raise ValueError("El número de períodos debe ser al menos 1.")

    g = crecimiento_pct / 100.0
    tasa = tasa_pct / 100.0

    if tasa_pct <= -100:
        raise ValueError("La tasa debe ser mayor que -100%.")
    if g < -1.0:
        raise ValueError("La tasa de decrecimiento no puede ser menor a -100%.")

    pagos = [primer_pago * ((1.0 + g) ** t) for t in range(periodos)]

    if abs(tasa - g) < 1e-9:
        vp = (periodos * primer_pago) / (1.0 + tasa)
        vf = periodos * primer_pago * ((1.0 + tasa) ** (periodos - 1))
    else:
        vp = primer_pago * ((1.0 - ((1.0 + g) / (1.0 + tasa)) ** periodos) / (tasa - g))
        vf = vp * ((1.0 + tasa) ** periodos)

    if tasa == 0:
        a_eq = vp / periodos
    else:
        a_eq = vp * (tasa / (1.0 - (1.0 + tasa) ** (-periodos)))

    return {
        "pagos": pagos,
        "valor_presente": vp,
        "valor_futuro": vf,
        "cuota_equivalente": a_eq,
    }
