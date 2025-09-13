# run.ps1 - Versi??n simplificada y corregida
Write-Host "=== HIGH GARDEN COFFEE - SISTEMA DE ANALITICA AVANZADA ===" -ForegroundColor Green
Write-Host "Iniciando preparacion para presentacion ejecutiva..." -ForegroundColor Yellow
Write-Host ""

# 1. Procesar datos
Write-Host "1. PROCESANDO DATOS HISTORICOS (1990-2020)..." -ForegroundColor Cyan
python -c "import sys; sys.path.append('src'); from data_processing import CoffeeDataProcessor; from utils import load_config; config = load_config('config/parameters.yaml'); processor = CoffeeDataProcessor(config); df = processor.process(); print('SUCCESS: Datos procesados - ' + str(df.shape[0]) + ' registros, ' + str(df.shape[1]) + ' caracteristicas')"

# 2. Verificar que los datos estan listos
Write-Host "`n2. VERIFICANDO INTEGRIDAD DE DATOS..." -ForegroundColor Cyan
python -c "import sys; sys.path.append('src'); from utils import load_config; import os; config = load_config('config/parameters.yaml'); processed_path = os.path.join(os.getcwd(), config['data']['processed_path']); print('Datos procesados disponibles en: ' + processed_path) if os.path.exists(processed_path) else print('ERROR: No se encontraron datos procesados')"

# 3. Iniciar dashboard interactivo
Write-Host "`n3. INICIANDO DASHBOARD INTERACTIVO..." -ForegroundColor Green
Write-Host "   URL local: http://localhost:8501" -ForegroundColor Yellow
Write-Host "   URL de red: http://192.168.1.1:8501" -ForegroundColor Yellow
Write-Host "   Presiona Ctrl+C para finalizar la presentacion" -ForegroundColor Red
Write-Host ""

# Mensaje final para la presentacion
Write-Host "`n=== PUNTOS CLAVE PARA LA PRESENTACION ===" -ForegroundColor Magenta
Write-Host "1. Demostrar tendencias de consumo por pais y tipo de cafe" -ForegroundColor White
Write-Host "2. Mostrar la relacion entre precio y consumo" -ForegroundColor White
Write-Host "3. Destacar oportunidades de mercado identificadas" -ForegroundColor White
Write-Host "4. Mencionar capacidades de IA generativa futuras" -ForegroundColor White
Write-Host ""

# Iniciar Streamlit
streamlit run src/basic_dashboard.py
