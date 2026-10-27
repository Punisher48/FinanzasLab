"""Pruebas de conversión de tasas, equivalencias y tasas combinadas."""

import unittest
from modules.tasas import (
    efectiva_anual_desde_periodica,
    periodica_desde_efectiva_anual,
    efectiva_anual_desde_nominal,
    nominal_desde_efectiva_anual,
    vencida_a_anticipada,
    anticipada_a_vencida,
    tasa_combinada,
    tasa_real_fisher,
    rentabilidad_con_retencion,
    generar_tabla_equivalencias,
)


class TasasTest(unittest.TestCase):
    def test_efectiva_anual_desde_periodica(self):
        # 1% mensual -> EA = (1.01)^12 - 1 = 12.6825%
        self.assertAlmostEqual(efectiva_anual_desde_periodica(1.0, 12), 12.682503, places=4)

    def test_periodica_desde_efectiva_anual(self):
        self.assertAlmostEqual(periodica_desde_efectiva_anual(12.682503, 12), 1.0, places=4)

    def test_nominal_a_efectiva(self):
        # 24% MV -> 2% mes -> EA = (1.02)^12 - 1 = 26.8242%
        ea = efectiva_anual_desde_nominal(24.0, 12, anticipada=False)
        self.assertAlmostEqual(ea, 26.824179, places=4)

    def test_vencida_y_anticipada(self):
        # iv = 2% -> ia = 0.02 / 1.02 = 1.96078%
        ia = vencida_a_anticipada(2.0)
        self.assertAlmostEqual(ia, 1.960784, places=4)

        # Regreso
        iv = anticipada_a_vencida(ia)
        self.assertAlmostEqual(iv, 2.0, places=4)

    def test_tasa_combinada_fisher(self):
        # inflacion 5%, spread 4% -> (1.05)*(1.04) - 1 = 9.2%
        tc = tasa_combinada(5.0, 4.0)
        self.assertAlmostEqual(tc, 9.2, places=4)

        # Despejar real: (1.092) / (1.05) - 1 = 4%
        tr = tasa_real_fisher(9.2, 5.0)
        self.assertAlmostEqual(tr, 4.0, places=4)

    def test_rentabilidad_con_retencion(self):
        res = rentabilidad_con_retencion(10_000_000, 11_000_000, 4.0, 360)
        self.assertEqual(res["rendimiento_bruto"], 1_000_000)
        self.assertEqual(res["retencion_valor"], 40_000)
        self.assertEqual(res["rendimiento_neto"], 960_000)
        self.assertAlmostEqual(res["ea_bruta"], 10.0, places=4)
        self.assertAlmostEqual(res["ea_neta"], 9.6, places=4)

    def test_tabla_equivalencias(self):
        df = generar_tabla_equivalencias(12.6825, "Efectiva Anual (EA)")
        self.assertEqual(len(df), 7)
        fila_mensual = df[df["Periodicidad"] == "Mensual"].iloc[0]
        self.assertEqual(fila_mensual["Periódica Vencida (ip)"], "1.0000%")


if __name__ == "__main__":
    unittest.main()
