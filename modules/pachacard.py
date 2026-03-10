# modules/pachacard.py

import pandas as pd
import plotly.express as px
import streamlit as st

CARD_COLORS = {
    "Estándar": "#3498db",
    "Premium": "#f39c12",
}

STATUS_COLORS = {
    "Emitidas": "#2ecc71",
    "Otorgadas": "#3498db",
    "Pendientes": "#e74c3c",
}


def load_pachacard_data():
    """Carga la data fija del programa PACHACARD."""
    emitidas_total = 2500
    otorgadas_total = 1780

    categorias_data = [
        {"CATEGORIA": "Estándar", "TARJETAS": 430},
        {"CATEGORIA": "Premium", "TARJETAS": 1350},
    ]

    empresas_afiliadas = [
        "Lo de Juan",
        "D'Carlos",
        "Privilegio",
        "Las Ruedas de Pachacámac",
        "Tikay Cafetería",
        "La Esquina",
        "La Ley",
        "Otros establecimientos afiliados",
    ]

    df_categorias = pd.DataFrame(categorias_data)
    df_categorias["PORCENTAJE"] = (
        df_categorias["TARJETAS"] / df_categorias["TARJETAS"].sum() * 100
    ).round(1)

    resumen_data = [
        {"ESTADO": "Emitidas", "CANTIDAD": emitidas_total},
        {"ESTADO": "Otorgadas", "CANTIDAD": otorgadas_total},
        {"ESTADO": "Pendientes", "CANTIDAD": emitidas_total - otorgadas_total},
    ]
    df_resumen = pd.DataFrame(resumen_data)

    df_empresas = pd.DataFrame({"EMPRESA": empresas_afiliadas})

    return df_categorias, df_resumen, df_empresas


def estadisticas_generales(df_categorias, df_resumen, df_empresas):
    """KPIs generales."""
    st.subheader("📊 Estadísticas Generales")

    c1, c2, c3, c4 = st.columns(4)

    emitidas = int(df_resumen.loc[df_resumen["ESTADO"] == "Emitidas", "CANTIDAD"].iloc[0])
    otorgadas = int(df_resumen.loc[df_resumen["ESTADO"] == "Otorgadas", "CANTIDAD"].iloc[0])
    pendientes = int(df_resumen.loc[df_resumen["ESTADO"] == "Pendientes", "CANTIDAD"].iloc[0])
    cobertura = (otorgadas / emitidas) * 100 if emitidas else 0

    categoria_top = df_categorias.loc[df_categorias["TARJETAS"].idxmax(), "CATEGORIA"]
    n_empresas = len(df_empresas)

    c1.metric("💳 Tarjetas Emitidas", f"{emitidas:,}")
    c2.metric("✅ Tarjetas Otorgadas", f"{otorgadas:,}")
    c3.metric("📌 Pendientes", f"{pendientes:,}")
    c4.metric("🏪 Empresas Afiliadas", f"{n_empresas}+" if n_empresas >= 8 else n_empresas)

    st.caption(
        f"Cobertura de entrega: {cobertura:.1f}% | Categoría predominante: {categoria_top}"
    )


def grafico_emitidas_otorgadas(df_resumen):
    """Gráfico de barras del estado de tarjetas."""
    st.subheader("💳 Estado General de Tarjetas")

    df_plot = df_resumen.copy()

    fig = px.bar(
        df_plot,
        x="ESTADO",
        y="CANTIDAD",
        color="ESTADO",
        text="CANTIDAD",
        color_discrete_map=STATUS_COLORS,
        height=380,
        labels={
            "ESTADO": "Estado",
            "CANTIDAD": "Cantidad de Tarjetas"
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Estado",
        yaxis_title="Cantidad de Tarjetas",
        showlegend=False
    )

    fig.update_xaxes(type="category")

    fig.update_traces(
        textposition="outside",
        marker_line_color="rgba(0,0,0,0.25)",
        marker_line_width=1.5
    )

    st.plotly_chart(fig, use_container_width=True)


def grafico_distribucion_categorias(df_categorias):
    """Gráfico tipo dona de tarjetas otorgadas por categoría."""
    st.subheader("🥇 Distribución de Tarjetas Otorgadas por Categoría")

    fig = px.pie(
        df_categorias,
        names="CATEGORIA",
        values="TARJETAS",
        color="CATEGORIA",
        color_discrete_map=CARD_COLORS,
        hole=0.55
    )

    fig.update_traces(
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Tarjetas: %{value}<br>Porcentaje: %{percent}<extra></extra>"
    )

    fig.update_layout(
        height=420,
        legend_title="Categoría"
    )

    st.plotly_chart(fig, use_container_width=True)


def grafico_comparativo_categorias(df_categorias):
    """Gráfico de barras de tarjetas otorgadas por categoría."""
    st.subheader("📈 Tarjetas Otorgadas por Categoría")

    fig = px.bar(
        df_categorias,
        x="CATEGORIA",
        y="TARJETAS",
        color="CATEGORIA",
        text="TARJETAS",
        color_discrete_map=CARD_COLORS,
        height=380,
        labels={
            "CATEGORIA": "Categoría",
            "TARJETAS": "Cantidad de Tarjetas"
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Categoría",
        yaxis_title="Cantidad de Tarjetas",
        showlegend=False
    )

    fig.update_xaxes(type="category")

    fig.update_traces(
        textposition="outside",
        marker_line_color="rgba(0,0,0,0.25)",
        marker_line_width=1.5
    )

    st.plotly_chart(fig, use_container_width=True)


def tabla_resumen(df_categorias, df_resumen):
    """Tabla resumen del programa."""
    st.subheader("📋 Tabla Resumen")

    emitidas = int(df_resumen.loc[df_resumen["ESTADO"] == "Emitidas", "CANTIDAD"].iloc[0])
    otorgadas = int(df_resumen.loc[df_resumen["ESTADO"] == "Otorgadas", "CANTIDAD"].iloc[0])
    pendientes = int(df_resumen.loc[df_resumen["ESTADO"] == "Pendientes", "CANTIDAD"].iloc[0])

    tabla_general = pd.DataFrame([
        {"Indicador": "Tarjetas emitidas", "Valor": emitidas},
        {"Indicador": "Tarjetas otorgadas", "Valor": otorgadas},
        {"Indicador": "Tarjetas pendientes", "Valor": pendientes},
        {"Indicador": "Cobertura de entrega (%)", "Valor": round((otorgadas / emitidas) * 100, 1)},
    ])

    st.markdown("**Resumen general**")
    st.dataframe(
        tabla_general,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Indicador": st.column_config.TextColumn("Indicador", width="large"),
            "Valor": st.column_config.NumberColumn("Valor", format="%.1f"),
        }
    )

    st.markdown("**Distribución por categoría**")
    tabla_cat = df_categorias.copy().rename(columns={
        "CATEGORIA": "Categoría",
        "TARJETAS": "Tarjetas Otorgadas",
        "PORCENTAJE": "Porcentaje (%)"
    })

    st.dataframe(
        tabla_cat,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Categoría": st.column_config.TextColumn("Categoría", width="medium"),
            "Tarjetas Otorgadas": st.column_config.NumberColumn("Tarjetas Otorgadas", format="%d"),
            "Porcentaje (%)": st.column_config.NumberColumn("Porcentaje (%)", format="%.1f"),
        }
    )


