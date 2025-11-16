"""
Dashboard Interactivo de Recomendación ICFES - VERSIÓN CORREGIDA
Sprint 4 - Compatible con API flexible
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# ==================== CONFIGURACIÓN ====================

st.set_page_config(
    page_title="Dashboard ICFES - Recomendaciones",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL de la API
API_URL = "http://localhost:8000"

# ==================== ESTILOS ====================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .recommendation-card {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 5px solid #2ecc71;
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNCIONES API ====================

def check_api_health():
    """Verificar si la API está activa"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def upload_student_scores_v1(estudiante_id, scores):
    """Versión 1: POST /upload con snake_case"""
    try:
        data = {
            "estudiante_id": estudiante_id,
            "punt_ingles": scores['ingles'],
            "punt_matematicas": scores['matematicas'],
            "punt_sociales_ciudadanas": scores['sociales'],
            "punt_c_naturales": scores['naturales'],
            "punt_lectura_critica": scores['lectura']
        }
        response = requests.post(f"{API_URL}/upload", json=data, timeout=5)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        return None


def upload_student_scores_v2(estudiante_id, scores):
    """Versión 2: POST /predict con camelCase (alternativo)"""
    try:
        data = {
            "estudiante_id": estudiante_id,
            "punt_ingles": scores['ingles'],
            "punt_matematicas": scores['matematicas'],
            "punt_sociales_ciudadanas": scores['sociales'],
            "punt_c_naturales": scores['naturales'],
            "punt_lectura_critica": scores['lectura']
        }
        response = requests.post(f"{API_URL}/predict", json=data, timeout=5)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        return None


def upload_student_scores(estudiante_id, scores):
    """Intentar ambas versiones automáticamente"""
    # Intentar versión 1
    result = upload_student_scores_v1(estudiante_id, scores)
    if result:
        return result
    
    # Si falla, intentar versión 2
    result = upload_student_scores_v2(estudiante_id, scores)
    if result:
        return result
    
    return None


