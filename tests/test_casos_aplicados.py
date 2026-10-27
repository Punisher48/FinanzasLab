"""Pruebas de los casos financieros aplicados."""

import unittest
from modules.tasas import rentabilidad_con_retencion, periodica_desde_efectiva_anual
from modules.amortizacion import amortizacion_frances, amortizacion_aleman
from modules.gradientes import calcular_gradiente_geometrico


class CasosAplicadosTest(unittest.TestCase):
    def test_caso_1_inversion_retencion(self):
        # 15M invertidos a 180 dias con 10% EA y 4% retefuente
        dias = 180.0
        tasa_per = ((1.0 + 0.10) ** (dias / 360.0)) - 1.0
        vf_bruto = 15_000_000.0 * (1.0 + tasa_per)
        res = rentabilidad_con_retencion(15_000_000.0, vf_bruto, 4.0, dias)
        self.assertTrue(res["rendimiento_neto"] > 0)
        self.assertTrue(res["ea_neta"] < 10.0)

    def test_caso_2_credito_vehiculo(self):
        # 40M a 48 meses con 1.25% mes
        df_f = amortizacion_frances(40_000_000.0, 0.0125, 48)
        df_a = amortizacion_aleman(40_000_000.0, 0.0125, 48)
        self.assertAlmostEqual(df_f["Saldo Final (COP)"].iloc[-1], 0.0, places=2)
        self.assertAlmostEqual(df_a["Saldo Final (COP)"].iloc[-1], 0.0, places=2)
        # El sistema alemán paga menos intereses que el francés
        self.assertTrue(df_a["Interés (COP)"].sum() < df_f["Interés (COP)"].sum())

    def test_caso_3_gradiente_ahorro(self):
        # Meta con gradiente geométrico
        res = calcular_gradiente_geometrico(500_000.0, 0.5, 0.68, 36)
        self.assertTrue(res["valor_futuro"] > 18_000_000.0)


if __name__ == "__main__":
    unittest.main()
