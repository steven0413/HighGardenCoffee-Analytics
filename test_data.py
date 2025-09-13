# test_data.py (debe estar en la raíz del proyecto)
import sys
import os

# Agregar la carpeta src al path para poder importar los módulos
sys.path.append('src')

from utils import load_config

# Imprimir el directorio actual para verificación
print(f"Directorio actual de trabajo: {os.getcwd()}")

# Cargar configuración
try:
    config = load_config('config/parameters.yaml')
    print("Configuración cargada exitosamente:")
    print(f"Ruta de datos: {config['data']['raw_path']}")
except Exception as e:
    print(f"Error al cargar configuración: {e}")
    sys.exit(1)

# Verificar si el archivo existe usando el directorio actual como base
raw_path = os.path.join(os.getcwd(), config['data']['raw_path'])
print(f"Ruta completa del archivo: {raw_path}")
print(f"¿Existe el archivo? {os.path.exists(raw_path)}")

if os.path.exists(raw_path):
    # Leer las primeras filas del CSV
    try:
        import pandas as pd
        df_sample = pd.read_csv(raw_path, nrows=5)
        print("Primeras filas del CSV:")
        print(df_sample)
        print("Columnas del CSV:")
        print(df_sample.columns.tolist())
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
else:
    print("El archivo no existe. Buscando archivos CSV en el proyecto...")
    # Buscar todos los archivos CSV
    csv_files = []
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    print("Archivos CSV encontrados:")
    for csv_file in csv_files:
        print(f"  - {csv_file}")
    
    # Buscar específicamente archivos de café
    coffee_files = [f for f in csv_files if 'coffee' in f.lower()]
    print("\nArchivos de café encontrados:")
    for coffee_file in coffee_files:
        print(f"  - {coffee_file}")