"""Pruebas para gradientes aritméticos y geométricos."""

import unittest
from modules.gradientes import (
    calcular_gradiente_aritmetico,
    calcular_gradiente_geometrico,
)


class GradientesTest(unittest.TestCase):
    def test_gradiente_aritmetico_completo(self):
        # A1 = 100, G = 20, i = 10%, n = 3
        # Pagos: 100, 120, 140
        # VP = 100/1.1 + 120/1.21 + 140/1.331 = 295.2667
        # VF = 295.2667 * 1.331 = 393
        # A_eq = 295.2667 * (0.10 / (1 - 1.1^-3)) = 118.7312
        res = calcular_gradiente_aritmetico(100.0, 20.0, 10.0, 3)
        self.assertEqual(res["pagos"], [100.0, 120.0, 140.0])
        self.assertAlmostEqual(res["valor_presente"], 295.266717, places=2)
        self.assertAlmostEqual(res["valor_futuro"], 393.0, places=1)
        self.assertAlmostEqual(res["cuota_equivalente"], 118.731175, places=2)

    def test_gradiente_geometrico_completo(self):
        # A1 = 100, g = 5%, i = 10%, n = 3
        # Pagos: 100, 105, 110.25
        # VP = 100/1.1 + 105/1.21 + 110.25/1.331 = 90.909 + 86.777 + 82.832 = 260.5186
        res = calcular_gradiente_geometrico(100.0, 5.0, 10.0, 3)
        self.assertEqual(len(res["pagos"]), 3)
        self.assertAlmostEqual(res["pagos"][1], 105.0)
        self.assertAlmostEqual(res["pagos"][2], 110.25)
        self.assertAlmostEqual(res["valor_presente"], 260.518407, places=2)
        self.assertAlmostEqual(res["valor_futuro"], 260.518407 * (1.1 ** 3), places=2)

    def test_gradiente_geometrico_caso_i_igual_g(self):
        # A1 = 100, g = 10%, i = 10%, n = 3
        # VP = 3 * 100 / 1.1 = 300 / 1.1 = 272.7272
        res = calcular_gradiente_geometrico(100.0, 10.0, 10.0, 3)
        self.assertAlmostEqual(res["valor_presente"], 272.727272, places=2)


if __name__ == "__main__":
    unittest.main()
