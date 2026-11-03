"""Las tres preguntas de la vida real, resueltas con los módulos del curso.

Aquí no hay fórmulas nuevas salvo las que se explican en cada función: se combinan
las de interés, tasas, series, gradientes y amortización. Cada `evaluar_caso_*`
recibe un diccionario de parámetros y devuelve resultados y texto de decisión.
"""

import pandas as pd

from motor.amortizacion import (
    PERIODICIDADES_AMORT,
    SISTEMAS,
    tabla_amortizacion,
    verificar_amortizacion,
)
from motor.datos_ejemplo import INTERES_RETIRADO, PLAN_ARITMETICO, PLAN_GEOMETRICO, PLAN_UNIFORME
from motor.formato import formato_cop
from motor.interes import (
    DIAS_POR_CONVENCION,
    calcular_monto_interes_compuesto,
    calcular_monto_interes_simple,
)
from motor.series import cuota_para_valor_futuro
from motor.tasas import (
    PERIODICIDADES,
    a_efectiva_anual,
    periodica_desde_efectiva_anual,
    rentabilidad_con_retencion,
    tasa_combinada,
    tasa_real_fisher,
)

PERIODICIDADES_TASA = dict(PERIODICIDADES)
TOLERANCIA_EA = 0.005  # dos tasas EA a menos de esta distancia se consideran iguales
TOLERANCIA_COP = 1.0


# ------------------ CASO A: ¿DÓNDE PONGO MI PLATA? ------------------

def evaluar_inversion(
    nombre: str,
    monto: float,
    dias: float,
    ea_pct: float,
    retencion_pct: float,
    inflacion_pct: float,
    base_dias: float = 360.0,
    periodos_simple: int | None = None,
) -> dict:
    """Evalúa un producto. Si `periodos_simple` tiene valor, los intereses se retiran sin reinvertir."""
    anios = dias / base_dias

    def valor_bruto(dia: float) -> float:
        if periodos_simple is None:
            return calcular_monto_interes_compuesto(monto, ea_pct, dia / base_dias)[1]
        tasa_periodica = periodica_desde_efectiva_anual(ea_pct, periodos_simple)
        return calcular_monto_interes_simple(monto, tasa_periodica, dia / base_dias * periodos_simple)[1]

    vf_bruto = valor_bruto(dias)
    renta = rentabilidad_con_retencion(monto, vf_bruto, retencion_pct, dias, base_dias)
    vf_neto = monto + renta["rendimiento_neto"]

    # Ganancia real: el valor final en pesos de hoy, menos lo que se invirtió.
    ganancia_real = vf_neto / (1.0 + inflacion_pct / 100.0) ** anios - monto

    dias_grafico = [dias * k / 24 for k in range(25)]
    factor_neto = 1.0 - retencion_pct / 100.0
    saldos_netos = [monto + (valor_bruto(d) - monto) * factor_neto for d in dias_grafico]

    return {
        "nombre": nombre,
        "ea_ofrecida": ea_pct,
        "ea_bruta": renta["ea_bruta"],
        "ea_neta": renta["ea_neta"],
        "vf_bruto": vf_bruto,
        "retencion": renta["retencion_valor"],
        "intereses_netos": renta["rendimiento_neto"],
        "vf_neto": vf_neto,
        "ganancia_real": ganancia_real,
        "tasa_real": tasa_real_fisher(renta["ea_neta"], inflacion_pct),
        "dias": dias_grafico,
        "saldos": saldos_netos,
    }


def recomendar_inversion(productos: list[dict], dias: float) -> str:
    """Redacta la recomendación a partir de los resultados, nunca de un nombre fijo."""
    orden = sorted(productos, key=lambda p: p["vf_neto"], reverse=True)
    mejor, segundo = orden[0], orden[1]
    diferencia = mejor["vf_neto"] - segundo["vf_neto"]
    if diferencia < TOLERANCIA_COP:
        texto = f"{mejor['nombre']} y {segundo['nombre']} dejan prácticamente lo mismo en {dias:,.0f} días."
    else:
        texto = (
            f"Con estos datos conviene **{mejor['nombre']}**: en {dias:,.0f} días terminas con "
            f"{formato_cop(mejor['vf_neto'])} netos, {formato_cop(diferencia)} más que {segundo['nombre']}."
        )
    if mejor["ganancia_real"] > 0:
        texto += f" Descontando la inflación ganas {formato_cop(mejor['ganancia_real'])} en pesos de hoy."
    else:
        texto += f" Pero ninguna opción le gana a la inflación: pierdes {formato_cop(-mejor['ganancia_real'])} de poder adquisitivo."
    return texto


