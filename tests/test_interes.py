"""Pruebas de los cálculos de interés simple y compuesto."""

import unittest
from modules.interes import (
    calcular_monto_interes_simple,
    calcular_vp_interes_simple,
    despejar_tasa_interes_simple,
    despejar_tiempo_interes_simple,
    calcular_monto_interes_compuesto,
    calcular_vp_interes_compuesto,
    despejar_tasa_interes_compuesto,
    despejar_periodos_interes_compuesto,
    calcular_saldos,
)


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

    def test_despejes_interes_simple(self):
        # C = 1000, i = 5%, t = 4 -> M = 1200, I = 200
        i, m = calcular_monto_interes_simple(1000, 5, 4)
        self.assertAlmostEqual(m, 1200.0)
        self.assertAlmostEqual(i, 200.0)

        # Despejar VP
        c, i_dev = calcular_vp_interes_simple(1200, 5, 4)
        self.assertAlmostEqual(c, 1000.0)
        self.assertAlmostEqual(i_dev, 200.0)

        # Despejar Tasa
        tasa = despejar_tasa_interes_simple(1000, 1200, 4)
        self.assertAlmostEqual(tasa, 5.0)

        # Despejar Tiempo
        t = despejar_tiempo_interes_simple(1000, 1200, 5)
        self.assertAlmostEqual(t, 4.0)

    def test_despejes_interes_compuesto(self):
        # VP = 1000, i = 10%, n = 3 -> VF = 1331, I = 331
        i, vf = calcular_monto_interes_compuesto(1000, 10, 3)
        self.assertAlmostEqual(vf, 1331.0)
        self.assertAlmostEqual(i, 331.0)

        # Despejar VP
        vp, i_dev = calcular_vp_interes_compuesto(1331, 10, 3)
        self.assertAlmostEqual(vp, 1000.0)
        self.assertAlmostEqual(i_dev, 331.0)

        # Despejar Tasa
        tasa = despejar_tasa_interes_compuesto(1000, 1331, 3)
        self.assertAlmostEqual(tasa, 10.0)

        # Despejar Períodos
        n = despejar_periodos_interes_compuesto(1000, 1331, 10)
        self.assertAlmostEqual(n, 3.0)


if __name__ == "__main__":
    unittest.main()
