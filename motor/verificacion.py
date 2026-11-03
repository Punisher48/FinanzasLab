"""Matriz de verificación: compara el motor en vivo contra una referencia calculada de otra forma.

La referencia nunca llama a la fórmula que se está probando. Se obtiene del flujo de caja
período a período o de la aritmética directa escrita en cada fila.
"""

from motor import amortizacion as am
from motor import decisiones as dc
from motor import gradientes as gr
from motor import interes as it
from motor import series as se
from motor import tasas as ta

TOLERANCIA = 0.01


def _vf_flujo(pagos: list[float], i: float) -> float:
    """Capitaliza pagos vencidos uno por uno, sin usar fórmulas de series."""
    saldo = 0.0
    for pago in pagos:
        saldo = saldo * (1 + i) + pago
    return saldo


def _vp_flujo(pagos: list[float], i: float) -> float:
    """Descuenta pagos vencidos uno por uno, sin usar fórmulas de series."""
    return sum(pago / (1 + i) ** (t + 1) for t, pago in enumerate(pagos))


def fila(modulo: str, prueba: str, referencia: str, esperado: float, motor: float) -> dict:
    diferencia = abs(esperado - motor)
    return {
        "Módulo": modulo,
        "Prueba": prueba,
        "Cómo se calcula la referencia": referencia,
        "Referencia": round(esperado, 4),
        "Motor": round(motor, 4),
        "Diferencia": round(diferencia, 6),
        "Estado": "✅ Coincide" if diferencia <= TOLERANCIA else "❌ No coincide",
    }


def matriz_verificacion() -> list[dict]:
    """Ejecuta el motor y devuelve una fila por comprobación, con su estado calculado."""
    francesa = am.amortizacion_frances(1_000_000, 0.10, 2)
    alemana = am.amortizacion_aleman(1_000_000, 0.10, 2)
    anticipada = am.tabla_amortizacion(1_000_000, 0.10, 2, am.CUOTA_FIJA, "Anticipada")
    ahorro = dc.plan_de_ahorro(10_000_000, 24, 12.0, 0, dc.PLAN_GEOMETRICO, 10)
    i_ahorro = 1.12 ** (1 / 12) - 1

    return [
        fila("Interés simple", "VF: C=1.000.000, i=10%, t=3", "1.000.000 + 3 × 100.000", 1_300_000, it.calcular_monto_interes_simple(1_000_000, 10, 3)[1]),
        fila("Interés simple", "Convención: 90 días a 12% anual, base 365", "1.000.000 × (1 + 0,12 × 90/365)", 1_000_000 * (1 + 0.12 * 90 / 365), it.calcular_monto_interes_simple(1_000_000, 12, it.tiempo_en_unidad_de_tasa(90, "Días", "Año", "Exacto (365 días)"))[1]),
        fila("Interés compuesto", "VF: VP=1.000.000, i=10%, n=3", "Multiplicar tres veces por 1,10", 1_000_000 * 1.1 * 1.1 * 1.1, it.calcular_monto_interes_compuesto(1_000_000, 10, 3)[1]),
        fila("Tasas", "24% nominal mes vencido a EA", "1,02 multiplicado 12 veces, menos 1", (1.02 ** 12 - 1) * 100, ta.a_efectiva_anual(24, "Nominal Anual Vencida", 12)),
        fila("Tasas", "2% anticipada a vencida", "Recibir 98 y devolver 100: 2/98", 2 / 98 * 100, ta.anticipada_a_vencida(2)),
        fila("Tasas", "Combinada: inflación 5% + 4 puntos", "1,05 × 1,04 − 1", (1.05 * 1.04 - 1) * 100, ta.tasa_combinada(5, 4)),
        fila("Tasas", "EA neta: 1.000.000 → 1.100.000, retención 4%", "Interés 100.000 menos 4.000, sobre 1.000.000", 9.6, ta.rentabilidad_con_retencion(1_000_000, 1_100_000, 4, 360)["ea_neta"]),
        fila("Series uniformes", "VF vencida: A=100.000, i=10%, n=3", "Capitalizar cada pago", _vf_flujo([100_000] * 3, 0.10), se.valor_futuro_serie(100_000, 10, 3, "Vencida")),
        fila("Series uniformes", "VP anticipada: A=100.000, i=10%, n=3", "Descontar pagos en t = 0, 1, 2", 100_000 + 100_000 / 1.1 + 100_000 / 1.21, se.valor_presente_serie(100_000, 10, 3, "Anticipada")),
        fila("Gradientes", "Aritmético VP: A1=100.000, G=20.000, i=10%, n=3", "Descontar 100.000, 120.000 y 140.000", _vp_flujo([100_000, 120_000, 140_000], 0.10), gr.calcular_gradiente_aritmetico(100_000, 20_000, 10, 3)["valor_presente"]),
        fila("Gradientes", "Geométrico VF: A1=100.000, g=5%, i=10%, n=3", "Capitalizar 100.000, 105.000 y 110.250", _vf_flujo([100_000, 105_000, 110_250], 0.10), gr.calcular_gradiente_geometrico(100_000, 5, 10, 3)["valor_futuro"]),
        fila("Amortización", "Cuota fija: VP de las cuotas = capital", "Descontar las cuotas de la tabla al 10%", 1_000_000, _vp_flujo(list(francesa["Cuota (COP)"]), 0.10)),
        fila("Amortización", "Abono constante: primera cuota", "500.000 de abono + 100.000 de interés", 600_000, float(alemana["Cuota (COP)"].iloc[0])),
        fila("Amortización", "Cuota fija: saldo final", "Debe cerrar en cero", 0, float(francesa["Saldo Final (COP)"].iloc[-1])),
        fila("Amortización", "Abono constante: suma de abonos", "Debe ser igual al capital", 1_000_000, float(alemana["Abono a Capital (COP)"].sum())),
        fila("Amortización", "Pago anticipado: valor de las cuotas en t=0", "Primera cuota + segunda / 1,10", 1_000_000, float(anticipada["Cuota (COP)"].iloc[0] + anticipada["Cuota (COP)"].iloc[1] / 1.1)),
        fila("Plan de ahorro", "Gradiente geométrico: el calendario llega a la meta", "Capitalizar los aportes del calendario", 10_000_000, _vf_flujo(list(ahorro["calendario"]["Aporte (COP)"]), i_ahorro)),
    ]
