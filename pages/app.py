import page2
import page1
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import json
from google.cloud import bigquery
import os
from dotenv import load_dotenv
import requests
load_dotenv()

# mapbox
token = os.getenv("MAPBOX_TOKEN")

# bigquery
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "credentials.json"
client = bigquery.Client()
project_id = os.getenv("PROJECT_ID")
dataset = os.getenv("DATASET")
table = os.getenv("TABLE")

# get data
query = """
    select * from `{}.{}.{}` where cargo = "Diputados nacionales"
""".format(project_id, dataset, table)

resultado = client.query(query).to_dataframe()

res = requests.get(
    "https://guidocaru.github.io/municipios_geo/municipios_pba_geo.json")
municipios_geo = json.loads(res.text)

# acorta el df de resultados para test
#resultado = resultado[resultado['paso'] == 0]

resultado = resultado.groupby(['fecha', 'municipio', 'candidatura', 'id_concat', 'paso']).agg(
    {'votos': 'sum'}).reset_index()

resultado['votos_perc'] = (resultado['votos'] / resultado.groupby(
    ['fecha', 'municipio', 'id_concat'])['votos'].transform('sum')) * 100

candidaturas = resultado["candidatura"].unique()
tipo_eleccion = resultado["paso"].unique()


app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    html.Div(
        className="app-header",
        children=[
            html.Div('Análisis Elecciones - Provincia de Buenos Aires',
                     className="app-header--title")
        ]
    ),
    html.P("Seleccione una candidatura:"),

    dcc.Dropdown(id='candidatura',
                 options=[{'label': i, 'value': i} for i in candidaturas],
                 value="+ VALORES",),

    dcc.Dropdown(id='tipo_eleccion',
                 options=[{'label': i, 'value': i} for i in tipo_eleccion],
                 value=0,),

    dcc.Graph(id="graph"),

    dcc.Link('Go to Page 1', href='/page1'),
    html.Br(),
    dcc.Link('Go to Page 2', href='/page2'),
])


@app.callback(
    Output("graph", "figure"),
    Input("candidatura", "value"),
    Input("tipo_eleccion", "value"))
def display_choropleth(candidatura, tipo_eleccion):
    int(tipo_eleccion)

    scale = "blues" if candidatura == "FRENTE DE TODOS" else "orrd" if candidatura == "JUNTOS" else "rdpu" if candidatura == "AVANZA LIBERTAD" else "reds" if candidatura == "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD" else "greens" if candidatura == "FRENTE VAMOS CON VOS" else "inferno"

    dff = resultado[resultado['candidatura'] == candidatura]
    dff = dff[dff['paso'] == tipo_eleccion]

    fig = px.choropleth_mapbox(
        dff, geojson=municipios_geo, color="votos_perc", color_continuous_scale=scale,
        locations="id_concat", featureidkey="properties.id_concat",
        center={"lat": -36.441723, "lon": -59.996306}, zoom=6,
        range_color=[dff["votos_perc"].min(), dff["votos_perc"].max()],
        width=1300, height=1000,
    )

    fig.update_layout(

        mapbox_accesstoken=token)

    return fig


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/page1':
        return page1.layout
    elif pathname == '/page2':
        return page2.layout
    else:
        return index_page


if __name__ == '__main__':
    app.run_server(debug=True)