def tabla_empresas(df_empresas):
    """Tabla de empresas afiliadas."""
    st.subheader("🏪 Empresas Afiliadas al Programa")

    st.dataframe(
        df_empresas.rename(columns={"EMPRESA": "Empresa afiliada"}),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Empresa afiliada": st.column_config.TextColumn("Empresa afiliada", width="large"),
        }
    )


def observaciones(df_categorias, df_resumen, df_empresas):
    """Observaciones automáticas."""
    st.subheader("📝 Observaciones")

    emitidas = int(df_resumen.loc[df_resumen["ESTADO"] == "Emitidas", "CANTIDAD"].iloc[0])
    otorgadas = int(df_resumen.loc[df_resumen["ESTADO"] == "Otorgadas", "CANTIDAD"].iloc[0])
    pendientes = int(df_resumen.loc[df_resumen["ESTADO"] == "Pendientes", "CANTIDAD"].iloc[0])

    cobertura = (otorgadas / emitidas) * 100 if emitidas else 0

    categoria_top = df_categorias.loc[df_categorias["TARJETAS"].idxmax()]
    categoria_min = df_categorias.loc[df_categorias["TARJETAS"].idxmin()]

    st.info(
        f"""
- El programa registra un total de **{emitidas:,} tarjetas emitidas**, de las cuales **{otorgadas:,}** ya han sido entregadas a contribuyentes.
- Actualmente quedan **{pendientes:,} tarjetas por otorgar**, lo que representa una cobertura de entrega de **{cobertura:.1f}%** respecto del total emitido.
- La categoría con mayor participación es **{categoria_top['CATEGORIA']}**, con **{int(categoria_top['TARJETAS'])}** tarjetas, equivalente al **{categoria_top['PORCENTAJE']:.1f}%** del total entregado.
- La categoría **{categoria_min['CATEGORIA']}** concentra **{int(categoria_min['TARJETAS'])}** tarjetas, equivalente al **{categoria_min['PORCENTAJE']:.1f}%**.
- El programa cuenta con **más de 15 empresas afiliadas**, entre ellas establecimientos gastronómicos y comerciales del distrito.
- La predominancia de la categoría Premium evidencia una alta aceptación del programa y refuerza su rol como herramienta de incentivo al cumplimiento tributario.
"""
    )


def conclusion():
    """Conclusión ejecutiva."""
    st.subheader("✅ Conclusión")

    st.success(
        """
El Programa **PACHACARD** se consolida como una herramienta municipal de reconocimiento al contribuyente puntual, al combinar incentivos concretos con beneficios comerciales dentro del distrito.

La diferencia entre tarjetas emitidas y otorgadas permite visualizar el avance operativo del programa, mientras que la alta participación de la categoría Premium y la red de empresas afiliadas reflejan su aceptación y sostenibilidad.
"""
    )


def show_pachacard_module():
    """Módulo completo de PACHACARD."""
    st.header("💳 Módulo del Programa PACHACARD")
    st.markdown("---")

    df_categorias, df_resumen, df_empresas = load_pachacard_data()

    if df_categorias is None or df_categorias.empty:
        st.error("No se pudieron cargar los datos.")
        return

    estadisticas_generales(df_categorias, df_resumen, df_empresas)
    st.markdown("---")

    grafico_emitidas_otorgadas(df_resumen)
    st.markdown("---")

    grafico_distribucion_categorias(df_categorias)
    st.markdown("---")

    grafico_comparativo_categorias(df_categorias)
    st.markdown("---")

    tabla_resumen(df_categorias, df_resumen)
    st.markdown("---")

    tabla_empresas(df_empresas)
    st.markdown("---")

    observaciones(df_categorias, df_resumen, df_empresas)
    st.markdown("---")

    conclusion()