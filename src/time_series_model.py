from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import numpy as np
import pandas as pd
import mlflow

class TimeSeriesModel:
    def __init__(self, config):
        self.config = config
        self.models = {}
        self.metrics = {}
        
    def prepare_prophet_data(self, df, country, coffee_type):
        """Prepare data for Prophet model"""
        filtered_df = df[
            (df[self.config['preprocessing']['country_column']] == country) &
            (df[self.config['preprocessing']['coffee_type_column']] == coffee_type)
        ]
        
        prophet_df = filtered_df[[
            self.config['preprocessing']['date_column'],
            self.config['preprocessing']['consumption_column']
        ]].rename(columns={
            self.config['preprocessing']['date_column']: 'ds',
            self.config['preprocessing']['consumption_column']: 'y'
        })
        
        return prophet_df
    
    def train_prophet(self, train_df, country, coffee_type):
        """Train Prophet model for specific country and coffee type"""
        prophet_df = self.prepare_prophet_data(train_df, country, coffee_type)
        
        model = Prophet(
            growth=self.config['models']['prophet']['growth'],
            seasonality_mode=self.config['models']['prophet']['seasonality_mode'],
            yearly_seasonality=self.config['models']['prophet']['yearly_seasonality'],
            weekly_seasonality=self.config['models']['prophet']['weekly_seasonality'],
            daily_seasonality=self.config['models']['prophet']['daily_seasonality']
        )
        
        model.fit(prophet_df)
        return model
    
    def evaluate_model(self, model, test_df, country, coffee_type):
        """Evaluate Prophet model"""
        prophet_test = self.prepare_prophet_data(test_df, country, coffee_type)
        
        future = model.make_future_dataframe(
            periods=len(prophet_test),
            freq=self.config['forecasting']['frequency']
        )
        
        forecast = model.predict(future)
        
        # Merge actual and predicted values
        comparison = forecast.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper']].join(
            prophet_test.set_index('ds')
        ).dropna()
        
        # Calculate metrics
        mae = mean_absolute_error(comparison['y'], comparison['yhat'])
        mse = mean_squared_error(comparison['y'], comparison['yhat'])
        rmse = np.sqrt(mse)
        mape = mean_absolute_percentage_error(comparison['y'], comparison['yhat'])
        
        metrics = {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'mape': mape
        }
        
        return metrics, comparison, forecast
    
    def train_all_models(self, train_df):
        """Train models for all country and coffee type combinations"""
        countries = train_df[self.config['preprocessing']['country_column']].unique()
        coffee_types = train_df[self.config['preprocessing']['coffee_type_column']].unique()
        
        for country in countries:
            for coffee_type in coffee_types:
                print(f"Training model for {country} - {coffee_type}")
                
                with mlflow.start_run():
                    model = self.train_prophet(train_df, country, coffee_type)
                    self.models[f"{country}_{coffee_type}"] = model
                    
                    # Log parameters and model
                    mlflow.log_params(self.config['models']['prophet'])
                    mlflow.prophet.log_model(model, f"prophet_{country}_{coffee_type}")
        
        return self.models
    
    def forecast_future(self, model, periods):
        """Generate future forecasts"""
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        return forecast
    
    def calculate_smape(self, actual, predicted):
        """Calculate Symmetric Mean Absolute Percentage Error"""
        return 200 * np.mean(np.abs(predicted - actual) / (np.abs(predicted) + np.abs(actual)))