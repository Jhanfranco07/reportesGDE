# modules/pachambear.py

import unicodedata
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Colores
TRAMITE_COLORS = {
    "Bolsa de Trabajo": "#3498db",
    "CUL": "#2ecc71",
    "Bolsa de Trabajo + CUL": "#f39c12",
    "Otros": "#95a5a6",
}

CUL_COLORS = {
    "EMITIDO": "#27ae60",
    "BUSQUEDA": "#f39c12",
    "EN PROCESO": "#3498db",
    "SIN ESTADO": "#bdc3c7",
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
    12: "Diciembre",
}


def get_spanish_month(month_num):
    return MONTH_MAP.get(month_num, "")


def normalize_text(text):
    """Normaliza texto para comparar sin tildes ni mayúsculas."""
    if pd.isna(text):
        return ""
    text = str(text).strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.upper()


def classify_tramite(asunto):
    """Clasifica el asunto en tipo de trámite."""
    asunto_norm = normalize_text(asunto)

    if "BOLSA DE TRABAJO" in asunto_norm and (
        "CERTIFICADO UNICO LABORAL" in asunto_norm or " CUL" in asunto_norm or asunto_norm.endswith("CUL")
    ):
        return "Bolsa de Trabajo + CUL"

    if "CERTIFICADO UNICO LABORAL" in asunto_norm or asunto_norm == "CUL":
        return "CUL"

    if "BOLSA DE TRABAJO" in asunto_norm:
        return "Bolsa de Trabajo"

    return "Otros"


def clean_cul_status(value):
    """Limpia el estado CUL."""
    if pd.isna(value):
        return "SIN ESTADO"

    value = str(value).strip().upper()

    if value in {"", "-", "NAN"}:
        return "SIN ESTADO"

    return value


def read_csv_with_fallback(data_path):
    """Lee el CSV intentando varias codificaciones."""
    encodings = ["utf-8-sig", "latin1", "cp1252"]

    for enc in encodings:
        try:
            return pd.read_csv(data_path, sep=";", dtype=str, encoding=enc)
        except UnicodeDecodeError:
            continue

    return pd.read_csv(data_path, sep=";", dtype=str, engine="python")


def load_pachambear_data():
    """Carga y procesa los datos del CSV de PACHAMBEAR."""
    try:
        data_path = Path(__file__).parent.parent / "data" / "pachambear.csv"
        df_raw = read_csv_with_fallback(data_path)

        # Limpiar nombres de columnas
        df_raw.columns = [str(col).strip() for col in df_raw.columns]

        required_cols = [
            "FECHA",
            "NOMBRES Y APELLIDOS",
            "DNI",
            "TELEFONO",
            "ASUNTO",
            "PROFESION U OFICIO",
            "CUL",
        ]

        missing = [col for col in required_cols if col not in df_raw.columns]
        if missing:
            raise ValueError(
                f"Faltan columnas necesarias en el CSV: {', '.join(missing)}"
            )

        df = df_raw[required_cols].copy()

        for col in required_cols:
            df[col] = df[col].fillna("").astype(str).str.strip()

        # Fechas
        df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["FECHA"]).copy()

        # Campos derivados
        df["AÑO"] = df["FECHA"].dt.year.astype(str)
        df["MES_NUM"] = df["FECHA"].dt.month
        df["MES"] = df["MES_NUM"].map(get_spanish_month)
        df["PERIODO"] = df["FECHA"].dt.strftime("%Y-%m")

        # Limpiezas
        df["TELEFONO"] = df["TELEFONO"].replace({"-": "", " -": "", "- ": ""})
        df["PROFESION U OFICIO"] = df["PROFESION U OFICIO"].replace({"": "-", "NAN": "-", "nan": "-"})
        df["CUL"] = df["CUL"].apply(clean_cul_status)
        df["TIPO_TRAMITE"] = df["ASUNTO"].apply(classify_tramite)

        # Etiqueta amigable para tablas/gráficos
        df["PERIODO_LABEL"] = df["MES"] + " " + df["AÑO"]

        df = df.sort_values("FECHA").reset_index(drop=True)
        return df

    except Exception as e:
        st.error(f"🚨 Error al cargar datos: {str(e)}")
        return None


def estadisticas_generales(df):
    """KPIs principales."""
    st.subheader("📊 Estadísticas Generales")
    st.caption("CUL = Certificado Único Laboral")

    c1, c2, c3, c4, c5 = st.columns(5)

    periodo = f"{df['FECHA'].min().strftime('%d/%m/%Y')} - {df['FECHA'].max().strftime('%d/%m/%Y')}"
    total_registros = len(df)
    total_bolsa = int((df["TIPO_TRAMITE"] == "Bolsa de Trabajo").sum())
    total_cul = int((df["TIPO_TRAMITE"] == "CUL").sum())
    total_combo = int((df["TIPO_TRAMITE"] == "Bolsa de Trabajo + CUL").sum())

    c1.metric("📅 Período", periodo)
    c2.metric("🧑 Total Registros", total_registros)
    c3.metric("💼 Bolsa de Trabajo", total_bolsa)
    c4.metric("📄 CUL", total_cul)
    c5.metric("🔗 Bolsa + CUL", total_combo)


