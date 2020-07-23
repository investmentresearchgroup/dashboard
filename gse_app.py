import pandas as pd
from glob import glob
import os
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Sign
from collections import OrderedDict
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import requests
from datetime import date 
import plotly.express as px


# =============================================================================
# Connect to Ghana Stock Market API 
# =============================================================================
api_url = 'https://dev.kwayisi.org/apis/gse/live'
gse_data = requests.get(api_url)
gse_json = gse_data.json()

gse_df = pd.DataFrame(gse_json)

gse_df['Date'] = date.today()


stock_url = 'https://dev.kwayisi.org/apis/gse/equities'
stock_pull = requests.get(stock_url)
stock_json = stock_pull.json()


# =============================================================================
# Import Historical Prices
# =============================================================================
stock_hist = pd.read_csv('C:\\Users\\fohask1\\Desktop\\Learning\\Web_development\\gse_app\\Financials\\Stock_Prices.csv')



os.getcwd()
os.chdir('C:\\Users\\fohask1\\Desktop\\Learning\\Web_development\\gse_app\\Financials')

# Use glob module to pick up all files with file type xlsx within the directory for pd.read_excel 
file = glob('C:\\Users\\fohask1\\Desktop\\Learning\\Web_development\\gse_app\\Financials\\*xlsx')
for path in file:
    print(path)


# =============================================================================
# Check for the nature of all excel files in the directory
# =============================================================================

inspect_dfs = [pd.read_excel(df, sheet_name=1, nrows=3, usecols="A:J") for df in file]

# =============================================================================
# Import all the excel files into a list. Rename all the columns in the process
# =============================================================================
# Create a general column name list to pass in excel reader method
rev_col_names_v1 = ['Statement_Item', 'Dec-2018', 'Dec-2017', 'Dec-2016', 'Dec-2015', 'Dec-2014', 'Dec-2013', 'Dec-2012', 'Dec-2011', 'Dec-2010']

def rev_importer(path_list):
    rev_df_list_v1 = [pd.read_excel(excel, sheet_name=1, header=1, usecols="A:J", names=rev_col_names_v1) for excel in path_list]
    filter_df = [rev_df.dropna(subset=['Statement_Item']) for rev_df in rev_df_list_v1]
    index_df = [rev_df.set_index('Statement_Item') for rev_df in filter_df]
    replace_df = [rev_df.fillna(0) for rev_df in index_df]
    integer_df = [rev_df.reset_index() for rev_df in replace_df]
    return integer_df
        
# IS is abbreviation for Income Statement
is_df_list = rev_importer(file)

# assign all dfs in list variable names
anglo_df = is_df_list[0]
ayrtn_df = is_df_list[1]
bopp_df = is_df_list[2]
cmlt_df = is_df_list[3]
cpc_df = is_df_list[4]
cyld_df = is_df_list[5]
fml_df = is_df_list[6]
ggbl_df = is_df_list[7]
goil_df = is_df_list[8]
hords_df = is_df_list[9]
m_lloyd_df = is_df_list[10]
mmh_df = is_df_list[11]
pbc_df = is_df_list[12]
pzc_df = is_df_list[13]
spl_df = is_df_list[14]
swl_df = is_df_list[15]
unl_df = is_df_list[16] 



statement_list = ['Revenue', 'Other Revenue', 'Total Revenue', 'Cost of Goods Sold', 'Gross Profit', 'Selling/Genera/Administrative Expense', 'Other Operating Expense/Income', 'EBIT', 'Interest Income/Expense', 'Other Financial Expense/Income', 'EBT', 'Income Tax', 'Net Profit']



def income_func(list_exclusion, statement_values):
    pd.options.display.float_format='{:,.2f}'.format
    df = pd.DataFrame(columns=rev_col_names_v1)
    df['Statement_Item'] = statement_list
    df = df.set_index('Statement_Item')
    statement_item = [element for element in statement_list if element not in list_exclusion]
    for item, value in zip(statement_item, statement_values):
        df.loc[item] = value
    df.fillna(0, inplace=True)
    df.astype('int32', errors='ignore')
    return df.reset_index()



bopp_rev = bopp_df.iloc[0, 1:]
bopp_other_rev = bopp_df.iloc[2:4, 1:].sum()
bopp_total_rev = bopp_df.iloc[[0,2,4], 1:].sum()
bopp_cogs = bopp_df.iloc[1, 1:]
bopp_g_profit = bopp_df.iloc[4, 1:]
bopp_sga = bopp_df.iloc[5, 1:]
bopp_other_operate_income = bopp_df.iloc[6, 1:]
bopp_operate_profit = bopp_df.iloc[7, 1:]
bopp_interest_income = bopp_df.iloc[8, 1:]
bopp_ebt = bopp_df.iloc[9, 1:]
bopp_tax = bopp_df.iloc[10, 1:]
bopp_net_profit = bopp_df.iloc[11, 1:]

bopp_item_values = [bopp_rev, bopp_other_rev, bopp_total_rev, bopp_cogs, bopp_g_profit, bopp_sga, bopp_other_operate_income, bopp_operate_profit, bopp_interest_income, bopp_ebt, bopp_tax, bopp_net_profit]


