"""Sección "Supuestos y fórmulas": convenciones, fórmulas, fuentes con fecha y verificación en vivo."""

import pandas as pd
import streamlit as st

from motor.datos_ejemplo import TEMAS_POR_CASO
from motor.verificacion import matriz_verificacion

FUENTES_CONSULTADAS = [
    {
        "Dato": "Tarifas de retención sobre rendimientos financieros (fuentes secundarias, por confirmar)",
        "Fuente": "PwC, boletín sobre cambios en retención en la fuente: https://legalytributarioenlinea.co.pwc.com/",
        "Fecha de consulta": "02/11/2026",
    },
    {
        "Dato": "Tarifas de retención sobre rendimientos financieros (fuentes secundarias, por confirmar)",
        "Fuente": "Siempre al Día, tabla de retención 2026: https://siemprealdia.co/colombia/impuestos/tabla-de-retencion-en-la-fuente-2026/",
        "Fecha de consulta": "02/11/2026",
    },
]

CASOS_FUENTE = [
    ("A. Tasas de CDT, cuenta de ahorros, inflación y puntos", "a_"),
    ("B. Condiciones de las ofertas de crédito", "b_"),
    ("C. Rentabilidad del plan de ahorro", "c_"),
]


def _tabla_fuentes() -> pd.DataFrame:
    filas = []
    for dato, prefijo in CASOS_FUENTE:
        fuente = st.session_state.get(f"{prefijo}fuente") or "Pendiente: datos de ejemplo"
        fecha = st.session_state.get(f"{prefijo}fecha")
        filas.append({
            "Dato": dato,
            "Fuente": fuente,
            "Fecha de consulta": fecha.strftime("%d/%m/%Y") if fecha else "Pendiente",
        })
    return pd.DataFrame(filas + FUENTES_CONSULTADAS)


