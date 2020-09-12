# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 17:35:32 2020

@author: FOHASK1
"""

import pandas as pd
import os
import requests
import statsmodels.api as sm
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State



os.chdir('C:\\Users\\fohask1\\Desktop\\Learning\\Web_development\\gse_app\\Financials')

dataset_list = [pd.read_csv(file, parse_dates=['Date'], thousands=',') for file in ['Market Summary (Equities) – Ghana Stock Exchange.csv', 'Stock_Prices_Update.csv']]

def risk_free_func():
    df = pd.read_csv('Treasury Bills.csv', header=0, names=['Date', 'Rate'], parse_dates=['Date'])
    df = df[(df.Date>=pd.to_datetime('20150101')) & (df.Date<=pd.to_datetime('20191231'))]
    df_index = df.set_index('Date').div(12)
    return df_index.reset_index()

risk_free_df = risk_free_func()

data_list = [df[(df.Date>=pd.to_datetime('20150101')) & (df.Date<=pd.to_datetime('20191231'))] for df in dataset_list]

index_data, stock_price_data = data_list


# =============================================================================
# Index data wrangle
# =============================================================================
def index_wrangle(df):
    filter_df = df.iloc[:, [1,3]]
    filter_df.columns = ['Date', 'Values']
    indexed_df = filter_df.set_index('Date')
    resampled_df = indexed_df.Values.resample('M').last()
    data_framed = resampled_df.to_frame()
    data_framed['Return'] = data_framed.pct_change().mul(100)
    return data_framed

index_df = index_wrangle(index_data)


def stock_wrangle(df):
    filter_df = df.iloc[:, :]
    filter_df.columns = ['Date', 'Values']
    filter_df['Values'] = pd.to_numeric(filter_df['Values'])
    indexed_df = filter_df.set_index('Date')
    resampled_df = indexed_df.Values.resample('M').last()
    data_framed = resampled_df.to_frame()
    data_framed['Return'] = data_framed.pct_change().mul(100)
    return data_framed
  
stock_name_list = stock_price_data.dropna(subset=['Share Code'])['Share Code'].unique().tolist()    
stock_df_list = [stock_wrangle(stock_price_data.loc[:, ['Date', 'Closing Price VWAP (GHS)']][stock_price_data['Share Code']==ticker]) for ticker in stock_price_data.dropna(subset=['Share Code'])['Share Code'].unique().tolist()]


def group_func(stock_df, market_df):
    merged_df = stock_df.merge(market_df, how='left', left_on='Date', right_on='Date')
    merged_df.columns = ['Stock_Price', 'Stock_Return', 'Market_Index', 'Market_Return']
    return merged_df.iloc[1:, :]

stock_index_df_list = [group_func(df, index_df) for df in stock_df_list]


def risk_premium_func():
    merged_df = pd.concat([index_df.reset_index(), risk_free_df], axis=1).iloc[1:, :]
    merged_df['Premium'] = merged_df['Return'] - merged_df['Rate']
    premium = merged_df['Premium'].mean()
    return premium

risk_premium = round(risk_premium_func(), 2)
risk_free_rate = round(risk_free_df.loc[59, 'Rate'], 2)


def regression_func(df):
    y = df['Stock_Return']
    x = df['Market_Return']
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    coeff = model.params
    rsquared = model.rsquared
    return coeff, rsquared

def rsquared_func():
    empty_list = []
    for df in stock_index_df_list:
        rsquared = regression_func(df)
        empty_list.append(rsquared[1])
    return empty_list

rsquared_list = np.nan_to_num(rsquared_func())

def beta_func():
    empty_list = []
    for df in stock_index_df_list:
        beta = regression_func(df)
        empty_list.append(round(beta[0][1], 2))
    return empty_list

beta_list = np.nan_to_num(beta_func())

def capm_func():
    empty_list = []
    for beta in beta_list:
        ror = risk_free_rate + (beta * risk_premium)
        annual_ror = round(ror, 2) * 12
        empty_list.append(annual_ror)
    return empty_list

return_rate_list = capm_func()

dict_list = [dict(zip(stock_name_list, metric_list)) for metric_list in [stock_index_df_list, stock_df_list, beta_list, return_rate_list]]

stock_index_dict, stock_dict, beta_dict, return_dict = dict_list

beta_graph_df = pd.DataFrame(list(beta_dict.items()), columns=['Ticker', 'Beta']).sort_values(by=['Beta'])


external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

beta_fig = go.Figure(go.Bar(
    x=beta_graph_df.Ticker,
    y=beta_graph_df.Beta,
))
beta_fig.update_layout(
    margin=dict(l=10, r=10, b=10, t=10, pad=2),
    plot_bgcolor="white"
)
beta_fig.update_traces(marker_color='rgb(118,183,178)')


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
        width=12)
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H1(id='company_name')
                    ]
                )
            ), 
        width=12)
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dbc.Row([
                        dbc.Col(
                            [
                            html.H4(
                                "2020 Rate of Return", 
                                className="return",
                                style={
                                    'textAlign': 'center'
                                }),
                            html.H2(
                                id="return",
                                style={
                                    'textAlign': 'center'
                                }),
                            ],
                        width=3),
                        dbc.Col(
                            [
                            html.H4(
                                "Beta", 
                                className="beta",
                                style = {
                                    'textAlign': 'center'
                                }),
                            html.H2(
                                id='beta',
                                style={
                                    'textAlign': 'center'
                                }
                                ),
                            ],
                            width=3),
                        dbc.Col(
                            [
                            html.H4(
                                "Risk-free Rate", 
                                className="risk_free",
                                style={
                                    'textAlign': 'center'
                                }),
                            html.H2(
                                f"{risk_free_rate}%",
                                id='risk_free',
                                style={
                                    'textAlign': 'center'
                                }),
                            ],
                        width=3),
                        dbc.Col(
                            [
                            html.H4(
                                "Risk Premium", 
                                className="risk_premium",
                                style={
                                    'textAlign': 'center'
                                }),
                            html.H2(
                                risk_premium,
                                id='risk_premium',
                                style={
                                    'textAlign': 'center'
                                }),
                            ],
                        width=3)
                    ]),
                ),
            outline=False),
        width=12)
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dbc.CardHeader(
                                    html.H4('Correlation between stock and market return')
                                ),
                                dbc.CardBody(
                                    [
                                    dcc.Graph(
                                    id='ticker_graph'        
                                    )
                                    ]
                                )
                            ])
                        )
                    )
                ]),
            ), width=6
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dbc.CardHeader(
                                    html.H4('Historic Monthly Returns')
                                ),
                                dbc.CardBody(
                                    [
                                    dcc.Graph(
                                    id='ticker_return_graph'        
                                    )
                                    ]
                                )
                            ])
                        )
                    )
                ]),
            ), width=6
        )
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Bar chart of Beta for all Companies"
                        )
                    ]
                )
            )
        )
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(
                            id='beta_graph',
                            figure=beta_fig
                        )
                    ]
                )
            )
        )
    ])
])


@app.callback(
    [Output('ticker_graph', 'figure'),
    Output('ticker_return_graph', 'figure'),
    Output('company_name', 'children'),
    Output('beta', 'children'),
    Output('return', 'children')],
    [Input('search_button', 'n_clicks')],
    [State('ticker_box', 'value')]
)
def fig_func(n_clicks, ticker_name):
    ticker_url = 'https://dev.kwayisi.org/apis/gse/equities/{}'.format(ticker_name)
    ticker_pull = requests.get(ticker_url)
    ticker_json = ticker_pull.json()
    ticker_company = ticker_json['company']['name']


    stock_index_return = stock_index_dict[ticker_name]
    fig = px.scatter(stock_index_return, x="Market_Return", y="Stock_Return", template='simple_white')
    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5)
    )

    return_df = stock_dict[ticker_name].reset_index()
    bar_fig = px.bar(return_df, x='Date', y='Return', template='simple_white')
    bar_fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5)
    )
    
    beta = beta_dict[ticker_name]
    
    return_rate = return_dict[ticker_name]
    rate_of_return = f"{return_rate:2f}%"
    
    return fig, bar_fig, ticker_company, beta, rate_of_return
    



if __name__ == '__main__':
    app.run_server(debug=True)
