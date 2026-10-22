"""Pruebas de los cálculos reutilizados por los casos aplicados."""

import math
import unittest

from modules.amortizacion import generar_tabla_amortizacion
from modules.casos_aplicados import calcular_vpn
from modules.series_uniformes import valor_futuro_serie


class CasosAplicadosTest(unittest.TestCase):
    def test_ahorro_para_meta_con_tasa_cero_y_positiva(self):
        self.assertEqual(valor_futuro_serie(250_000, 0, 24), 6_000_000)
        acumulado = valor_futuro_serie(250_000, 0.5, 24)
        self.assertGreater(acumulado, 6_000_000)
        self.assertAlmostEqual(valor_futuro_serie(250_000, 0.5, 1), 250_000)

    def test_compra_financiada_con_tasa_positiva_y_cero(self):
        tabla = generar_tabla_amortizacion(24_000_000, 1.2, 24)
        self.assertGreater(tabla["Cuota (COP)"].iloc[0], 1_000_000)
        self.assertEqual(tabla["Saldo final (COP)"].iloc[-1], 0)
        self.assertAlmostEqual(tabla["Abono a capital (COP)"].sum(), 24_000_000, places=5)

        tabla_cero = generar_tabla_amortizacion(1_200_000, 0, 12)
        self.assertAlmostEqual(tabla_cero["Cuota (COP)"].iloc[0], 100_000)
        self.assertEqual(tabla_cero["Interés (COP)"].sum(), 0)

    def test_vpn_positivo_y_convencion_de_signos(self):
        vpn, valores_presentes = calcular_vpn(10_000_000, [3_000_000] * 4, 1)
        esperado = math.fsum(3_000_000 / (1.01 ** periodo) for periodo in range(1, 5)) - 10_000_000
        self.assertAlmostEqual(vpn, esperado)
        self.assertGreater(vpn, 0)
        self.assertEqual(len(valores_presentes), 4)

    def test_vpn_cero_con_tasa_cero_y_un_periodo(self):
        vpn, valores_presentes = calcular_vpn(1_100, [1_100], 0)
        self.assertEqual(valores_presentes, [1_100])
        self.assertEqual(vpn, 0)
        vpn_un_periodo, _ = calcular_vpn(100, [110], 10)
        self.assertAlmostEqual(vpn_un_periodo, 0)

    def test_vpn_rechaza_datos_invalidos(self):
        for inversion, flujos, tasa in (
            (0, [100], 0),
            (100, [], 0),
            (100, [-1], 0),
            (100, [100], -100),
            (100, [float("inf")], 5),
        ):
            with self.subTest(inversion=inversion, flujos=flujos, tasa=tasa), self.assertRaises(ValueError):
                calcular_vpn(inversion, flujos, tasa)


if __name__ == "__main__":
    unittest.main()
