#################################Import packages and initial app setup#################################

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
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error
import datetime

server = flask.Flask(__name__)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, server=server, url_base_pasthname = '/Housing Market Predictor', external_stylesheets=external_stylesheets)

##########Read in data and rename columns/variables so that they are interpretable to users###########

df = pd.read_csv('housingdata.csv') #data to be plotted
coefs = pd.read_csv('coefs.csv') #the coefficients for the predictors
pred_error = round(coefs.Error, 0) #prediction error (RMSE)

#list of columns that need renamed
colstorename = ['ADDRESS', 'SQFT', 'BTH_STYLE', 'KITCH_STYLE',
              'PROPERTY_TYPE', 'YRS_SINCE_REMOD', 'HOA_FEES']

#change bath styles to be readable
df['BATH_STYLES'] = df.BTH_STYLE
df.BATH_STYLES = np.where(df.BATH_STYLES == 'M', 'Modern', df.BATH_STYLES)
df.BATH_STYLES = np.where(df.BATH_STYLES == 'S', 'Semi-Modern', df.BATH_STYLES)
df.BATH_STYLES = np.where(df.BATH_STYLES == 'L', 'Luxury', df.BATH_STYLES)
df.BATH_STYLES = np.where(df.BATH_STYLES == 'N', 'No Remodeling', df.BATH_STYLES)

#change kitchen styles to be readable
df['KITCH_STYLES'] = df.KITCH_STYLE
df.KITCH_STYLES = np.where(df.KITCH_STYLES == 'M', 'Modern', df.KITCH_STYLES)
df.KITCH_STYLES = np.where(df.KITCH_STYLES == 'S', 'Semi-Modern', df.KITCH_STYLES)
df.KITCH_STYLES = np.where(df.KITCH_STYLES == 'L', 'Luxury', df.KITCH_STYLES)
df.KITCH_STYLES = np.where(df.KITCH_STYLES == 'N', 'No Remodeling', df.KITCH_STYLES)

#renaming columns
df.rename(columns = {'ADDRESS':'Address',
                     'BATH_STYLES':'Bathroom Style',
                     'KITCH_STYLES':'Kitchen Style',
                     'PROPERTY_TYPE':'Property Type',
                     'YRS_SINCE_REMOD':'Years since last remodel',
                     'HOA_FEES':'HOA Fees'}, inplace = True)

#columns that will be shown to people when they hover over data points
colstoshow = ['Address', 'SQFT', 'Bathroom Style', 'Kitchen Style',
              'Property Type', 'Years since last remodel', 'HOA Fees']

#gathering names of neighborhoods and alphabetically sorting them
Neighborhoods = df.NEIGHBORHOOD.dropna().unique()
Neighborhoods.sort()

#gathering types of properties and alphabetically sorting them
PropType = df['Property Type'].dropna().unique()
PropType.sort()

#gathering number of bedrooms and sorting them
Beds = df.BEDS.dropna().unique()
Beds.sort()

#gathering number of bathrooms and sorting them
Baths = df.BATHS.dropna().unique()
Baths.sort()

#gathering bathroom styles and sorting them
BathStyles = df['Bathroom Style'].dropna().unique()
BathStyles.sort()

#gathering kitchen styles and sorting them
KitchStyles = df['Kitchen Style'].dropna().unique()
KitchStyles.sort()

#change title so that tab doesn't say "Dash" but the name of the app
app.title = 'Going Going Sold!'


################################App Layout##############################################

