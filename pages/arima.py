import streamlit as st
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
from config import ARIMA as ARIMA_CONFIG
from utils import plot_timeseries, plot_arima_prediction

def show_arima(df_data, score_cols):
    """Mostrar pagina de prediccion ARIMA"""
    st.header("Prediccion de Puntuaciones ICFES con ARIMA")
    
    st.markdown("""
    Analisis de Series Temporales:
    - Agrupacion de puntuaciones por PERIODO
    - Descomposicion de series temporales
    - Prediccion con modelo ARIMA
    """)
    
    # ==================== VERIFICAR COLUMNA PERIODO ====================
    
    if 'PERIODO' not in df_data.columns:
        st.error("No se encuentra la columna PERIODO")
        st.stop()
    
    # ==================== SELECCIONAR AREA ====================
    
    selected_area = st.selectbox(
        "Selecciona un area para predecir:",
        options=score_cols,
        format_func=lambda x: x.replace('PUNT_', '')
    )
    
    # ==================== CREAR SERIE TEMPORAL ====================
    
    ts_data = df_data.groupby('PERIODO')[selected_area].mean().sort_index()
    
    if len(ts_data) < ARIMA_CONFIG['min_periods']:
        st.error(f"No hay suficientes periodos para ARIMA (se necesitan al menos {ARIMA_CONFIG['min_periods']})")
        st.stop()
    
    st.success(f"Serie temporal creada: {len(ts_data)} periodos unicos")
    
    st.markdown(f"""
    <div class="metric-box">
        <strong>Informacion de la Serie:</strong><br>
        Periodos: {len(ts_data)}<br>
        Rango de puntajes: {ts_data.min():.1f} - {ts_data.max():.1f}
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== GRAFICO SERIE TEMPORAL ====================
    
    st.markdown("#### Serie Temporal Original")
    fig_ts = plot_timeseries(ts_data, selected_area.replace('PUNT_', ''))
    st.plotly_chart(fig_ts, use_container_width=True)
    
    # ==================== PRUEBA ADF ====================
    
    st.markdown("#### Prueba ADF de Estacionariedad")
    
    adf_result = adfuller(ts_data.values)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Estadistico ADF", f"{adf_result[0]:.4f}")
    
    with col2:
        st.metric("P-valor", f"{adf_result[1]:.4f}")
    
    with col3:
        status = "Estacionaria" if adf_result[1] < 0.05 else "No estacionaria"
        st.metric("Estado", status)
    
    # ==================== ARIMA ====================
    
    st.markdown("#### Prediccion ARIMA")
    
    if st.button("Generar Prediccion ARIMA", type="primary", use_container_width=True):
        
        with st.spinner("Entrenando modelo ARIMA..."):
            try:
                test_size = min(ARIMA_CONFIG['test_size'], len(ts_data) // 3)
                train = ts_data[:-test_size]
                test = ts_data[-test_size:]
                
                # Entrenar ARIMA
                model = ARIMA(train, order=ARIMA_CONFIG['order'])
                fitted_model = model.fit()
                
                # Predecir
                predictions = fitted_model.forecast(steps=test_size)
                
                # Calcular metricas
                rmse = np.sqrt(mean_squared_error(test, predictions))
                mae = mean_absolute_error(test, predictions)
                mse = mean_squared_error(test, predictions)
                
                st.success("Modelo ARIMA entrenado")
                
                # ==================== METRICAS ====================
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("RMSE", f"{rmse:.4f}")
                
                with col2:
                    st.metric("MAE", f"{mae:.4f}")
                
                with col3:
                    st.metric("MSE", f"{mse:.4f}")
                
                # ==================== GRAFICO PREDICCION ====================
                
                fig_pred = plot_arima_prediction(train, test, predictions)
                st.plotly_chart(fig_pred, use_container_width=True)
                
                # ==================== INTERPRETACION ====================
                
                st.markdown("""
                <div class="prediction-card">
                    <h4>Interpretacion de Resultados:</h4>
                    <ul>
                        <li><strong>Linea Azul (Entrenamiento):</strong> Datos historicos usados para entrenar</li>
                        <li><strong>Linea Naranja (Real):</strong> Valores reales del periodo final</li>
                        <li><strong>Linea Verde (Prediccion):</strong> Lo que el modelo predice</li>
                    </ul>
                    <p><strong>Nota:</strong> Con pocos periodos, ARIMA muestra tendencias generales.</p>
                </div>
                """, unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"Error: {str(e)}")