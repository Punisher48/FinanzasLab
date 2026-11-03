"""Pago anticipado y abonos extra, comparados contra numpy-financial."""

import unittest

import numpy_financial as npf

from motor import amortizacion as am


class PagoAnticipadoTest(unittest.TestCase):
    def test_cuota_fija_coincide_con_numpy_financial(self):
        tabla = am.tabla_amortizacion(20_000_000, 0.015, 24, am.CUOTA_FIJA, "Anticipada")
        self.assertAlmostEqual(tabla["Cuota (COP)"].iloc[0], npf.pmt(0.015, 24, -20_000_000, 0, 1), places=4)
        self.assertEqual(tabla["Período"].iloc[0], 0)
        self.assertEqual(tabla["Período"].iloc[-1], 23)
        self.assertEqual(tabla["Interés (COP)"].iloc[0], 0.0)

    def test_ambas_tablas_cierran_y_cuestan_la_tasa_pactada(self):
        for sistema in am.SISTEMAS:
            with self.subTest(sistema=sistema):
                tabla = am.tabla_amortizacion(20_000_000, 0.015, 24, sistema, "Anticipada")
                verificacion = am.verificar_amortizacion(tabla, 20_000_000)
                self.assertTrue(verificacion["ok_saldo"])
                self.assertTrue(verificacion["ok_abonos"])
                # Flujo: en t=0 se recibe el capital y se paga la primera cuota.
                flujo = [20_000_000 - tabla["Cuota (COP)"].iloc[0]] + list(-tabla["Cuota (COP)"].iloc[1:]) + [0.0]
                self.assertAlmostEqual(npf.irr(flujo), 0.015, places=6)

    def test_tasa_cero_y_plazo_uno(self):
        self.assertAlmostEqual(am.tabla_amortizacion(1200, 0, 12, am.CUOTA_FIJA, "Anticipada")["Cuota (COP)"].iloc[0], 100.0)
        tabla = am.tabla_amortizacion(1000, 0.1, 1, am.CUOTA_FIJA, "Anticipada")
        self.assertAlmostEqual(tabla["Cuota (COP)"].iloc[0], 1000.0)
        self.assertAlmostEqual(tabla["Saldo Final (COP)"].iloc[0], 0.0)


class AbonoExtraTest(unittest.TestCase):
    def test_acorta_el_plazo_y_ahorra_intereses(self):
        for sistema in am.SISTEMAS:
            for pago in am.FORMAS_PAGO:
                with self.subTest(sistema=sistema, pago=pago):
                    efecto = am.efecto_abono_extra(30_000_000, 0.015, 48, sistema, pago, 300_000)
                    self.assertGreater(efecto["intereses_ahorrados"], 0)
                    self.assertGreater(efecto["cuotas_menos"], 0)
                    verificacion = am.verificar_amortizacion(efecto["tabla"], 30_000_000)
                    self.assertTrue(verificacion["ok_saldo"])
                    self.assertTrue(verificacion["ok_abonos"])
                    self.assertTrue(verificacion["ok_total"])

    def test_coincide_con_nper_de_numpy_financial(self):
        # Pagar cuota + extra equivale a una cuota mayor: nper da el nuevo plazo.
        i, n, capital, extra = 0.015, 48, 30_000_000, 300_000
        cuota = npf.pmt(i, n, -capital)
        efecto = am.efecto_abono_extra(capital, i, n, am.CUOTA_FIJA, "Vencida", extra)
        self.assertEqual(efecto["cuotas_con_extra"], int(npf.nper(i, -(cuota + extra), capital)) + 1)

    def test_sin_abono_extra_no_hay_efecto(self):
        efecto = am.efecto_abono_extra(1_000_000, 0.01, 12, am.CUOTA_FIJA, "Vencida", 0.0)
        self.assertEqual(efecto["cuotas_menos"], 0)
        self.assertAlmostEqual(efecto["intereses_ahorrados"], 0.0)

    def test_abono_mayor_que_el_saldo(self):
        tabla = am.tabla_amortizacion(1000, 0.01, 12, am.CUOTA_FIJA, "Vencida", 5000)
        self.assertEqual(len(tabla), 1)
        self.assertAlmostEqual(tabla["Saldo Final (COP)"].iloc[0], 0.0)


if __name__ == "__main__":
    unittest.main()
