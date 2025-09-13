import streamlit as st
import pandas as pd
import plotly.express as px
from data_processing import CoffeeDataProcessor
from exploratory_analysis import ExploratoryAnalysis
from src.time_series_model import TimeSeriesModel
from src.predictive_modeling import PredictiveModeling
from src.market_segmentation import MarketSegmentation
from src.generative_ai_chatbot import CoffeeAnalyticsChatbot
from src.utils import load_config, setup_logging
import warnings
warnings.filterwarnings('ignore')

# Setup
config = load_config("config/parameters.yaml")
logger = setup_logging()

def main():
    st.set_page_config(
        page_title="High Garden Coffee Analytics",
        page_icon="☕",
        layout="wide"
    )
    
    st.title("☕ High Garden Coffee Analytics Platform")
    st.sidebar.title("Navigation")
    
    # Navigation
    pages = {
        "Data Overview": data_overview,
        "Exploratory Analysis": exploratory_analysis,
        "Forecasting": forecasting,
        "Market Segmentation": market_segmentation,
        "AI Assistant": ai_assistant
    }
    
    page = st.sidebar.selectbox("Select Page", list(pages.keys()))
    pages[page]()
    
def data_overview():
    st.header("Data Overview")
    
    if st.button("Load and Process Data"):
        with st.spinner("Processing data..."):
            processor = CoffeeDataProcessor(config)
            df = processor.process()
            st.session_state.df = df
        
        st.success("Data processed successfully!")
        st.dataframe(df.head())
        
        st.subheader("Data Summary")
        st.json({
            "Total Records": len(df),
            "Countries": df[config['preprocessing']['country_column']].nunique(),
            "Coffee Types": df[config['preprocessing']['coffee_type_column']].nunique(),
            "Date Range": f"{df[config['preprocessing']['date_column']].min()} to {df[config['preprocessing']['date_column']].max()}"
        })

def exploratory_analysis():
    st.header("Exploratory Analysis")
    
    if 'df' not in st.session_state:
        st.warning("Please load data first from the Data Overview page")
        return
    
    df = st.session_state.df
    analyzer = CoffeeExploratoryAnalysis(df, config)
    
    if st.button("Generate Analysis"):
        with st.spinner("Creating visualizations..."):
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(analyzer.plot_consumption_timeseries(), use_container_width=True)
            
            with col2:
                st.plotly_chart(analyzer.plot_correlation_matrix(), use_container_width=True)
            
            st.plotly_chart(analyzer.create_dashboard(), use_container_width=True)

def forecasting():
    st.header("Forecasting Models")
    
    if 'df' not in st.session_state:
        st.warning("Please load data first from the Data Overview page")
        return
    
    df = st.session_state.df
    
    # Model selection
    model_type = st.selectbox("Select Model", ["Prophet", "Random Forest", "XGBoost"])
    
    if st.button("Train Models"):
        with st.spinner("Training models..."):
            if model_type == "Prophet":
                ts_model = TimeSeriesModel(config)
                models = ts_model.train_all_models(df)
                st.success("Prophet models trained successfully!")
                
            # Add other model types...

def market_segmentation():
    st.header("Market Segmentation")
    
    if 'df' not in st.session_state:
        st.warning("Please load data first from the Data Overview page")
        return
    
    df = st.session_state.df
    segmenter = MarketSegmentation(config)
    
    if st.button("Analyze Markets"):
        with st.spinner("Performing segmentation..."):
            clustered_data = segmenter.prepare_clustering_data(df)
            clusters, model = segmenter.perform_kmeans_clustering(clustered_data)
            
            st.plotly_chart(
                segmenter.visualize_clusters(clustered_data, clusters),
                use_container_width=True
            )
            
            growth_markets = segmenter.identify_growth_markets(clustered_data, clusters)
            st.dataframe(growth_markets)

def ai_assistant():
    st.header("AI Analytics Assistant")
    
    if 'df' not in st.session_state:
        st.warning("Please load data first from the Data Overview page")
        return
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        analytics_data = {
            "total_records": len(st.session_state.df),
            "countries": st.session_state.df[config['preprocessing']['country_column']].unique().tolist(),
            "coffee_types": st.session_state.df[config['preprocessing']['coffee_type_column']].unique().tolist(),
            "time_range": f"{st.session_state.df[config['preprocessing']['date_column']].min()} to {st.session_state.df[config['preprocessing']['date_column']].max()}"
        }
        
        st.session_state.chatbot = CoffeeAnalyticsChatbot(config, analytics_data)
        st.session_state.chatbot.setup_chatbot()
        st.session_state.messages = []
    
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about coffee consumption trends..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.query_chatbot(prompt)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()