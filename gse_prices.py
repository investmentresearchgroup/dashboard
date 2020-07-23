# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 00:41:24 2020

@author: FOHASK1
"""

import pandas as pd
import os
import requests
from glob import glob
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc


def gse_api_func():
    stocks_url = 'https://dev.kwayisi.org/apis/gse/live'
    stock_data = requests.get(stocks_url)
    stock_dict = stock_data.json()
    return pd.DataFrame(stock_dict)

stock_df = gse_api_func()

stock_names = stock_df.name.tolist()


file_path_list = ['C:\\Users\\fohask1\\Desktop\\Learning\\Web_development\\gse_app\\Prices\\GSE\\{}'.format(stock_name) for stock_name in stock_names if stock_name not in ['DASPHARMA']]

glob_path_list = [glob('{}\\*csv'.format(file_path)) for file_path in file_path_list]


all_data_paths = [path for path_list in glob_path_list for path in path_list]

stock_price_df_list = [pd.read_csv(path, parse_dates=['Date']) for path in all_data_paths]

stock_price_df = pd.concat(stock_price_df_list, axis=0)

stock_price_df['Closing Price VWAP (GHS)'] = pd.to_numeric(stock_price_df['Closing Price VWAP (GHS)'], errors='coerce')

stock_price_tickers = [{'label':i, 'value':i} for i in stock_price_df['Share Code'].unique().tolist()]
print(stock_price_tickers)

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server


app.layout = html.Div([
    dbc.Row([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Page 1", href="#")),
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("More pages", header=True),
                        dbc.DropdownMenuItem("Page 2", href="#"),
                        dbc.DropdownMenuItem("Page 3", href="#"),
                    ],
                    nav=True,
                    in_navbar=True,
                    label="More",
                ),
            ],
            brand="NavbarSimple",
            brand_href="#",
            color="primary",
            dark=True,
        )
    ]),
    dbc.Row([
        html.H1(children='GSE Stock Prices'),
        html.Div(children='''
            Dash: A web application framework for Python.
        '''),
        html.Div([
            dcc.Input(
                id='select_ticker',
                type='text',
                value='AADS'
            ),
        ]),
    ]),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(width=4),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(
                        id='ticker_graph'        
                        ),
                        dcc.Input(id='date', type='text'),
                        html.Button(id='return_button', n_clicks=0, children='Submit'),
                        html.Div(id='return')
                    ]
                )
            ),
        width=4),
        dbc.Col(width=2)
    ]),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(width=4),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Input(id='ticker', type='text')
                    ]
                )
            ),
        width=4),
        dbc.Col(width=2)
    ]),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(width=4),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Input(id='investment', type='number')
                    ]
                )
            ),
        width=4),
        dbc.Col(width=2)
    ])
])


@app.callback(
    Output('ticker_graph', 'figure'),
    [Input('select_ticker', 'value')]
)
def fig_func(ticker_name):
    df = stock_price_df[stock_price_df['Share Code']==ticker_name]
    fig = px.line(df, x="Date", y="Closing Price VWAP (GHS)", title=ticker_name)
    return fig


@app.callback(
    Output('return', 'children'),
    [Input('return_button', 'n_clicks')],
    [State('ticker', 'value'),
    State('investment', 'value'),
    State('date', 'value')]
)
def return_func(n_clicks, ticker, amount, date):
    df = stock_price_df[stock_price_df['Share Code']==ticker]
    start_date = pd.to_datetime(date)
    end_date = pd.to_datetime('20191231')
    start_price = df['Closing Price VWAP (GHS)'][df['Date']==start_date]
    end_price = df['Closing Price VWAP (GHS)'][df['Date']==end_date]
    share_quantity = amount * start_price
    return_amount = (end_price - start_price) * share_quantity
    return amount

if __name__ == '__main__':
    app.run_server(debug=True)