bopp_data = income_func(['Other Financial Expense/Income'], bopp_item_values)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(id="ticker_box" ,type="search", value="AADS")),
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
                                dbc.Col(dbc.NavbarBrand("IRG", className="ml-2")),
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
                        html.H1(id='company')
                    ]
                )
            ), 
        width=8),
        dbc.Col(width=2)
    ]),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dbc.Row([
                        dbc.Col(
                            [
                            html.H6(
                                "Last Trade (GHS)", 
                                className="price",
                                style={
                                    'textAlign': 'center'
                                }),
                            html.H2(
                                id="last_trade",
                                style={
                                    'textAlign': 'center'
                                }),
                            ],
                        width=3),
                        dbc.Col(
                            [
                            html.H6(
                                "Change", 
                                className="change",
                                style = {
                                    'textAlign': 'center'
                                }),
                            html.H2(
                                id='change',
                                style={
                                    'textAlign': 'center'
                                }
                                ),
                            ],
                            width=3),
                        dbc.Col(
                            [
                            html.H6(
                                "Volume", 
                                className="volume",
                                style={
                                    'textAlign': 'center'
                                }),
                            html.H2(
                                id='volume',
                                style={
                                    'textAlign': 'center'
                                }),
                            ],
                        width=3),
                        dbc.Col(
                            [
                            html.H6(
                                "Value (GHS)", 
                                className="value",
                                style={
                                    'textAlign': 'center'
                                }),
                            html.H2(
                                id='value',
                                style={
                                    'textAlign': 'center'
                                }),
                            ],
                        width=3)
                    ]),
                ),
            outline=False),
        width=8),
        dbc.Col(width=2)
    ]),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                    dbc.ButtonGroup(
                        [dbc.Button("1mth"), dbc.Button("3mth"), dbc.Button("6mth"), dbc.Button("1yr"), dbc.Button("3yrs"), dbc.Button("5yrs")],
                        size="md",
                    ),
                    dcc.Graph(id='stock_price')
                    ]
                )
            ), 
        width=8),
        dbc.Col(width=2)
    ]),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Profile", active=True, href="#")),
                    dbc.NavItem(dbc.NavLink("Stock Analysis", active=True, href="#")),
                    dbc.NavItem(dbc.NavLink("Corporate Finance", active=True, href="#")),
                    dbc.NavItem(dbc.NavLink("Financials", active=True, href="#")),
                    dbc.NavItem(dbc.NavLink("Key Ratios", active=True, href="#")),
                    dbc.NavItem(dbc.NavLink("Valuation", active=True, href="#")),
                ]
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
                        dbc.Row([
                            dbc.Col(
                                dbc.Card(
                                    dcc.RadioItems(
                                    id='statement_element',
                                    options=[{'label':i, 'value':i} for i in bopp_data['Statement_Item'].unique()],
                                    value='Revenue'
                                ) 
                            ), width=3),
                            dbc.Col(dcc.Graph(
                            id='bopp_graph'
                            ), width=9)
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
                [
                    dbc.CardHeader(
                        dbc.Tabs(
                            [
                                dbc.Tab(label="Income Statement", tab_id="income_statement"),
                                dbc.Tab(label="Balance Sheet", tab_id="balance_sheet"),
                                dbc.Tab(label="Cash Flow", tab_id="cash_flow"),
                            ]
                        )
                    ),
                    dbc.CardBody([
                        dash_table.DataTable(
                            columns=[{'name':'All values in Thousands', 'id':j, 'type':'text'} for j in [rev_col_names_v1[0]]] + [{'name':i, 'id':i, 'type':'numeric'} for i in rev_col_names_v1[1:]],
                            data=bopp_data.to_dict('records'),
                            style_as_list_view=True,
                            style_cell={
                                'padding':'5px',
                                'font_size':'16px'},
                            style_header={
                                'backgroundColor':'rgb(230, 230, 230)',
                                'fontWeight':'bold',
                                'font_size':'16px'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index':'odd'},
                                    'backgroundColor':'rgb(248, 248, 248)'
                                }
                            ],
                            style_cell_conditional=[
                                {
                                    'if':{'column_id':i},
                                    'textAlign': 'left'
                                } for i in ['Statement_Item']
                            ],
                            editable=True,
                            export_format='xlsx',
                            export_headers='display',
                            merge_duplicate_headers=True
                        ),
                    ])
                ]
            ),
        width=8),
        dbc.Col(width=2)
    ])
])

@app.callback(
    [Output('last_trade', 'children'),
     Output('change', 'children'),
     Output('volume', 'children'),
     Output('value', 'children'),
     Output('company', 'children'),
     Output('stock_price', 'figure')],
    [Input('search_button', 'n_clicks')],
    [State('ticker_box', 'value')])
def gse_update(n_clicks, ticker):
    ticker_url = 'https://dev.kwayisi.org/apis/gse/equities/{}'.format(ticker)
    ticker_pull = requests.get(ticker_url)
    ticker_json = ticker_pull.json()
    ticker_price = gse_df[gse_df['name']==ticker].iloc[:, 1]
    ticker_change = gse_df[gse_df['name']==ticker].iloc[:, 2]
    ticker_volume = gse_df[gse_df['name']==ticker].iloc[:, 3]
    ticker_value = ticker_price * ticker_volume
    ticker_company = ticker_json['company']['name']
    df = stock_hist[stock_hist['Share Code']==ticker]
    fig = px.line(df, x='Date', y='Closing Price VWAP (GHS)')
    return ticker_price, ticker_change, ticker_volume, ticker_value, ticker_company, fig






@app.callback(
    Output('bopp_graph', 'figure'),
    [Input('statement_element', 'value')])
def bopp_fig(select_item):
    y_values = bopp_data[bopp_data['Statement_Item']==select_item].iloc[0,1:]
    fig = go.Figure(data=[go.Bar(
        x=rev_col_names_v1[1:],
        y=y_values,
        text=bopp_total_rev,
        marker_color='lightslategrey'
    )])
    fig.update_layout(transition_duration=500)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)



