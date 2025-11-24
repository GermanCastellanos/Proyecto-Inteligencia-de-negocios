import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from config import AREA_MAPPING, FACULTY_PROGRAMS
from utils import plot_scores_bar, show_recommendation_card

# Configuracion API
API_BASE_URL = "http://localhost:8000"

def show_recomendaciones():
    """Mostrar pagina de recomendaciones con API CRUD"""
    st.header("Recomendaciones de Carrera")
    
    st.markdown("""
    Sistema de Recomendacion con API
    - Ingresa puntuaciones de estudiante
    - Guardado
    - Obtiene recomendaciones
    - Gestiona datos
    """)
    
    # ==================== TABS PRINCIPALES ====================
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Crear Estudiante",
        "Obtener Recomendacion",
        "Ver Estudiantes",
        "Gestion"
    ])
    
    # ==================== TAB 1: CREAR ESTUDIANTE ====================
    
    with tab1:
        st.markdown("### Crear Nuevo Estudiante")
        st.markdown("Ingresa las puntuaciones y guarda en la API")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            estudiante_id = st.text_input(
                "ID del Estudiante",
                value="",
                placeholder="EST_001",
                help="Identificador unico del estudiante"
            )
        
        with col2:
            st.markdown("")
            if not estudiante_id:
                st.warning("Ingresa un ID valido")
        
        st.markdown("#### Ingresa Puntuaciones (0-100)")
        
        col1, col2, col3 = st.columns(3)
        
        scores = {}
        
        with col1:
            scores['punt_ingles'] = st.number_input(
                "Ingles",
                min_value=0.0, max_value=100.0, value=75.0, step=1.0
            )
            scores['punt_matematicas'] = st.number_input(
                "Matematicas",
                min_value=0.0, max_value=100.0, value=75.0, step=1.0
            )
        
        with col2:
            scores['punt_sociales_ciudadanas'] = st.number_input(
                "Sociales Ciudadanas",
                min_value=0.0, max_value=100.0, value=75.0, step=1.0
            )
            scores['punt_c_naturales'] = st.number_input(
                "Ciencias Naturales",
                min_value=0.0, max_value=100.0, value=75.0, step=1.0
            )
        
        with col3:
            scores['punt_lectura_critica'] = st.number_input(
                "Lectura Critica",
                min_value=0.0, max_value=100.0, value=75.0, step=1.0
            )
            st.markdown("")
        
        # ==================== MOSTRAR GRAFICO ====================
        
        st.markdown("#### Vista Previa de Puntuaciones")
        
        scores_for_plot = {
            'PUNT_INGLES': scores['punt_ingles'],
            'PUNT_MATEMATICAS': scores['punt_matematicas'],
            'PUNT_SOCIALES_CIUDADANAS': scores['punt_sociales_ciudadanas'],
            'PUNT_C_NATURALES': scores['punt_c_naturales'],
            'PUNT_LECTURA_CRITICA': scores['punt_lectura_critica']
        }
        
        fig = plot_scores_bar(scores_for_plot, f"Estudiante: {estudiante_id or 'Nuevo'}")
        st.plotly_chart(fig, use_container_width=True)
        
        # ==================== BOTON GUARDAR ====================
        
        if st.button("Guardar Estudiante", type="primary", use_container_width=True):
            
            if not estudiante_id:
                st.error("El ID del estudiante es requerido")
            else:
                with st.spinner("Enviando datos a la API..."):
                    try:
                        # Preparar payload
                        payload = {
                            "estudiante_id": estudiante_id,
                            **scores
                        }
                        
                        # POST a la API
                        response = requests.post(
                            f"{API_BASE_URL}/predict",
                            json=payload,
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.success(f"{data['mensaje']}")
                            
                            # Mostrar detalles
                            col_left, col_right = st.columns(2)
                            with col_left:
                                st.write(f"ID: {data['estudiante_id']}")
                                st.write(f"Estado: {data['estado']}")
                            
                            with col_right:
                                st.write(f"Timestamp: {data['timestamp']}")
                            
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Error desconocido')}")
                    
                    except requests.exceptions.ConnectionError:
                        st.error("No se puede conectar con la API. Verificar si esta en localhost:8000")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    # ==================== TAB 2: OBTENER RECOMENDACION (GET) ====================
    
    with tab2:
        st.markdown("### Obtener Recomendacion")
        st.markdown("Recupera las recomendaciones de un estudiante guardado")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            rec_student_id = st.text_input(
                "ID del Estudiante",
                value="",
                placeholder="EST_001",
                key="rec_student",
                help="ID del estudiante para obtener recomendacion"
            )
        
        with col2:
            st.markdown("")
            if st.button("Buscar", type="primary", use_container_width=True):
                
                if not rec_student_id:
                    st.error("Ingresa un ID valido")
                else:
                    with st.spinner(f"Buscando recomendaciones para {rec_student_id}..."):
                        try:
                            # GET recomendacion
                            response = requests.get(
                                f"{API_BASE_URL}/recommendation/{rec_student_id}",
                                timeout=5
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                
                                st.success(f"{data['mensaje']}")
                                
                                # ==================== MOSTRAR DATOS ====================
                                
                                st.markdown("#### Puntuaciones")
                                
                                scores_display = data['puntuaciones']
                                
                                # Grafico
                                fig = plot_scores_bar(scores_display, rec_student_id)
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Tabla de puntuaciones
                                df_scores = pd.DataFrame([
                                    {
                                        'Area': k.replace('PUNT_', ''),
                                        'Puntuacion': v
                                    }
                                    for k, v in scores_display.items()
                                ])
                                
                                st.markdown("Tabla de Puntuaciones:")
                                st.dataframe(df_scores, use_container_width=True, hide_index=True)
                                
                                # ==================== MOSTRAR TOP AREAS ====================
                                
                                st.markdown("#### Areas Destacadas")
                                
                                col1, col2 = st.columns(2)
                                
                                for i, top_area in enumerate(data['top_areas'][:2]):
                                    with col1 if i == 0 else col2:
                                        st.markdown(f"""
                                        <div class="metric-box">
                                            <strong>#{i+1} {top_area['area']}</strong><br>
                                            Puntuacion: <strong>{top_area['puntuacion']:.1f}/100</strong><br>
                                            Categoria: {top_area['categoria']}
                                        </div>
                                        """, unsafe_allow_html=True)
                                
                                # ==================== MOSTRAR RECOMENDACIONES ====================
                                
                                st.markdown("#### Carreras Recomendadas")
                                
                                for rec in data['recomendaciones']:
                                    show_recommendation_card(
                                        position=rec['posicion'],
                                        program=rec['carrera'],
                                        category=rec['categoria'],
                                        reason=rec['razon'],
                                        relevancia=rec['relevancia']
                                    )
                                
                                # ==================== RESUMEN ====================
                                
                                st.markdown("#### Informacion de la Respuesta")
                                
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("ID Estudiante", rec_student_id)
                                
                                with col2:
                                    promedio = sum(scores_display.values()) / len(scores_display)
                                    st.metric("Promedio", f"{promedio:.1f}/100")
                                
                                with col3:
                                    st.metric("Timestamp", datetime.now().strftime("%H:%M:%S"))
                            
                            elif response.status_code == 404:
                                st.error(f"{response.json()['detail']}")
                            
                            else:
                                st.error(f"Error: {response.json().get('detail', 'Error desconocido')}")
                        
                        except requests.exceptions.ConnectionError:
                            st.error("No se puede conectar con la API. Verificar si esta en localhost:8000")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    
    # ==================== TAB 3: VER ESTUDIANTES (GET LIST) ====================
    
    with tab3:
        st.markdown("### Estudiantes Guardados")
        st.markdown("Lista de todos los estudiantes en la API")
        
        if st.button("Refrescar Lista", use_container_width=True):
            try:
                response = requests.get(
                    f"{API_BASE_URL}/students",
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    total = data['total_estudiantes']
                    
                    st.success(f"Total de estudiantes: {total}")
                    
                    if total > 0:
                        # Mostrar tabla
                        estudiantes_list = []
                        for est in data['estudiantes']:
                            estudiantes_list.append({
                                'ID': est['id'],
                                'Timestamp Guardado': est['timestamp_guardado']
                            })
                        
                        df = pd.DataFrame(estudiantes_list)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    else:
                        st.info("No hay estudiantes guardados aun")
                
                else:
                    st.error(f"Error: {response.json()}")
            
            except requests.exceptions.ConnectionError:
                st.error("No se puede conectar con la API")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # ==================== TAB 4: GESTION (GET DETAIL + DELETE) ====================
    
    with tab4:
        st.markdown("### Gestion de Estudiantes")
        
        manage_id = st.text_input(
            "ID del Estudiante",
            value="",
            placeholder="EST_001",
            key="manage_student"
        )
        
        col1, col2 = st.columns(2)
        
        # ==================== BOTON VER DATOS (GET DETAIL) ====================
        
        with col1:
            if st.button("Ver Datos", use_container_width=True):
                
                if not manage_id:
                    st.error("Ingresa un ID valido")
                else:
                    with st.spinner(f"Obteniendo datos de {manage_id}..."):
                        try:
                            response = requests.get(
                                f"{API_BASE_URL}/student/{manage_id}",
                                timeout=5
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                
                                st.success("Datos encontrados")
                                
                                st.markdown(f"""
                                <div class="metric-box">
                                    <strong>ID:</strong> {data['estudiante_id']}<br>
                                    <strong>Guardado:</strong> {data['timestamp_guardado']}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Tabla de puntuaciones
                                puntuaciones = data['puntuaciones']
                                df = pd.DataFrame([
                                    {
                                        'Area': k.replace('PUNT_', ''),
                                        'Puntuacion': v
                                    }
                                    for k, v in puntuaciones.items()
                                ])
                                
                                st.dataframe(df, use_container_width=True, hide_index=True)
                            
                            elif response.status_code == 404:
                                st.error(f"{response.json()['detail']}")
                            
                            else:
                                st.error(f"Error: {response.json()}")
                        
                        except requests.exceptions.ConnectionError:
                            st.error("No se puede conectar con la API")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        # ==================== BOTON ELIMINAR (DELETE) ====================
        
        with col2:
            if st.button("Eliminar", type="secondary", use_container_width=True):
                
                if not manage_id:
                    st.error("Ingresa un ID valido")
                else:
                    # Confirmacion
                    if st.checkbox(f"Confirmar eliminacion de {manage_id}", value=False):
                        
                        with st.spinner(f"Eliminando {manage_id}..."):
                            try:
                                response = requests.delete(
                                    f"{API_BASE_URL}/student/{manage_id}",
                                    timeout=5
                                )
                                
                                if response.status_code == 200:
                                    data = response.json()
                                    st.success(f"{data['mensaje']}")
                                
                                elif response.status_code == 404:
                                    st.error(f"{response.json()['detail']}")
                                
                                else:
                                    st.error(f"Error: {response.json()}")
                            
                            except requests.exceptions.ConnectionError:
                                st.error("No se puede conectar con la API")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
        
        