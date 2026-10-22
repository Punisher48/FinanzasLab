"""Pruebas automatizadas de las conversiones de tasas y rentabilidad."""

import unittest

from modules.tasas import (
    efectiva_anual_desde_nominal,
    efectiva_anual_desde_periodica,
    periodica_desde_efectiva_anual,
    rentabilidad_porcentual,
)


class TasasTest(unittest.TestCase):
    def test_tasa_periodica_a_efectiva_anual(self):
        self.assertAlmostEqual(efectiva_anual_desde_periodica(1, 12), 12.6825030132)

    def test_tasa_efectiva_anual_a_periodica(self):
        periodica = periodica_desde_efectiva_anual(12, 12)
        self.assertAlmostEqual(periodica, 0.9488792935)
        self.assertAlmostEqual(efectiva_anual_desde_periodica(periodica, 12), 12)

    def test_tasa_nominal_a_efectiva_anual(self):
        self.assertAlmostEqual(efectiva_anual_desde_nominal(12, 12), 12.6825030132)

    def test_rentabilidad_del_periodo(self):
        self.assertAlmostEqual(rentabilidad_porcentual(1_000_000, 1_120_000), 12)
        self.assertAlmostEqual(rentabilidad_porcentual(100, 80), -20)

    def test_rechaza_tasas_incoherentes_y_periodos_invalidos(self):
        with self.assertRaises(ValueError):
            efectiva_anual_desde_periodica(-100, 12)
        with self.assertRaises(ValueError):
            periodica_desde_efectiva_anual(-100, 12)
        with self.assertRaises(ValueError):
            efectiva_anual_desde_nominal(-1200, 12)
        with self.assertRaises(ValueError):
            efectiva_anual_desde_periodica(5, 0)

    def test_rechaza_valor_inicial_cero(self):
        with self.assertRaises(ValueError):
            rentabilidad_porcentual(0, 100)


if __name__ == "__main__":
    unittest.main()