def get_recommendations(estudiante_id):
    """Obtener recomendaciones de un estudiante"""
    try:
        response = requests.get(f"{API_URL}/recommendation/{estudiante_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        
        # Si falla, intentar con /recommendations
        response = requests.get(f"{API_URL}/recommendations/{estudiante_id}", timeout=5)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def get_all_students():
    """Obtener lista de estudiantes"""
    try:
        response = requests.get(f"{API_URL}/students", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None


def get_stats():
    """Obtener estadísticas del sistema"""
    try:
        response = requests.get(f"{API_URL}/stats", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None


# ==================== HEADER ====================

st.markdown('<p class="main-header">🎓 Sistema de Recomendación ICFES</p>', unsafe_allow_html=True)

# Verificar estado de la API
api_status = check_api_health()

col_status = st.sidebar.columns(3)
with col_status[0]:
    if api_status:
        st.sidebar.success("✅ API Activa")
    else:
        st.sidebar.error("❌ API Inactiva")

if not api_status:
    st.error("⚠️ No se puede conectar con la API.")
    st.info("""
    **Solución:**
    1. Abre una terminal
    2. Ejecuta: `python main.py`
    3. Espera a que aparezca: "Application startup complete"
    4. Recarga esta página
    """)
    st.stop()

# ==================== SIDEBAR ====================

st.sidebar.title("🎯 Navegación")
page = st.sidebar.radio(
    "Selecciona una opción:",
    ["📝 Ingresar Estudiante", "📊 Ver Recomendaciones", "👥 Estudiantes Registrados"]
)

# ==================== PÁGINA 1: INGRESAR ESTUDIANTE ====================

if page == "📝 Ingresar Estudiante":
    st.header("📝 Registrar Nuevo Estudiante")
    
    with st.form("form_estudiante"):
        st.subheader("Datos del Estudiante")
        
        estudiante_id = st.text_input(
            "ID del Estudiante",
            placeholder="Ej: EST001",
            help="Identificador único del estudiante"
        )
        
        st.markdown("### Puntuaciones ICFES (0-100)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ingles = st.slider("📘 Inglés", 0, 100, 75)
            matematicas = st.slider("🔢 Matemáticas", 0, 100, 80)
            sociales = st.slider("🌍 Sociales Ciudadanas", 0, 100, 70)
        
        with col2:
            naturales = st.slider("🧪 Ciencias Naturales", 0, 100, 85)
            lectura = st.slider("📖 Lectura Crítica", 0, 100, 90)
        
        submit_button = st.form_submit_button("✅ Registrar Estudiante", use_container_width=True)
    
    if submit_button:
        if not estudiante_id:
            st.error("❌ Por favor ingresa un ID de estudiante")
        else:
            scores = {
                'ingles': ingles,
                'matematicas': matematicas,
                'sociales': sociales,
                'naturales': naturales,
                'lectura': lectura
            }
            
            with st.spinner("📤 Guardando datos..."):
                result = upload_student_scores(estudiante_id, scores)
            
            if result:
                st.success(f"✅ ¡Estudiante registrado exitosamente!")
                st.balloons()
                
                # Mostrar resumen
                st.markdown("### 📊 Puntuaciones Registradas")
                df_scores = pd.DataFrame({
                    'Área': ['Inglés', 'Matemáticas', 'Sociales', 'Naturales', 'Lectura'],
                    'Puntuación': [ingles, matematicas, sociales, naturales, lectura]
                })
                
                fig = px.bar(
                    df_scores,
                    x='Área',
                    y='Puntuación',
                    title=f'Puntuaciones de {estudiante_id}',
                    color='Puntuación',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Promedio
                promedio = (ingles + matematicas + sociales + naturales + lectura) / 5
                st.metric("Puntaje Promedio", f"{promedio:.1f}/100")
            else:
                st.error("❌ Error guardando datos. Verifica que la API esté corriendo.")
                st.info("💡 Ejecuta en una terminal: `python main.py`")


# ==================== PÁGINA 2: VER RECOMENDACIONES ====================

elif page == "📊 Ver Recomendaciones":
    st.header("📊 Obtener Recomendaciones de Carrera")
    
    students_data = get_all_students()
    
    if students_data and students_data.get('total_estudiantes', 0) > 0:
        estudiantes = [e['id'] for e in students_data['estudiantes']]
        
        selected_id = st.selectbox("Selecciona un estudiante:", options=estudiantes)
        
        if st.button("🔍 Obtener Recomendaciones", type="primary", use_container_width=True):
            with st.spinner("Generando recomendaciones..."):
                rec_data = get_recommendations(selected_id)
            
            if rec_data:
                st.success(f"✅ Recomendaciones generadas para {selected_id}")
                
                # Puntuaciones
                st.markdown("### 📊 Puntuaciones del Estudiante")
                
                if 'puntuaciones' in rec_data:
                    puntuaciones = rec_data['puntuaciones']
                elif 'estudiante_puntuaciones' in rec_data:
                    puntuaciones = rec_data['estudiante_puntuaciones']
                else:
                    puntuaciones = {}
                
                if puntuaciones:
                    df_punt = pd.DataFrame({
                        'Área': [k.replace('PUNT_', '') for k in puntuaciones.keys()],
                        'Puntuación': list(puntuaciones.values())
                    })
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig_bar = px.bar(
                            df_punt,
                            x='Área',
                            y='Puntuación',
                            title='Puntuaciones por Área',
                            color='Puntuación',
                            color_continuous_scale='Viridis'
                        )
                        fig_bar.update_layout(height=400)
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    with col2:
                        fig_radar = go.Figure(data=go.Scatterpolar(
                            r=list(puntuaciones.values()),
                            theta=[k.replace('PUNT_', '').replace('_', ' ') for k in puntuaciones.keys()],
                            fill='toself'
                        ))
                        fig_radar.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            title='Perfil del Estudiante',
                            height=400
                        )
                        st.plotly_chart(fig_radar, use_container_width=True)
                
                # Áreas top
                if 'top_areas' in rec_data:
                    st.markdown("### 🎯 Áreas Destacadas")
                    
                    col1, col2 = st.columns(2)
                    
                    for i, top in enumerate(rec_data['top_areas']):
                        with col1 if i == 0 else col2:
                            st.info(f"""
                            **#{i+1} {top['area']}**
                            
                            Puntuación: **{top['puntuacion']}/100**
                            
                            Categoría: {top['categoria']}
                            """)
                
                # Recomendaciones
                if 'recomendaciones' in rec_data:
                    st.markdown("### 💼 Recomendaciones de Carrera")
                    
                    for rec in rec_data['recomendaciones']:
                        st.markdown(f"""
                        <div class="recommendation-card">
                            <h3>🎓 Opción {rec['posicion']}: {rec['carrera']}</h3>
                            <p><strong>Categoría:</strong> {rec['categoria']}</p>
                            <p><strong>Razón:</strong> {rec['razon']}</p>
                            <p><strong>Relevancia:</strong> {rec['relevancia']*100:.0f}%</p>
                            <div style="background-color: #3498db; width: {rec['relevancia']*100}%; height: 10px; border-radius: 5px;"></div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("❌ Error obteniendo recomendaciones")
    else:
        st.warning("⚠️ No hay estudiantes registrados")
        st.info("💡 Ve a 'Ingresar Estudiante' primero")


# ==================== PÁGINA 3: ESTUDIANTES REGISTRADOS ====================

elif page == "👥 Estudiantes Registrados":
    st.header("👥 Estudiantes Registrados en el Sistema")
    
    students_data = get_all_students()
    
    if students_data and students_data.get('total_estudiantes', 0) > 0:
        st.success(f"✅ Total de estudiantes: {students_data['total_estudiantes']}")
        
        estudiantes_list = []
        for est in students_data['estudiantes']:
            rec = get_recommendations(est['id'])
            if rec:
                if 'puntuaciones' in rec:
                    puntuaciones = rec['puntuaciones']
                elif 'estudiante_puntuaciones' in rec:
                    puntuaciones = rec['estudiante_puntuaciones']
                else:
                    puntuaciones = {}
                
                if puntuaciones:
                    promedio = sum(puntuaciones.values()) / len(puntuaciones)
                    top_area = rec['top_areas'][0]['area'] if rec.get('top_areas') else 'N/A'
                    
                    estudiantes_list.append({
                        'ID': est['id'],
                        'Promedio': f"{promedio:.1f}",
                        'Área Top': top_area,
                        'Fecha': datetime.fromisoformat(est['timestamp_guardado']).strftime('%d/%m/%Y')
                    })
        
        if estudiantes_list:
            df_est = pd.DataFrame(estudiantes_list)
            st.dataframe(df_est, use_container_width=True)
            
            # Descarga
            csv = df_est.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Descargar CSV",
                csv,
                "estudiantes.csv",
                "text/csv"
            )
    else:
        st.warning("⚠️ No hay estudiantes registrados")

# ==================== FOOTER ====================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 1rem;">
    <p>🎓 Dashboard ICFES | Sprint 4 | Versión Compatible</p>
</div>
""", unsafe_allow_html=True)