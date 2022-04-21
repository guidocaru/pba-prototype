from dash import dcc, html, Input, Output, callback
import app

layout = html.Div([
    html.P("Seleccione una candidatura:"),
    dcc.RadioItems(
        id='candidatura',
        options=[{'label': i, 'value': i} for i in app.candidaturas],
        value="FRENTE DE TODOS",
        inline=True
    ),
    dcc.Graph(id="graph"),
    html.Div(id='page-1-display-value'),
    dcc.Link('Go to Page 2', href='/page2')
])


@callback(
    Output('page-1-display-value', 'children'),
    Input('page-1-dropdown', 'value'))
def display_value(value):
    return f'You have selected {value}'