def evaluar_caso_a(p: dict) -> dict:
    """Compara CDT, cuenta de ahorros y alternativa a tasa combinada (inflación + puntos)."""
    base = DIAS_POR_CONVENCION[p["a_convencion"]]
    monto, dias, inflacion = p["a_monto"], p["a_dias"], p["a_inflacion"]

    m_cdt = PERIODICIDADES_TASA[p["a_cdt_periodicidad"]]
    ea_cdt = a_efectiva_anual(p["a_cdt_tasa"], p["a_cdt_tipo"], m_cdt)
    cdt = evaluar_inversion(
        "CDT", monto, dias, ea_cdt, p["a_cdt_retencion"], inflacion, base,
        periodos_simple=m_cdt if p["a_cdt_intereses"] == INTERES_RETIRADO else None,
    )

    m_ahorro = PERIODICIDADES_TASA[p["a_ahorro_periodicidad"]]
    ea_ahorro = a_efectiva_anual(p["a_ahorro_tasa"], p["a_ahorro_tipo"], m_ahorro)
    ahorro = evaluar_inversion("Cuenta de ahorros", monto, dias, ea_ahorro, p["a_ahorro_retencion"], inflacion, base)

    ea_combinada = tasa_combinada(inflacion, p["a_comb_puntos"])
    combinada = evaluar_inversion(
        f"Alternativa inflación + {p['a_comb_puntos']:g} puntos", monto, dias, ea_combinada, p["a_comb_retencion"], inflacion, base
    )

    productos = [cdt, ahorro, combinada]
    dias_grafico = cdt["dias"]
    return {
        "productos": productos,
        "mejor": max(productos, key=lambda x: x["vf_neto"]),
        "recomendacion": recomendar_inversion(productos, dias),
        "dias": dias_grafico,
        "poder_adquisitivo": [monto * (1.0 + inflacion / 100.0) ** (d / base) for d in dias_grafico],
    }


# ------------------ CASO B: ¿ME CONVIENE ESTE CRÉDITO? ------------------

def valor_presente_pagos(tabla: pd.DataFrame, tasa_descuento_ea: float, pagos_por_anio: int) -> float:
    """Trae cada pago a hoy: VP = suma de Pago_t / (1 + d)^(t / m). El periodo 0 no se descuenta."""
    d = tasa_descuento_ea / 100.0
    return float(sum(
        pago / (1.0 + d) ** (periodo / pagos_por_anio)
        for periodo, pago in zip(tabla["Período"], tabla["Cuota (COP)"])
    ))


def cuotas_del_plazo(meses: int, pagos_por_anio: int) -> int:
    """Número de pagos del plazo. El plazo debe ser múltiplo de la periodicidad de pago."""
    cuotas = meses * pagos_por_anio / 12
    if cuotas < 1 or cuotas != int(cuotas):
        meses_por_pago = 12 // pagos_por_anio
        raise ValueError(f"Un plazo de {meses} meses no se divide en pagos cada {meses_por_pago} mes(es).")
    return int(cuotas)


def evaluar_oferta(
    nombre: str,
    capital: float,
    tasa: float,
    tipo: str,
    periodicidad_tasa: str,
    meses: int,
    periodicidad_pago: str,
    pago: str,
    tasa_descuento_ea: float,
) -> dict:
    """Convierte la tasa a EA y genera la tabla de cada sistema con sus totales."""
    ea = a_efectiva_anual(tasa, tipo, PERIODICIDADES_TASA[periodicidad_tasa])
    m_pago = PERIODICIDADES_AMORT[periodicidad_pago]
    tasa_periodica = periodica_desde_efectiva_anual(ea, m_pago) / 100.0
    n = cuotas_del_plazo(meses, m_pago)

    sistemas = {}
    for sistema in SISTEMAS:
        tabla = tabla_amortizacion(capital, tasa_periodica, n, sistema, pago)
        verificacion = verificar_amortizacion(tabla, capital)
        sistemas[sistema] = {
            "tabla": tabla,
            "verificacion": verificacion,
            "cuota_inicial": float(tabla["Cuota (COP)"].iloc[0]),
            "cuota_final": float(tabla["Cuota (COP)"].iloc[-1]),
            "intereses": verificacion["total_intereses"],
            "total_pagado": verificacion["total_pagado"],
            "costo_hoy": valor_presente_pagos(tabla, tasa_descuento_ea, m_pago) - capital,
        }
    return {
        "nombre": nombre,
        "capital": capital,
        "ea": ea,
        "tasa_periodica": tasa_periodica,
        "n": n,
        "m_pago": m_pago,
        "meses": meses,
        "pago": pago,
        "sistemas": sistemas,
    }