def create_tramite_chart(df):
    """Gráfico por tipo de trámite."""
    st.subheader("📌 Solicitudes por Tipo de Trámite")

    resumen = (
        df["TIPO_TRAMITE"]
        .value_counts()
        .rename_axis("TIPO_TRAMITE")
        .reset_index(name="TOTAL")
    )

    fig = px.bar(
        resumen,
        x="TOTAL",
        y="TIPO_TRAMITE",
        orientation="h",
        color="TIPO_TRAMITE",
        color_discrete_map=TRAMITE_COLORS,
        text="TOTAL",
        height=420,
        labels={"TOTAL": "N° de Solicitudes", "TIPO_TRAMITE": ""}
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Número de Solicitudes",
        showlegend=False
    )

    fig.update_traces(
        textposition="outside",
        marker_line_color="rgba(0,0,0,0.25)",
        marker_line_width=1.2
    )

    st.plotly_chart(fig, use_container_width=True)


def create_cul_chart(df):
    """Gráfico de estado CUL."""
    st.subheader("📝 Estado de Certificados (CUL)")

    resumen = (
        df["CUL"]
        .value_counts()
        .rename_axis("CUL")
        .reset_index(name="TOTAL")
    )

    fig = px.pie(
        resumen,
        names="CUL",
        values="TOTAL",
        color="CUL",
        color_discrete_map=CUL_COLORS,
        hole=0.45,
        height=420
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        marker=dict(line=dict(color="#FFFFFF", width=1))
    )

    st.plotly_chart(fig, use_container_width=True)


def create_monthly_chart(df):
    """Tendencia mensual total."""
    st.subheader("📈 Tendencia Mensual de Solicitudes")

    monthly = (
        df.groupby(["PERIODO", "PERIODO_LABEL", "AÑO", "MES_NUM"])
        .size()
        .reset_index(name="SOLICITUDES")
        .sort_values(["PERIODO", "MES_NUM"])
    )

    # Orden cronológico correcto
    period_order = monthly["PERIODO_LABEL"].tolist()

    fig = px.line(
        monthly,
        x="PERIODO_LABEL",
        y="SOLICITUDES",
        markers=True,
        line_shape="spline",
        color_discrete_sequence=["#3498db"],
        height=420,
        labels={"PERIODO_LABEL": "Mes", "SOLICITUDES": "Total Solicitudes"}
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Mes",
        yaxis_title="Total Solicitudes",
        xaxis={"type": "category", "categoryorder": "array", "categoryarray": period_order}
    )

    fig.update_traces(
        marker=dict(size=8),
        line=dict(width=3)
    )

    st.plotly_chart(fig, use_container_width=True)


def create_monthly_tramite_chart(df):
    """Gráfico mensual por tipo de trámite."""
    st.subheader("📚 Comportamiento Mensual por Tipo de Trámite")

    monthly = (
        df.groupby(["PERIODO", "PERIODO_LABEL", "TIPO_TRAMITE"])
        .size()
        .reset_index(name="TOTAL")
        .sort_values("PERIODO")
    )

    period_order = (
        monthly[["PERIODO", "PERIODO_LABEL"]]
        .drop_duplicates()
        .sort_values("PERIODO")["PERIODO_LABEL"]
        .tolist()
    )

    fig = px.bar(
        monthly,
        x="PERIODO_LABEL",
        y="TOTAL",
        color="TIPO_TRAMITE",
        barmode="group",
        color_discrete_map=TRAMITE_COLORS,
        height=430,
        labels={
            "PERIODO_LABEL": "Mes",
            "TOTAL": "Cantidad",
            "TIPO_TRAMITE": "Tipo de trámite"
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Mes",
        yaxis_title="Cantidad de solicitudes",
        xaxis={"type": "category", "categoryorder": "array", "categoryarray": period_order},
        legend_title="Tipo de trámite"
    )

    st.plotly_chart(fig, use_container_width=True)


def tabla_resumen_tramite(df):
    """Tabla resumen por tipo de trámite."""
    st.subheader("📋 Tabla Resumen por Tipo de Trámite")

    resumen = (
        df["TIPO_TRAMITE"]
        .value_counts()
        .rename_axis("Tipo de trámite")
        .reset_index(name="Cantidad")
    )

    resumen["Porcentaje (%)"] = (resumen["Cantidad"] / resumen["Cantidad"].sum() * 100).round(1)

    st.dataframe(
        resumen,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Tipo de trámite": st.column_config.TextColumn("Tipo de trámite", width="large"),
            "Cantidad": st.column_config.NumberColumn("Cantidad", format="%d"),
            "Porcentaje (%)": st.column_config.NumberColumn("Porcentaje (%)", format="%.1f"),
        }
    )


