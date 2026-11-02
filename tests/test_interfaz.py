"""Pruebas de la interfaz real con el simulador de Streamlit."""

import logging
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

logging.disable(logging.WARNING)
APP = str(Path(__file__).resolve().parent.parent / "app.py")
SECCIONES = {
    "interes": "💰 Interés Simple y Compuesto",
    "tasas": "📈 Tasas y Rentabilidad",
    "series": "🔁 Series Uniformes",
    "gradientes": "📉 Gradientes (Aritmético/Geom.)",
    "amortizacion": "🧾 Tablas de Amortización",
}


def abrir(seccion=None):
    app = AppTest.from_file(APP, default_timeout=60).run()
    if seccion:
        app.sidebar.radio[0].set_value(seccion).run()
    return app


def entrada(app, key=None, etiqueta=None):
    for widget in app.number_input:
        if (key and widget.key == key) or (etiqueta and widget.label.startswith(etiqueta)):
            return widget
    raise KeyError(key or etiqueta)


class PantallasTest(unittest.TestCase):
    def test_todas_las_secciones_abren_sin_error(self):
        app = abrir()
        for seccion in app.sidebar.radio[0].options:
            app = abrir(seccion)
            self.assertEqual(len(app.exception), 0, seccion)

    def test_la_convencion_de_dias_cambia_el_resultado(self):
        app = abrir(SECCIONES["interes"])
        app.selectbox(key="simple_unidad").set_value("Días").run()
        antes = [m.value for m in app.metric][:3]
        app.selectbox(key="simple_convencion").set_value("Exacto (365 días)").run()
        self.assertNotEqual(antes, [m.value for m in app.metric][:3])

    def test_recalcula_sin_pulsar_un_boton(self):
        app = abrir(SECCIONES["series"])
        antes = [m.value for m in app.metric]
        entrada(app, etiqueta="Tasa periódica").set_value(5.0).run()
        self.assertNotEqual(antes, [m.value for m in app.metric])

    def test_valores_borde_no_tumban_la_pantalla(self):
        casos = [
            ("amortizacion", "comp_tasa_ea", None, 0.0),
            ("interes", "comp_cap", None, 0.0),
            ("gradientes", None, "Gradiente constante", -200_000.0),
            ("tasas", None, "Valor final bruto", 9_000_000.0),
        ]
        for seccion, key, etiqueta, valor in casos:
            with self.subTest(seccion=seccion):
                app = abrir(SECCIONES[seccion])
                entrada(app, key, etiqueta).set_value(valor).run()
                self.assertEqual(len(app.exception), 0)

    def test_sustitucion_anticipada_incluye_el_factor(self):
        app = abrir(SECCIONES["series"])
        app.radio(key="serie_modalidad").set_value("Anticipada").run()
        self.assertTrue(any(r"\cdot (1 + 0.015)" in l.value for l in app.latex))


if __name__ == "__main__":
    unittest.main()