app.layout = html.Div([
    dcc.Markdown('''
###### Going...Going...Sold! 
    '''),
    html.Br(),


#use a button to toggle between making predictions based on user inputs and plotting homes
    html.Div([
        html.P("I want to..."),
        dcc.RadioItems(
            id='toggle',
            options=[{'label':i, 'value': i} for i in ['use the prediction engine', 'compare my home to other homes']],
            value = 'use the prediction engine'
            ),
        html.Br(),

###Mode 1: user imputs info about a home and it predicts how long it will take to sell
        
        html.Div(id = 'mode-1', children = [
            #Dropdown to pick a neighborhood
            html.Div([
                html.P('Neighborhood'),
                dcc.Dropdown(
                    id='Neighborhood_pred',
                    options=[{'label': i, 'value': i} for i in Neighborhoods],
                    value='Allston'
                    )],
                     style={'width': '25%'}),
            html.Br(),
            #Numeric textbox for List price
            html.Div([
                html.P('List Price'),
                dcc.Input(id='List_Price', type = 'number', inputMode='numeric', value = 750000)],
                     style={'width': '25%'}),
            html.Br(),
            #Numeric textbox for HOA Fees
            html.Div([
                html.P('HOA Fees'),
                dcc.Input(id='HOA_FEES', type = 'number', inputMode='numeric', value = 0)],
                     style={'width': '25%'}),
            html.Br(),
            #Numeric textbox for Years Since Last Remodel
            html.Div([
                html.P('Years Since Last Remodel'),
                dcc.Input(id='YRS_SNC_REMOD', type = 'number', inputMode='numeric', value = 0)],
                     style={'width': '25%'}),
            html.Br(),
            #Numeric textbox for Age of Home
            html.Div([
                html.P('Age of Home in Years'),
                dcc.Input(id='HOME_AGE', type = 'number', inputMode='numeric', value = 0)],
                     style={'width': '25%'}),
            html.Br(),
            #Dropdown to pick property type
            html.Div([
                html.P('Property Type'),
                dcc.Dropdown(
                    id='PropType_Pred',
                    options=[{'label': i, 'value': i} for i in PropType],
                    value='Condo/Co-op'
                    )],
                     style={'width': '25%'}),
            html.Br(),
            #Dropdown to pick bathroom style
            html.Div([
                html.P('Bathroom Style'),
                dcc.Dropdown(
                    id='BathStyle_Pred',
                    options=[{'label': i, 'value': i} for i in BathStyles],
                    value='No Remodeling'
                    )],
                     style={'width': '25%'}),
            html.Br(),
            #Dropdown to pick kitchen style
            html.Div([
                html.P('Kitchen Style'),
                dcc.Dropdown(
                    id='KitchStyle_Pred',
                    options=[{'label': i, 'value': i} for i in KitchStyles],
                    value='No Remodeling'
                    )],
                     style={'width': '25%'}),
            html.Br(),
            #submit button all input values are only used when clicked
            html.Div([
                html.Button(id='submit-button', n_clicks=0, children='Submit'),
                html.Br(),
                html.Br(),
                html.Div(id='output1', style = {'fontSize':18, 'width': '49%'}, children = '')])
            ]), 

###Mode 2: User inputs features of a homes and shows homes fitting that criteria and how long it took to sell based on list price

        html.Div(id = 'mode-2', children=[
            #dropdown to select neighborhoods uses a different id from the one above so that the two are not tied
            html.Div([
                html.P('Neighborhood'),
                dcc.Dropdown(
                    id='Neighborhood_id',
                    options=[{'label': i, 'value': i} for i in Neighborhoods],
                    value='Allston'
                    )],
                     style={'width': '25%'}),
            html.Br(),
            #dropdown to select number of beds
            html.Div([
                html.P('Number of Beds'),
                dcc.Dropdown(
                id='Number_Beds',
                options=[{'label': i, 'value': i} for i in Beds],
                value=1)],
                     style={'width': '25%'}),
            html.Br(),
            #dropwdown to select number of bathrooms
            html.Div([
                html.P('Number of Bathrooms'),
                dcc.Dropdown(
                    id='Number_Baths',
                    options=[{'label': i, 'value': i} for i in Baths],
                value=1)],
                     style={'width': '25%'}),
            html.Br(),
            #Range slider to select a SQFT in a range. Kept at a minimum range of 500 to help make sure data are available to be plotted
            html.Div([
                html.P('Square Footage'),
                dcc.RangeSlider(id='SQFT', marks = {i:'{}'.format(i) for i in range(0, 6500, 500)},
                           min = 0, max = 6000, value = [0, 6000], pushable =500, step = 50)],
                     style={'width': '49%'}),
            html.Br(),
            #Graph that updates based on user inputs (as soon as the inputs change)
            #the custom data is the address of the places that will be used to generate the table below the graph
            html.Div([
                html.Div([
                dcc.Graph(
                    id='housegraph', hoverData={'points': [{'customdata': '15 N Beacon St #1003'}]}
                    ),
                #table that updates based on hovering over points
                html.Div(id='table-holder')],
                style={'width':'49%'})
                ])
            ])           
        ])
    ])


############################App callbacks###################################

####First callbacks changes between the modes####

#hide/show prediction inputs
@app.callback(
    Output('mode-1', 'style'),
    [Input('toggle', 'value')])
def toggle_container(toggle_value):
    if toggle_value == 'use the prediction engine':
        return {'display': 'block'}
    else:
        return {'display': 'none'}
    
#hide/show graphing inputs and graph
@app.callback(
    Output('mode-2', 'style'),
    [Input('toggle', 'value')])
def toggle_container(toggle_value):
    if toggle_value == 'use the prediction engine':
        return {'display': 'none'}
    else:
        return {'display': 'block'}

                    
#######Second app callback to provide prediction#######
@app.callback(
    Output('output1', 'children'),
    [Input('submit-button','n_clicks')],
    [State('Neighborhood_pred', 'value'),
     State('List_Price', 'value'),
     State('HOA_FEES', 'value'),
     State('YRS_SNC_REMOD', 'value'),
     State('HOME_AGE', 'value'),
     State('PropType_Pred', 'value'),
     State('BathStyle_Pred', 'value'),
     State('KitchStyle_Pred', 'value')])
