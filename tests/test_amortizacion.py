"""Pruebas para la tabla de amortización francesa."""

import unittest

from modules.amortizacion import generar_tabla_amortizacion
from modules.series_uniformes import cuota_para_prestamo


class AmortizacionTest(unittest.TestCase):
    def test_cuota_y_primera_cuota_con_tasa_positiva(self):
        principal = 1_000_000
        tasa = 1
        cuotas = 12
        tabla = generar_tabla_amortizacion(principal, tasa, cuotas)
        cuota_esperada = cuota_para_prestamo(principal, tasa, cuotas)
        primera = tabla.iloc[0]

        self.assertAlmostEqual(primera["Cuota (COP)"], cuota_esperada)
        self.assertAlmostEqual(primera["Interés (COP)"], 10_000)
        self.assertAlmostEqual(primera["Abono a capital (COP)"], cuota_esperada - 10_000)
        self.assertAlmostEqual(primera["Saldo final (COP)"], principal - (cuota_esperada - 10_000))

    def test_tasa_cero_cuota_igual_a_prestamo_sobre_cuotas(self):
        tabla = generar_tabla_amortizacion(1_000, 0, 4)
        self.assertTrue(all(tabla["Cuota (COP)"] == 250))
        self.assertTrue(all(tabla["Interés (COP)"] == 0))
        self.assertAlmostEqual(tabla["Abono a capital (COP)"].sum(), 1_000)
        self.assertEqual(tabla.iloc[-1]["Saldo final (COP)"], 0)

    def test_saldo_final_cero_y_suma_de_abonos_igual_al_principal(self):
        tabla = generar_tabla_amortizacion(2_500_000, 2.3, 36)
        self.assertEqual(tabla.iloc[-1]["Saldo final (COP)"], 0)
        self.assertAlmostEqual(tabla["Abono a capital (COP)"].sum(), 2_500_000, places=6)
        self.assertTrue((tabla["Saldo final (COP)"] >= 0).all())

    def test_un_periodo_liquida_prestamo_y_cobra_interes(self):
        tabla = generar_tabla_amortizacion(1_000, 10, 1)
        self.assertAlmostEqual(tabla.iloc[0]["Interés (COP)"], 100)
        self.assertAlmostEqual(tabla.iloc[0]["Cuota (COP)"], 1_100)
        self.assertAlmostEqual(tabla.iloc[0]["Abono a capital (COP)"], 1_000)
        self.assertEqual(tabla.iloc[0]["Saldo final (COP)"], 0)

    def test_rechaza_entradas_invalidas(self):
        for principal in (0, -100, float("nan")):
            with self.subTest(principal=principal), self.assertRaises(ValueError):
                generar_tabla_amortizacion(principal, 1, 12)
        for tasa in (-100, float("inf")):
            with self.subTest(tasa=tasa), self.assertRaises(ValueError):
                generar_tabla_amortizacion(1_000, tasa, 12)
        for cuotas in (0, 1.5, 1001):
            with self.subTest(cuotas=cuotas), self.assertRaises(ValueError):
                generar_tabla_amortizacion(1_000, 1, cuotas)


if __name__ == "__main__":
    unittest.main()
