"""La matriz visible en la interfaz debe calcularse y poder detectar diferencias."""

import unittest

from motor import verificacion as ve


class MatrizTest(unittest.TestCase):
    def test_todas_las_filas_coinciden(self):
        for fila in ve.matriz_verificacion():
            with self.subTest(prueba=fila["Prueba"]):
                self.assertIn("✅", fila["Estado"])

    def test_cubre_todos_los_temas(self):
        modulos = {fila["Módulo"] for fila in ve.matriz_verificacion()}
        self.assertEqual(modulos, {"Interés simple", "Interés compuesto", "Tasas", "Series uniformes", "Gradientes", "Amortización", "Plan de ahorro"})

    def test_una_diferencia_se_marca_como_falla(self):
        self.assertIn("❌", ve.fila("X", "Y", "Z", 100.0, 101.0)["Estado"])


if __name__ == "__main__":
    unittest.main()
