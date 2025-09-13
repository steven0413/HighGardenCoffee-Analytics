from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import umap
import pandas as pd
import numpy as np
import plotly.express as px

class MarketSegmentation:
    def __init__(self, config):
        self.config = config
        self.scaler = StandardScaler()
        
    def prepare_clustering_data(self, df):
        """Prepare data for clustering analysis"""
        # Aggregate data by country and coffee type
        aggregated = df.groupby([
            self.config['preprocessing']['country_column'],
            self.config['preprocessing']['coffee_type_column']
        ]).agg({
            self.config['preprocessing']['consumption_column']: ['mean', 'std', 'sum'],
            'year': 'count'
        }).reset_index()
        
        # Flatten column names
        aggregated.columns = ['_'.join(col).strip('_') for col in aggregated.columns]
        
        return aggregated
    
    def perform_kmeans_clustering(self, data, n_clusters=None):
        """Perform K-Means clustering"""
        if n_clusters is None:
            n_clusters = self.config['segmentation']['n_clusters']
        
        # Scale data
        scaled_data = self.scaler.fit_transform(data)
        
        # Apply K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(scaled_data)
        
        return clusters, kmeans
    
    def perform_umap_clustering(self, data, n_neighbors=15, min_dist=0.1):
        """Perform UMAP for dimensionality reduction and clustering"""
        scaled_data = self.scaler.fit_transform(data)
        
        # Apply UMAP
        reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, random_state=42)
        embedding = reducer.fit_transform(scaled_data)
        
        return embedding
    
    def analyze_clusters(self, df, clusters):
        """Analyze cluster characteristics"""
        df['cluster'] = clusters
        
        cluster_analysis = df.groupby('cluster').agg({
            'consumption_mean': ['mean', 'std'],
            'consumption_std': 'mean',
            'consumption_sum': 'mean',
            'year_count': 'mean'
        }).round(2)
        
        return cluster_analysis
    
    def visualize_clusters(self, df, clusters, reduction_method='pca'):
        """Visualize clusters using dimensionality reduction"""
        scaled_data = self.scaler.fit_transform(df)
        
        if reduction_method == 'pca':
            reducer = PCA(n_components=2)
            reduced_data = reducer.fit_transform(scaled_data)
        elif reduction_method == 'umap':
            reducer = umap.UMAP(random_state=42)
            reduced_data = reducer.fit_transform(scaled_data)
        
        # Create visualization
        viz_df = pd.DataFrame({
            'x': reduced_data[:, 0],
            'y': reduced_data[:, 1],
            'cluster': clusters,
            'country': df.index.get_level_values(0),
            'coffee_type': df.index.get_level_values(1)
        })
        
        fig = px.scatter(
            viz_df, x='x', y='y', color='cluster',
            hover_data=['country', 'coffee_type'],
            title=f"Market Segmentation ({reduction_method.upper()})"
        )
        
        return fig
    
    def identify_growth_markets(self, df, clusters):
        """Identify high-growth potential markets"""
        df['cluster'] = clusters
        
        # Calculate growth metrics (simplified)
        growth_metrics = df.groupby('cluster').agg({
            'consumption_mean': 'mean',
            'consumption_std': 'mean'
        })
        
        # Identify clusters with high mean and low volatility (stable growth)
        growth_metrics['growth_score'] = (
            growth_metrics['consumption_mean'] / growth_metrics['consumption_std']
        )
        
        return growth_metrics.sort_values('growth_score', ascending=False)