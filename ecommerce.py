import os
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
from datetime import datetime as dt, timedelta
from server import app

def layout():
    ecommerce = pd.read_csv('grouped_ecommerce.csv')
    ecommerce['date'] = pd.to_datetime(ecommerce['date'])
    ecommerce = ecommerce.groupby('date')['precio lab'].sum().reset_index()

    asofarma = pd.read_csv('Asofarma.csv')
    asofarma['date'] = pd.to_datetime(asofarma['date'])
    asofarma = asofarma.groupby('date')['precio lab'].sum().reset_index()

    min_date = min(ecommerce['date'].min(), asofarma['date'].min())
    max_date = max(ecommerce['date'].max(), asofarma['date'].max())
    today = dt.today()
    one_month_ago = today - timedelta(days=30)

    return html.Div([
        html.Div([
            dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                start_date=one_month_ago,
                end_date=today,
                display_format='DD/MM/YYYY',
            ),
            dcc.Graph(id='my-graph', style={
                'margin-top': '32px', 
                'margin-right': '32px', 
                'border-radius': '8px', 
                'background-color': 'white'
            })
        ], style={'margin-left': '32px'})
    ], style={'height': '60vw'})

@app.callback(
    Output('my-graph', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graph(start_date, end_date):
    ecommerce = pd.read_csv('grouped_ecommerce.csv')
    ecommerce['date'] = pd.to_datetime(ecommerce['date'], format='ISO8601')
    ecommerce = ecommerce.groupby('date')['precio lab'].sum().reset_index()

    asofarma = pd.read_csv('Asofarma.csv')
    asofarma['date'] = pd.to_datetime(asofarma['date'], format='ISO8601')
    asofarma = asofarma.groupby('date')['precio lab'].sum().reset_index()

    # Convert start_date and end_date to datetime
    start_date = pd.to_datetime(start_date, format='ISO8601')
    end_date = pd.to_datetime(end_date, format='ISO8601')

    # Filter data based on date range
    ecommerce = ecommerce[(ecommerce['date'] >= start_date) & (ecommerce['date'] <= end_date)]
    asofarma = asofarma[(asofarma['date'] >= start_date) & (asofarma['date'] <= end_date)]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=ecommerce['date'], y=ecommerce['precio lab'], name='Ingresos totales de BP', marker_color='#26A6EE'))
    fig.add_trace(go.Bar(x=asofarma['date'], y=asofarma['precio lab'], name='Asofarma', marker_color='#FF8587'))

    fig.update_layout(
        barmode='overlay',
        plot_bgcolor='rgba(0,0,0,0)',  # this makes the plot background transparent
        paper_bgcolor='rgba(0,0,0,0)',  # this makes the paper background transparent
    )
    fig.update_traces(opacity=0.80)

    return fig