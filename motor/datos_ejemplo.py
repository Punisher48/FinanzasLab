"""Parámetros precargados de los tres casos.

Son DATOS DE EJEMPLO: cifras razonables para ilustrar el cálculo, no ofertas reales
de ninguna entidad. El usuario las edita en pantalla y completa la fuente y la fecha.
"""

INTERES_REINVERTIDO = "Se reinvierten (interés compuesto)"
INTERES_RETIRADO = "Se retiran cada periodo (interés simple)"

PLAN_UNIFORME = "Cuota uniforme"
PLAN_ARITMETICO = "Gradiente aritmético (sube un valor fijo cada año)"
PLAN_GEOMETRICO = "Gradiente geométrico (sube un porcentaje cada año)"
PLANES = [PLAN_UNIFORME, PLAN_ARITMETICO, PLAN_GEOMETRICO]

CASO_A = {
    "a_monto": 10_000_000.0,
    "a_dias": 360,
    "a_convencion": "Comercial (360 días)",
    "a_inflacion": 5.2,
    "a_cdt_tasa": 9.0,
    "a_cdt_tipo": "Nominal Anual Vencida",
    "a_cdt_periodicidad": "Trimestral",
    "a_cdt_intereses": INTERES_RETIRADO,
    "a_cdt_retencion": 4.0,
    "a_ahorro_tasa": 5.5,
    "a_ahorro_tipo": "Efectiva Anual (EA)",
    "a_ahorro_periodicidad": "Mensual",
    "a_ahorro_retencion": 7.0,
    "a_comb_puntos": 3.0,
    "a_comb_retencion": 4.0,
    "a_fuente": "",
    "a_fecha": None,
}

CASO_B = {
    "b_descuento": 9.0,
    "b_sistema": "Cuota fija (francés)",
    "b_extra": 300_000.0,
    "b_a_capital": 30_000_000.0,
    "b_a_tasa": 19.5,
    "b_a_tipo": "Efectiva Anual (EA)",
    "b_a_periodicidad_tasa": "Mensual",
    "b_a_meses": 48,
    "b_a_periodicidad_pago": "Mensual",
    "b_a_pago": "Vencida",
    "b_b_capital": 30_000_000.0,
    "b_b_tasa": 17.0,
    "b_b_tipo": "Nominal Anual Anticipada",
    "b_b_periodicidad_tasa": "Mensual",
    "b_b_meses": 48,
    "b_b_periodicidad_pago": "Mensual",
    "b_b_pago": "Anticipada",
    "b_fuente": "",
    "b_fecha": None,
}

CASO_C = {
    "c_meta": 60_000_000.0,
    "c_meses": 60,
    "c_tasa": 9.0,
    "c_tipo": "Efectiva Anual (EA)",
    "c_periodicidad": "Mensual",
    "c_capital": 5_000_000.0,
    "c_plan": PLAN_GEOMETRICO,
    "c_crecimiento_pct": 6.0,
    "c_crecimiento_cop": 60_000.0,
    "c_fuente": "",
    "c_fecha": None,
}

TEMAS_POR_CASO = [
    {
        "Caso": "A. ¿Dónde pongo mi plata?",
        "Temas que cubre": "Interés simple, interés compuesto, rentabilidad y equivalencia de tasas (tasa combinada y retención)",
        "Dónde se ve": "El CDT retira intereses sin reinvertirlos (simple); la cuenta y la alternativa capitalizan (compuesto)",
    },
    {
        "Caso": "B. ¿Me conviene este crédito?",
        "Temas que cubre": "Equivalencia de tasas (incluida la anticipada), series uniformes y amortización",
        "Dónde se ve": "La oferta B tiene tasa nominal anticipada y pago anticipado; la cuota fija es una serie uniforme",
    },
    {
        "Caso": "C. ¿Cuánto debo ahorrar para mi meta?",
        "Temas que cubre": "Series uniformes, gradientes aritmético y geométrico, e interés compuesto",
        "Dónde se ve": "El plan se elige entre cuota uniforme o gradiente; el capital inicial crece con interés compuesto",
    },
]
