# clustering_engine.py
"""
Módulo de Clusterización
Implementa KMeans, DBSCAN y Clustering Jerárquico
"""

import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from scipy.cluster.hierarchy import linkage, fcluster


class ClusteringEngine:
    """Engine exclusivo para clustering"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.X_scaled = None
        self.X_pca = None
        self.pca = None
        
    def prepare_data(self, df, sample_size=1000):
        """Preparar y normalizar datos"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        X_full = df[numeric_cols].dropna()
        
        X_sample = X_full.sample(n=min(sample_size, len(X_full)), random_state=42)
        self.X_scaled = self.scaler.fit_transform(X_sample)
        
        return {
            'original_shape': X_full.shape,
            'normalized_shape': self.X_scaled.shape
        }
    
    def kmeans(self, n_clusters):
        """Ejecutar KMeans"""
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=5, max_iter=100)
        labels = kmeans.fit_predict(self.X_scaled)
        return {'labels': labels, 'model': kmeans}
    
    def dbscan(self, eps=2.0, min_samples=5):
        """Ejecutar DBSCAN"""
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(self.X_scaled)
        
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)
        
        return {
            'labels': labels,
            'n_clusters': n_clusters,
            'n_noise': n_noise
        }
    
    def hierarchical(self, n_clusters=3):
        """Ejecutar clustering jerárquico"""
        Z = linkage(self.X_scaled, method='ward')
        labels = fcluster(Z, n_clusters, criterion='maxclust') - 1
        return {'labels': labels, 'linkage_matrix': Z}
    
    def k_distance(self, n_neighbors=5):
        """Calcular K-distance para eps de DBSCAN"""
        neighbors = NearestNeighbors(n_neighbors=n_neighbors)
        neighbors_fit = neighbors.fit(self.X_scaled)
        distances, _ = neighbors_fit.kneighbors(self.X_scaled)
        return np.sort(distances[:, -1], axis=0)
    
    def pca_transform(self, n_components=2):
        """Aplicar PCA para visualización"""
        self.pca = PCA(n_components=n_components)
        self.X_pca = self.pca.fit_transform(self.X_scaled)
        return {
            'X_pca': self.X_pca,
            'explained_variance': self.pca.explained_variance_ratio_
        }
