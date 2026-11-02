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
    "a": "💸 ¿Dónde pongo mi plata?",
    "b": "🏦 ¿Me conviene este crédito?",
    "c": "🎯 ¿Cuánto debo ahorrar para mi meta?",
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


class PreguntasTest(unittest.TestCase):
    def test_recomendacion_a_cambia_con_los_datos(self):
        app = abrir(SECCIONES["a"])
        self.assertIn("conviene **CDT**", app.success[0].value)
        entrada(app, key="a_ahorro_tasa").set_value(30.0).run()
        self.assertIn("conviene **Cuenta de ahorros**", app.success[0].value)

    def test_veredicto_b_cambia_con_los_datos(self):
        app = abrir(SECCIONES["b"])
        self.assertIn("**B** es más barata", app.success[0].value)
        entrada(app, key="b_a_tasa").set_value(10.0).run()
        self.assertIn("**A** es más barata", app.success[0].value)
        self.assertEqual(len(app.exception), 0)

    def test_b_plazo_incompatible_muestra_mensaje(self):
        app = abrir(SECCIONES["b"])
        app.selectbox(key="b_a_periodicidad_pago").set_value("Trimestral").run()
        entrada(app, key="b_a_meses").set_value(10).run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("Revisa los datos" in e.value for e in app.error))

    def test_c_cambia_de_plan_sin_error(self):
        app = abrir(SECCIONES["c"])
        for plan in app.selectbox(key="c_plan").options:
            app.selectbox(key="c_plan").set_value(plan).run()
            self.assertEqual(len(app.exception), 0, plan)
            self.assertTrue(any("llega a la meta" in s.value for s in app.success))

    def test_tasa_cero_no_tumba_las_preguntas(self):
        for seccion, claves in (("a", ["a_cdt_tasa", "a_ahorro_tasa"]), ("b", ["b_a_tasa", "b_b_tasa"]), ("c", ["c_tasa"])):
            app = abrir(SECCIONES[seccion])
            for clave in claves:
                entrada(app, key=clave).set_value(0.0).run()
            self.assertEqual(len(app.exception), 0, seccion)

    def test_los_valores_editados_se_conservan_al_navegar(self):
        app = abrir(SECCIONES["a"])
        entrada(app, key="a_monto").set_value(7_000_000.0).run()
        app.sidebar.radio[0].set_value(SECCIONES["series"]).run()
        app.sidebar.radio[0].set_value(SECCIONES["a"]).run()
        self.assertEqual(entrada(app, key="a_monto").value, 7_000_000.0)

    def test_cada_pregunta_marca_datos_de_ejemplo_y_pide_fuente(self):
        for seccion in ("a", "b", "c"):
            app = abrir(SECCIONES[seccion])
            self.assertTrue(any("Datos de ejemplo" in w.value for w in app.warning), seccion)
            self.assertEqual(app.text_input(key=f"{seccion}_fuente").value, "")


if __name__ == "__main__":
    unittest.main()
