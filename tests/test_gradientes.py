"""Pruebas para flujos de gradientes aritméticos y geométricos."""

import unittest

from modules.gradientes import calcular_gradiente_aritmetico, calcular_gradiente_geometrico


class GradientesTest(unittest.TestCase):
    def test_gradiente_aritmetico_y_incremento_desde_segundo_pago(self):
        pagos, presente = calcular_gradiente_aritmetico(100, 10, 10, 3)
        self.assertEqual(pagos, [100, 110, 120])
        self.assertAlmostEqual(presente, 271.9759579264)

    def test_gradiente_geometrico(self):
        pagos, presente = calcular_gradiente_geometrico(100, 10, 10, 3)
        for pago, esperado in zip(pagos, [100, 110, 121]):
            self.assertAlmostEqual(pago, esperado)
        self.assertAlmostEqual(presente, 272.7272727273)

    def test_tasa_de_descuento_cero(self):
        pagos_a, presente_a = calcular_gradiente_aritmetico(100, 10, 0, 3)
        pagos_g, presente_g = calcular_gradiente_geometrico(100, 10, 0, 3)
        self.assertEqual((pagos_a, presente_a), ([100, 110, 120], 330))
        for pago, esperado in zip(pagos_g, [100, 110, 121]):
            self.assertAlmostEqual(pago, esperado)
        self.assertAlmostEqual(presente_g, 331)

    def test_crecimiento_geometrico_negativo_valido(self):
        pagos, presente = calcular_gradiente_geometrico(100, -50, 0, 3)
        self.assertEqual(pagos, [100, 50, 25])
        self.assertEqual(presente, 175)

    def test_un_periodo(self):
        self.assertEqual(calcular_gradiente_aritmetico(100, -500, 10, 1), ([100], 100 / 1.1))
        self.assertEqual(calcular_gradiente_geometrico(100, -100, 10, 1), ([100], 100 / 1.1))

    def test_rechaza_periodos_tasas_y_pagos_invalidos(self):
        for periodos in (0, 2.5, 1001):
            with self.subTest(periodos=periodos), self.assertRaises(ValueError):
                calcular_gradiente_aritmetico(100, 10, 5, periodos)
        with self.assertRaises(ValueError):
            calcular_gradiente_aritmetico(100, -60, 0, 3)
        with self.assertRaises(ValueError):
            calcular_gradiente_geometrico(100, -100.01, 0, 3)
        with self.assertRaises(ValueError):
            calcular_gradiente_geometrico(100, 0, -100, 3)
        with self.assertRaises(ValueError):
            calcular_gradiente_aritmetico(float("nan"), 0, 0, 1)


if __name__ == "__main__":
    unittest.main()