def render() -> None:
    st.title("Supuestos y fórmulas")
    st.write("Convención de días, tipos de tasa, periodicidad, fórmulas usadas, fuentes de datos con fecha de consulta y verificación del motor.")

    tab_supuestos, tab_formulas, tab_fuentes, tab_temas, tab_matriz = st.tabs([
        "📋 Supuestos",
        "📐 Fórmulas",
        "📎 Fuentes y fechas",
        "🗂️ Temas por caso",
        "✅ Verificación en vivo",
    ])

    with tab_supuestos:
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown(
                r"""
                ### Convención de días
                * **Comercial (360 días):** el año tiene 360 días y el mes 30.
                * **Exacta (365 días):** el año tiene 365 días.
                * La convención es un parámetro editable. Solo cambia el resultado cuando el plazo está en días.

                ### Tipos de tasa
                * **Efectiva periódica vencida ($i_v$):** los intereses se liquidan al final del periodo.
                * **Efectiva periódica anticipada ($i_a$):** los intereses se liquidan al inicio del periodo.
                * **Nominal anual ($j$):** se divide por $m$ para obtener la tasa del periodo, $i = j / m$.
                * **Efectiva anual (EA):** es la medida común con la que se comparan todas las tasas.

                ### Periodicidad ($m$, periodos por año)
                Anual 1, semestral 2, cuatrimestral 3, trimestral 4, bimestral 6, mensual 12 y diaria 360.
                """
            )
        with col2:
            st.markdown(
                r"""
                ### Forma de pago de un crédito
                * **Vencida:** pagos en los periodos $1, 2, \dots, n$.
                * **Anticipada:** pagos en los periodos $0, 1, \dots, n-1$. El primero no lleva intereses.
                * La forma de pago es independiente del tipo de tasa, que se convierte primero a EA.

                ### Retención en la fuente
                * Se aplica sobre los rendimientos, no sobre el capital.
                * Es un parámetro editable por producto. Valores precargados de ejemplo: 4% para el CDT y la alternativa, 7% para la cuenta de ahorros.
                * **Por confirmar:** estas tarifas vienen de fuentes secundarias. Verifícalas en el Estatuto Tributario y el Decreto 1625 de 2016.

                ### Plan de ahorro
                * Aportes mensuales vencidos. La cuota se mantiene 12 meses y sube al empezar cada año.

                ### Criterio del veredicto de crédito
                * Gana la menor EA. Si son iguales, gana el menor costo en pesos de hoy.
                * Comparar solo intereses totales favorece siempre al plazo más corto, por eso no es el criterio principal.

                ### Alcance
                * La recomendación compara dinero: no incluye liquidez, riesgo, seguros ni otros costos del producto.
                """
            )

    with tab_formulas:
        st.markdown(
            r"""
            | Tema | Concepto | Fórmula |
            | :--- | :--- | :--- |
            | **Interés simple** | Monto final | $M = C (1 + i \cdot t)$ |
            | | Interés | $I = C \cdot i \cdot t$ |
            | | Valor presente | $C = \frac{M}{1 + i \cdot t}$ |
            | | Despeje de tasa | $i = \frac{M - C}{C \cdot t}$ |
            | | Despeje de plazo | $t = \frac{M - C}{C \cdot i}$ |
            | **Interés compuesto** | Valor futuro | $VF = VP (1 + i)^n$ |
            | | Valor presente | $VP = VF (1 + i)^{-n}$ |
            | | Despeje de tasa | $i = (VF / VP)^{1/n} - 1$ |
            | | Despeje de periodos | $n = \frac{\ln(VF / VP)}{\ln(1 + i)}$ |
            | **Tasas** | Vencida a anticipada | $i_a = \frac{i_v}{1 + i_v}$ |
            | | Anticipada a vencida | $i_v = \frac{i_a}{1 - i_a}$ |
            | | Periódica a EA | $EA = (1 + i_v)^m - 1$ |
            | | EA a periódica | $i_v = (1 + EA)^{1/m} - 1$ |
            | | Tasa combinada | $i_t = (1 + \pi)(1 + s) - 1$ |
            | | Tasa real | $i_r = \frac{1 + i}{1 + \pi} - 1$ |
            | | EA neta de retención | $EA_n = \left(1 + \frac{(VF - C)(1 - r)}{C}\right)^{B/d} - 1$ |
            | **Series uniformes** | VF vencida | $VF = A \frac{(1 + i)^n - 1}{i}$ |
            | | VP vencida | $VP = A \frac{1 - (1 + i)^{-n}}{i}$ |
            | | Anticipada | Se multiplica la vencida por $(1 + i)$ |
            | **Gradiente aritmético** | Pago | $P_t = A_1 + (t - 1) G$ |
            | | Valor presente | $VP = A_1 \frac{1 - (1+i)^{-n}}{i} + \frac{G}{i}\left[\frac{1 - (1+i)^{-n}}{i} - \frac{n}{(1+i)^n}\right]$ |
            | **Gradiente geométrico** | Pago | $P_t = A_1 (1 + g)^{t - 1}$ |
            | | Valor presente, $i \neq g$ | $VP = A_1 \frac{1 - \left(\frac{1+g}{1+i}\right)^n}{i - g}$ |
            | | Valor presente, $i = g$ | $VP = \frac{n A_1}{1 + i}$ |
            | **Amortización** | Cuota fija vencida | $A = P \frac{i}{1 - (1 + i)^{-n}}$ |
            | | Cuota fija anticipada | $A = \frac{P}{\frac{1 - (1 + i)^{-n}}{i} (1 + i)}$ |
            | | Abono constante | $K = P / n$, $\; \text{Cuota}_t = K + S_{t-1} \cdot i$ |
            | | Costo en pesos de hoy | $\sum_t \frac{\text{Pago}_t}{(1 + d)^{t / m}} - P$ |
            | **Plan de ahorro** | Primera cuota | $A_1 = \frac{\text{Meta} - K (1 + i)^n - G \cdot F_G}{F_A}$ |
            | | Factores | $F_A = \sum_t w_t (1 + i)^{n-t}$, $\; F_G = \sum_t a_t (1 + i)^{n-t}$ |
            """
        )

    with tab_fuentes:
        st.write("Las filas de los casos se llenan con los campos de fuente y fecha de cada pregunta.")
        st.dataframe(_tabla_fuentes(), width="stretch", hide_index=True)

    with tab_temas:
        st.dataframe(pd.DataFrame(TEMAS_POR_CASO), width="stretch", hide_index=True)

    with tab_matriz:
        st.write(
            "Cada fila ejecuta el motor en este momento y lo compara con una referencia obtenida de otra forma. "
            "Las pruebas automáticas del repositorio, además, comparan cada módulo contra numpy-financial."
        )
        matriz = matriz_verificacion()
        fallas = sum("❌" in f["Estado"] for f in matriz)
        if fallas:
            st.error(f"❌ {fallas} de {len(matriz)} comprobaciones no coinciden.")
        else:
            st.success(f"✅ Las {len(matriz)} comprobaciones coinciden.")
        st.dataframe(pd.DataFrame(matriz), width="stretch", hide_index=True)
