"""Formato de presentación compartido por todas las pantallas."""

import math


def formato_cop(valor: float) -> str:
    """Formatea un valor en pesos colombianos para presentación."""
    if not math.isfinite(valor):
        return "N/A"
    return f"${valor:,.2f} COP".replace(",", "X").replace(".", ",").replace("X", ".")


def variacion_pct(parte: float, base: float) -> float:
    """Calcula parte / base en porcentaje; devuelve 0 si la base es 0 para evitar dividir por cero."""
    return (parte / base) * 100.0 if base else 0.0
