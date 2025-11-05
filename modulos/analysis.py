"""
Módulo de Análisis de Series Temporales y Predicción ARIMA (ACTUALIZADO)
- Agrupa por PERIODO (no registros individuales)
- Usa índice numérico en descomposición
- Predicción con los 13 periodos disponibles
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.decomposition import PCA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error, mean_absolute_error


class AnalysisEngine:
    """Engine para análisis de clustering y series temporales"""
    
    def __init__(self):
        self.X_scaled = None
        self.ts_values = None
        self.ts_periodos = None
        self.pca = None
        self.X_pca = None
    
    # ==================== ANÁLISIS CLUSTERING ====================
    
    def evaluate_kmeans(self, X_scaled, labels):
        """Evaluar KMeans con métricas"""
        return {
            'silhouette': silhouette_score(X_scaled, labels),
            'davies_bouldin': davies_bouldin_score(X_scaled, labels),
            'calinski_harabasz': calinski_harabasz_score(X_scaled, labels)
        }
    
    def evaluate_dbscan(self, X_scaled, labels):
        """Evaluar DBSCAN con métricas"""
        mask = labels != -1
        metrics = {}
        
        if len(set(labels[mask])) > 1:
            metrics['silhouette'] = silhouette_score(X_scaled[mask], labels[mask])
            metrics['davies_bouldin'] = davies_bouldin_score(X_scaled[mask], labels[mask])
        
        return metrics
    
    def evaluate_hierarchical(self, X_scaled, labels):
        """Evaluar clustering jerárquico con métricas"""
        return {
            'silhouette': silhouette_score(X_scaled, labels),
            'davies_bouldin': davies_bouldin_score(X_scaled, labels)
        }
    
    def find_optimal_k(self, X_scaled, k_range=range(2, 7)):
        """Encontrar k óptimo"""
        from sklearn.cluster import KMeans
        inertias = []
        silhouettes = []
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=5, max_iter=100)
            kmeans.fit(X_scaled)
            inertias.append(kmeans.inertia_)
            silhouettes.append(silhouette_score(X_scaled, kmeans.labels_))
        
        k_optimal = list(k_range)[np.argmax(silhouettes)]
        
        return {
            'k_range': list(k_range),
            'inertias': inertias,
            'silhouettes': silhouettes,
            'k_optimal': k_optimal
        }
    
    def apply_pca(self, X_scaled, n_components=2):
        """Aplicar PCA para visualización"""
        self.pca = PCA(n_components=n_components)
        self.X_pca = self.pca.fit_transform(X_scaled)
        
        return {
            'X_pca': self.X_pca,
            'explained_variance': self.pca.explained_variance_ratio_
        }
    
    def print_metrics(self, model_name, metrics):
        """Imprimir métricas formateadas"""
        print(f"\n✅ {model_name}:")
        for metric, value in metrics.items():
            if isinstance(value, float):
                print(f"   {metric}: {value:.4f}")
            else:
                print(f"   {metric}: {value}")
    
    # ==================== ANÁLISIS SERIES TEMPORALES ====================
    
    def create_timeseries(self, df, time_col='PERIODO', value_col='PUNT_GLOBAL'):
        """
        Crear serie temporal AGRUPADA POR PERIODO
        (NO registros individuales, sino promedio por periodo)
        """
        if value_col not in df.columns or time_col not in df.columns:
            return None, 0, None
        
        # Agrupar por PERIODO y calcular promedio
        ts_data = df.groupby(time_col)[value_col].mean().sort_index()
        self.ts_values = ts_data.values
        self.ts_periodos = ts_data.index.values
        
        return self.ts_values, len(self.ts_values), self.ts_periodos
    
    def adf_test(self):
        """Prueba ADF de estacionariedad"""
        if self.ts_values is None or len(self.ts_values) < 2:
            return None
        
        adf = adfuller(self.ts_values)
        return {
            'statistic': adf[0],
            'p_value': adf[1],
            'is_stationary': adf[1] < 0.05
        }
    
    def decompose_series(self, period=6):
        """
        Descomponer serie temporal
        Con pocos periodos, usa índice numérico simple
        """
        if self.ts_values is None or len(self.ts_values) < 4:
            return None
        
        # Usar índice numérico (NO pd.date_range que causa overflow con muchos registros)
        ts_series = pd.Series(
            self.ts_values,
            index=np.arange(len(self.ts_values))
        )
        
        try:
            # Ajustar período según longitud
            adjusted_period = min(period, max(2, len(self.ts_values)//2))
            
            decomp = seasonal_decompose(ts_series, model='additive', period=adjusted_period)
            return {
                'trend': decomp.trend,
                'seasonal': decomp.seasonal,
                'resid': decomp.resid,
                'original': ts_series,
                'adjusted_period': adjusted_period
            }
        except:
            return None
    
    # ==================== PREDICCIÓN ARIMA ====================
    
    def train_arima(self, order=(1, 1, 1), test_size=3):
        """
        Entrenar ARIMA con los periodos disponibles
        test_size: cuántos periodos finales usar para test/predicción
        """
        if self.ts_values is None or len(self.ts_values) < 4:
            return None
        
        ts_array = np.asarray(self.ts_values).flatten()
        
        # Validar que test_size no sea mayor que los datos disponibles
        test_size = min(test_size, max(1, len(ts_array) - 1))
        train_size = len(ts_array) - test_size
        
        train_ts = ts_array[:train_size]
        test_ts = ts_array[train_size:]
        
        if len(train_ts) < 2 or len(test_ts) < 1:
            return None
        
        try:
            # Entrenar ARIMA
            model = ARIMA(train_ts, order=order)
            fitted = model.fit()
            
            # Pronosticar
            forecast = fitted.get_forecast(steps=len(test_ts))
            pred = np.asarray(forecast.predicted_mean).flatten()
            
            # Métricas
            metrics = {
                'rmse': np.sqrt(mean_squared_error(test_ts, pred)),
                'mae': mean_absolute_error(test_ts, pred),
                'mse': mean_squared_error(test_ts, pred)
            }
            
            return {
                'model': fitted,
                'train': train_ts,
                'test': test_ts,
                'predictions': pred,
                'metrics': metrics,
                'train_size': train_size,
                'test_periods': self.ts_periodos[train_size:] if self.ts_periodos is not None else None
            }
        except Exception as e:
            return None