def update_output1(n_clicks, Neighborhood, ListPrice, HOAS, YRS_REMOD, AGE_HOME, PropType, BathStyle, KitchStyle): #Order matters. Match to the callback above

    #Use neighborhood so difference from ave list price in the selected neighborhood can be determined.
    #If no neighborhood is selected will use overall average
    overallpricemean = df.LIST_PRICE.mean()
    AveNeighPrice = np.where(df.NEIGHBORHOOD == Neighborhood, df.AVE_PRICE_IN_NEIGHBORHOOD[0], overallpricemean)[0]
    AvePricediff = ListPrice - AveNeighPrice

    #setting property type parameters, only multi-family and condo are used to make predictions
    if PropType == 'Condo/Co-op':
        PropCondo = 1
        PropMultiFam = 0
    elif PropType == 'Multi-Family (2-4) Unit':
        PropCondo = 0
        PropMultiFam = 0
    else:
        PropCondo = 0
        PropMultiFam = 0

    #Setting Bath Style and Kitchen Style Parameters.
    #Since only modern style was a predictor it only matters if modern is selected for either
    #although this makes it likely that a person will change something and nothing happens, this was done because the other styles had no predictive power
    if BathStyle == 'Modern':
        Bath_Style_M = 1
    else:
        Bath_Style_M = 0
    if KitchStyle == 'Modern':
        Kitch_Style_M = 1
    else:
        Kitch_Style_M = 0

    ##Grab current time to then create appropriate value for trend
    curryear = datetime.datetime.today().year

    if (curryear > 2019):
        trendyear = curryear - 2019
    else:
        trendyear = 0
    currmonth = datetime.datetime.today().month
    
    if (curryear > 2019):
        trendmonth = trendyear*12 + currmonth
    else:
        trendmonth = currmonth

    #create trend_value
    trend_val = 47.377732 - 0.0941*(trendmonth)

    #create blank prediction
    prediction = ''

    #use values to create prediction using the coefficients and the user inputs
    prediction = int((coefs.DIFF_FROM_NEIGH_AVE_LIST_PRICE*AvePricediff + coefs.HOA_FEES*HOAS+ coefs.YRS_SINCE_REMOD*YRS_REMOD+
                   coefs.AGE_OF_HOME*AGE_HOME+ coefs['PROPERTY_TYPE_Condo/Co-op']*PropCondo + coefs['PROPERTY_TYPE_Multi-Family (2-4 Unit)']*PropMultiFam +
                   coefs.BTH_STYLE_M*Bath_Style_M+ coefs.KITCH_STYLE_M*Kitch_Style_M+ coefs.trend*trend_val+ coefs.Intercept))

    #provide an interval for the predictions
    lowpred = int(prediction - pred_error)
    highpred = int(prediction + pred_error)

    ##if predictions fall below 0 change value to 0
    if (lowpred < 0):
        lowpred = 0
    if (highpred < 0):
        highpred = 0

    return 'If that home is listed now, it would be under agreement/pending sale between {:d} and {:d} days. (Note: Predictions may not change upon submit because some home features cause minor changes in predictions)'.format(lowpred, highpred)



####App callback for mode 2, i.e., viewing/comparing homes####

@app.callback(
    Output('housegraph', 'figure'),
    [Input('Neighborhood_id', 'value'),
     Input('Number_Beds', 'value'),
     Input('Number_Baths', 'value'),
     Input('SQFT', 'value')])
def update_graph(neighborhoodfilt, bedfilt, bathfilt, sqftfilt):
    #create copy of dataframe
    dff = df
    #update graph based on user inputs so long as they are specified
    if len(neighborhoodfilt) >  0:
        dff = dff[dff['NEIGHBORHOOD'] == neighborhoodfilt]
    if pd.notnull(bedfilt):
        dff = dff[dff['BEDS'] == bedfilt]
    if pd.notnull(bathfilt):
        dff = dff[dff['BATHS'] == bathfilt]
    #because square footage is on a range slider square footage will always have values provided   
    dff = dff[(dff['SQFT'] > sqftfilt[0]) & (dff['SQFT'] < sqftfilt[1])]

    #if there are no data to plot because of the user inputs print an error message on the graph
    if len(dff) == 0:
        return {
        'data': [go.Scatter(
            x=[2],
            y=[2],
            mode='markers+text',
            text=['Sorry, no homes meet those criteria'],
            customdata=['15 N Beacon St #1003'],
            marker={
                'size': 15,
                'opacity': 0,
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

    #plot the data and have the address be the custom data so that it's displayed when the point is hovered over
    return {
        'data': [go.Scatter(
            x=dff['LIST_PRICE'],
            y=dff['DAYS_ON_MKT'],
            mode='markers',
            text=dff['Address'],
            customdata=dff['Address'],
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

#####app callback to generate a table underneath the graph with more information about the homes#####
@app.callback(
    Output('table-holder', 'children'),
    [Input('housegraph', 'hoverData')])
def update_table(hoverData):
    dft = df[df['Address'] == hoverData['points'][0]['customdata']]
    return dash_table.DataTable(id = 'home-info',
                                columns=[{"name": i, "id": i} for i in colstoshow],
                                data = dft.to_dict('records'),
                                style_cell={'fontSize':14, 'font-family':'sans-serif'})
        

###other app setup code, i.e., the flask wrapper for the dash app###
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
