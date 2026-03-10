# modules/comercio_ambulatorio.py

import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

# Paleta de colores por año
YEAR_COLORS = {
    "2023": "#e74c3c",
    "2024": "#3498db",
    "2025": "#2ecc71",
    "2026": "#f39c12",
}

MONTH_ORDER = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

MONTH_MAP = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}


def get_spanish_month(month_num):
    return MONTH_MAP.get(month_num, "")


def load_comercio_ambulatorio_data():
    """Carga y procesa los datos de autorizaciones de comercio ambulatorio."""
    try:
        data_path = Path(__file__).parent.parent / "data" / "comercio_ambulatorio.csv"

        # Leer CSV como texto para evitar problemas al inicio
        df_raw = pd.read_csv(
            data_path,
            sep=";",
            encoding="utf-8-sig",
            dtype=str
        )

        # Limpiar nombres de columnas
        df_raw.columns = df_raw.columns.str.strip()

        # Caso 1: si ya existe una columna FECHA_EMITIDA
        if "FECHA_EMITIDA" in df_raw.columns:
            df = df_raw.copy()
            df["FECHA_EMITIDA"] = pd.to_datetime(
                df["FECHA_EMITIDA"],
                dayfirst=True,
                errors="coerce"
            )
            df = df.dropna(subset=["FECHA_EMITIDA"])
            df["AÑO"] = df["FECHA_EMITIDA"].dt.year.astype(str)

        else:
            # Caso 2: tu CSV actual viene con columnas 2023, 2024, 2025, 2026...
            year_cols = [col for col in df_raw.columns if col.strip().isdigit()]

            if not year_cols:
                raise ValueError(
                    "No se encontró la columna 'FECHA_EMITIDA' ni columnas de años como 2023, 2024, 2025, 2026."
                )

            # Convertir de formato ancho a formato largo
            df = df_raw[year_cols].melt(
                var_name="AÑO",
                value_name="FECHA_EMITIDA"
            )

            # Limpiar vacíos
            df["FECHA_EMITIDA"] = df["FECHA_EMITIDA"].astype(str).str.strip()
            df = df[
                df["FECHA_EMITIDA"].notna() &
                (df["FECHA_EMITIDA"] != "") &
                (df["FECHA_EMITIDA"].str.lower() != "nan")
            ]

            # Convertir a fecha
            df["FECHA_EMITIDA"] = pd.to_datetime(
                df["FECHA_EMITIDA"],
                format="%d/%m/%Y",
                errors="coerce"
            )

            # Quitar fechas inválidas
            df = df.dropna(subset=["FECHA_EMITIDA"])

        # Campos derivados
        df["MES_NUM"] = df["FECHA_EMITIDA"].dt.month
        df["MES"] = df["MES_NUM"].map(get_spanish_month)

        # Ordenar por fecha
        df = df.sort_values("FECHA_EMITIDA").reset_index(drop=True)

        return df

    except Exception as e:
        st.error(f"🚨 Error al cargar datos: {str(e)}")
        return None


