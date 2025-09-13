# src/visualization.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def create_presentation_visualizations(df, output_dir='reports'):
    """Create key visualizations for the presentation"""
    
    # Crear directorio de reportes si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Tendencia de consumo global a lo largo del tiempo
    global_consumption = df.groupby('year')['consumption_cups'].sum().reset_index()
    fig1 = px.line(global_consumption, x='year', y='consumption_cups', 
                   title='Tendencia Global de Consumo de Café (1990-2020)',
                   labels={'consumption_cups': 'Consumo (tazas)', 'year': 'Año'})
    fig1.write_html(f'{output_dir}/global_trend.html')
    
    # 2. Consumo por país (top 5)
    country_consumption = df.groupby('country')['consumption_cups'].sum().reset_index()
    country_consumption = country_consumption.sort_values('consumption_cups', ascending=False).head(5)
    fig2 = px.bar(country_consumption, x='country', y='consumption_cups',
                  title='Consumo Total por País (Top 5)',
                  labels={'consumption_cups': 'Consumo (tazas)', 'country': 'País'})
    fig2.write_html(f'{output_dir}/country_consumption.html')
    
    # 3. Consumo por tipo de café
    type_consumption = df.groupby('coffee_type')['consumption_cups'].sum().reset_index()
    fig3 = px.pie(type_consumption, values='consumption_cups', names='coffee_type',
                  title='Distribución del Consumo por Tipo de Café')
    fig3.write_html(f'{output_dir}/coffee_type_distribution.html')
    
    # 4. Precio promedio a lo largo del tiempo
    price_trend = df.groupby('year')['price_per_cup'].mean().reset_index()
    fig4 = px.line(price_trend, x='year', y='price_per_cup',
                   title='Evolución del Precio Promedio por Taza (1990-2020)',
                   labels={'price_per_cup': 'Precio (USD)', 'year': 'Año'})
    fig4.write_html(f'{output_dir}/price_trend.html')
    
    # 5. Relación entre precio y consumo
    price_consumption = df.groupby('year').agg({'price_per_cup': 'mean', 'consumption_cups': 'sum'}).reset_index()
    fig5 = px.scatter(price_consumption, x='price_per_cup', y='consumption_cups', 
                      trendline='ols', title='Relación entre Precio y Consumo',
                      labels={'price_per_cup': 'Precio Promedio (USD)', 'consumption_cups': 'Consumo Total'})
    fig5.write_html(f'{output_dir}/price_consumption_relationship.html')
    
    print(f'Visualizaciones guardadas en el directorio: {output_dir}')

if __name__ == "__main__":
    from data_processing import CoffeeDataProcessor
    from utils import load_config
    
    config = load_config('../config/parameters.yaml')
    processor = CoffeeDataProcessor(config)
    df = processor.process()
    
    create_presentation_visualizations(df)