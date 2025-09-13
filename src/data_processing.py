import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os

warnings.filterwarnings('ignore')

class CoffeeDataProcessor:
    def __init__(self, config):
        self.config = config
        self.df = None
        
    def load_data(self):
        """Load raw coffee consumption data"""
        # Obtener la ruta absoluta del archivo
        # Usar el directorio actual como base en lugar de subir dos niveles
        base_dir = os.getcwd()  # Cambio importante: usar el directorio actual
        raw_path = os.path.join(base_dir, self.config['data']['raw_path'])
        
        print(f"Loading data from: {raw_path}")
        
        # Verificar si el archivo existe
        if not os.path.exists(raw_path):
            raise FileNotFoundError(f"El archivo {raw_path} no existe")
        
        self.df = pd.read_csv(raw_path)
        
        # Convertir la columna de año a datetime (asumiendo 1 de enero de cada año)
        self.df['date'] = pd.to_datetime(self.df[self.config['preprocessing']['date_column']].astype(str) + '-01-01')
        
        # Filtrar por rango de años
        min_year = int(self.config['preprocessing']['min_date'])
        max_year = int(self.config['preprocessing']['max_date'])
        
        mask = (
            (self.df[self.config['preprocessing']['date_column']] >= min_year) &
            (self.df[self.config['preprocessing']['date_column']] <= max_year)
        )
        self.df = self.df[mask]
        
        return self.df
    
    def handle_missing_values(self):
        """Handle missing values in the dataset"""
        # Los datos anuales pueden tener menos valores faltantes, pero igual verificamos
        self.df = self.df.sort_values([
            self.config['preprocessing']['country_column'],
            self.config['preprocessing']['coffee_type_column'],
            self.config['preprocessing']['date_column']
        ])
        
        # Group by country and coffee type for forward fill
        group_cols = [
            self.config['preprocessing']['country_column'],
            self.config['preprocessing']['coffee_type_column']
        ]
        
        self.df[self.config['preprocessing']['consumption_column']] = self.df.groupby(
            group_cols
        )[self.config['preprocessing']['consumption_column']].ffill()
        
        return self.df
    
    def create_temporal_features(self):
        """Create temporal features from date column"""
        # Para datos anuales, las características temporales son más limitadas
        self.df['year'] = self.df[self.config['preprocessing']['date_column']]
        self.df['decade'] = (self.df['year'] // 10) * 10
        
        return self.df
    
    def create_lag_features(self):
        """Create lag features for time series"""
        group_cols = [
            self.config['preprocessing']['country_column'],
            self.config['preprocessing']['coffee_type_column']
        ]
        
        for lag in self.config['features']['lag_features']:
            self.df[f'lag_{lag}'] = self.df.groupby(
                group_cols
            )[self.config['preprocessing']['consumption_column']].shift(lag)
        
        return self.df
    
    def create_rolling_features(self):
        """Create rolling window features"""
        group_cols = [
            self.config['preprocessing']['country_column'],
            self.config['preprocessing']['coffee_type_column']
        ]
        
        for window in self.config['features']['rolling_windows']:
            self.df[f'rolling_mean_{window}'] = self.df.groupby(
                group_cols
            )[self.config['preprocessing']['consumption_column']].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean()
            )
            
            self.df[f'rolling_std_{window}'] = self.df.groupby(
                group_cols
            )[self.config['preprocessing']['consumption_column']].transform(
                lambda x: x.rolling(window=window, min_periods=1).std()
            )
        
        return self.df
    
    def process(self):
        """Complete data processing pipeline"""
        print("Loading data...")
        self.load_data()
        
        print("Handling missing values...")
        self.handle_missing_values()
        
        print("Creating temporal features...")
        self.create_temporal_features()
        
        print("Creating lag features...")
        self.create_lag_features()
        
        print("Creating rolling features...")
        self.create_rolling_features()
        
        # Create processed directory if it doesn't exist
        processed_dir = os.path.dirname(os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            self.config['data']['processed_path']
        ))
        if not os.path.exists(processed_dir):
            os.makedirs(processed_dir)
        
        # Guardar datos procesados
        processed_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            self.config['data']['processed_path']
        )
        
        print(f"Saving processed data to: {processed_path}")
        self.df.to_parquet(processed_path)
        
        return self.df