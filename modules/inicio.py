"""Panel principal: todo lo que muestra sale del motor con los parámetros actuales de los casos."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.ui import COLORES, aplicar_estilo, parametros, texto_dinero
from motor.datos_ejemplo import CASO_A, CASO_B, CASO_C, TEMAS_POR_CASO
from motor.decisiones import evaluar_caso_a, evaluar_caso_b, evaluar_caso_c
from motor.formato import formato_cop

PREGUNTAS = [
    ("💸 ¿Dónde pongo mi plata?", "Compara CDT, cuenta de ahorros y una alternativa a tasa combinada."),
    ("🏦 ¿Me conviene este crédito?", "Pon dos ofertas lado a lado y descubre cuál es más barata y por cuánto."),
    ("🎯 ¿Cuánto debo ahorrar para mi meta?", "Calcula la cuota con un plan uniforme o con cuotas crecientes."),
]


def _ir_a(seccion: str) -> None:
    st.session_state["nav"] = seccion


def _evaluar(funcion, caso: dict):
    """Evalúa un caso; si los datos editados no son válidos, devuelve None en lugar de caerse."""
    try:
        return funcion(parametros(caso))
    except ValueError:
        return None


def _oferta_recomendada(credito: dict) -> dict:
    """Devuelve la oferta ganadora. Si hay empate, usa la A, porque cuestan lo mismo."""
    return credito["b"] if credito["veredicto"]["ganadora"] == "B" else credito["a"]


def _indicadores(inversion, credito, ahorro, sistema: str) -> None:
    st.subheader("📌 Indicadores clave")
    k1, k2, k3, k4 = st.columns(4)
    if inversion:
        mejor = inversion["mejor"]
        k1.metric("EA neta de la mejor inversión", f"{mejor['ea_neta']:.2f}%", delta=mejor["nombre"], delta_color="off", delta_arrow="off")
    if credito:
        oferta = _oferta_recomendada(credito)
        resumen = oferta["sistemas"][sistema]
        k2.metric("Cuota del crédito recomendado", formato_cop(resumen["cuota_inicial"]), delta=f"Oferta {oferta['nombre']}, {oferta['ea']:.2f}% EA", delta_color="off", delta_arrow="off")
        k3.metric("Intereses totales del crédito", formato_cop(resumen["intereses"]))
        k4.metric("Saldo final del crédito", formato_cop(resumen["verificacion"]["saldo_final"]), delta="Verificado" if resumen["verificacion"]["ok_saldo"] else "No cierra", delta_color="off", delta_arrow="off")
    if ahorro:
        st.caption(texto_dinero(f"Plan de ahorro: cuota inicial de {formato_cop(ahorro['cuota_inicial'])} y saldo acumulado de {formato_cop(ahorro['saldo_final'])}."))


def _resumen(inversion, credito, ahorro, sistema: str) -> None:
    filas = []
    if inversion:
        mejor = inversion["mejor"]
        filas.append({"Caso": "A. Inversión", "Tasa": f"{mejor['ea_neta']:.2f}% EA neta", "Resultado": f"Valor final neto: {formato_cop(mejor['vf_neto'])}"})
    if credito:
        oferta = _oferta_recomendada(credito)
        filas.append({"Caso": "B. Crédito", "Tasa": f"{oferta['ea']:.2f}% EA", "Resultado": f"Total pagado: {formato_cop(oferta['sistemas'][sistema]['total_pagado'])}"})
    if ahorro:
        filas.append({"Caso": "C. Ahorro", "Tasa": f"{ahorro['ea']:.2f}% EA", "Resultado": f"Intereses ganados: {formato_cop(ahorro['intereses'])}"})
    st.subheader("📑 Resumen de los casos aplicados")
    st.dataframe(pd.DataFrame(filas), width="stretch", hide_index=True)


def _grafico_tasas(inversion, credito) -> None:
    fig = go.Figure()
    if inversion:
        productos = inversion["productos"]
        fig.add_trace(go.Bar(
            y=[p["nombre"] for p in productos], x=[p["ea_neta"] for p in productos], orientation="h",
            name="Inversión (EA neta)", marker_color=COLORES[0], text=[f"{p['ea_neta']:.2f}%" for p in productos], textposition="outside",
        ))
    if credito:
        ofertas = [credito["a"], credito["b"]]
        fig.add_trace(go.Bar(
            y=[f"Crédito: oferta {o['nombre']}" for o in ofertas], x=[o["ea"] for o in ofertas], orientation="h",
            name="Crédito (EA)", marker_color=COLORES[1], text=[f"{o['ea']:.2f}%" for o in ofertas], textposition="outside",
        ))
    aplicar_estilo(fig, "Tasas efectivas anuales evaluadas", "Tasa efectiva anual (% EA)", "", 400)
    # Se deja espacio a la derecha para que las etiquetas de valor no se recorten.
    tasas = [x for traza in fig.data for x in traza.x]
    fig.update_layout(hovermode="closest", yaxis=dict(autorange="reversed"), xaxis=dict(range=[0, max(tasas, default=1) * 1.3]), margin=dict(t=110))
    st.plotly_chart(fig, width="stretch")


def _decisiones(inversion, credito, ahorro) -> None:
    st.subheader("✅ Decisión recomendada")
    casos = [
        ("A. ¿Dónde pongo mi plata?", inversion and inversion["recomendacion"]),
        ("B. ¿Me conviene este crédito?", credito and credito["veredicto"]["texto"]),
        ("C. ¿Cuánto debo ahorrar para mi meta?", ahorro and ahorro["recomendacion"]),
    ]
    for titulo, texto in casos:
        if texto:
            st.success(texto_dinero(f"**{titulo}** {texto}"))
        else:
            st.error(f"**{titulo}** Revisa los datos de este caso: no se pudo calcular.")


def render(integrantes: list[str], secciones_modulos: list[str]) -> None:
    pastillas = "".join(f'<span class="team-pill">🎓 {nombre}</span>' for nombre in integrantes)
    st.markdown(
        f"""
        <section class="hero">
            <h1>FinanzasLab: tus decisiones de dinero, con ingeniería financiera</h1>
            <p>Taller Final de Ingeniería Financiera. Interés simple y compuesto, equivalencia de tasas, series uniformes, gradientes y amortización aplicados a tres preguntas de la vida real.</p>
            <div class="team-container">{pastillas}<span class="team-pill">🏛️ UPB, Escuela de Ingenierías</span></div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("🧭 ¿Qué quieres resolver?")
    for columna, (pregunta, descripcion) in zip(st.columns(3, gap="medium"), PREGUNTAS):
        with columna:
            st.markdown(f'<div class="section-card"><h3>{pregunta}</h3><p>{descripcion}</p></div>', unsafe_allow_html=True)
            st.button("Abrir", key=f"ir_{pregunta}", on_click=_ir_a, args=(pregunta,), width="stretch")

    inversion = _evaluar(evaluar_caso_a, CASO_A)
    credito = _evaluar(evaluar_caso_b, CASO_B)
    ahorro = _evaluar(evaluar_caso_c, CASO_C)
    sistema = st.session_state["b_sistema"]

    st.info("🧪 Estos resultados usan los parámetros actuales de cada caso. Los valores precargados son datos de ejemplo, no ofertas reales.")
    _indicadores(inversion, credito, ahorro, sistema)
    _decisiones(inversion, credito, ahorro)

    col_resumen, col_grafico = st.columns([0.5, 0.5], gap="large")
    with col_resumen:
        _resumen(inversion, credito, ahorro, sistema)
    with col_grafico:
        _grafico_tasas(inversion, credito)

    st.subheader("🗂️ Qué tema cubre cada caso")
    st.table(pd.DataFrame(TEMAS_POR_CASO).set_index("Caso"))

    st.subheader("🧮 Módulos del curso")
    for inicio_fila in range(0, len(secciones_modulos), 3):
        fila = secciones_modulos[inicio_fila:inicio_fila + 3]
        for columna, seccion in zip(st.columns(3), fila):
            columna.button(seccion, key=f"ir_{seccion}", on_click=_ir_a, args=(seccion,), width="stretch")