def veredicto_credito(a: dict, b: dict, sistema: str, tasa_descuento_ea: float) -> dict:
    """Decide por la menor EA; si son iguales, por el menor costo en pesos de hoy."""
    costo_a, costo_b = a["sistemas"][sistema]["costo_hoy"], b["sistemas"][sistema]["costo_hoy"]
    if abs(a["ea"] - b["ea"]) >= TOLERANCIA_EA:
        ganadora, otra = (a, b) if a["ea"] < b["ea"] else (b, a)
    elif abs(costo_a - costo_b) >= TOLERANCIA_COP:
        ganadora, otra = (a, b) if costo_a < costo_b else (b, a)
    else:
        return {"ganadora": None, "texto": "Las dos ofertas cuestan lo mismo: decide por otras condiciones.", "avisos": []}

    r_g, r_o = ganadora["sistemas"][sistema], otra["sistemas"][sistema]
    ahorro_hoy = r_o["costo_hoy"] - r_g["costo_hoy"]
    dif_intereses = r_o["intereses"] - r_g["intereses"]

    texto = (
        f"La oferta **{ganadora['nombre']}** es más barata: cuesta {ganadora['ea']:.2f}% EA "
        f"frente a {otra['ea']:.2f}% EA de la oferta {otra['nombre']}."
    )
    if ahorro_hoy > 0:
        texto += f" Te ahorra {formato_cop(ahorro_hoy)} en pesos de hoy, descontando al {tasa_descuento_ea:g}% EA."
    palabra = "menos" if dif_intereses >= 0 else "más"
    texto += f" En intereses totales pagas {formato_cop(abs(dif_intereses))} {palabra}."

    avisos = []
    if ahorro_hoy <= 0:
        avisos.append(
            f"A tu tasa de descuento del {tasa_descuento_ea:g}% EA, la oferta {otra['nombre']} cuesta "
            f"{formato_cop(-ahorro_hoy)} menos en pesos de hoy, aunque su EA sea mayor: el dinero se paga más tarde."
        )
    if a["capital"] != b["capital"]:
        avisos.append("Las ofertas prestan montos diferentes: compara también si necesitas todo el capital.")
    if a["meses"] != b["meses"]:
        avisos.append("Los plazos son diferentes: el de plazo más largo suele acumular más intereses aunque tenga menor tasa.")
    return {"ganadora": ganadora["nombre"], "texto": texto, "avisos": avisos}


def evaluar_caso_b(p: dict) -> dict:
    """Evalúa las ofertas A y B en ambos sistemas y da el veredicto del sistema elegido."""
    d = p["b_descuento"]
    ofertas = []
    for letra in ("a", "b"):
        ofertas.append(evaluar_oferta(
            letra.upper(),
            p[f"b_{letra}_capital"],
            p[f"b_{letra}_tasa"],
            p[f"b_{letra}_tipo"],
            p[f"b_{letra}_periodicidad_tasa"],
            int(p[f"b_{letra}_meses"]),
            p[f"b_{letra}_periodicidad_pago"],
            p[f"b_{letra}_pago"],
            d,
        ))
    return {"a": ofertas[0], "b": ofertas[1], "veredicto": veredicto_credito(ofertas[0], ofertas[1], p["b_sistema"], d)}


# ------------------ CASO C: ¿CUÁNTO DEBO AHORRAR PARA MI META? ------------------

