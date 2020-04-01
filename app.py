import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import os
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_table
import dash_bootstrap_components as dbc


#Determine the current working directory
print(os.getcwd())

#set desired working directory
os.chdir('C:/Users/fohask1/.conda/venv')

#pull data
alldata = pd.read_csv('Revenue_Data.csv')


alldata = alldata.assign(Gross_margin = (alldata['Gross profit/loss']/alldata['Net revenue'])*100, Operating_margin = (alldata['EBIT']/alldata['Net revenue'])*100, Before_tax_margin = (alldata['EBT']/alldata['Net revenue'])*100, Net_margin = (alldata['Net Profit/Loss']/alldata['Net revenue'])*100)



allrev = alldata[["Net revenue", "EBIT", "EBT", "Net Profit/Loss"]]
allcost = alldata[["Cost of Sales", "Selling and distribution costs", "General and administrative expenses", "Other income/expense"]]
allmargin = alldata[['Gross_margin', 'Operating_margin', 'Before_tax_margin', 'Net_margin']]








external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = 'PACT'

server = app.server

colors = {
    'background' : '#9090a6',
    'text': '#7FDBFF' 
}





app.layout = html.Div([
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
        className = 'row'),
    html.Div([
        html.H1(children='Ghana Stock Exchange Dashboard')
    ], className = 'row'),
    html.Div([
        html.Div([
            html.H4(children='Choose Company'),
            html.Div([
                dcc.RadioItems(
                    id='ticker',
                    options=[
                        {'label': 'Cocoa Processing Company', 'value': 'CPC'},
                        {'label': 'Produce Buying Company', 'value': 'PBC'},
                        {'label': 'Fan Milk Ltd', 'value': 'FML'},
                        {'label': 'Benso Oil Palm Plantation', 'value': 'BOPP'},
                        {'label': 'Camelot Ghana Ltd', 'value': 'CMLT'}
                    ],
                    value='CPC'
                ),
            ], className = 'row'),
        ], className = 'two columns'),
        html.Div([
            html.H4(children='Revenue Analysis'),
            html.Div([
                dcc.Dropdown(
                    id='revenue',
                    options=[
                        {'label': 'Net Revenue', 'value': 'Net revenue'},
                        {'label': 'Gross Income', 'value': 'Gross profit/loss'},
                        {'label': 'Net Income', 'value': 'Net Profit/Loss'},
                        {'label': 'EBIT', 'value': 'EBIT'},
                        {'label': 'EBT', 'value': 'EBT'}
                    ],
                    value='Net revenue'
                ),
            ]),
            html.Div(id='Revenue Graph'),
        ], className = 'three columns'),
        html.Div([
            html.H4(children='Cost Analysis'),
            html.Div([
                dcc.Dropdown(
                    id='costs',
                    options=[
                        {'label': 'Cost of Sales', 'value': 'Cost of Sales'},
                        {'label': 'Selling and distribution', 'value': 'Selling and distribution costs'},
                        {'label': 'General and Administrative', 'value': 'General and administrative expenses'},
                        {'label': 'Other income/expenses', 'value': 'Other income/expense'}
                    ],
                    value='Cost of Sales'
                ),
            ]),
            html.Div(id='Cost Graph'),
        ], className = 'three columns'),
        html.Div([
            html.H4(children='Income Ratio Analysis'),
            html.Div([
                dcc.Dropdown(
                    id='margins',
                    options=[
                        {'label': 'Gross Margin', 'value': 'Gross_margin'},
                        {'label': 'Operating Margin', 'value': 'Operating_margin'},
                        {'label': 'Before Tax Margin', 'value': 'Before_tax_margin'},
                        {'label': 'Net Margin', 'value': 'Net_margin'}
                    ],
                    value='Gross_margin'
                ),
            ]),
            html.Div(id='Margin Graph'),
        ], className = 'three columns'),
    ], className = 'row'),
    html.Div([
        dbc.Table(id='Revenue Table',
            bordered=True,
            dark=True,
            hover=True,
            responsive=True,
            striped=True,        
        ),
    ], className = 'row'),
])    



@app.callback(
    Output("Revenue Graph", "children"),
    [Input("ticker", "value"),
    Input("revenue", "value")]  #scan through the code and look for id called "ticker", and pick whatever value that is showing
)
def update_figure(ticker, revenue):
    profit = alldata[alldata['Ticker'] == ticker][revenue]
    datetable = alldata[alldata['Ticker'] == ticker]['Year']

    data = []
    trace_rev = go.Bar(x=datetable, 
                        y=profit
                        )
    
    data.append(trace_rev)

    layout = {}

    graph=dcc.Graph(
        id='Revenue',
        figure={
    "data": data,
    "layout": layout
    }
    )

    return graph


@app.callback(
    Output("Cost Graph", "children"),
    [Input("ticker", "value"),
    Input("costs", "value")]  #scan through the code and look for id called "ticker", and pick whatever value that is showing
)
def update_figure(ticker, costs):
    cost = alldata[alldata['Ticker'] == ticker][costs]
    datetable = alldata[alldata['Ticker'] == ticker]['Year']

    data = []
    trace_rev = go.Bar(x=datetable, 
                        y=cost
                        )
    
    data.append(trace_rev)

    layout = {}

    graph=dcc.Graph(
        id='Costs',
        figure={
    "data": data,
    "layout": layout
    }
    )

    return graph


@app.callback(
    Output("Margin Graph", "children"),
    [Input("ticker", "value"),
    Input("margins", "value")]  #scan through the code and look for id called "ticker", and pick whatever value that is showing
)
def update_figure(ticker, margins):
    margin = alldata[alldata['Ticker'] == ticker][margins]
    datetable = alldata[alldata['Ticker'] == ticker]['Year']

    data = []
    trace_rev = go.Bar(x=datetable, 
                        y=margin
                        )
    
    data.append(trace_rev)

    layout = {}

    graph=dcc.Graph(
        id='Costs',
        figure={
    "data": data,
    "layout": layout
    }
    )

    return graph


@app.callback(
    Output("Revenue Table", "children"),
    [Input("ticker", "value")]
)
def update_table(ticker):
    profit = alldata.loc[alldata['Ticker'] == ticker, ['Year', 'Net Revenue', 'Cost of Sales', 'Gain from fair value change', 'Gross profit/loss', 'Selling and distribution costs', 'General and administrative expenses', 'Other income/expense', 'EBIT', 'Net Profit/Loss']]
    #profit['Year'] = profit['Year'].astype(str)
    df_profit = profit.T
    table = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in profit.columns],
    data=profit.to_dict('records'),
    )

    return table






if __name__ == '__main__':
    app.run_server(debug=True)