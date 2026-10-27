"""Pruebas para series uniformes vencidas y anticipadas."""

import unittest
from modules.series_uniformes import (
    valor_futuro_serie,
    valor_presente_serie,
    cuota_para_valor_futuro,
    cuota_para_prestamo,
)


class SeriesUniformesTest(unittest.TestCase):
    def test_serie_vencida_manual(self):
        # A = 100, i = 10%, n = 3 -> VF = 331, VP = 248.6852
        vf = valor_futuro_serie(100.0, 10.0, 3, "Vencida")
        self.assertAlmostEqual(vf, 331.0, places=2)

        vp = valor_presente_serie(100.0, 10.0, 3, "Vencida")
        self.assertAlmostEqual(vp, 248.685199, places=2)

    def test_serie_anticipada_manual(self):
        # VF_ant = 331 * 1.10 = 364.10
        vf_ant = valor_futuro_serie(100.0, 10.0, 3, "Anticipada")
        self.assertAlmostEqual(vf_ant, 364.10, places=2)

        # VP_ant = 248.6852 * 1.10 = 273.5537
        vp_ant = valor_presente_serie(100.0, 10.0, 3, "Anticipada")
        self.assertAlmostEqual(vp_ant, 273.553719, places=2)

    def test_cuotas_vencida_y_anticipada(self):
        # Cuota para VF = 331 vencida -> A = 100
        a_vf_v = cuota_para_valor_futuro(331.0, 10.0, 3, "Vencida")
        self.assertAlmostEqual(a_vf_v, 100.0, places=2)

        # Cuota para VF = 364.10 anticipada -> A = 100
        a_vf_a = cuota_para_valor_futuro(364.10, 10.0, 3, "Anticipada")
        self.assertAlmostEqual(a_vf_a, 100.0, places=2)

        # Cuota para VP = 248.6852 vencida -> A = 100
        a_vp_v = cuota_para_prestamo(248.685199, 10.0, 3, "Vencida")
        self.assertAlmostEqual(a_vp_v, 100.0, places=2)


if __name__ == "__main__":
    unittest.main()
