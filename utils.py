# utils.py
"""
Funciones utilitarias compartidas
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import COLORS

# ==================== ESTILOS ====================

def apply_styles():
    """Aplicar estilos CSS"""
    st.markdown(f"""
    <style>
        .main-header {{
            font-size: 2.5rem;
            font-weight: bold;
            color: {COLORS['primary']};
            text-align: center;
            margin-bottom: 1rem;
        }}
        .metric-box {{
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid {COLORS['primary']};
            margin: 0.5rem 0;
        }}
        .prediction-card {{
            background-color: #e8f4f8;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
            border-left: 5px solid {COLORS['success']};
        }}
    </style>
    """, unsafe_allow_html=True)

# ==================== CARGA DE DATOS ====================

@st.cache_data
def load_data(csv_file):
    """Cargar y preparar datos CSV"""
    try:
        df = pd.read_csv(csv_file)
        # Convertir columnas de puntuación a numérico
        score_cols = [col for col in df.columns if 'PUNT_' in col]
        df[score_cols] = df[score_cols].apply(pd.to_numeric, errors='coerce')
        df[score_cols] = df[score_cols].fillna(0)
        return df, score_cols
    except FileNotFoundError:
        st.error(f"❌ Archivo '{csv_file}' no encontrado")
        return None, None

# ==================== GRÁFICOS ====================

def plot_scatter_clusters(X_pca, labels, k_optimal):
    """Gráfico scatter de clusters"""
    df_plot = pd.DataFrame({
        'PC1': X_pca[:, 0],
        'PC2': X_pca[:, 1],
        'Cluster': labels
    })
    
    fig = px.scatter(
        df_plot,
        x='PC1',
        y='PC2',
        color='Cluster',
        title=f'Clusters KMeans (k={k_optimal})',
        labels={'PC1': 'PC1', 'PC2': 'PC2'},
        color_continuous_scale='Viridis',
        height=500
    )
    fig.update_traces(marker=dict(size=8))
    return fig

def plot_cluster_distribution(cluster_counts):
    """Gráfico de distribución de clusters"""
    fig = px.bar(
        x=cluster_counts.index,
        y=cluster_counts.values,
        labels={'x': 'Cluster', 'y': 'Estudiantes'},
        title='Distribución de Estudiantes por Cluster',
        color=cluster_counts.values,
        color_continuous_scale='Blues',
        height=400
    )
    return fig

def plot_scores_bar(scores_dict, student_id="Estudiante"):
    """Gráfico de barras de puntuaciones"""
    df_scores = pd.DataFrame({
        'Área': [k.replace('PUNT_', '') for k in scores_dict.keys()],
        'Puntuación': list(scores_dict.values())
    })
    
    fig = px.bar(
        df_scores,
        x='Área',
        y='Puntuación',
        title=f'Puntuaciones - {student_id}',
        color='Puntuación',
        color_continuous_scale='Blues',
        height=400
    )
    return fig

def plot_timeseries(ts_data, area_name):
    """Gráfico de serie temporal"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(ts_data))),
        y=ts_data.values,
        mode='lines+markers',
        name=area_name,
        line=dict(color=COLORS['primary'], width=2),
        marker=dict(size=8)
    ))
    fig.update_layout(
        title=f'Serie Temporal: {area_name}',
        xaxis_title='Período',
        yaxis_title='Puntuación',
        hovermode='x unified',
        height=400
    )
    return fig

def plot_arima_prediction(train, test, predictions):
    """Gráfico de predicción ARIMA"""
    fig = go.Figure()
    
    x_train = list(range(len(train)))
    x_test = list(range(len(train), len(train) + len(test)))
    
    fig.add_trace(go.Scatter(
        x=x_train, y=train.values, mode='lines+markers',
        name='Entrenamiento', line=dict(color='blue'), marker=dict(size=6)
    ))
    fig.add_trace(go.Scatter(
        x=x_test, y=test.values, mode='lines+markers',
        name='Real', line=dict(color='orange'), marker=dict(size=6)
    ))
    fig.add_trace(go.Scatter(
        x=x_test, y=predictions.values, mode='lines+markers',
        name='Predicción ARIMA', line=dict(color='green', dash='dash'), marker=dict(size=6)
    ))
    
    fig.update_layout(
        title='Predicción ARIMA',
        xaxis_title='Período',
        yaxis_title='Puntuación',
        hovermode='x unified',
        height=500
    )
    return fig

# ==================== COMPONENTES DE UI ====================

def show_metric_box(title, value, subtitle=""):
    """Mostrar caja de métrica"""
    html = f"""
    <div class="metric-box">
        <strong>{title}</strong><br>
        <p style="font-size: 1.5rem; margin: 0.5rem 0;">{value}</p>
        {f'<p style="color: #7f8c8d;">{subtitle}</p>' if subtitle else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def show_recommendation_card(position, program, category, reason, relevancia):
    """Mostrar tarjeta de recomendación"""
    html = f"""
    <div class="prediction-card">
        <h4>🎓 Opción {position}: {program}</h4>
        <p><strong>Categoría:</strong> {category}</p>
        <p><strong>Razón:</strong> {reason}</p>
        <p><strong>Relevancia:</strong> {relevancia*100:.0f}%</p>
        <div style="background-color: {COLORS['info']}; width: {relevancia*100}%; height: 15px; border-radius: 5px;"></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
