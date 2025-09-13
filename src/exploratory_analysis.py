import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Deshabilitar tsfresh debido a problemas de compatibilidad
TSFRESH_AVAILABLE = False

class CoffeeExploratoryAnalysis:
    def __init__(self, df, config):
        self.df = df
        self.config = config
        
    def plot_consumption_timeseries(self):
        """Plot coffee consumption time series by country and type"""
        fig = px.line(
            self.df,
            x=self.config['preprocessing']['date_column'],
            y=self.config['preprocessing']['consumption_column'],
            color=self.config['preprocessing']['country_column'],
            facet_row=self.config['preprocessing']['coffee_type_column'],
            title="Coffee Consumption Trends by Country and Type",
            height=800
        )
        return fig
        
    def plot_seasonal_patterns(self):
        """Plot seasonal patterns by month and year"""
        monthly_avg = self.df.groupby([
            'year', 'month', 
            self.config['preprocessing']['country_column'],
            self.config['preprocessing']['coffee_type_column']
        ])[self.config['preprocessing']['consumption_column']].mean().reset_index()
        
        fig = px.line(
            monthly_avg,
            x='month',
            y=self.config['preprocessing']['consumption_column'],
            color=self.config['preprocessing']['country_column'],
            facet_col='year',
            facet_row=self.config['preprocessing']['coffee_type_column'],
            title="Monthly Consumption Patterns by Year",
            height=1200
        )
        return fig
        
    def plot_correlation_matrix(self):
        """Plot correlation matrix of features"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        corr_matrix = self.df[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdBu_r',
            zmin=-1,
            zmax=1
        ))
        
        fig.update_layout(
            title="Feature Correlation Matrix",
            width=800,
            height=800
        )
        return fig
        
    def analyze_features(self):
        """Alternative feature analysis without tsfresh"""
        print("Realizando análisis de características alternativo (sin tsfresh)")
        
        # Calcular características básicas manualmente
        features = {}
        
        # Estadísticas por país y tipo de café
        for country in self.df[self.config['preprocessing']['country_column']].unique():
            for coffee_type in self.df[self.config['preprocessing']['coffee_type_column']].unique():
                key = f"{country}_{coffee_type}"
                subset = self.df[
                    (self.df[self.config['preprocessing']['country_column']] == country) &
                    (self.df[self.config['preprocessing']['coffee_type_column']] == coffee_type)
                ]
                
                if len(subset) > 0:
                    consumption = subset[self.config['preprocessing']['consumption_column']]
                    features[key] = {
                        'mean': consumption.mean(),
                        'std': consumption.std(),
                        'min': consumption.min(),
                        'max': consumption.max(),
                        'trend': np.polyfit(range(len(consumption)), consumption, 1)[0]  # Pendiente de la tendencia
                    }
        
        return pd.DataFrame.from_dict(features, orient='index')
        
    def create_dashboard(self):
        """Create comprehensive exploratory dashboard"""
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Consumption Trends",
                "Seasonal Patterns",
                "Country Comparison",
                "Coffee Type Distribution"
            )
        )
        
        # Add time series plot
        for country in self.df[self.config['preprocessing']['country_column']].unique()[:5]:
            country_data = self.df[
                self.df[self.config['preprocessing']['country_column']] == country
            ]
            fig.add_trace(
                go.Scatter(
                    x=country_data[self.config['preprocessing']['date_column']],
                    y=country_data[self.config['preprocessing']['consumption_column']],
                    name=country
                ),
                row=1, col=1
            )
        
        # Add seasonal patterns
        monthly_avg = self.df.groupby(['month'])[
            self.config['preprocessing']['consumption_column']
        ].mean().reset_index()
        
        fig.add_trace(
            go.Bar(x=monthly_avg['month'], y=monthly_avg[
                self.config['preprocessing']['consumption_column']
            ]),
            row=1, col=2
        )
        
        # Add country comparison
        country_avg = self.df.groupby([
            self.config['preprocessing']['country_column']
        ])[self.config['preprocessing']['consumption_column']].mean().reset_index()
        
        fig.add_trace(
            go.Bar(x=country_avg[self.config['preprocessing']['country_column']], 
                  y=country_avg[self.config['preprocessing']['consumption_column']]),
            row=2, col=1
        )
        
        # Add coffee type distribution
        type_avg = self.df.groupby([
            self.config['preprocessing']['coffee_type_column']
        ])[self.config['preprocessing']['consumption_column']].mean().reset_index()
        
        fig.add_trace(
            go.Pie(labels=type_avg[self.config['preprocessing']['coffee_type_column']], 
                  values=type_avg[self.config['preprocessing']['consumption_column']]),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=True, title_text="Coffee Consumption Analysis Dashboard")
        return fig