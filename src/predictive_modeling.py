from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
import numpy as np
import mlflow

class PredictiveModeling:
    def __init__(self, config):
        self.config = config
        self.models = {}
        self.feature_importance = {}
        
    def prepare_ml_data(self, df):
        """Prepare data for machine learning models"""
        # Select features
        feature_cols = [
            'year', 'month', 'quarter', 'day_of_week', 'is_weekend'
        ] + [f'lag_{lag}' for lag in self.config['features']['lag_features']
        ] + [f'rolling_mean_{window}' for window in self.config['features']['rolling_windows']
        ] + [f'rolling_std_{window}' for window in self.config['features']['rolling_windows']]
        
        # One-hot encode categorical variables
        df_encoded = pd.get_dummies(
            df, 
            columns=[
                self.config['preprocessing']['country_column'],
                self.config['preprocessing']['coffee_type_column']
            ]
        )
        
        # Ensure all feature columns exist
        available_features = [col for col in feature_cols if col in df_encoded.columns]
        X = df_encoded[available_features]
        y = df_encoded[self.config['preprocessing']['consumption_column']]
        
        return X, y, available_features
    
    def train_random_forest(self, X_train, y_train):
        """Train Random Forest model"""
        model = RandomForestRegressor(
            n_estimators=self.config['models']['random_forest']['n_estimators'],
            max_depth=self.config['models']['random_forest']['max_depth'],
            random_state=self.config['models']['random_forest']['random_state'],
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        return model
    
    def train_xgboost(self, X_train, y_train):
        """Train XGBoost model"""
        model = XGBRegressor(
            n_estimators=self.config['models']['xgboost']['n_estimators'],
            max_depth=self.config['models']['xgboost']['max_depth'],
            learning_rate=self.config['models']['xgboost']['learning_rate'],
            random_state=42
        )
        
        model.fit(X_train, y_train)
        return model
    
    def evaluate_model(self, model, X_test, y_test):
        """Evaluate model performance"""
        y_pred = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        metrics = {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'mape': mape
        }
        
        return metrics, y_pred
    
    def cross_validate(self, model, X, y):
        """Perform time series cross-validation"""
        tscv = TimeSeriesSplit(n_splits=self.config['training']['cv_folds'])
        scores = cross_val_score(
            model, X, y, 
            cv=tscv, 
            scoring='neg_mean_absolute_error'
        )
        return -scores.mean()
    
    def train_models(self, X_train, y_train, X_test, y_test):
        """Train and compare multiple models"""
        models = {
            'random_forest': self.train_random_forest(X_train, y_train),
            'xgboost': self.train_xgboost(X_train, y_train)
        }
        
        results = {}
        for name, model in models.items():
            with mlflow.start_run():
                # Cross-validation
                cv_score = self.cross_validate(model, X_train, y_train)
                
                # Test evaluation
                metrics, y_pred = self.evaluate_model(model, X_test, y_test)
                
                # Log metrics
                mlflow.log_metrics(metrics)
                mlflow.log_metric('cv_mae', cv_score)
                
                # Log model
                mlflow.sklearn.log_model(model, name)
                
                # Store feature importance
                if hasattr(model, 'feature_importances_'):
                    self.feature_importance[name] = dict(zip(
                        X_train.columns, model.feature_importances_
                    ))
                
                results[name] = {
                    'model': model,
                    'metrics': metrics,
                    'cv_score': cv_score,
                    'predictions': y_pred
                }
        
        return results