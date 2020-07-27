import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go
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


# =============================================================================
# # Import historical stock price data
# def import_hist_data():
#     file_path_list = ['C:\\Users\\fohask1\\Desktop\\Learning\\Web_development\\gse_app\\Prices\\GSE\\{}'.format(stock_name) for stock_name in stock_names if stock_name not in ['DASPHARMA']]
#     glob_path_list = [glob('{}\\*csv'.format(file_path)) for file_path in file_path_list]
#     all_data_paths = [path for path_list in glob_path_list for path in path_list]
#     stock_price_df_list = [pd.read_csv(path, parse_dates=['Date']) for path in all_data_paths]
#     stock_price_hist = pd.concat(stock_price_df_list, axis=0)
#     return stock_price_hist.iloc[:, :5]
# 
# stock_price_df_hist = import_hist_data()
# 
# # Import 2020 Stock price information
# def import_2020_data():
#     file_path_2020 = glob('C:\\Users\\fohask1\\Desktop\\Learning\\Web_development\\gse_app\\Prices\\GSE\\Current\\GSE 2020 (Jan - April)\\*csv')
#     df_2020 = [pd.read_csv(file_path, parse_dates=['Date']) for file_path in file_path_2020]
#     merged_df = pd.concat(df_2020, axis=0)
#     return merged_df
# 
# stock_price_df_2020 = import_2020_data()
# 
# # Full stock prices dataset
# stock_price_df = pd.concat([stock_price_df_hist, stock_price_df_2020], axis=0)
# 
# =============================================================================

# Import historical stock prices
stock_price_df = pd.read_csv('C:\\Users\\fohask1\\Desktop\\Learning\\Web_development\\gse_app\\Financials\\Stock_Prices_Update.csv', parse_dates=['Date'])

# Convert price to float 
stock_price_df['Closing Price VWAP (GHS)'] = pd.to_numeric(stock_price_df['Closing Price VWAP (GHS)'], errors='coerce')

stock_price_tickers = [{'label':i, 'value':i} for i in stock_price_df['Share Code'].unique().tolist()]
#print(stock_price_tickers)

# Create a list of all share codes
share_code = stock_price_df['Share Code'].unique().tolist()
share_code_list = [share for share in share_code if str(share) != 'nan']



# Import stock general information
def share_charac_func(share_code):
    ticker_url = 'https://dev.kwayisi.org/apis/gse/equities/{}'.format(share_code)
    ticker_pull = requests.get(ticker_url)
    ticker_json = ticker_pull.json()
    return ticker_json
stock_charact_list = [share_charac_func(share) for share in share_code_list]

# Extract market cap
market_cap = [stock_charact_list[i]['capital'] for i in range(39) if i != 31]

# Extract company names
company_names = [stock_charact_list[i]['company']['name'] for i in range(39) if i != 31]

# Extract company share codes
company_share_codes = [stock_charact_list[i]['name'] for i in range(39) if i != 31]

#extract industry names
industry_names = [stock_charact_list[i]['company']['sector'] for i in range(39) if i != 31]

# Create DataFrame for extracted information
capital_company = pd.DataFrame(zip(company_names, industry_names, market_cap), columns=['Name', 'Sector', 'Capitalization'])
capital_industry = capital_company.groupby(by='Sector', as_index=False).Capitalization.sum().sort_values(by='Capitalization')

# Create dictionary of industry dfs 
industry_share = [capital_company.loc[capital_company['Sector']==sector] for sector in industry_names[1:]]
industry_share_dict = dict(zip(company_share_codes[1:], industry_share))

# create function to calculate the number of shares for a 10,000 cedi investment at inception of stocks trading
def stock_share_func(df, ticker):
    stock_df = df.loc[df['Share Code']==ticker]
    stock_inception_date = stock_df['Date'].min()
    stock_inception_price = stock_df[['Closing Price VWAP (GHS)']][stock_df['Date']==stock_inception_date].iat[0, 0]
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

fig_industry = go.Figure(go.Bar(
    x=capital_industry['Capitalization'],
    y=capital_industry['Sector'],
    orientation='h',
))
fig_industry.update_layout(
    margin=dict(l=5, r=5, t=5, b=5),
    template='simple_white'
)

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
                        html.H1(id='company_name')
                    ]
                )
            ), 
        width=8),
        dbc.Col(width=2)
    ]),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col([
            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        html.H3("Company Facts"),
                        dash_table.DataTable(
                            id="company_facts",
                            style_cell={'textAlign': 'left', 'font_size': '16px', 'padding': '5px'},
                            style_header={'fontWeight': 'bold', 'font_size': '18px'},
                            style_as_list_view=True
                        )
                    ])
                )
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dcc.Graph(id='industry_view',
                        figure=fig_industry
                        )
                    )
                )
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dcc.Graph(id='industry_share'
                        )
                    )
                )
            )],
        width=3),
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
    Output('ticker_return_graph', 'figure'),
    Output('company_name', 'children'),
    Output('company_facts', 'data'),
    Output('company_facts', 'columns'),
    Output('industry_share', 'figure')],
    [Input('search_button', 'n_clicks')],
    [State('ticker_box', 'value')]
)
def fig_func(n_clicks, ticker_name):
    ticker_url = 'https://dev.kwayisi.org/apis/gse/equities/{}'.format(ticker_name)
    ticker_pull = requests.get(ticker_url)
    ticker_json = ticker_pull.json()
    ticker_company = ticker_json['company']['name']

    company_df = pd.DataFrame(list(ticker_json['company'].items()), columns=['Attribute', 'Detail'])
    company_data = company_df.to_dict('records')
    company_col = [
        {'name': i, 'id': i} for i in ['Attribute', 'Detail']
    ]

    industry_share_df = industry_share_dict[ticker_name]
    pie_fig = px.pie(industry_share_df, values='Capitalization', names='Name')

    stock_df = stock_price_df.loc[stock_price_df['Share Code']==ticker_name].copy()
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
    return fig, bar_fig, ticker_company, company_data, company_col, pie_fig
    



if __name__ == '__main__':
    app.run_server(debug=True)
