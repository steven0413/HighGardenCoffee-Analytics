Descripción del Proyecto
Este proyecto analiza datos históricos de consumo de café (1990-2020) para identificar tendencias, predecir demanda y optimizar estrategias comerciales. La solución incluye un dashboard interactivo y un chatbot con IA generativa para consultas en lenguaje natural.

Características
Procesamiento de datos con Python y Pandas
Dashboard interactivo con Streamlit y visualizaciones Plotly
Modelos predictivos de series de tiempo (Prophet, ARIMA)
Segmentación de mercados mediante clustering
Chatbot analítico con OpenAI GPT-3.5-turbo
Análisis de tendencias y patrones estacionales
Optimización de precios basada en elasticidad de demanda

🛠️ Instalación
Clonar el repositorio:
bash
git clone https://github.com/steven0413/HighGardenCoffee-Analytics.git
cd HighGardenCoffee-Analytics

Crear entorno virtual:
bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

Instalar dependencias:
bash
pip install -r requirements.txt
Configurar variables de entorno:

Crear archivo .env en la raíz del proyecto
Agregar tu API key de OpenAI: OPENAI_API_KEY= api_key

Uso
Ejecutar el dashboard interactivo:


🤖 Chatbot Analítico
El proyecto incluye un chatbot con IA generativa que permite hacer consultas en lenguaje natural:

-¿Cuál es el país con mayor consumo en 2020?
-Compara el consumo de Arábica vs Robusta
-Predice el consumo para Colombia en 2025
-Muestra la tendencia de precios para café Liberica

📁 Estructura del Proyecto
text
HighGardenCoffee-Analytics/
├── src/
│   ├── data_processing.py          # Procesamiento de datos
│   ├── exploratory_analysis.py     # Análisis exploratorio
│   ├── predictive_modeling.py      # Modelos predictivos
│   ├── market_segmentation.py      # Segmentación de mercados
│   ├── generative_ai_chatbot.py    # Chatbot con IA
│   ├── basic_dashboard.py          # Dashboard principal
│   └── utils.py                    # Funciones auxiliares
├── config/
│   └── parameters.yaml             # Configuración del proyecto
├── data/
│   ├── raw/                        # Datos crudos
│   └── processed/                  # Datos procesados
├── .gitignore                      # Archivos excluidos de Git
├── requirements.txt                # Dependencias del proyecto
├── run.ps1                         # Script de ejecución (PowerShell)
└── README.md                       # Documentación del proyecto
📊 Resultados Destacados

Precisión de modelos: MAPE < 8% en predicciones de consumo
Segmentación: Identificación de 3 clusters de mercado
Tendencias: Crecimiento anual compuesto de 1.8-2.1%
Oportunidades: Mercados subexplotados con alto potencial identificados
Relación precio-consumo: Elasticidades calculadas por segmento

Configuración
El archivo config/parameters.yaml contiene la configuración del proyecto:

yaml
data:
  raw_path: "data/raw/coffee_consumption_historical.csv"
  processed_path: "data/processed/coffee_consumption_processed.parquet"

preprocessing:
  date_column: "year"
  country_column: "country"
  coffee_type_column: "coffee_type"
  consumption_column: "consumption_cups"
  min_date: "1990"
  max_date: "2020"

features:
  lag_features: [1, 2, 3, 6, 12]
  rolling_windows: [3, 6, 12]

Contribución
Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

Crea una rama para tu feature (git checkout -b feature/AmazingFeature)
Commit tus cambios (git commit -m 'Add some AmazingFeature')
Push a la rama (git push origin feature/AmazingFeature)
Abre un Pull Request

Contacto
Para preguntas sobre este proyecto, puedes contactar a través de:

GitHub: steven0413
Repositorio: HighGardenCoffee-Analytics

Nota: Este proyecto fue desarrollado como parte de un reto técnico para High Garden Coffee, demostrando habilidades en ingeniería de machine learning, análisis de datos e implementación de soluciones de IA generativa.
