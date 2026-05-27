import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================
# ✅ DATA
# ==============================
df = pd.read_csv("data/datos_procesados.csv")

estados_desercion = ["Retirado", "Desertor", "Inactivo"]

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# ==============================
# ✅ LAYOUT PRINCIPAL
# ==============================
app.layout = html.Div([

    html.H1("📊 Dashboard de Análisis de Estudiantes", style={"textAlign": "center"}),

    dcc.Location(id="url"),

    # ✅ FILTROS
    html.Div([
        dcc.Dropdown(
            id="filtro_facultad",
            options=[{"label": i, "value": i} for i in df["Facultad"].unique()],
            multi=True,
            placeholder="Filtrar por Facultad"
        ),

        dcc.Dropdown(
            id="filtro_estado",
            options=[{"label": i, "value": i} for i in df["Estado"].unique()],
            multi=True,
            placeholder="Filtrar por Estado Académico"
        ),
    ], style={"width": "60%", "margin": "auto"}),

    html.Br(),

    # ✅ MENÚ
    html.Div([
        dcc.Link("📊 Análisis Exploratorio", href="/"),
        html.Span(" | "),
        dcc.Link("📈 Patrones y Tendencias", href="/tendencias"),
        html.Span(" | "),
        dcc.Link("📉 KPIs Estratégicos", href="/kpis"),
    ], style={"textAlign": "center", "fontSize": "20px"}),

    html.Hr(),

    html.Div(id="page-content")

])

# ==============================
# ✅ PAGINA 1 - EDA
# ==============================
def pagina_eda(dff):

    estado_counts = dff['Estado'].value_counts().reset_index()
    estado_counts.columns = ['Estado', 'Cantidad']

    facultad_counts = dff['Facultad'].value_counts().reset_index()
    facultad_counts.columns = ['Facultad', 'Cantidad']

    return html.Div([

        html.H2("📊 Análisis Exploratorio de Datos"),

        dcc.Graph(figure=px.histogram(
            dff, x='Promedio',
            title='Distribución del Promedio Académico'
        )),

        dcc.Graph(figure=px.histogram(
            dff, x='Edad',
            title='Distribución de Edad de los Estudiantes'
        )),

        dcc.Graph(figure=px.box(
            dff, y='Créditos_Matriculados',
            title='Distribución de Créditos Matriculados'
        )),

        dcc.Graph(figure=px.bar(
            estado_counts,
            x='Estado',
            y='Cantidad',
            title='Distribución del Estado Académico'
        )),

        dcc.Graph(figure=px.bar(
            facultad_counts,
            x='Facultad',
            y='Cantidad',
            title='Cantidad de Estudiantes por Facultad'
        )),

        dcc.Graph(figure=px.box(
            dff, x='Estado', y='Promedio',
            title='Promedio Académico según Estado'
        )),

        dcc.Graph(figure=px.box(
            dff, x='Estado', y='Edad',
            title='Edad de los Estudiantes según Estado Académico'
        )),

        dcc.Graph(figure=px.box(
            dff, x='Becado', y='Promedio',
            title='Promedio Académico según Condición de Beca'
        )),

        dcc.Graph(figure=px.scatter(
            dff,
            x='Créditos_Matriculados',
            y='Promedio',
            color='Estado',
            size='Edad',
            title='Relación entre Créditos Matriculados, Promedio y Estado Académico'
        )),

        dcc.Graph(figure=px.box(
            dff,
            x='Facultad',
            y='Promedio',
            title='Comparación del Promedio Académico por Facultad'
        )),

        dcc.Graph(figure=px.imshow(
            dff.corr(numeric_only=True),
            text_auto=True,
            title='Matriz de Correlación entre Variables Numéricas'
        ))

    ])

# ==============================
# ✅ PAGINA 2 - TENDENCIAS
# ==============================
def pagina_tendencias(dff):

    riesgo_programa = dff[dff['Estado'] != 'Activo']['Programa'].value_counts().reset_index()
    riesgo_programa.columns = ['Programa', 'Casos']

    abandono = dff[dff['Estado'] != 'Activo'].groupby('Año_Ingreso').size().reset_index(name='Cantidad')

    return html.Div([

        html.H2("📈 Análisis de Patrones y Tendencias"),

        dcc.Graph(figure=px.bar(
            riesgo_programa.head(10),
            x='Programa',
            y='Casos',
            title='Top 10 Programas con Mayor Riesgo de Abandono'
        )),

        dcc.Graph(figure=px.line(
            abandono,
            x='Año_Ingreso',
            y='Cantidad',
            markers=True,
            title='Tendencia de Abandono según Año de Ingreso'
        )),

        dcc.Graph(figure=px.histogram(
            dff,
            x='Año_Ingreso',
            color='Estado',
            barmode='group',
            title='Estado Académico por Año de Ingreso'
        )),

        dcc.Graph(figure=px.box(
            dff,
            x='Estado',
            y='Promedio',
            title='Relación entre Promedio Académico y Estado'
        )),

        dcc.Graph(figure=px.scatter(
            dff,
            x='Promedio',
            y='Créditos_Matriculados',
            color='Estado',
            size='Edad',
            title='Relación entre Rendimiento, Carga Académica y Estado Académico'
        ))

    ])

# ==============================
# ✅ PAGINA 3 - KPIs
# ==============================
def pagina_kpis(dff):

    total = len(dff)

    desercion = dff[dff['Estado'].isin(estados_desercion)].shape[0]
    tasa_desercion = (desercion / total) * 100 if total > 0 else 0

    tasa_retencion = 100 - tasa_desercion

    riesgo = (dff[dff['Promedio'] < 3].shape[0] / total) * 100 if total > 0 else 0

    promedio = dff['Promedio'].mean()

    alerta = dff[(dff['Promedio'] < 3) & (dff['Créditos_Matriculados'] > 20)]
    porcentaje_alerta = (len(alerta) / total) * 100 if total > 0 else 0

    def gauge(valor, titulo, maximo=100):
        return go.Figure(go.Indicator(
            mode="gauge+number",
            value=valor,
            title={'text': titulo},
            gauge={'axis': {'range': [0, maximo]}}
        ))

    return html.Div([

        html.H2("📉 Indicadores Clave de Desempeño (KPIs)"),

        dcc.Graph(figure=gauge(tasa_desercion, "Tasa de Deserción (%)")),
        dcc.Graph(figure=gauge(tasa_retencion, "Tasa de Retención (%)")),
        dcc.Graph(figure=gauge(riesgo, "Estudiantes en Riesgo Académico (%)")),
        dcc.Graph(figure=gauge(promedio, "Promedio Académico General", 5)),
        dcc.Graph(figure=gauge(porcentaje_alerta, "Índice de Alerta Temprana (%)"))

    ])

# ==============================
# ✅ CALLBACK GLOBAL
# ==============================
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    Input("filtro_facultad", "value"),
    Input("filtro_estado", "value")
)
def render_page(path, facultades, estados):

    dff = df.copy()

    if facultades:
        dff = dff[dff["Facultad"].isin(facultades)]

    if estados:
        dff = dff[dff["Estado"].isin(estados)]

    if path == "/tendencias":
        return pagina_tendencias(dff)

    if path == "/kpis":
        return pagina_kpis(dff)

    return pagina_eda(dff)

# ==============================
# ✅ RUN
# ==============================
if __name__ == "__main__":
    app.run(debug=True)