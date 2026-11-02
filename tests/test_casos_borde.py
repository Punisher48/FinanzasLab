"""Casos borde del motor: tasa 0, plazo 1, valores negativos y convención de días."""

import unittest

from motor import amortizacion as am
from motor import gradientes as gr
from motor import interes as it
from motor import series as se
from motor import tasas as ta


class ConvencionDiasTest(unittest.TestCase):
    def test_la_convencion_cambia_el_resultado_en_dias(self):
        t360 = it.tiempo_en_unidad_de_tasa(90, "Días", "Año", "Comercial (360 días)")
        t365 = it.tiempo_en_unidad_de_tasa(90, "Días", "Año", "Exacto (365 días)")
        self.assertAlmostEqual(t360, 0.25)
        self.assertAlmostEqual(t365, 90 / 365)
        self.assertAlmostEqual(it.calcular_monto_interes_simple(1000, 12, t360)[1], 1030.0)

    def test_tasa_mensual_con_plazo_en_dias(self):
        self.assertAlmostEqual(it.tiempo_en_unidad_de_tasa(90, "Días", "Mes", "Comercial (360 días)"), 3.0)


class ValoresInvalidosTest(unittest.TestCase):
    def test_negativos_e_imposibles_se_rechazan(self):
        casos = [
            lambda: it.calcular_monto_interes_simple(-1000, 10, 2),
            lambda: it.calcular_monto_interes_compuesto(-1000, 10, 2),
            lambda: it.calcular_saldos_compuesto(1000, -150, 2),
            lambda: it.despejar_tiempo_interes_simple(1000, 800, 5),
            lambda: am.amortizacion_frances(1000, -0.5, 2),
            lambda: am.amortizacion_aleman(1000, -2.0, 2),
            lambda: gr.calcular_gradiente_aritmetico(100, 1, -100, 2),
            lambda: gr.calcular_gradiente_geometrico(100, 1, -100, 2),
            lambda: ta.rentabilidad_con_retencion(100, 110, 4, 0),
            lambda: am.calcular_tasa_periodica(24, "Tipo inventado", "Mensual"),
            lambda: am.calcular_tasa_periodica(24, "Nominal Anual Vencida", "Quincenal"),
        ]
        for i, caso in enumerate(casos):
            with self.subTest(caso=i):
                with self.assertRaises(ValueError):
                    caso()


class TasasBordeTest(unittest.TestCase):
    def test_tabla_con_tasa_mayor_a_100(self):
        tabla = ta.generar_tabla_equivalencias(150, "Efectiva Anual (EA)")
        fila = tabla[tabla["Periodicidad"] == "Anual"].iloc[0]
        self.assertEqual(fila["Periódica Anticipada (ia)"], "60.0000%")

    def test_nominal_anticipada_en_amortizacion(self):
        # 24% nominal mes anticipado: ia = 2%, iv = 0.02 / 0.98
        self.assertAlmostEqual(am.calcular_tasa_periodica(24, "Nominal Anual Anticipada", "Mensual"), 0.02 / 0.98)

    def test_retencion_con_base_365(self):
        res = ta.rentabilidad_con_retencion(1000, 1100, 0, 365, base_dias=365)
        self.assertAlmostEqual(res["ea_bruta"], 10.0)


class TasaCeroYPlazoUnoTest(unittest.TestCase):
    def test_series_y_gradientes_con_tasa_cero(self):
        self.assertAlmostEqual(se.valor_presente_serie(100, 0, 3, "Anticipada"), 300.0)
        self.assertAlmostEqual(gr.calcular_gradiente_aritmetico(100, 10, 0, 3)["valor_futuro"], 330.0)
        self.assertAlmostEqual(gr.calcular_gradiente_geometrico(100, 0, 0, 3)["cuota_equivalente"], 100.0)

    def test_plazo_uno(self):
        self.assertAlmostEqual(se.valor_futuro_serie(100, 10, 1, "Vencida"), 100.0)
        self.assertAlmostEqual(am.amortizacion_aleman(1000, 0.1, 1)["Cuota (COP)"].iloc[0], 1100.0)


if __name__ == "__main__":
    unittest.main()
