"""Pruebas automatizadas para las fórmulas de series uniformes vencidas."""

import unittest

from modules.series_uniformes import (
    cuota_para_prestamo,
    cuota_para_valor_futuro,
    valor_futuro_serie,
    valor_presente_serie,
)


class SeriesUniformesTest(unittest.TestCase):
    def test_valor_futuro_con_tasa_positiva(self):
        self.assertAlmostEqual(valor_futuro_serie(100, 10, 2), 210)

    def test_valor_presente_con_tasa_positiva(self):
        self.assertAlmostEqual(valor_presente_serie(100, 10, 2), 173.5537190083)

    def test_cuota_para_valor_futuro_con_tasa_positiva(self):
        cuota = cuota_para_valor_futuro(210, 10, 2)
        self.assertAlmostEqual(cuota, 100)
        self.assertAlmostEqual(valor_futuro_serie(cuota, 10, 2), 210)

    def test_cuota_para_prestamo_con_tasa_positiva(self):
        cuota = cuota_para_prestamo(173.5537190083, 10, 2)
        self.assertAlmostEqual(cuota, 100)
        self.assertAlmostEqual(valor_presente_serie(cuota, 10, 2), 173.5537190083)

    def test_limites_con_tasa_cero(self):
        self.assertEqual(valor_futuro_serie(100, 0, 5), 500)
        self.assertEqual(valor_presente_serie(100, 0, 5), 500)
        self.assertEqual(cuota_para_valor_futuro(500, 0, 5), 100)
        self.assertEqual(cuota_para_prestamo(500, 0, 5), 100)

    def test_rechaza_tasa_y_periodos_invalidos(self):
        with self.assertRaises(ValueError):
            valor_futuro_serie(100, -100, 2)
        with self.assertRaises(ValueError):
            valor_presente_serie(100, 5, 0)
        with self.assertRaises(ValueError):
            cuota_para_prestamo(100, 5, 2.5)


if __name__ == "__main__":
    unittest.main()
