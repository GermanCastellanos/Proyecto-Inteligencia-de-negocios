# app.py - SIN EMOJIS
"""
Dashboard ICFES - Aplicacion Principal
Integracion con API de Recomendaciones
"""

import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# Importar configuracion y utilidades
from config import PAGE_CONFIG, MESSAGES, CSV_FILE
from utils import apply_styles, load_data

# Importar paginas
from pages.clustering import show_clustering
from pages.arima import show_arima
from pages.recomendaciones import show_recomendaciones
from pages.estadisticas import show_estadisticas

# ==================== CONFIGURACION ====================

st.set_page_config(**PAGE_CONFIG)
apply_styles()

# ==================== HEADER ====================
st.markdown(
    '''
    <style>
        div[data-testid="stSidebarNav"] {display:none;}
        section[data-testid="stSidebar"] header {display:none;}
    </style>
    ''', unsafe_allow_html=True
)

st.markdown(
    '''
    <h1 style="font-size:3rem; margin-bottom: 0.5rem;">
        Dashboard de Prediccion ICFES
    </h1>
    ''',
    unsafe_allow_html=True
)
st.markdown("Sistema de Analisis y Prediccion de Puntuaciones ICFES")
st.markdown("""
- Analisis de clustering de estudiantes
- Prediccion temporal de puntuaciones con ARIMA
- Recomendaciones de carrera basadas en datos
""")

# ==================== CARGAR DATOS (OPCIONAL) ====================

df_data, score_cols = load_data(CSV_FILE)

if df_data is not None and score_cols is not None:
    st.sidebar.success(f"Datos cargados: {len(df_data)} registros")
else:
    st.sidebar.warning("Dataset no disponible (opcional para recomendaciones)")

# ==================== NAVEGACION ====================

st.sidebar.title("Navegacion")
page = st.sidebar.radio(
    "Selecciona una seccion:",
    [
        "Analisis de Clustering",
        "Prediccion ARIMA",
        "Recomendaciones",
        "Estadisticas Generales"
    ]
)

# ==================== MOSTRAR PAGINA SELECCIONADA ====================

if page == "Analisis de Clustering":
    if df_data is not None:
        show_clustering(df_data, score_cols)
    else:
        st.error("Se requiere el dataset para esta seccion")

elif page == "Prediccion ARIMA":
    if df_data is not None:
        show_arima(df_data, score_cols)
    else:
        st.error("Se requiere el dataset para esta seccion")

elif page == "Recomendaciones":
    show_recomendaciones()

elif page == "Estadisticas Generales":
    if df_data is not None:
        show_estadisticas(df_data, score_cols)
    else:
        st.error("Se requiere el dataset para esta seccion")

# ==================== FOOTER ====================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 1rem;">
    <p>Dashboard ICFES</p>
    <p>Analisis del Rendimiento de Estudiantes</p>
</div>
""", unsafe_allow_html=True)