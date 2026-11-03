# FinanzasLab

Dashboard interactivo de matemáticas e ingeniería financiera desarrollado con **Python** y **Streamlit**. FinanzasLab permite explorar fórmulas, simular escenarios y comparar decisiones financieras mediante cálculos reproducibles, tablas y visualizaciones interactivas en pesos colombianos (COP).

> Proyecto académico de la **UPB — Escuela de Ingenierías**.

## Funcionalidades

El panel principal resume los resultados en vivo y lleva a tres preguntas de la vida real:

- **¿Dónde pongo mi plata?** Compara CDT, cuenta de ahorros y una alternativa a tasa combinada, con EA bruta y neta, ganancia real y recomendación.
- **¿Me conviene este crédito?** Compara dos ofertas con tablas de amortización, veredicto, gráficos y efecto de abonos extra.
- **¿Cuánto debo ahorrar para mi meta?** Calcula la cuota con plan uniforme o gradiente, con calendario de aportes.

Los valores precargados son **datos de ejemplo**, no ofertas reales. Cada pregunta tiene campos para registrar la fuente y la fecha de consulta.

Los módulos del curso siguen disponibles en la navegación: interés simple y compuesto, tasas y rentabilidad, series uniformes, gradientes, tablas de amortización, y la sección de supuestos y fórmulas con verificación en vivo.

| Caso | Temas |
| :--- | :--- |
| A. Inversión | Interés simple, interés compuesto, equivalencia de tasas, tasa combinada y retención |
| B. Crédito | Equivalencia de tasas (incluida la anticipada), series uniformes y amortización |
| C. Ahorro | Series uniformes, gradientes aritmético y geométrico, e interés compuesto |

## Estructura del proyecto

```text
.
├── app.py                 # Punto de entrada y navegación
├── motor/                 # Cálculo financiero, sin dependencia de la interfaz
│   ├── interes.py         # Interés simple y compuesto
│   ├── tasas.py           # Conversión de tasas y rentabilidad
│   ├── series.py          # Anualidades vencidas y anticipadas
│   ├── gradientes.py      # Gradientes aritméticos y geométricos
│   ├── amortizacion.py    # Cuota fija, abono constante, pago anticipado y abonos extra
│   ├── decisiones.py      # Las tres preguntas
│   ├── datos_ejemplo.py   # Parámetros precargados
│   ├── verificacion.py    # Matriz de verificación en vivo
│   └── formato.py         # Formato de presentación
├── modules/               # Pantallas de Streamlit
├── tests/                 # Pruebas automáticas
├── requirements.txt       # Dependencias de la aplicación
├── requirements-dev.txt   # Dependencias de las pruebas
└── render.yaml            # Despliegue en Render
```

## Tecnologías

- **Python**
- **Streamlit** — interfaz web interactiva
- **Pandas** — tablas y transformación de datos
- **Plotly** — gráficos interactivos
- **unittest** y **numpy-financial** — pruebas y referencia independiente

## Instalación y ejecución local

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

## Ejecutar las pruebas

Las pruebas comparan cada módulo contra numpy-financial o contra el flujo de caja período a período, y prueban la interfaz con el simulador de Streamlit.

```bash
pip install -r requirements-dev.txt
python -m unittest discover -s tests -p "test_*.py"
```

## Despliegue en Render

El archivo `render.yaml` define un servicio web Python con:

- **Build:** `pip install -r requirements.txt`
- **Start:** `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`

Para desplegarlo, conecta el repositorio a Render y utiliza la configuración definida en `render.yaml`.

## Notas metodológicas

- Los cálculos se expresan en pesos colombianos (COP).
- La convención comercial usa 360 días por año y la exacta 365. Es un parámetro editable.
- El veredicto de crédito se decide por la menor EA y mide la diferencia en pesos de hoy.
- El saldo final de las tablas se calcula sin forzarlo a cero, y la verificación se muestra en rojo si no cierra.
- Las tarifas de retención son parámetros editables y deben confirmarse en la norma vigente.

## Equipo

- Santiago Izef
- Miguel Arboleda
- Andrés Rojas

**Docente:** Adriana Arango L.  
**Institución:** UPB — Escuela de Ingenierías
