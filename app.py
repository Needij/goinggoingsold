import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import flask
import pandas as pd
import numpy as np
import sklearn
from sklearn import linear_model

server = flask.Flask(__name__)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, server=server, url_base_pasthname = '/Housing Market Predictor', external_stylesheets=external_stylesheets)

df = pd.read_csv('housingdata.csv')

Neighborhoods = df.NEIGHBORHOOD.dropna().unique()
Neighborhoods.sort()
Beds = df.BEDS.dropna().unique()
Beds.sort()
#Clean up bath styles for users
df['BATH_STYLES'] = df.BTH_STYLE
df.BATH_STYLES = np.where(df.BATH_STYLES == 'M', 'Modern', df.BATH_STYLES)
df.BATH_STYLES = np.where(df.BATH_STYLES == 'S', 'Semi-Modern', df.BATH_STYLES)
df.BATH_STYLES = np.where(df.BATH_STYLES == 'L', 'Luxury', df.BATH_STYLES)
df.BATH_STYLES = np.where(df.BATH_STYLES == 'N', 'No Remodeling', df.BATH_STYLES)

BStyles = df.BATH_STYLES.dropna().unique()
BStyles.sort()

X2 = df[['BEDS', 'BTH_STYLE_M', 'BTH_STYLE_L', 'BTH_STYLE_S','SQFT', 'LIST_PRICE']]
y2 = df[['DAYS_ON_MKT']]
lm = linear_model.LinearRegression(normalize = False)
model = lm.fit(X = X2, y = y2)

app.title = 'Going Going Sold!'
app.layout = html.Div([
    dcc.Markdown('''
###### Going...Going...Sold! 
    '''),
    html.Br(),

    html.Div([
        html.P("I want to..."),
        dcc.RadioItems(
            id='toggle',
            options=[{'label':i, 'value': i} for i in ['to see homes', 'use the prediction engine']],
            value = 'to see homes'
            ),

###Mode 1: User inputs features of a homes and shows homes fitting that criteria and how long it took to sell based on list price

        html.Div(id = 'mode-1', children=[
            html.Br(),
            html.Div([
                html.P('Neighborhood'),
                dcc.Dropdown(
                    id='Neighborhood_id',
                    options=[{'label': i, 'value': i} for i in Neighborhoods],
                    value='Allston'
                    )],
                     style={'width': '49%'}),
            html.Br(),
            html.Div([
                html.P('Number of Beds'),
                dcc.Dropdown(
                id='Number_Beds',
                options=[{'label': i, 'value': i} for i in Beds],
                value=1)],
                     style={'width': '49%'}),
            html.Br(),
            html.Div([
                html.P('Bath Style'),
                dcc.Dropdown(
                    id='Bath_Style',
                    options=[{'label': i, 'value': i} for i in BStyles],
                value='')],
                     style={'width': '49%'}),
            html.Br(),
            html.Div([
                html.P('Square Footage'),
                dcc.RangeSlider(id='SQFT', marks = {i:'{}'.format(i) for i in range(0, 6500, 500)},
                           min = 0, max = 6000, value = [0, 6000], pushable =500, step = 50)],
                     style={'width': '49%'}),
            html.Br(),
            html.Div([
                html.Div([
                dcc.Graph(
                    id='housegraph', hoverData={'points': [{'customdata': '15 N Beacon St #1003'}]}
                    ),
                html.Div(id='table-holder')],
                style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'})
                         ]),
                ]),



###Mode 2: user imputs info about a home and it predicts how long it will take to sell
        
        html.Div(id = 'mode-2', children = [
            html.Div([
                html.P('List_Price'),
                dcc.Input(id='List_Price', type = 'number', inputMode='numeric', value = 0)],
                     style={'width': '49%'}),
            html.Div([
                html.Button(id='submit-button', n_clicks=0, children='Submit'),
                html.Div(id='output1', children = '')])
            ])            
        ])
    ])


@app.callback(
    Output('mode-1', 'style'),
    [Input('toggle', 'value')])
def toggle_container(toggle_value):
    if toggle_value == 'to see homes':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
    Output('mode-2', 'style'),
    [Input('toggle', 'value')])
def toggle_container(toggle_value):
    if toggle_value == 'to see homes':
        return {'display': 'none'}
    else:
        return {'display': 'block'}




@app.callback(
    Output('output1', 'children'),
    [Input('submit-button','n_clicks')],
    [State('Number_Beds', 'value'),
     State('Bath_Style', 'value'),
     State('SQFT', 'value'),
     State('List_Price', 'value')])
def update_output1(n_clicks, Number_Beds, Bath_Style, SQFT, List_Price): #Order matters!
    if Bath_Style == 'Modern':
        Bath_Style_S = 0
        Bath_Style_M = 1
        Bath_Style_L = 0
    elif Bath_Style == 'Semi-Modern':
        Bath_Style_S = 1
        Bath_Style_M = 0
        Bath_Style_L = 0
    elif Bath_Style == 'Luxury':
        Bath_Style_S = 0
        Bath_Style_M = 0
        Bath_Style_L = 1
    else:
        Bath_Style_S = 0
        Bath_Style_M = 0
        Bath_Style_L = 0

    prediction1 = ''
    prediction2 = ''
    SQFTave = np.mean([SQFT[0], SQFT[1]])
    Xs = np.array([[Number_Beds, Bath_Style_M, Bath_Style_L, Bath_Style_S, SQFTave, List_Price]])
    #Xs_red = np.array([[Number_Beds, Bath_Style_M, Bath_Style_L, Bath_Style_S, SQFT, (List_Price - 25000)]])
    prediction1 = model.predict(Xs)
    prediction1 = round(prediction1[0, 0], 2)
    #prediction2 = model.predict(Xs_red)
        
    return u'''
            Predicted days until pending sale = {}            
    '''.format(prediction1, prediction2)

@app.callback(
    Output('housegraph', 'figure'),
    [Input('Neighborhood_id', 'value'),
     Input('Number_Beds', 'value'),
     Input('Bath_Style', 'value'),
     Input('SQFT', 'value')])
def update_graph(neighborhoodfilt, bedfilt, bathstylefilt, sqftfilt):
    dff = df[df['NEIGHBORHOOD'] == neighborhoodfilt]
    dff = dff[dff['BEDS'] == bedfilt]
    if len(bathstylefilt) > 0:
        dff = dff[dff['BATH_STYLES'] == bathstylefilt]
    else:
        dff = dff
        
    dff = dff[(dff['SQFT'] > sqftfilt[0]) & (dff['SQFT'] < sqftfilt[1])]

    return {
        'data': [go.Scatter(
            x=dff['LIST_PRICE'],
            y=dff['DAYS_ON_MKT'],
            mode='markers',
            text=dff['ADDRESS'],
            customdata=dff['ADDRESS'],
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': go.Layout(
            xaxis={'title': 'List Price'},
            yaxis={'title': 'Days on the Market'},
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            height=450,
            hovermode='closest')
    }

@app.callback(
    Output('table-holder', 'children'),
    [Input('housegraph', 'hoverData')])
def update_table(hoverData):
    dft = df[df['ADDRESS'] == hoverData['points'][0]['customdata']]
    return dash_table.DataTable(id = 'home-info',
                                columns=[{"name": i, "id": i} for i in dft.columns],
                                data = dft.to_dict('records'))
        

@server.route('/')
def index():
    return '''
<html>
<div>
    <h1>Flask App</h1>
</div>
</html>
'''

if __name__ == '__main__':
    server.run(debug=True)