def grafico_comparativa_meses(df):
    """Gráfico de barras comparativo por meses y años."""
    st.subheader("📊 Comparativa por Meses")

    comparativa = (
        df.groupby(["MES", "MES_NUM", "AÑO"])
        .size()
        .reset_index(name="AUTORIZACIONES")
        .sort_values(["MES_NUM", "AÑO"])
    )

    fig = px.bar(
        comparativa,
        x="MES",
        y="AUTORIZACIONES",
        color="AÑO",
        barmode="group",
        color_discrete_map=YEAR_COLORS,
        height=450,
        category_orders={"MES": MONTH_ORDER},
        labels={
            "AUTORIZACIONES": "Cantidad de Autorizaciones",
            "MES": "Mes",
            "AÑO": "Año",
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Mes",
        yaxis_title="Cantidad de Autorizaciones",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)


def grafico_crecimiento_mensual(df):
    """Gráfico de líneas de crecimiento mensual por año."""
    st.subheader("📈 Crecimiento Mensual por Año")

    monthly_data = (
        df.groupby(["MES", "MES_NUM", "AÑO"])
        .size()
        .reset_index(name="AUTORIZACIONES")
        .sort_values(["AÑO", "MES_NUM"])
    )

    fig = px.line(
        monthly_data,
        x="MES",
        y="AUTORIZACIONES",
        color="AÑO",
        markers=True,
        line_shape="spline",
        color_discrete_map=YEAR_COLORS,
        height=450,
        category_orders={"MES": MONTH_ORDER},
        labels={
            "AUTORIZACIONES": "Cantidad de Autorizaciones",
            "MES": "Mes",
            "AÑO": "Año",
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Mes",
        yaxis_title="Cantidad de Autorizaciones",
        hovermode="x unified"
    )

    fig.update_traces(
        marker=dict(size=8),
        line=dict(width=3)
    )

    st.plotly_chart(fig, use_container_width=True)


def grafico_comparativa_por_ano(df):
    """Gráfico de barras con totales por año."""
    st.subheader("📅 Total de Autorizaciones por Año")

    anual = (
        df.groupby("AÑO")
        .size()
        .reset_index(name="TOTAL_AUTORIZACIONES")
        .sort_values("AÑO")
    )

    fig = px.bar(
        anual,
        x="AÑO",
        y="TOTAL_AUTORIZACIONES",
        color="AÑO",
        color_discrete_map=YEAR_COLORS,
        height=350,
        text="TOTAL_AUTORIZACIONES",
        labels={
            "TOTAL_AUTORIZACIONES": "Total de Autorizaciones",
            "AÑO": "Año",
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Año",
        yaxis_title="Total de Autorizaciones",
        showlegend=False
    )

    fig.update_traces(
        textposition="outside",
        marker_line_color="rgba(0,0,0,0.3)",
        marker_line_width=2
    )

    st.plotly_chart(fig, use_container_width=True)


def tabla_resumen(df):
    """Tabla resumen por mes y año."""
    st.subheader("📋 Tabla Resumen: Autorizaciones por Mes y Año")

    resumen = (
        df.groupby(["MES_NUM", "MES", "AÑO"])
        .size()
        .reset_index(name="TOTAL")
    )

    tabla_df = (
        resumen.pivot_table(
            index=["MES_NUM", "MES"],
            columns="AÑO",
            values="TOTAL",
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
        .sort_values("MES_NUM")
    )

    # Asegurar columnas
    for year in ["2023", "2024", "2025", "2026"]:
        if year not in tabla_df.columns:
            tabla_df[year] = 0

    tabla_df["Total"] = tabla_df[["2023", "2024", "2025", "2026"]].sum(axis=1)

    tabla_df = tabla_df[["MES", "2023", "2024", "2025", "2026", "Total"]]
    tabla_df = tabla_df.rename(columns={"MES": "Mes"})

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
    """Muestra KPIs generales."""
    st.subheader("📊 Estadísticas Generales")

    c1, c2, c3, c4 = st.columns(4)

    total_autorizaciones = len(df)
    total_anios = df["AÑO"].nunique()

    mes_max = (
        df.groupby("MES")
        .size()
        .sort_values(ascending=False)
        .index[0]
    )

    promedio_mes = (
        df.groupby(["AÑO", "MES_NUM"])
        .size()
        .mean()
    )

    c1.metric("📜 Total Autorizaciones", total_autorizaciones)
    c2.metric("📅 Años", total_anios)
    c3.metric("🏆 Mes Más Activo", mes_max)
    c4.metric("📈 Promedio/Mes", f"{promedio_mes:.1f}")


def show_comercio_ambulatorio_module():
    """Módulo completo de Comercio Ambulatorio."""
    st.header("📍 Módulo de Autorizaciones de Comercio Ambulatorio")
    st.markdown("---")

    with st.spinner("🔍 Cargando datos..."):
        df = load_comercio_ambulatorio_data()

    if df is None or df.empty:
        st.error("No se pudieron cargar los datos.")
        return

    # Debug temporal, si quieres luego lo quitas
    # st.write("Columnas:", df.columns.tolist())
    # st.write(df.head())

    estadisticas_generales(df)
    st.markdown("---")

    grafico_comparativa_meses(df)
    st.markdown("---")

    grafico_crecimiento_mensual(df)
    st.markdown("---")

    grafico_comparativa_por_ano(df)
    st.markdown("---")

    tabla_resumen(df)