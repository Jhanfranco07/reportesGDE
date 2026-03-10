# modules/comercio_ambulatorio.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from pathlib import Path
from utils.helpers import get_spanish_month

# Paleta de colores para años
YEAR_COLORS = {
    '2023': '#e74c3c',
    '2024': '#3498db',
    '2025': '#2ecc71',
    '2026': '#f39c12'
}

MONTH_ORDER = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
               'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

MONTH_NUM_MAP = {
    'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5, 'Junio': 6,
    'Julio': 7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
}


def load_comercio_ambulatorio_data():
    """Carga y procesa los datos de autorizaciones de comercio ambulatorio"""
    try:
        data_path = Path(__file__).parent.parent / "data" / "comercio_ambulatorio.csv"
        df = pd.read_csv(data_path, sep=',', encoding='utf-8')
        
        # Convertir a datetime
        df['FECHA_EMITIDA'] = pd.to_datetime(df['FECHA_EMITIDA'], dayfirst=True)
        
        # Extraer año y mes
        df['AÑO'] = df['FECHA_EMITIDA'].dt.year.astype(str)
        df['MES_NUM'] = df['FECHA_EMITIDA'].dt.month
        df['MES'] = df['MES_NUM'].map(get_spanish_month)
        
        return df
    except Exception as e:
        st.error(f"🚨 Error al cargar datos: {str(e)}")
        return None


def grafico_comparativa_meses(df):
    """Gráfico de barras comparativo: mismos meses en diferentes años"""
    st.subheader("📊 Comparativa por Meses (Años Superpuestos)")
    
    # Contar autorizaciones por mes y año
    comparativa = df.groupby(['MES', 'MES_NUM', 'AÑO']).size().reset_index(name='AUTORIZACIONES')
    comparativa = comparativa.sort_values('MES_NUM')
    
    # Crear gráfico de barras agrupadas
    fig = px.bar(
        comparativa,
        x='MES',
        y='AUTORIZACIONES',
        color='AÑO',
        barmode='group',
        color_discrete_map=YEAR_COLORS,
        height=450,
        category_orders={'MES': MONTH_ORDER},
        labels={'AUTORIZACIONES': 'Cantidad de Autorizaciones', 'MES': 'Mes', 'AÑO': 'Año'}
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title='Mes',
        yaxis_title='Cantidad de Autorizaciones',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def grafico_crecimiento_mensual(df):
    """Gráfico de líneas mostrando crecimiento mes a mes por año"""
    st.subheader("📈 Crecimiento Mensual por Año")
    
    # Contar autorizaciones por mes y año
    monthly_data = df.groupby(['MES', 'MES_NUM', 'AÑO']).size().reset_index(name='AUTORIZACIONES')
    monthly_data = monthly_data.sort_values(['AÑO', 'MES_NUM'])
    
    # Crear gráfico de líneas
    fig = px.line(
        monthly_data,
        x='MES',
        y='AUTORIZACIONES',
        color='AÑO',
        markers=True,
        line_shape='spline',
        color_discrete_map=YEAR_COLORS,
        height=450,
        category_orders={'MES': MONTH_ORDER},
        labels={'AUTORIZACIONES': 'Cantidad de Autorizaciones', 'MES': 'Mes', 'AÑO': 'Año'}
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title='Mes',
        yaxis_title='Cantidad de Autorizaciones',
        hovermode='x unified'
    )
    
    fig.update_traces(
        marker=dict(size=8),
        line=dict(width=3)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def grafico_comparativa_por_ano(df):
    """Gráfico de resumen anual con total de autorizaciones"""
    st.subheader("📅 Total de Autorizaciones por Año")
    
    # Contar por año
    anual = df.groupby('AÑO').size().reset_index(name='TOTAL_AUTORIZACIONES')
    anual = anual.sort_values('AÑO')
    
    # Crear gráfico de barras
    fig = px.bar(
        anual,
        x='AÑO',
        y='TOTAL_AUTORIZACIONES',
        color='AÑO',
        color_discrete_map=YEAR_COLORS,
        height=350,
        text='TOTAL_AUTORIZACIONES',
        labels={'TOTAL_AUTORIZACIONES': 'Total de Autorizaciones', 'AÑO': 'Año'}
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title='Año',
        yaxis_title='Total de Autorizaciones',
        showlegend=False
    )
    
    fig.update_traces(
        textposition='outside',
        marker_line_color='rgba(0,0,0,0.3)',
        marker_line_width=2
    )
    
    st.plotly_chart(fig, use_container_width=True)


def tabla_resumen(df):
    """Tabla resumen con estadísticas por mes y año"""
    st.subheader("📋 Tabla Resumen: Autorizaciones por Mes y Año")
    
    # Pivot table
    resumen = df.groupby(['MES', 'MES_NUM']).agg({
        'AÑO': lambda x: x.value_counts().to_dict()
    }).reset_index()
    
    # Crear tabla formateada
    tabla_data = []
    for _, row in resumen.iterrows():
        mes = row['MES']
        años_data = row['AÑO']
        tabla_data.append({
            'Mes': mes,
            '2023': años_data.get('2023', 0),
            '2024': años_data.get('2024', 0),
            '2025': años_data.get('2025', 0),
            '2026': años_data.get('2026', 0),
            'Total': sum(años_data.values())
        })
    
    tabla_df = pd.DataFrame(tabla_data)
    
    # Mostrar tabla interactiva
    st.dataframe(
        tabla_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Mes": st.column_config.TextColumn("Mes", width="medium"),
            "2023": st.column_config.NumberColumn("2023", format="%d"),
            "2024": st.column_config.NumberColumn("2024", format="%d"),
            "2025": st.column_config.NumberColumn("2025", format="%d"),
            "2026": st.column_config.NumberColumn("2026", format="%d"),
            "Total": st.column_config.NumberColumn("Total", format="%d"),
        }
    )


def estadisticas_generales(df):
    """Mostrar KPIs generales"""
    st.subheader("📊 Estadísticas Generales")
    
    c1, c2, c3, c4 = st.columns(4)
    
    # Total de autorizaciones
    c1.metric("📜 Total Autorizaciones", len(df))
    
    # Años representados
    c2.metric("📅 Años", df['AÑO'].nunique())
    
    # Mes con más autorizaciones
    mes_max = df.groupby('MES').size().idxmax()
    c3.metric("🏆 Mes Más Activo", mes_max)
    
    # Promedio por mes
    promedio = len(df) / df['MES_NUM'].nunique()
    c4.metric("📈 Promedio/Mes", f"{promedio:.1f}")


def show_comercio_ambulatorio_module():
    """Módulo completo de Comercio Ambulatorio"""
    st.header("📍 Módulo de Autorizaciones de Comercio Ambulatorio")
    st.markdown("---")
    
    with st.spinner("🔍 Cargando datos..."):
        df = load_comercio_ambulatorio_data()
    
    if df is None or df.empty:
        st.error("No se pudieron cargar los datos.")
        return
    
    # Estadísticas generales
    estadisticas_generales(df)
    st.markdown("---")
    
    # Comparativa por meses
    grafico_comparativa_meses(df)
    st.markdown("---")
    
    # Crecimiento mensual
    grafico_crecimiento_mensual(df)
    st.markdown("---")
    
    # Comparativa anual
    grafico_comparativa_por_ano(df)
    st.markdown("---")
    
    # Tabla resumen
    tabla_resumen(df)
