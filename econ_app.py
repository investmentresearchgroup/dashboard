# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 21:25:13 2020

@author: FOHASK1
"""

import pandas as pd
import requests
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import os


url = 'http://dataservices.imf.org/REST/SDMX_JSON.svc/'

interest_key = ['CompactData/IFS/M.GH.PCPI_PC_PP_PT', 'CompactData/IFS/M.GH.FITB_PA', 'CompactData/IFS/M.GH.FIGB_PA', 'CompactData/IFS/M.GH.FIMM_PA', 
                'CompactData/IFS/M.GH.FISR_PA', 'CompactData/IFS/M.GH.FITB_PA', 'CompactData/IFS/M.GH.FPOLM_PA']

interest_key_name = ['Financial, Interest Rates, Government Securities, Government Bonds, Percent per annum', 
                     'Financial, Interest Rates, Government Securities, Treasury Bills, Percent per annum', 
                     'Financial, Interest Rates, Monetary Policy-Related Interest Rate, Percent per annum',
                     'Financial, Interest Rates, Money Market, Percent per annum',
                     'Financial, Interest Rates, Savings Rate, Percent per annum',
                     'Prices, Consumer Price Index, All items, Percentage change, Previous period, Percent']

inflation_key = ['CompactData/IFS/M.GH.PCPI_PC_CP_A_PT', 'CompactData/IFS/M.GH.PCPI_PC_PP_PT']#, 'CompactData/IFS/M.GH.PCPI_IX', 'CompactData/IFS/M.GH.PPPI_IX']

inflation_key_name = ['Prices, Consumer Price Index, All items, Percentage change, Corresponding period previous year, Percent',
                      'Prices, Consumer Price Index, All items, Percentage change, Previous period, Percent']
#                      'Prices, Consumer Price Index, All items, Index',
#                      'Prices, Producer Price Index, All Commodities, Index']

# Exchange rate
exchange_rate_key = ['CompactData/IFS/M.GH.EDNA_USD_XDC_RATE', 'CompactData/IFS/M.GH.EECUNE_XEU_XDC_RATE', 'CompactData/IFS/M.GH.EENA_EUR_XDC_RATE', 
                     'CompactData/IFS/M.GH.EENE_EUR_XDC_RATE', 'CompactData/IFS/M.GH.ENDA_XDC_USD_RATE', 'CompactData/IFS/M.GH.ENDE_XDC_USD_RATE', 
                     'CompactData/IFS/M.GH.ENEA_XDC_EUR_RATE', 'CompactData/IFS/M.GH.ENECUA_XDC_XEU_RATE', 'CompactData/IFS/M.GH.ENDE_XDC_USD_RATE']

exchange_rate_key_name = ['Exchange Rates, Domestic Currency per ECU, Period Average, Rate', 
                          'Exchange Rates, Domestic Currency per Euro, Period Average, Rate',
                          'Exchange Rates, Domestic Currency per U.S. Dollar, End of Period, Rate',
                          'Exchange Rates, Domestic Currency per U.S. Dollar, Period Average, Rate',
                          'Exchange Rates, ECUs per Domestic Currency, End of period, Rate',
                          'Exchange Rates, Euro per Domestic Currency, End of Period, Rate',
                          'Exchange Rates, Euro per Domestic Currency, Period Average, Rate',
                          'Exchange Rates, US Dollar per Domestic Currency, Period Average, Rate']


# Consumer Price Index
# key = 'CompactData/AFRREO201910/PCPI_EOP_PC_PP_PT'
# Navigate to series in API-returned JSON data
interest_data = [pd.DataFrame(requests.get(f'{url}{key}').json()['CompactData']['DataSet']['Series']['Obs']) for key in interest_key]

inflation_data = [pd.DataFrame(requests.get(f'{url}{key}').json()['CompactData']['DataSet']['Series']['Obs']).iloc[:, [0, 1]] for key in inflation_key]

exchange_rate_data = [pd.DataFrame(requests.get(f'{url}{key}').json()['CompactData']['DataSet']['Series']['Obs']).iloc[:, [0,1]] for key in exchange_rate_key]

#cpi_df = pd.DataFrame(data)
def data_func(data_df):
    data_df.columns = ['Date', 'Rate']
    data_df['Date'] = pd.to_datetime(data_df['Date'])
    data_df['Rate'] = pd.to_numeric(data_df['Rate'])
    return data_df
#int_df_plot_abg = cpi_df_plot.iloc[-16:, :]
#int_df_plot.plot.line()


#xcr_df_plot.plot.line()
interest_data_list = [data_func(df) for df in interest_data]

inflation_data_list = [data_func(df) for df in inflation_data]

exchange_rate_data_list = [data_func(df) for df in exchange_rate_data]

# Dictionaries
interest_data_dict = dict(zip(interest_key_name, interest_data_list))

inflation_rate_dict = dict(zip(inflation_key_name, inflation_data_list))

exchange_rate_dict = dict(zip(exchange_rate_key_name, exchange_rate_data_list))

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(id="ticker_box" ,type="search", value="BOPP")),
        dbc.Col(
            dbc.Button("Search", id="search_button", color="primary", className="ml-2"),
            width="auto",
        ),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"


app.layout = html.Div([
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(
            dbc.Navbar(
                [
                    html.A(
                        # Use row and col to control vertical alignment of logo / brand
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=PLOTLY_LOGO, height="60px")),
                                dbc.Col(dbc.NavbarBrand("INVESTMENT RESEARCH GROUP", className="ml-2")),
                            ],
                            align="center",
                            no_gutters=True,
                        ),
                        href="https://plot.ly",
                    ),
                    dbc.NavbarToggler(id="navbar-toggler"),
                    dbc.Collapse(search_bar, id="navbar-collapse", navbar=True),
                ],
                color="dark",
                dark=True,
            ),
        width=8),
        dbc.Col(width=2)
    ]),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                    dbc.CardHeader(
                        html.H4('Interest rates')
                    ),
                    dbc.CardBody(
                        [
                        dcc.Dropdown(
                            id='interest_type',
                            options=[{'label': i, 'value': i} for i in interest_key_name],
                            value='Financial, Interest Rates, Government Securities, Government Bonds, Percent per annum'
                        ),
                        dcc.Graph(
                        id='interest_graph'        
                        )
                    ])
                ])
            ),
        width=8),
        dbc.Col(width=2)
    ]),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                    dbc.CardHeader(
                        html.H4('Inflation rates')
                    ),
                    dbc.CardBody(
                        [
                        dcc.Dropdown(
                            id='inflation_type',
                            options=[{'label': i, 'value': i} for i in inflation_key_name],
                            value='Prices, Consumer Price Index, All items, Percentage change, Corresponding period previous year, Percent'
                        ),
                        dcc.Graph(
                        id='inflation_graph'        
                        )
                    ])
                ])
            ),
        width=8),
        dbc.Col(width=2)
    ]),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                    dbc.CardHeader(
                        html.H4('Exchange rates')
                    ),
                    dbc.CardBody(
                        [
                        dcc.Dropdown(
                            id='forex_type',
                            options=[{'label': i, 'value': i} for i in exchange_rate_key_name],
                            value='Exchange Rates, Domestic Currency per ECU, Period Average, Rate'
                        ),
                        dcc.Graph(
                        id='forex_graph'        
                        )
                    ])
                ])
            ),
        width=8),
        dbc.Col(width=2)
    ])
])


@app.callback(
    Output('interest_graph', 'figure'),
    [Input('interest_type', 'value')]
)
def interest_graph(interest_type):
    interest_df = interest_data_dict[interest_type]
    fig = px.line(interest_df, x="Date", y="Rate", template='simple_white')
    return fig


@app.callback(
    Output('inflation_graph', 'figure'),
    [Input('inflation_type', 'value')]
)
def inflation_graph(inflation_type):
    inflation_df = inflation_rate_dict[inflation_type]
    fig = px.line(inflation_df, x="Date", y="Rate", template='simple_white')
    return fig



@app.callback(
    Output('forex_graph', 'figure'),
    [Input('forex_type', 'value')]
)
def forex_graph(forex_type):
    forex_df = exchange_rate_dict[forex_type]
    fig = px.line(forex_df, x="Date", y="Rate", template='simple_white')
    return fig




if __name__ == '__main__':
    app.run_server(debug=True)








