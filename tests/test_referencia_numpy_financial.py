"""Compara el motor contra numpy-financial, una referencia independiente.

Convención de numpy-financial: el dinero que sale lleva signo negativo y
`when` indica si el pago es al final (0, vencida) o al inicio (1, anticipada).
"""

import subprocess
import sys
import unittest

import numpy_financial as npf

from motor import amortizacion as am
from motor import gradientes as gr
from motor import interes as it
from motor import series as se
from motor import tasas as ta


class InteresCompuestoTest(unittest.TestCase):
    def test_valor_futuro(self):
        _, vf = it.calcular_monto_interes_compuesto(1_000_000, 2, 12)
        self.assertAlmostEqual(vf, npf.fv(0.02, 12, 0, -1_000_000), places=6)

    def test_valor_presente(self):
        vp, _ = it.calcular_vp_interes_compuesto(1_000_000, 2, 12)
        self.assertAlmostEqual(vp, npf.pv(0.02, 12, 0, -1_000_000), places=6)

    def test_despeje_de_tasa(self):
        tasa = it.despejar_tasa_interes_compuesto(1_000_000, 1_300_000, 12)
        self.assertAlmostEqual(tasa / 100, npf.rate(12, 0, -1_000_000, 1_300_000), places=8)

    def test_despeje_de_periodos(self):
        n = it.despejar_periodos_interes_compuesto(1_000_000, 1_300_000, 2)
        self.assertAlmostEqual(n, npf.nper(0.02, 0, -1_000_000, 1_300_000), places=8)


class InteresSimpleTest(unittest.TestCase):
    """numpy-financial no modela interés simple: se compara con flujo sin capitalizar."""

    def test_monto_igual_a_suma_de_intereses_constantes(self):
        _, monto = it.calcular_monto_interes_simple(1_000_000, 2, 12)
        self.assertAlmostEqual(monto, 1_000_000 + sum(1_000_000 * 0.02 for _ in range(12)), places=6)


class TasasTest(unittest.TestCase):
    def test_tasa_efectiva_reproduce_el_crecimiento_del_dinero(self):
        ea = ta.efectiva_anual_desde_nominal(24, 12)
        self.assertAlmostEqual(1 + ea / 100, npf.fv(0.02, 12, 0, -1), places=10)

    def test_anticipada_equivale_a_vencida_en_flujo_de_caja(self):
        # Recibir 98 hoy y devolver 100 en un periodo es 2% anticipado.
        vencida = ta.anticipada_a_vencida(2.0)
        self.assertAlmostEqual(vencida / 100, npf.irr([98, -100]), places=8)


class SeriesTest(unittest.TestCase):
    def test_todas_las_variables_en_ambas_modalidades(self):
        for when, modalidad in ((0, "Vencida"), (1, "Anticipada")):
            for tasa in (1.5, 0.0):
                i = tasa / 100
                with self.subTest(modalidad=modalidad, tasa=tasa):
                    self.assertAlmostEqual(se.valor_futuro_serie(500_000, tasa, 24, modalidad), npf.fv(i, 24, -500_000, 0, when), places=4)
                    self.assertAlmostEqual(se.valor_presente_serie(500_000, tasa, 24, modalidad), npf.pv(i, 24, -500_000, 0, when), places=4)
                    self.assertAlmostEqual(se.cuota_para_valor_futuro(20_000_000, tasa, 24, modalidad), npf.pmt(i, 24, 0, -20_000_000, when), places=4)
                    self.assertAlmostEqual(se.cuota_para_prestamo(20_000_000, tasa, 24, modalidad), npf.pmt(i, 24, -20_000_000, 0, when), places=4)


class GradientesTest(unittest.TestCase):
    def _comparar(self, resultado, tasa, n):
        i = tasa / 100
        vp = npf.npv(i, [0.0] + list(resultado["pagos"]))
        self.assertAlmostEqual(resultado["valor_presente"], vp, places=4)
        self.assertAlmostEqual(resultado["valor_futuro"], vp * (1 + i) ** n, places=4)
        self.assertAlmostEqual(resultado["cuota_equivalente"], npf.pmt(i, n, -vp), places=4)

    def test_aritmetico(self):
        for g, tasa, n in ((50_000, 1.5, 12), (-5_000, 1.5, 12), (50_000, 0.0, 12), (50_000, 1.5, 1)):
            with self.subTest(g=g, tasa=tasa, n=n):
                self._comparar(gr.calcular_gradiente_aritmetico(1_000_000, g, tasa, n), tasa, n)

    def test_geometrico(self):
        casos = ((3, 1.5, 12), (1.5, 1.5, 12), (-2, 1.5, 12), (3, 0.0, 12), (0, 1.5, 1))
        for g, tasa, n in casos:
            with self.subTest(g=g, tasa=tasa, n=n):
                self._comparar(gr.calcular_gradiente_geometrico(1_000_000, g, tasa, n), tasa, n)


class AmortizacionTest(unittest.TestCase):
    def test_cuota_fija_periodo_a_periodo(self):
        i, n, capital = 0.015, 24, 20_000_000
        tabla = am.amortizacion_frances(capital, i, n)
        for fila in tabla.itertuples(index=False):
            p = fila[0]
            self.assertAlmostEqual(tabla["Cuota (COP)"].iloc[p - 1], npf.pmt(i, n, -capital), places=4)
            self.assertAlmostEqual(tabla["Interés (COP)"].iloc[p - 1], -npf.ipmt(i, p, n, capital), places=4)
            self.assertAlmostEqual(tabla["Abono a Capital (COP)"].iloc[p - 1], -npf.ppmt(i, p, n, capital), places=4)

    def test_tasa_cero_y_plazo_uno(self):
        self.assertAlmostEqual(am.amortizacion_frances(1200, 0, 12)["Cuota (COP)"].iloc[0], npf.pmt(0, 12, -1200), places=8)
        self.assertAlmostEqual(am.amortizacion_frances(1000, 0.1, 1)["Cuota (COP)"].iloc[0], npf.pmt(0.1, 1, -1000), places=8)

    def test_ambos_sistemas_cuestan_la_tasa_pactada(self):
        for sistema in (am.amortizacion_frances, am.amortizacion_aleman):
            tabla = sistema(20_000_000, 0.015, 24)
            tir = npf.irr([20_000_000] + list(-tabla["Cuota (COP)"]))
            self.assertAlmostEqual(tir, 0.015, places=6)


class SeparacionTest(unittest.TestCase):
    def test_el_motor_no_depende_de_la_interfaz(self):
        codigo = "import sys, motor.interes, motor.tasas, motor.series, motor.gradientes, motor.amortizacion; sys.exit('streamlit' in sys.modules)"
        self.assertEqual(subprocess.run([sys.executable, "-c", codigo]).returncode, 0)


if __name__ == "__main__":
    unittest.main()
