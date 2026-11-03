"""Pruebas de las tres preguntas, comparadas contra referencias independientes."""

import unittest

import numpy_financial as npf

from motor import datos_ejemplo as de
from motor import decisiones as dc
from motor import gradientes as gr
from motor.amortizacion import ABONO_CONSTANTE, CUOTA_FIJA


class CasoATest(unittest.TestCase):
    def test_compuesto_coincide_con_numpy_financial(self):
        r = dc.evaluar_inversion("X", 1_000_000, 360, 10, 0, 5)
        self.assertAlmostEqual(r["vf_neto"], npf.fv(0.10, 1, 0, -1_000_000), places=4)
        self.assertAlmostEqual(r["ea_neta"], 10.0)

    def test_retencion_reduce_la_tasa_neta(self):
        r = dc.evaluar_inversion("X", 1_000_000, 360, 10, 4, 5)
        self.assertAlmostEqual(r["intereses_netos"], 96_000.0, places=4)
        self.assertAlmostEqual(r["ea_neta"], 9.6)

    def test_interes_simple_no_capitaliza(self):
        # 3% trimestral sin reinvertir durante un año: 12% exacto.
        ea = (1.03 ** 4 - 1) * 100
        r = dc.evaluar_inversion("X", 1_000_000, 360, ea, 0, 5, periodos_simple=4)
        self.assertAlmostEqual(r["vf_bruto"], 1_120_000.0, places=4)

    def test_ganancia_real_descuenta_inflacion(self):
        r = dc.evaluar_inversion("X", 1_000_000, 360, 10, 0, 10)
        self.assertAlmostEqual(r["ganancia_real"], 0.0, places=6)
        self.assertAlmostEqual(r["tasa_real"], 0.0, places=8)

    def test_la_convencion_cambia_el_valor_final(self):
        comercial = dc.evaluar_inversion("X", 1_000_000, 180, 10, 0, 5, 360.0)
        exacta = dc.evaluar_inversion("X", 1_000_000, 180, 10, 0, 5, 365.0)
        self.assertGreater(comercial["vf_bruto"], exacta["vf_bruto"])

    def test_la_recomendacion_sigue_a_los_datos(self):
        p = dict(de.CASO_A)
        self.assertEqual(dc.evaluar_caso_a(p)["mejor"]["nombre"], "CDT")
        p["a_ahorro_tasa"] = 25.0
        resultado = dc.evaluar_caso_a(p)
        self.assertEqual(resultado["mejor"]["nombre"], "Cuenta de ahorros")
        self.assertIn("Cuenta de ahorros", resultado["recomendacion"])

    def test_advierte_si_ninguna_le_gana_a_la_inflacion(self):
        p = dict(de.CASO_A, a_inflacion=30.0, a_comb_puntos=0.0, a_cdt_tasa=1.0, a_ahorro_tasa=1.0)
        self.assertIn("ninguna opción le gana", dc.evaluar_caso_a(p)["recomendacion"])


class CasoBTest(unittest.TestCase):
    def test_tasa_anticipada_se_convierte_a_ea(self):
        r = dc.evaluar_caso_b(de.CASO_B)
        # 17% nominal mes anticipado: ia = 17%/12, iv = ia / (1 - ia), EA = (1 + iv)^12 - 1
        ia = 0.17 / 12
        self.assertAlmostEqual(r["b"]["ea"] / 100, (1 + ia / (1 - ia)) ** 12 - 1)

    def test_las_tablas_cierran_en_todos_los_sistemas(self):
        r = dc.evaluar_caso_b(de.CASO_B)
        for oferta in (r["a"], r["b"]):
            for resumen in oferta["sistemas"].values():
                self.assertTrue(resumen["verificacion"]["ok_saldo"])
                self.assertTrue(resumen["verificacion"]["ok_abonos"])

    def test_descontar_a_la_tasa_del_credito_da_el_capital(self):
        # A su propia tasa, los pagos valen hoy exactamente lo prestado (costo cero).
        for pago in ("Vencida", "Anticipada"):
            for sistema in (CUOTA_FIJA, ABONO_CONSTANTE):
                with self.subTest(pago=pago, sistema=sistema):
                    o = dc.evaluar_oferta("X", 10_000_000, 18, "Efectiva Anual (EA)", "Mensual", 24, "Mensual", pago, 18)
                    self.assertAlmostEqual(o["sistemas"][sistema]["costo_hoy"], 0.0, places=4)

    def test_valor_presente_coincide_con_numpy_financial(self):
        o = dc.evaluar_oferta("X", 10_000_000, 18, "Efectiva Anual (EA)", "Mensual", 24, "Mensual", "Vencida", 9)
        tabla = o["sistemas"][CUOTA_FIJA]["tabla"]
        d = 1.09 ** (1 / 12) - 1
        self.assertAlmostEqual(dc.valor_presente_pagos(tabla, 9, 12), npf.npv(d, [0.0] + list(tabla["Cuota (COP)"])), places=4)

    def test_gana_la_menor_ea_y_el_veredicto_cambia_con_los_datos(self):
        self.assertEqual(dc.evaluar_caso_b(de.CASO_B)["veredicto"]["ganadora"], "B")
        p = dict(de.CASO_B, b_a_tasa=10.0)
        self.assertEqual(dc.evaluar_caso_b(p)["veredicto"]["ganadora"], "A")

    def test_empate(self):
        p = dict(de.CASO_B)
        for campo in ("capital", "tasa", "tipo", "periodicidad_tasa", "meses", "periodicidad_pago", "pago"):
            p[f"b_b_{campo}"] = p[f"b_a_{campo}"]
        self.assertIsNone(dc.evaluar_caso_b(p)["veredicto"]["ganadora"])

    def test_avisa_si_los_plazos_son_diferentes(self):
        p = dict(de.CASO_B, b_b_meses=60)
        self.assertTrue(any("plazos" in a for a in dc.evaluar_caso_b(p)["veredicto"]["avisos"]))

    def test_rechaza_plazo_que_no_es_multiplo_de_la_periodicidad(self):
        with self.assertRaises(ValueError):
            dc.cuotas_del_plazo(10, 4)


