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
resultado = resultado[resultado['paso'] == 0]

resultado = resultado.groupby(['fecha', 'municipio', 'candidatura', 'id_concat']).agg(
    {'votos': 'sum'}).reset_index()

resultado['votos_perc'] = (resultado['votos'] / resultado.groupby(
    ['fecha', 'municipio', 'id_concat'])['votos'].transform('sum')) * 100

candidaturas = resultado["candidatura"].unique()


app = Dash(__name__)

app.layout = html.Div([
    html.H3('Prototipo elecciones Provincia de Buenos Aires'),
    html.P("Seleccione una candidatura:"),
    dcc.RadioItems(
        id='candidatura',
        options=[{'label': i, 'value': i} for i in candidaturas],
        value="FRENTE DE TODOS",
        inline=True
    ),
    dcc.Graph(id="graph"),
])


@app.callback(
    Output("graph", "figure"),
    Input("candidatura", "value"))
def display_choropleth(candidatura):

    dff = resultado[resultado['candidatura'] == candidatura]

    fig = px.choropleth_mapbox(
        dff, geojson=municipios_geo, color="votos_perc",
        locations="id_concat", featureidkey="properties.id_concat",
        center={"lat": -36.441723, "lon": -59.996306}, zoom=5,
        range_color=[0, 100],
        width=1300, height=1000)
    fig.update_layout(

        mapbox_accesstoken=token)

    return fig


app.run_server(debug=True)
