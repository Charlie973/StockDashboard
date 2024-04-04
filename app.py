# Import necessary libraries
import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output
import gunicorn
import plotly.graph_objs as go
import pandas as pd

# Load dataset
df = pd.read_csv('./all_stocks_5yr.csv')

# Create Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1("Stock Market Trends Dashboard"),
    
    # Dropdown to select stock
    html.Label("Select Stock"),
    dcc.Dropdown(
        id='stock-dropdown',
        options=[{'label': stock, 'value': stock} for stock in df['Name'].unique()],
        value=df['Name'].unique()[0]
    ),
    
    # Slider to select date range
    html.Label("Select Date Range"),
    dcc.RangeSlider(
        id='date-slider',
        min=pd.to_datetime(df['date']).min().timestamp(),
        max=pd.to_datetime(df['date']).max().timestamp(),
        step=None,  # Allows for any date to be chosen
        marks={int(date.timestamp()): str(date.date()) for date in pd.date_range(start=pd.to_datetime(df['date']).min(), end=pd.to_datetime(df['date']).max(), freq='Y')},
        value=[pd.to_datetime(df['date']).min().timestamp(), pd.to_datetime(df['date']).max().timestamp()]
    ),
    
    # Checklist to select data attributes
    html.Label("Select Data Attributes"),
    dcc.Checklist(
        id='attributes-checklist',
        options=[
            {'label': 'Open', 'value': 'open'},
            {'label': 'High', 'value': 'high'},
            {'label': 'Low', 'value': 'low'},
            {'label': 'Close', 'value': 'close'},
            {'label': 'Volume', 'value': 'volume'}
        ],
        value=['close'],
        inline=True
    ),
    
    # RadioItems to select chart type
    html.Label("Select Chart Type"),
    dcc.RadioItems(
        id='chart-type-radio',
        options=[
            {'label': 'Line Chart', 'value': 'line'},
            {'label': 'Bar Chart', 'value': 'bar'},
            {'label': 'Scatter Plot', 'value': 'scatter'},
            {'label': 'Candlestick Chart', 'value': 'candlestick'}
        ],
        value='line',
        labelStyle={'display': 'block'}
    ),
    
    # Placeholder for charts
    html.Div(id='charts-container')
])

# Define callback to update charts based on user input
@app.callback(
    Output('charts-container', 'children'),
    [Input('stock-dropdown', 'value'),
     Input('date-slider', 'value'),
     Input('attributes-checklist', 'value'),
     Input('chart-type-radio', 'value')]
)
def update_charts(selected_stock, selected_dates, selected_attributes, chart_type):
    start_date = pd.to_datetime(selected_dates[0], unit='s')
    end_date = pd.to_datetime(selected_dates[1], unit='s')
    
    filtered_df = df[(df['Name'] == selected_stock) & 
                     (pd.to_datetime(df['date']).between(start_date, end_date))]
    
    if chart_type == 'scatter':
        # Scatter plot
        fig = go.Figure(data=go.Scatter(x=filtered_df['close'], y=filtered_df['volume'], mode='markers'))
        fig.update_layout(title=f"{selected_stock} Closing Price vs Volume")
    elif chart_type == 'candlestick':
        # Candlestick chart
        fig = go.Figure(data=[go.Candlestick(x=filtered_df['date'],
                                             open=filtered_df['open'],
                                             high=filtered_df['high'],
                                             low=filtered_df['low'],
                                             close=filtered_df['close'])])
        fig.update_layout(title=f"{selected_stock} Candlestick Chart")
    else:
        # Create subplots for multiple attributes
        fig = px.line(filtered_df, x='date', y=selected_attributes, title=f"{selected_stock} Stock Data")
        if chart_type == 'bar':
            fig.update_traces(mode='lines+markers')  # Change to lines + markers for bar chart
    
    return dcc.Graph(figure=fig)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)