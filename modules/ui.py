"""Piezas de interfaz compartidas entre pantallas."""

import streamlit as st

from motor.formato import formato_cop


def mostrar_verificacion(verificacion: dict) -> None:
    """Muestra la comprobación de una tabla: verde si cumple y rojo si no cumple."""
    col_saldo, col_abonos = st.columns(2)
    with col_saldo:
        mensaje = f"Saldo final: {formato_cop(verificacion['saldo_final'])}"
        if verificacion["ok_saldo"]:
            st.success(f"✅ {mensaje} (cierra en cero)")
        else:
            st.error(f"❌ {mensaje} (no cierra en cero)")
    with col_abonos:
        mensaje = f"Suma de abonos: {formato_cop(verificacion['suma_abonos'])}"
        if verificacion["ok_abonos"]:
            st.success(f"✅ {mensaje} (igual al capital)")
        else:
            st.error(f"❌ {mensaje} (diferente del capital)")
