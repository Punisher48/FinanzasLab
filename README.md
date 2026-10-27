# FinanzasLab 📊

Dashboard interactivo de matemáticas e ingeniería financiera desarrollado con **Python** y **Streamlit**. FinanzasLab permite explorar fórmulas, simular escenarios y comparar decisiones financieras mediante cálculos reproducibles, tablas y visualizaciones interactivas en pesos colombianos (COP).

> Proyecto académico de la **UPB — Escuela de Ingenierías**.

## ✨ Funcionalidades

El tablero reúne los siguientes módulos:

- **Interés simple y compuesto**
  - Cálculo de valor presente, valor futuro, interés, tasa y plazo.
  - Convenciones de días comercial (360) y exacta (365).
  - Comparación gráfica entre crecimiento lineal y compuesto.
- **Tasas y rentabilidad**
  - Conversión entre tasas vencidas, anticipadas, nominales y efectivas.
  - Conversión entre tasas periódicas y efectivas anuales (EA).
  - Tasas combinadas y tasa real mediante la ecuación de Fisher.
  - Cálculo de rentabilidad bruta y neta con retención en la fuente.
  - Tabla de equivalencias para distintas periodicidades.
- **Series uniformes**
  - Anualidades vencidas y anticipadas.
  - Cálculo de valor presente, valor futuro y cuota periódica.
  - Simulación de ahorro, préstamos e inversiones.
- **Gradientes financieros**
  - Gradientes aritméticos y geométricos, crecientes o decrecientes.
  - Valor presente, valor futuro y cuota uniforme equivalente.
  - Detalle de flujos y acumulación período a período.
- **Tablas de amortización**
  - Sistema francés, con cuota fija.
  - Sistema alemán, con abono constante a capital.
  - Comparación de cuotas, intereses totales, costo total y saldo pendiente.
- **Casos financieros aplicados**
  - CDT Bancolombia vs. cuenta de rendimientos Nu.
  - Crédito de vehículo: sistema francés vs. alemán.
  - Plan de ahorro para vivienda con cuota fija vs. gradiente creciente.
- **Supuestos y verificación**
  - Documentación de convenciones temporales, fórmulas y supuestos.
  - Matriz de comprobaciones manuales por módulo.

## 🧱 Estructura del proyecto

```text
.
├── app.py                         # Punto de entrada de la aplicación Streamlit
├── modules/                       # Módulos de cálculo y sus vistas interactivas
│   ├── interes.py                 # Interés simple y compuesto
│   ├── tasas.py                   # Conversión de tasas y rentabilidad
│   ├── series_uniformes.py        # Anualidades vencidas y anticipadas
│   ├── gradientes.py              # Gradientes aritméticos y geométricos
│   ├── amortizacion.py            # Sistemas francés y alemán
│   ├── casos_aplicados.py         # Escenarios financieros aplicados
│   └── supuestos_verificacion.py  # Fórmulas, supuestos y verificaciones
├── tests/                         # Pruebas unitarias de los cálculos
├── .streamlit/config.toml         # Tema y configuración del servidor Streamlit
├── requirements.txt               # Dependencias de Python
├── render.yaml                    # Configuración de despliegue en Render
└── .gitignore
```

La aplicación se inicia en `app.py`, que configura la interfaz y ofrece navegación lateral entre los módulos. Cada archivo de `modules/` combina funciones matemáticas reutilizables con una función `render()` para mostrar formularios, métricas, fórmulas, tablas y gráficos Plotly. Los casos aplicados reutilizan los cálculos de tasas, gradientes, series y amortización.

## 🛠️ Tecnologías

- **Python**
- **Streamlit** — interfaz web interactiva
- **Pandas** — tablas y transformación de datos
- **Plotly** — gráficos interactivos
- **unittest** — pruebas unitarias

## 🚀 Instalación y ejecución local

### 1. Clonar el repositorio

```bash
git clone https://github.com/Punisher48/FinanzasLab.git
cd FinanzasLab
```

### 2. Crear y activar un entorno virtual

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Iniciar el dashboard

```bash
streamlit run app.py
```

Después, abre en el navegador la URL local mostrada por Streamlit, normalmente `http://localhost:8501`.

## 🧪 Ejecutar las pruebas

El proyecto incluye pruebas unitarias para interés, tasas, series uniformes, gradientes, amortización y casos aplicados.

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## ☁️ Despliegue en Render

El archivo `render.yaml` define un servicio web Python con:

- **Build:** `pip install -r requirements.txt`
- **Start:** `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`

Para desplegarlo, conecta el repositorio a Render y utiliza la configuración definida en `render.yaml`.

## 📚 Notas metodológicas

- Los cálculos financieros se expresan principalmente en **pesos colombianos (COP)**.
- La convención comercial utiliza 360 días por año; la convención exacta utiliza 365 días.
- Las tasas efectivas consideran capitalización y reinversión según la periodicidad seleccionada.
- En las tablas de amortización, el saldo final y la suma de abonos se verifican para cerrar el crédito correctamente.
- Los casos de mercado incorporan tasas y referencias con fechas de consulta. Antes de tomar decisiones financieras reales, verifica las condiciones vigentes directamente con la entidad correspondiente.

## 👥 Equipo

- Santiago Izef
- Miguel Arboleda
- Andrés Rojas

**Docente:** Adriana Arango L.  
**Institución:** UPB — Escuela de Ingenierías
