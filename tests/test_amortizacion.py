"""Pruebas de las tablas de amortización (Francés y Alemán)."""

import unittest
from modules.amortizacion import (
    amortizacion_frances,
    amortizacion_aleman,
    calcular_tasa_periodica,
)


class AmortizacionTest(unittest.TestCase):
    def test_amortizacion_frances_cierre_y_suma(self):
        df = amortizacion_frances(1_000_000, 0.10, 2)
        self.assertEqual(len(df), 2)
        # Saldo final cero
        self.assertAlmostEqual(df["Saldo Final (COP)"].iloc[-1], 0.0, places=2)
        # Suma de abonos = monto
        self.assertAlmostEqual(df["Abono a Capital (COP)"].sum(), 1_000_000, places=2)
        # Cuotas iguales
        self.assertAlmostEqual(df["Cuota (COP)"].iloc[0], 576190.48, places=1)

    def test_amortizacion_aleman_cierre_y_suma(self):
        df = amortizacion_aleman(1_000_000, 0.10, 2)
        self.assertEqual(len(df), 2)
        # Abonos constantes
        self.assertAlmostEqual(df["Abono a Capital (COP)"].iloc[0], 500_000.0)
        self.assertAlmostEqual(df["Abono a Capital (COP)"].iloc[1], 500_000.0)
        # Saldo final cero
        self.assertAlmostEqual(df["Saldo Final (COP)"].iloc[-1], 0.0, places=2)
        # Suma de abonos = monto
        self.assertAlmostEqual(df["Abono a Capital (COP)"].sum(), 1_000_000.0)
        # Cuotas decrecientes
        self.assertAlmostEqual(df["Cuota (COP)"].iloc[0], 600_000.0)
        self.assertAlmostEqual(df["Cuota (COP)"].iloc[1], 550_000.0)

    def test_calcular_tasa_periodica(self):
        # 12% nominal anual vencida mensual -> 1% mes
        tp = calcular_tasa_periodica(12.0, "Nominal Anual Vencida", "Mensual")
        self.assertAlmostEqual(tp, 0.01)


if __name__ == "__main__":
    unittest.main()
