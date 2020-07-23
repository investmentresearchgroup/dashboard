import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import os
import requests
from glob import glob

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Import current Stocks and corresponding prices in real time 
def gse_api_func():
    stocks_url = 'https://dev.kwayisi.org/apis/gse/live'
    stock_data = requests.get(stocks_url)
    stock_dict = stock_data.json()
    return pd.DataFrame(stock_dict)

stock_df = gse_api_func()
stock_names = stock_df.name.tolist()

# Import historical stock price data
file_path_list = ['C:\\Users\\fohask1\\Desktop\\Learning\\Web_development\\gse_app\\Prices\\GSE\\{}'.format(stock_name) for stock_name in stock_names if stock_name not in ['DASPHARMA']]
glob_path_list = [glob('{}\\*csv'.format(file_path)) for file_path in file_path_list]
all_data_paths = [path for path_list in glob_path_list for path in path_list]
stock_price_df_list = [pd.read_csv(path, parse_dates=['Date']) for path in all_data_paths]
stock_price_df = pd.concat(stock_price_df_list, axis=0)

# Convert price to float 
stock_price_df['Closing Price VWAP (GHS)'] = pd.to_numeric(stock_price_df['Closing Price VWAP (GHS)'], errors='coerce')

stock_price_tickers = [{'label':i, 'value':i} for i in stock_price_df['Share Code'].unique().tolist()]
print(stock_price_tickers)

# Create a list of all share codes
share_code = stock_price_df['Share Code'].unique().tolist()
share_code_list = [share for share in share_code if str(share) != 'nan']

# create function to calculate the number of shares for a 10,000 cedi investment at inception of stocks trading
def stock_share_func(df, ticker):
    stock_df = df.loc[df['Share Code']==ticker]
    stock_inception_date = stock_df['Date'].min()
    stock_inception_price = stock_df[['Closing Price VWAP (GHS)']][stock_df['Date']==stock_inception_date].at[0,'Closing Price VWAP (GHS)']
    stock_inception_shares = 10000 / stock_inception_price
    return stock_inception_shares

# Assign function to a variable 
start_shares_list = [stock_share_func(stock_price_df, share) for share in share_code_list]


# Zip the share code names to share count at inception for a 10,000 cedi investment
ticker_share_dict = dict(zip(share_code_list, start_shares_list))   


# Function for closing year prices
stock_price_df['Year'] = stock_price_df['Date'].dt.year

# Annual return function under development

def annual_rate_func(df, stock):
#    df = old_df.loc[old_df['Share Code']==stock].copy()
    begin = list(df.loc[df['Share Code']==stock].groupby(by='Year', as_index=False).apply(lambda x: x[x['Date'] == x['Date'].min()]['Closing Price VWAP (GHS)'].mean()))
    end = list(df.loc[df['Share Code']==stock].groupby(by='Year', as_index=False).apply(lambda x: x[x['Date'] == x['Date'].max()]['Closing Price VWAP (GHS)'].mean()))
    year = stock_price_df.loc[stock_price_df['Share Code']==stock]['Year'].unique().tolist()
    annual_df = pd.DataFrame(list(zip(year, end, begin)), columns=['Year', 'Close', 'Start'])
    annual_df['Returns'] = annual_df.apply(lambda x: (x['Close'] - x['Start']) / x['Start'], axis=1)
    return annual_df


# Create a list of the annual returns df calculated based on the annual return function
annual_return_list = [annual_rate_func(stock_price_df, share) for share in share_code_list]


# create a share code annual return df dictionary for the callback function
annual_return_df_dict = dict(zip(share_code_list, annual_return_list))




app.layout = html.Div([
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H1(children='GSE Stock Prices')
                    ]
                )
            ),
        width=8),
        dbc.Col(width=2)
    ]),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(width=4),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
            dcc.Input(
                id='select_ticker',
                type='text',
                value='AADS'),
            html.Button(
                id='click_button', n_clicks=0, children='Submit')
                    ]
                )
            ),
        width=4),
        dbc.Col(width=2)
    ]),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(width=3),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dbc.Row(
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                    html.H4('Company Objectives'),
                                    html.Div("The company focuses on mining activities")
                                    ]
                                )
                            )
                        )
                    ),
                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dbc.CardHeader(
                                    html.H4('Growth of GHS 10,000 Investment')
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
                    ),
                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dbc.CardHeader(
                                    html.H4('Historic Annual Returns')
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
            ), width=5
        ),
        dbc.Col(width=2)
    ])
])


@app.callback(
    [Output('ticker_graph', 'figure'),
    Output('ticker_return_graph', 'figure')],
    [Input('click_button', 'n_clicks')],
    [State('select_ticker', 'value')]
)
def fig_func(n_clicks, ticker_name):
#    df = stock_price_df[stock_price_df['Share Code']==ticker_name]
    stock_df = stock_price_df.loc[stock_price_df['Share Code']==ticker_name].copy()
#    stock_inception_date = stock_df['Date'].min()
#    stock_inception_price = stock_df[['Closing Price VWAP (GHS)']][stock_df['Date']==stock_inception_date].at[0,'Closing Price VWAP (GHS)']
#    stock_inception_shares = 10000 / stock_inception_price
    stock_df['Share Volume'] = ticker_share_dict[ticker_name]
    stock_df['Investment Value'] = stock_df['Closing Price VWAP (GHS)'] * stock_df['Share Volume']
    fig = px.line(stock_df, x="Date", y="Investment Value", template='simple_white')
    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5)
    )

    return_df = annual_return_df_dict[ticker_name]
    bar_fig = px.bar(return_df, x='Year', y='Returns', template='simple_white')
    bar_fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5)
    )
    return fig, bar_fig



if __name__ == '__main__':
    app.run_server(debug=True)
