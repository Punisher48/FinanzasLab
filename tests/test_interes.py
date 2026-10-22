"""Pruebas de los saldos del módulo de interés simple y compuesto."""

import unittest

from modules.interes import calcular_saldos


class InteresTest(unittest.TestCase):
    def test_interes_simple_con_tasa_positiva(self):
        self.assertEqual(calcular_saldos(1_000, 10, 2, "Interés simple"), [1_000, 1_100, 1_200])

    def test_interes_compuesto_con_tasa_positiva(self):
        saldos = calcular_saldos(1_000, 10, 2, "Interés compuesto")
        self.assertEqual(saldos[0], 1_000)
        self.assertEqual(saldos[1], 1_100)
        self.assertAlmostEqual(saldos[2], 1_210)

    def test_tasa_cero_y_un_periodo(self):
        self.assertEqual(calcular_saldos(1_000, 0, 3, "Interés simple"), [1_000] * 4)
        self.assertEqual(calcular_saldos(1_000, 0, 3, "Interés compuesto"), [1_000] * 4)
        self.assertEqual(calcular_saldos(1_000, 10, 1, "Interés simple"), [1_000, 1_100])
        self.assertEqual(calcular_saldos(1_000, 10, 1, "Interés compuesto"), [1_000, 1_100])


if __name__ == "__main__":
    unittest.main()