class CasoCTest(unittest.TestCase):
    def _vf_con_numpy_financial(self, plan, capital, i, meses):
        flujo = [capital] + list(plan["calendario"]["Aporte (COP)"])
        return npf.npv(i, flujo) * (1 + i) ** meses

    def test_todos_los_planes_llegan_a_la_meta(self):
        for nombre_plan in de.PLANES:
            for capital in (0.0, 5_000_000.0):
                with self.subTest(plan=nombre_plan, capital=capital):
                    plan = dc.plan_de_ahorro(60_000_000, 60, 9, capital, nombre_plan, 6, 60_000)
                    i = plan["tasa_mensual"]
                    self.assertAlmostEqual(self._vf_con_numpy_financial(plan, capital, i, 60), 60_000_000, places=3)
                    self.assertTrue(plan["ok_meta"])

    def test_uniforme_coincide_con_pmt(self):
        plan = dc.plan_de_ahorro(60_000_000, 60, 9)
        self.assertAlmostEqual(plan["cuota_inicial"], npf.pmt(plan["tasa_mensual"], 60, 0, -60_000_000), places=4)
        self.assertAlmostEqual(plan["cuota_inicial"], plan["cuota_final"])

    def test_escalones_cada_doce_meses(self):
        aportes = dc.plan_de_ahorro(60_000_000, 36, 9, 0, de.PLAN_GEOMETRICO, 10)["calendario"]["Aporte (COP)"]
        self.assertAlmostEqual(aportes[0], aportes[11])
        self.assertAlmostEqual(aportes[12], aportes[0] * 1.10)
        self.assertAlmostEqual(aportes[24], aportes[0] * 1.21)
        aportes = dc.plan_de_ahorro(60_000_000, 36, 9, 0, de.PLAN_ARITMETICO, 0, 50_000)["calendario"]["Aporte (COP)"]
        self.assertAlmostEqual(aportes[12], aportes[0] + 50_000)

    def test_el_primer_aporte_del_gradiente_es_menor_que_el_uniforme(self):
        plan = dc.plan_de_ahorro(60_000_000, 60, 9, 0, de.PLAN_GEOMETRICO, 6)
        self.assertLess(plan["cuota_inicial"], plan["cuota_uniforme"])
        self.assertGreater(plan["cuota_final"], plan["cuota_uniforme"])

    def test_coincide_con_el_modulo_de_gradientes_en_periodos_anuales(self):
        # Un aporte anual es un gradiente de periodos anuales: F_A debe ser el mismo VF.
        i_anual = 9.0
        vf_unitario = gr.calcular_gradiente_geometrico(1.0, 6.0, i_anual, 5)["valor_futuro"]
        s = ((1.09) - 1) / ((1.09) ** (1 / 12) - 1)  # valor a fin de año de $1 mensual
        plan = dc.plan_de_ahorro(60_000_000, 60, i_anual, 0, de.PLAN_GEOMETRICO, 6)
        self.assertAlmostEqual(plan["cuota_inicial"] * s * vf_unitario, 60_000_000, places=3)
        vf_arit = gr.calcular_gradiente_aritmetico(0.0, 1.0, i_anual, 5)["valor_futuro"]
        vf_unif = gr.calcular_gradiente_aritmetico(1.0, 0.0, i_anual, 5)["valor_futuro"]
        plan = dc.plan_de_ahorro(60_000_000, 60, i_anual, 0, de.PLAN_ARITMETICO, 0, 60_000)
        self.assertAlmostEqual(s * (plan["cuota_inicial"] * vf_unif + 60_000 * vf_arit), 60_000_000, places=3)

    def test_tasa_cero_plazo_uno_y_meta_ya_cubierta(self):
        self.assertAlmostEqual(dc.plan_de_ahorro(1200, 12, 0)["cuota_inicial"], 100.0)
        self.assertAlmostEqual(dc.plan_de_ahorro(1200, 1, 9)["cuota_inicial"], 1200.0)
        plan = dc.plan_de_ahorro(1000, 12, 9, 2000, de.PLAN_ARITMETICO, 0, 500)
        self.assertTrue(plan["ya_cubierta"])
        self.assertEqual(plan["total_cuotas"], 0.0)
        self.assertTrue(plan["ok_meta"])

    def test_rechaza_aumento_imposible(self):
        with self.assertRaises(ValueError):
            dc.plan_de_ahorro(1_000_000, 60, 9, 0, de.PLAN_ARITMETICO, 0, 10_000_000)

    def test_intereses_mas_aportes_igual_a_la_meta(self):
        plan = dc.evaluar_caso_c(de.CASO_C)
        self.assertAlmostEqual(plan["total_aportado"] + plan["intereses"], de.CASO_C["c_meta"], places=3)


if __name__ == "__main__":
    unittest.main()
