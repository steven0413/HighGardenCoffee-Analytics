# src/basic_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import warnings
from dotenv import load_dotenv
from generative_ai_chatbot import CoffeeAnalyticsChatbot


warnings.filterwarnings('ignore')

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio src al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import load_config

# Configuración de la página
st.set_page_config(
    page_title="High Garden Coffee Analytics",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función para cargar datos con caching
@st.cache_data
def load_data():
    """Cargar datos procesados con caching"""
    try:
        # Cargar configuración
        config = load_config('config/parameters.yaml')
        
        # Cargar datos procesados
        processed_path = config['data']['processed_path']
        if os.path.exists(processed_path):
            df = pd.read_parquet(processed_path)
            return df
        else:
            # Si no existen datos procesados, procesarlos
            from data_processing import CoffeeDataProcessor
            processor = CoffeeDataProcessor(config)
            df = processor.process()
            return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return None

def main():
    st.title("☕ High Garden Coffee - Dashboard Analítico")
    
    # Cargar datos
    with st.spinner('Cargando datos...'):
        df = load_data()
    
    if df is None:
        st.error("No se pudieron cargar los datos. Verifica la configuración.")
        return
    
    # Sidebar con filtros
    st.sidebar.header("Filtros")
    
    # Obtener opciones únicas para los filtros
    countries = df['country'].unique().tolist()
    coffee_types = df['coffee_type'].unique().tolist()
    years = df['year'].unique().tolist()
    
    selected_countries = st.sidebar.multiselect(
        "Seleccionar Países",
        options=countries,
        default=countries[:3] if len(countries) > 3 else countries
    )
    
    selected_types = st.sidebar.multiselect(
        "Seleccionar Tipos de Café",
        options=coffee_types,
        default=coffee_types
    )
    
    year_range = st.sidebar.slider(
        "Rango de Años",
        min_value=int(min(years)),
        max_value=int(max(years)),
        value=(int(min(years)), int(max(years)))
    )
    
    # Filtrar datos
    if not selected_countries:
        selected_countries = countries
        
    if not selected_types:
        selected_types = coffee_types
    
    filtered_df = df[
        (df['country'].isin(selected_countries)) &
        (df['coffee_type'].isin(selected_types)) &
        (df['year'] >= year_range[0]) &
        (df['year'] <= year_range[1])
    ]
    
    # Sección del Chatbot Analítico
    st.sidebar.header("🤖 Chatbot Analítico")
    
    # Obtener API key de variables de entorno o input de usuario
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        api_key = st.sidebar.text_input(
            "OpenAI API Key:",
            type="password",
            help="Ingresa tu API key de OpenAI o configúrala como variable de entorno OPENAI_API_KEY"
        )
    else:
        st.sidebar.info("API key cargada desde variables de entorno")
    
    # Input para preguntas
    question = st.sidebar.text_input(
        "Haz una pregunta sobre los datos:",
        placeholder="Ej: ¿Cuál fue el consumo en Brasil en 2020?"
    )
    
    if api_key and question:
        try:
            chatbot = CoffeeAnalyticsChatbot(filtered_df, api_key)
            answer = chatbot.ask_question(question)
            
            st.sidebar.success("Respuesta del chatbot:")
            st.sidebar.info(answer)
            
        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")
    elif question and not api_key:
        st.sidebar.warning("Por favor ingresa una API key válida de OpenAI")
    
    # Mostrar información básica
    st.header("Resumen del Dataset")
    st.write(f"**Total de registros:** {len(filtered_df)}")
    st.write(f"**Países seleccionados:** {', '.join(selected_countries)}")
    st.write(f"**Tipos de café seleccionados:** {', '.join(selected_types)}")
    st.write(f"**Rango de años:** {year_range[0]} - {year_range[1]}")
    
    # Métricas clave
    st.header("Métricas Clave")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_consumption = filtered_df['consumption_cups'].sum()
        st.metric("Consumo Total", f"{total_consumption:,.0f} tazas")
    
    with col2:
        avg_consumption = filtered_df['consumption_cups'].mean()
        st.metric("Consumo Promedio", f"{avg_consumption:,.1f} tazas/año")
    
    with col3:
        # Calcular precio promedio ponderado por consumo
        total_consumption_val = filtered_df['consumption_cups'].sum()
        if total_consumption_val > 0:
            weighted_price = (filtered_df['price_per_cup'] * filtered_df['consumption_cups']).sum() / total_consumption_val
            st.metric("Precio Promedio", f"${weighted_price:.2f}")
        else:
            st.metric("Precio Promedio", "N/A")
    
    with col4:
        countries_count = filtered_df['country'].nunique()
        st.metric("Países", countries_count)
    
    # Gráfico de tendencias
    st.header("Tendencias de Consumo")
    
    # Preparar datos para el gráfico
    trend_data = filtered_df.groupby(['year', 'country', 'coffee_type'])['consumption_cups'].sum().reset_index()
    
    fig = px.line(trend_data, x='year', y='consumption_cups', 
                  color='country', line_dash='coffee_type',
                  title='Tendencia de Consumo por País y Tipo de Café',
                  labels={'consumption_cups': 'Consumo (tazas)', 'year': 'Año'})
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráficos adicionales
    col1, col2 = st.columns(2)
    
    with col1:
        # Consumo por país
        country_data = filtered_df.groupby('country')['consumption_cups'].sum().reset_index()
        fig2 = px.bar(country_data, x='country', y='consumption_cups',
                     title='Consumo Total por País',
                     labels={'consumption_cups': 'Consumo (tazas)', 'country': 'País'})
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        # Consumo por tipo de café
        type_data = filtered_df.groupby('coffee_type')['consumption_cups'].sum().reset_index()
        fig3 = px.pie(type_data, values='consumption_cups', names='coffee_type',
                     title='Distribución por Tipo de Café')
        st.plotly_chart(fig3, use_container_width=True)
    
    # Relación precio-consumo
    st.header("Relación Precio-Consumo")
    price_consumption_data = filtered_df.groupby(['year', 'country']).agg({
        'price_per_cup': 'mean', 
        'consumption_cups': 'sum'
    }).reset_index()
    
    fig4 = px.scatter(price_consumption_data, x='price_per_cup', y='consumption_cups',
                     color='country', size='consumption_cups', hover_data=['year'],
                     title='Relación entre Precio y Consumo por País',
                     labels={'price_per_cup': 'Precio Promedio (USD)', 'consumption_cups': 'Consumo Total'})
    
    st.plotly_chart(fig4, use_container_width=True)
    
    # Mostrar datos tabulares
    st.header("Datos Detallados")
    st.dataframe(filtered_df[['year', 'country', 'coffee_type', 'consumption_cups', 'price_per_cup']].sort_values(['year', 'country']))

if __name__ == "__main__":
    main()