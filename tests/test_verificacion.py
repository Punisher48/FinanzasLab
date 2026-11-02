"""La verificación de amortización debe poder fallar: no basta con que pase."""

import unittest

from motor import amortizacion as am


class VerificacionTest(unittest.TestCase):
    def test_tablas_correctas_pasan(self):
        for sistema in (am.amortizacion_frances, am.amortizacion_aleman):
            resultado = am.verificar_amortizacion(sistema(20_000_000, 0.015, 24), 20_000_000)
            self.assertTrue(resultado["ok_saldo"])
            self.assertTrue(resultado["ok_abonos"])
            self.assertTrue(resultado["ok_total"])

    def test_el_saldo_final_no_se_fuerza_a_cero(self):
        tabla = am.amortizacion_frances(20_000_000, 0.015, 24)
        saldo_calculado = tabla["Saldo Inicial (COP)"].iloc[-1] - tabla["Abono a Capital (COP)"].iloc[-1]
        self.assertEqual(tabla["Saldo Final (COP)"].iloc[-1], saldo_calculado)
        # La última cuota sale de la misma fórmula que las demás.
        self.assertEqual(tabla["Cuota (COP)"].iloc[-1], tabla["Cuota (COP)"].iloc[0])

    def test_una_tabla_alterada_no_pasa(self):
        tabla = am.amortizacion_frances(20_000_000, 0.015, 24)
        tabla.loc[tabla.index[-1], "Saldo Final (COP)"] = 5_000.0
        tabla.loc[tabla.index[3], "Abono a Capital (COP)"] += 1_000.0
        resultado = am.verificar_amortizacion(tabla, 20_000_000)
        self.assertFalse(resultado["ok_saldo"])
        self.assertFalse(resultado["ok_abonos"])


if __name__ == "__main__":
    unittest.main()
