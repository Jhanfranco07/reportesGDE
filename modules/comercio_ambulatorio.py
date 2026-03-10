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

YEAR_ORDER = ["2023", "2024", "2025", "2026"]

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

        df_raw = pd.read_csv(
            data_path,
            sep=";",
            encoding="utf-8-sig",
            dtype=str
        )

        df_raw.columns = df_raw.columns.str.strip()

        # Caso 1: si el archivo ya viene con FECHA_EMITIDA
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
            # Caso 2: columnas por año: 2023, 2024, 2025, 2026...
            year_cols = [col for col in df_raw.columns if col.strip().isdigit()]

            if not year_cols:
                raise ValueError(
                    "No se encontró la columna 'FECHA_EMITIDA' ni columnas de años como 2023, 2024, 2025, 2026."
                )

            df = df_raw[year_cols].melt(
                var_name="AÑO",
                value_name="FECHA_EMITIDA"
            )

            df["FECHA_EMITIDA"] = df["FECHA_EMITIDA"].astype(str).str.strip()

            df = df[
                df["FECHA_EMITIDA"].notna() &
                (df["FECHA_EMITIDA"] != "") &
                (df["FECHA_EMITIDA"].str.lower() != "nan")
            ]

            df["FECHA_EMITIDA"] = pd.to_datetime(
                df["FECHA_EMITIDA"],
                format="%d/%m/%Y",
                errors="coerce"
            )

            df = df.dropna(subset=["FECHA_EMITIDA"])

        # Campos derivados
        df["AÑO"] = df["AÑO"].astype(str)
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
        category_orders={
            "MES": MONTH_ORDER,
            "AÑO": YEAR_ORDER
        },
        height=450,
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
        hovermode="x unified",
        legend_title="Año"
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
        category_orders={
            "MES": MONTH_ORDER,
            "AÑO": YEAR_ORDER
        },
        height=450,
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
        hovermode="x unified",
        legend_title="Año"
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
        .reindex(YEAR_ORDER, fill_value=0)
        .reset_index(name="TOTAL_AUTORIZACIONES")
    )

    fig = px.bar(
        anual,
        x="AÑO",
        y="TOTAL_AUTORIZACIONES",
        color="AÑO",
        text="TOTAL_AUTORIZACIONES",
        color_discrete_map=YEAR_COLORS,
        category_orders={"AÑO": YEAR_ORDER},
        height=350,
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

    fig.update_xaxes(type="category")

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

    for year in YEAR_ORDER:
        if year not in tabla_df.columns:
            tabla_df[year] = 0

    tabla_df["Total"] = tabla_df[YEAR_ORDER].sum(axis=1)
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


def observaciones(df):
    """Muestra observaciones automáticas del comportamiento anual y mensual."""
    st.subheader("📝 Observaciones")

    total_anual = (
        df.groupby("AÑO")
        .size()
        .reindex(YEAR_ORDER, fill_value=0)
    )

    mes_general = (
        df.groupby(["MES_NUM", "MES"])
        .size()
        .reset_index(name="TOTAL")
        .sort_values(["TOTAL", "MES_NUM"], ascending=[False, True])
        .iloc[0]
    )

    pico_por_anio = (
        df.groupby(["AÑO", "MES_NUM", "MES"])
        .size()
        .reset_index(name="TOTAL")
        .sort_values(["AÑO", "TOTAL", "MES_NUM"], ascending=[True, False, True])
        .drop_duplicates(subset=["AÑO"])
        .sort_values("AÑO")
    )

    def obtener_pico(anio):
        fila = pico_por_anio[pico_por_anio["AÑO"] == anio]
        return fila.iloc[0] if not fila.empty else None

    pico_2023 = obtener_pico("2023")
    pico_2024 = obtener_pico("2024")
    pico_2025 = obtener_pico("2025")
    pico_2026 = obtener_pico("2026")

    def variacion_pct(base, actual):
        if base == 0:
            return None
        return ((actual - base) / base) * 100

    var_23_24 = variacion_pct(total_anual.get("2023", 0), total_anual.get("2024", 0))
    var_24_25 = variacion_pct(total_anual.get("2024", 0), total_anual.get("2025", 0))
    var_25_26 = variacion_pct(total_anual.get("2025", 0), total_anual.get("2026", 0))

    nota_2026 = ""
    df_2026 = df[df["AÑO"] == "2026"]
    if not df_2026.empty:
        ultimo_mes_2026 = int(df_2026["MES_NUM"].max())
        ultimo_mes_nombre = MONTH_MAP.get(ultimo_mes_2026, "")
        if ultimo_mes_2026 < 12:
            nota_2026 = (
                f"- El año **2026** presenta información parcial hasta **{ultimo_mes_nombre}**, "
                "por lo que su comparación con años completos debe interpretarse con cautela.\n"
            )

    texto = (
        f"- En el periodo analizado, el año con mayor número de autorizaciones emitidas fue "
        f"**{total_anual.idxmax()}**, con **{int(total_anual.max())}** registros.\n"
        f"- El mes con mayor concentración de autorizaciones en todo el periodo fue "
        f"**{mes_general['MES']}**, con **{int(mes_general['TOTAL'])}** registros acumulados.\n"
    )

    if pico_2023 is not None:
        texto += (
            f"- En **2023**, el mes con mayor número de autorizaciones fue "
            f"**{pico_2023['MES']}**, con **{int(pico_2023['TOTAL'])}** registros.\n"
        )

    if pico_2024 is not None:
        texto += (
            f"- En **2024**, el mes con mayor número de autorizaciones fue "
            f"**{pico_2024['MES']}**, con **{int(pico_2024['TOTAL'])}** registros.\n"
        )

    if pico_2025 is not None:
        texto += (
            f"- En **2025**, el mes con mayor número de autorizaciones fue "
            f"**{pico_2025['MES']}**, con **{int(pico_2025['TOTAL'])}** registros.\n"
        )

    if pico_2026 is not None:
        texto += (
            f"- En **2026**, el mes con mayor número de autorizaciones fue "
            f"**{pico_2026['MES']}**, con **{int(pico_2026['TOTAL'])}** registros.\n"
        )

    if var_23_24 is not None:
        tendencia = "disminución" if var_23_24 < 0 else "incremento"
        texto += (
            f"- Entre **2023 y 2024** se observa una **{tendencia}** de "
            f"**{abs(var_23_24):.1f}%** en el total de autorizaciones emitidas.\n"
        )

    if var_24_25 is not None:
        tendencia = "disminución" if var_24_25 < 0 else "incremento"
        texto += (
            f"- Entre **2024 y 2025** se observa una **{tendencia}** de "
            f"**{abs(var_24_25):.1f}%** en el total de autorizaciones emitidas.\n"
        )

    if var_25_26 is not None:
        tendencia = "disminución" if var_25_26 < 0 else "incremento"
        texto += (
            f"- Entre **2025 y 2026** se observa una **{tendencia}** de "
            f"**{abs(var_25_26):.1f}%** en el total registrado.\n"
        )

    texto += nota_2026

    st.info(texto)


def show_comercio_ambulatorio_module():
    """Módulo completo de Comercio Ambulatorio."""
    st.header("📍 Módulo de Autorizaciones de Comercio Ambulatorio")
    st.markdown("---")

    with st.spinner("🔍 Cargando datos..."):
        df = load_comercio_ambulatorio_data()

    if df is None or df.empty:
        st.error("No se pudieron cargar los datos.")
        return

    estadisticas_generales(df)
    st.markdown("---")

    grafico_comparativa_meses(df)
    st.markdown("---")

    grafico_crecimiento_mensual(df)
    st.markdown("---")

    grafico_comparativa_por_ano(df)
    st.markdown("---")

    tabla_resumen(df)
    st.markdown("---")

    observaciones(df)