def plan_de_ahorro(
    meta: float,
    meses: int,
    ea_pct: float,
    capital_inicial: float = 0.0,
    plan: str = PLAN_UNIFORME,
    crecimiento_pct: float = 0.0,
    crecimiento_cop: float = 0.0,
) -> dict:
    """Halla la primera cuota mensual con la que el saldo llega exactamente a la meta.

    La cuota no cambia durante 12 meses y sube al empezar cada año, como un aumento de sueldo.
    Con `año(t)` = 0 en los primeros 12 meses, 1 en los siguientes, etc.:

        Uniforme:    Cuota(t) = A1
        Aritmético:  Cuota(t) = A1 + G * año(t)
        Geométrico:  Cuota(t) = A1 * (1 + g) ^ año(t)

    La cuota t gana intereses durante (n - t) meses, y la meta debe cumplir:

        Meta = K * (1 + i)^n + suma de Cuota(t) * (1 + i)^(n - t)

    La suma se separa en una parte que multiplica a A1 y otra que multiplica a G:

        A1 = [Meta - K * (1 + i)^n - G * F_G] / F_A
        F_A = suma de peso(t) * (1 + i)^(n - t), con peso(t) = 1 o (1 + g)^año(t)
        F_G = suma de año(t) * (1 + i)^(n - t)
    """
    if meta <= 0 or meses < 1 or capital_inicial < 0:
        raise ValueError("La meta y el plazo deben ser positivos, y el capital inicial no puede ser negativo.")
    if plan not in (PLAN_UNIFORME, PLAN_ARITMETICO, PLAN_GEOMETRICO):
        raise ValueError(f"Plan desconocido: {plan}")

    i = periodica_desde_efectiva_anual(ea_pct, 12) / 100.0
    g = crecimiento_pct / 100.0 if plan == PLAN_GEOMETRICO else 0.0
    incremento = crecimiento_cop if plan == PLAN_ARITMETICO else 0.0

    anio = [(t - 1) // 12 for t in range(1, meses + 1)]
    peso = [(1.0 + g) ** a for a in anio]
    capitalizacion = [(1.0 + i) ** (meses - t) for t in range(1, meses + 1)]
    factor_a = sum(w * c for w, c in zip(peso, capitalizacion))
    factor_g = sum(a * c for a, c in zip(anio, capitalizacion))

    # Lo que falta después de que el capital inicial crece con interés compuesto.
    _, capital_al_final = calcular_monto_interes_compuesto(capital_inicial, ea_pct, meses / 12)
    faltante = meta - capital_al_final

    if faltante <= 0:
        primera_cuota, incremento = 0.0, 0.0
        peso = [0.0] * meses
    else:
        primera_cuota = (faltante - incremento * factor_g) / factor_a
        if primera_cuota < 0:
            raise ValueError("El aumento anual es tan alto que la primera cuota sería negativa: redúcelo.")

    filas = []
    saldo = capital_inicial
    for t, (a, w) in enumerate(zip(anio, peso), start=1):
        aporte = primera_cuota * w + incremento * a
        interes = saldo * i
        saldo += interes + aporte
        filas.append({
            "Mes": t,
            "Año": a + 1,
            "Aporte (COP)": aporte,
            "Interés Ganado (COP)": interes,
            "Saldo Acumulado (COP)": saldo,
        })
    calendario = pd.DataFrame(filas)

    total_cuotas = float(calendario["Aporte (COP)"].sum())
    total_aportado = capital_inicial + total_cuotas
    return {
        "calendario": calendario,
        "tasa_mensual": i,
        "capital_al_final": capital_al_final,
        "faltante": max(faltante, 0.0),
        "cuota_inicial": float(calendario["Aporte (COP)"].iloc[0]),
        "cuota_final": float(calendario["Aporte (COP)"].iloc[-1]),
        "cuota_uniforme": cuota_para_valor_futuro(max(faltante, 0.0), i * 100.0, meses),
        "total_cuotas": total_cuotas,
        "total_aportado": total_aportado,
        "saldo_final": saldo,
        "intereses": saldo - total_aportado,
        "ok_meta": saldo >= meta - TOLERANCIA_COP,
        "ya_cubierta": faltante <= 0,
    }


def evaluar_caso_c(p: dict) -> dict:
    """Calcula el plan elegido y redacta la decisión comparándolo con la cuota uniforme."""
    ea = a_efectiva_anual(p["c_tasa"], p["c_tipo"], PERIODICIDADES_TASA[p["c_periodicidad"]])
    meses = int(p["c_meses"])
    plan = plan_de_ahorro(p["c_meta"], meses, ea, p["c_capital"], p["c_plan"], p["c_crecimiento_pct"], p["c_crecimiento_cop"])
    plan["ea"] = ea

    if plan["ya_cubierta"]:
        texto = (
            f"Tu capital inicial ya alcanza la meta: sin aportar nada más llega a {formato_cop(plan['saldo_final'])} "
            f"en {meses} meses."
        )
    elif p["c_plan"] == PLAN_UNIFORME:
        texto = (
            f"Para llegar a {formato_cop(p['c_meta'])} en {meses} meses debes ahorrar "
            f"**{formato_cop(plan['cuota_inicial'])} al mes**. Los intereses aportan {formato_cop(plan['intereses'])} de la meta."
        )
    else:
        texto = (
            f"Para llegar a {formato_cop(p['c_meta'])} en {meses} meses empiezas con "
            f"**{formato_cop(plan['cuota_inicial'])} al mes** y terminas con {formato_cop(plan['cuota_final'])}. "
            f"Con cuota uniforme serían {formato_cop(plan['cuota_uniforme'])} desde el primer mes. "
            "Conviene si esperas que tus ingresos suban cada año."
        )
    plan["recomendacion"] = texto
    return plan
