import streamlit as st
import pandas as pd
import plotly.express as px

def show_estadisticas(df_data, score_cols):
    """Mostrar pagina de estadisticas"""
    st.header("Estadisticas Generales del Dataset")
    
    from datetime import datetime
    
    # ==================== RESUMEN GENERAL ====================
    
    st.markdown("### Resumen del Dataset")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Registros", len(df_data))
    
    with col2:
        st.metric("Total de Columnas", len(df_data.columns))
    
    with col3:
        st.metric("Periodos Unicos", df_data['PERIODO'].nunique() if 'PERIODO' in df_data.columns else 'N/A')
    
    with col4:
        st.metric("Fecha de Datos", datetime.now().strftime('%d/%m/%Y'))
    
    # ==================== DISTRIBUCION DE PUNTUACIONES ====================
    
    st.markdown("### Distribucion de Puntuaciones por Area")
    
    df_melted = df_data[score_cols].melt(var_name='Area', value_name='Puntuacion')
    df_melted['Area'] = df_melted['Area'].str.replace('PUNT_', '')
    
    fig = px.box(
        df_melted,
        x='Area',
        y='Puntuacion',
        title='Distribucion de Puntuaciones',
        color='Area',
        height=500
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== MATRIZ DE CORRELACION ====================
    
    st.markdown("### Matriz de Correlacion")
    
    corr_matrix = df_data[score_cols].corr()
    
    fig = px.imshow(
        corr_matrix,
        labels=dict(color="Correlacion"),
        x=[col.replace('PUNT_', '') for col in score_cols],
        y=[col.replace('PUNT_', '') for col in score_cols],
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== ESTADISTICAS DESCRIPTIVAS ====================
    
    st.markdown("### Estadisticas Descriptivas")
    
    stats_df = df_data[score_cols].describe().T
    stats_df.index = stats_df.index.str.replace('PUNT_', '')
    
    st.dataframe(stats_df, use_container_width=True)