def tabla_resumen_mensual(df):
    """Tabla mensual por tipo de trámite."""
    st.subheader("🗓️ Tabla Resumen Mensual")

    resumen = (
        df.groupby(["PERIODO", "PERIODO_LABEL", "TIPO_TRAMITE"])
        .size()
        .reset_index(name="TOTAL")
    )

    tabla = (
        resumen.pivot_table(
            index=["PERIODO", "PERIODO_LABEL"],
            columns="TIPO_TRAMITE",
            values="TOTAL",
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
        .sort_values("PERIODO")
    )

    for col in ["Bolsa de Trabajo", "CUL", "Bolsa de Trabajo + CUL", "Otros"]:
        if col not in tabla.columns:
            tabla[col] = 0

    tabla["Total"] = tabla[["Bolsa de Trabajo", "CUL", "Bolsa de Trabajo + CUL", "Otros"]].sum(axis=1)

    tabla = tabla.rename(columns={"PERIODO_LABEL": "Mes"})
    tabla = tabla[
        ["Mes", "Bolsa de Trabajo", "CUL", "Bolsa de Trabajo + CUL", "Otros", "Total"]
    ]

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Mes": st.column_config.TextColumn("Mes", width="medium"),
            "Bolsa de Trabajo": st.column_config.NumberColumn("Bolsa de Trabajo", format="%d"),
            "CUL": st.column_config.NumberColumn("CUL", format="%d"),
            "Bolsa de Trabajo + CUL": st.column_config.NumberColumn("Bolsa + CUL", format="%d"),
            "Otros": st.column_config.NumberColumn("Otros", format="%d"),
            "Total": st.column_config.NumberColumn("Total", format="%d"),
        }
    )


def tabla_profesiones(df):
    """Tabla de oficios/profesiones más frecuentes."""
    st.subheader("🛠️ Profesiones u Oficios Más Frecuentes")

    prof = df.copy()
    prof["PROFESION U OFICIO"] = prof["PROFESION U OFICIO"].fillna("-").astype(str).str.strip()
    prof = prof[~prof["PROFESION U OFICIO"].isin(["", "-", "NAN", "nan"])]

    if prof.empty:
        st.info("No hay profesiones u oficios válidos para mostrar.")
        return

    resumen = (
        prof["PROFESION U OFICIO"]
        .value_counts()
        .head(15)
        .rename_axis("Profesión u oficio")
        .reset_index(name="Cantidad")
    )

    st.dataframe(
        resumen,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Profesión u oficio": st.column_config.TextColumn("Profesión u oficio", width="large"),
            "Cantidad": st.column_config.NumberColumn("Cantidad", format="%d"),
        }
    )


def observaciones(df):
    """Observaciones automáticas."""
    st.subheader("📝 Observaciones")

    tramite_counts = df["TIPO_TRAMITE"].value_counts()
    tramite_top = tramite_counts.idxmax()
    tramite_top_total = int(tramite_counts.max())

    monthly = (
        df.groupby(["PERIODO", "PERIODO_LABEL"])
        .size()
        .reset_index(name="TOTAL")
        .sort_values(["TOTAL", "PERIODO"], ascending=[False, True])
    )
    mes_pico = monthly.iloc[0]

    total_cul = int((df["TIPO_TRAMITE"] == "CUL").sum())
    total_combo = int((df["TIPO_TRAMITE"] == "Bolsa de Trabajo + CUL").sum())
    total_emitidos = int((df["CUL"] == "EMITIDO").sum())

    st.info(
        f"""
- El trámite con mayor demanda en el periodo analizado es **{tramite_top}**, con **{tramite_top_total}** registros.
- El mes con mayor número de atenciones fue **{mes_pico['PERIODO_LABEL']}**, con **{int(mes_pico['TOTAL'])}** solicitudes.
- Se registran **{total_cul}** trámites clasificados directamente como **CUL**.
- Adicionalmente, existen **{total_combo}** registros combinados de **Bolsa de Trabajo + CUL**.
- En la columna de estado CUL se contabilizan **{total_emitidos}** registros en estado **EMITIDO**.
- El análisis considera que **CUL corresponde a Certificado Único Laboral**.
"""
    )


def show_pachambear_module():
    """Módulo completo PACHAMBEAR."""
    st.header("📊 Módulo PACHAMBEAR - Reporte Laboral")
    st.markdown("---")

    with st.spinner("🔍 Cargando datos..."):
        df = load_pachambear_data()

    if df is None or df.empty:
        st.error("No se pudieron cargar los datos.")
        return

    estadisticas_generales(df)
    st.markdown("---")

    create_tramite_chart(df)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        create_cul_chart(df)
    with col2:
        create_monthly_chart(df)

    st.markdown("---")

    create_monthly_tramite_chart(df)
    st.markdown("---")

    tabla_resumen_tramite(df)
    st.markdown("---")

    tabla_resumen_mensual(df)
    st.markdown("---")

    tabla_profesiones(df)
    st.markdown("---")

    observaciones(df)

    with st.expander("📁 Ver datos completos", expanded=False):
        st.dataframe(df, use_container_width=True, hide_index=True)