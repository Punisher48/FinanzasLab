"""Piezas de interfaz compartidas entre pantallas."""

import streamlit as st

from motor.datos_ejemplo import CASO_A, CASO_B, CASO_C
from motor.formato import formato_cop

# Paleta categórica en orden fijo: cada serie conserva su color. El gris es para referencias.
COLORES = ["#2a78d6", "#eb6834", "#1baf7a"]
GRIS = "#6b7280"
PREFIJOS_CASOS = ("a_", "b_", "c_")


def texto_dinero(texto: str) -> str:
    """Escapa el signo $ para que Streamlit no interprete las cifras como fórmulas matemáticas."""
    return texto.replace("$", r"\$")


def iniciar_estado() -> None:
    """Carga los datos de ejemplo una vez y conserva lo editado al cambiar de sección.

    Streamlit olvida el valor de un control que no se dibuja en la página actual. Volver a
    asignarlo al inicio de cada ejecución lo conserva, y así el panel principal puede leerlo.
    """
    for clave in list(st.session_state):
        if clave.startswith(PREFIJOS_CASOS):
            st.session_state[clave] = st.session_state[clave]
    for caso in (CASO_A, CASO_B, CASO_C):
        for clave, valor in caso.items():
            st.session_state.setdefault(clave, valor)


def parametros(caso: dict) -> dict:
    """Lee los valores actuales de un caso."""
    return {clave: st.session_state[clave] for clave in caso}


def aviso_datos_ejemplo() -> None:
    st.warning(
        "🧪 **Datos de ejemplo.** Las cifras precargadas ilustran el cálculo y no son ofertas reales de "
        "ninguna entidad. Reemplázalas por datos consultados y registra abajo la fuente y la fecha."
    )


def campos_fuente(prefijo: str) -> None:
    """Campos que el equipo completa con la fuente de los datos y su fecha de consulta."""
    st.markdown("##### 📎 Fuente de los datos")
    col_fuente, col_fecha = st.columns([0.7, 0.3])
    col_fuente.text_input("Fuente (entidad, documento o enlace)", key=f"{prefijo}fuente", placeholder="Pendiente de completar")
    col_fecha.date_input("Fecha de consulta", key=f"{prefijo}fecha", format="DD/MM/YYYY")


def aplicar_estilo(fig, titulo: str, eje_x: str, eje_y: str, altura: int = 340):
    """Da a todos los gráficos título, unidades en los ejes y el mismo aspecto."""
    fig.update_layout(
        title=titulo,
        xaxis_title=eje_x,
        yaxis_title=eje_y,
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=80, b=20),
        height=altura,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0),
        separators=",.",
    )
    return fig


def tabla_cop(tabla, columnas_cop: list[str]):
    """Devuelve una copia de la tabla con las columnas de dinero formateadas."""
    copia = tabla.copy()
    for columna in columnas_cop:
        if columna in copia:
            copia[columna] = copia[columna].map(formato_cop)
    return copia


def mostrar_verificacion(verificacion: dict) -> None:
    """Muestra la comprobación de una tabla: verde si cumple y rojo si no cumple."""
    col_saldo, col_abonos = st.columns(2)
    with col_saldo:
        mensaje = f"Saldo final: {formato_cop(verificacion['saldo_final'])}"
        if verificacion["ok_saldo"]:
            st.success(texto_dinero(f"✅ {mensaje} (cierra en cero)"))
        else:
            st.error(texto_dinero(f"❌ {mensaje} (no cierra en cero)"))
    with col_abonos:
        mensaje = f"Suma de abonos: {formato_cop(verificacion['suma_abonos'])}"
        if verificacion["ok_abonos"]:
            st.success(texto_dinero(f"✅ {mensaje} (igual al capital)"))
        else:
            st.error(texto_dinero(f"❌ {mensaje} (diferente del capital)"))
