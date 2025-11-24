import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from config import CLUSTERING
from utils import plot_scatter_clusters, plot_cluster_distribution

def show_clustering(df_data, score_cols):
    """Mostrar analisis de clustering"""
    st.header("Analisis de Clustering de Estudiantes")
    
    st.markdown("""
    Agrupa estudiantes segun similitudes en sus puntuaciones ICFES
    utilizando KMeans y reduccion dimensional con PCA.
    """)
    
    st.markdown(f"Areas encontradas: {', '.join([c.replace('PUNT_', '') for c in score_cols])}")
    
    # ==================== PREPARACION DE DATOS ====================
    
    st.markdown("### Procesando Clustering...")
    
    sample_size = CLUSTERING['sample_size']
    df_sample = df_data[score_cols].sample(n=min(sample_size, len(df_data)), random_state=CLUSTERING['random_state'])
    
    # Normalizar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_sample)
    
    st.success(f"Datos normalizados ({len(df_sample)} estudiantes)")
    
    # ==================== CONFIGURACION DE KMEANS ====================
    
    st.markdown("#### KMeans Clustering")
    
    col1, col2 = st.columns(2)
    
    with col1:
        k_optimal = st.slider(
            "Selecciona k (numero de clusters):",
            CLUSTERING['k_min'],
            CLUSTERING['k_max'],
            CLUSTERING['k_default']
        )
    
    with col2:
        st.info(f"Muestra de {len(df_sample)} estudiantes")
    
    # ==================== ENTRENAR KMEANS ====================
    
    kmeans = KMeans(
        n_clusters=k_optimal,
        random_state=CLUSTERING['random_state'],
        n_init=CLUSTERING['n_init']
    )
    labels = kmeans.fit_predict(X_scaled)
    
    st.success(f"KMeans completado con {k_optimal} clusters")
    
    # ==================== PCA PARA VISUALIZACION ====================
    
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    # ==================== GRAFICOS ====================
    
    st.markdown("#### Visualizacion de Clusters (PCA 2D)")
    fig_scatter = plot_scatter_clusters(X_pca, labels, k_optimal)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("#### Distribucion de Estudiantes por Cluster")
    cluster_counts = pd.Series(labels).value_counts().sort_index()
    fig_bar = plot_cluster_distribution(cluster_counts)
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # ==================== INFORMACION DE PCA ====================
    
    st.markdown("#### Varianza Explicada")
    
    var_exp = pca.explained_variance_ratio_
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("PC1", f"{var_exp[0]*100:.1f}%")
    
    with col2:
        st.metric("PC2", f"{var_exp[1]*100:.1f}%")
    
    with col3:
        st.metric("Total", f"{sum(var_exp)*100:.1f}%")
    
    st.success(f"Varianza total explicada: {sum(var_exp)*100:.1f}%")
    
    # ==================== TABLA DE CLUSTERS ====================
    
    st.markdown("#### Estadisticas por Cluster")
    
    cluster_stats = []
    for cluster_id in range(k_optimal):
        cluster_mask = labels == cluster_id
        cluster_size = cluster_mask.sum()
        cluster_percentage = (cluster_size / len(labels)) * 100
        
        cluster_stats.append({
            'Cluster': cluster_id,
            'Estudiantes': cluster_size,
            'Porcentaje': f"{cluster_percentage:.1f}%"
        })
    
    df_stats = pd.DataFrame(cluster_stats)
    st.dataframe(df_stats, use_container_width=True, hide_index=True)