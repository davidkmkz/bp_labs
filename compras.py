import pandas as pd
import plotly.express as px
from dash import dcc, html, Dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from datetime import datetime as dt, timedelta

from server import app  # Import the app from server.py

def layout():
    # Read the data from the CSV file
    df = pd.read_csv('Ordenes.csv')
    # Convert 'fecha pago' to datetime
    df['fecha pago'] = pd.to_datetime(df['fecha pago'])
    # Group by date and sum 'total'
    df_grouped = df.groupby(df['fecha pago'].dt.date)['total'].sum().reset_index()

    min_date = df['fecha pago'].min()
    max_date = df['fecha pago'].max()

    today = dt.today()
    one_month_ago = today - timedelta(days=30)

    date_picker_div = html.Div([
        dcc.DatePickerRange(
            id='date-picker-range',
            min_date_allowed=min_date,
            max_date_allowed=max_date,
            start_date=one_month_ago,
            end_date=today,
            display_format='DD/MM/YYYY',
        )
    ], style={'margin-left': '32px', 'margin-right': '32px'})

    graph_div = html.Div([
        html.Div([
            dcc.Graph(id='bar-chart')
        ], style={'padding': '24px'})
    ], style={'margin-left': '32px', 'margin-right': '32px', 'margin-top': '32px', 'border-radius': '8px', 'background-color': '#ffffff'})

    # Create a table
    table = html.Table([
        html.Thead([
            html.Tr([html.Th(col) for col in df.columns])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col], style={
                    'height': '62px',  # Set the height of the row
                    'border-bottom': '0.5px solid #999'
                }) for col in df.columns
            ]) for i in range(len(df))
        ])
    ])

    table_div = html.Div([
        html.Div(table, id='table-div', style={
            'height': '533px',
            'overflow': 'auto',
        })
    ], style={
        'margin': '32px',
        'padding': '24px',
        'background-color': '#ffffff',
        'border-radius': '8px'
    })

    return date_picker_div, graph_div, table_div

@app.callback(
    [Output('bar-chart', 'figure'),
     Output('table-div', 'children')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_outputs(start_date, end_date):
    df = pd.read_csv('Ordenes.csv')
    df['fecha pago'] = pd.to_datetime(df['fecha pago'])

    # Convert start_date and end_date to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter data based on date range
    filtered_data = df[(df['fecha pago'] >= start_date) & (df['fecha pago'] <= end_date)]

    # Group by date and sum 'total'
    df_grouped = filtered_data.groupby(filtered_data['fecha pago'].dt.date)['total'].sum().reset_index()

    # Create a bar chart
    fig = px.bar(df_grouped, x='fecha pago', y='total', color_discrete_sequence=['#26A6EE'])
    # Update layout to adjust margins
    fig.update_layout(
        autosize=True,
        height=500,  # Adjust this value as needed
        margin=dict(l=24, r=24, t=24, b=24, pad=0),
    )

    # Format 'total' as money and 'fecha pago' as date
    filtered_data['total'] = filtered_data['total'].map('${:,.2f}'.format)
    filtered_data['fecha pago'] = filtered_data['fecha pago'].dt.strftime('%d/%m/%Y')

    # Create a download button for each order
    filtered_data['Descarga'] = filtered_data['orden'].apply(lambda x: html.A('Download', href=f'/ordenes/{x}.pdf', download='', target='_blank'))

    # Define a function to create a status element
    def create_status_element(status):
        colors = {
            "Completo": {"background": "rgba(230, 248, 243, 1)", "text": "#22282A"},
            "Proceso": {"background": "rgba(253, 245, 216, 1)", "text": "#22282A"},
            "Cancelado": {"background": "rgba(255, 242, 242, 1)", "text": "#22282A"},
        }
        return html.Div(status, style={
            'width': '98px',
            'height': '30px',
            'border-radius': '8px',
            'background-color': colors[status]["background"],
            'color': colors[status]["text"],
            'text-align': 'center',
            'line-height': '30px'
        })

    # Replace 'status' column with HTML elements
    filtered_data['status'] = filtered_data['status'].apply(create_status_element)

    # Add calendar icon to 'fecha pago'
    filtered_data['fecha pago'] = filtered_data['fecha pago'].apply(lambda x: html.Div([
        html.Img(src='assets/calendar.svg', style={'height': '16px', 'margin-right': '8px'}),
        x
    ]))

    # Create a table
    table = html.Table([
        html.Thead([
            html.Tr([html.Th(col) for col in filtered_data.columns])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(filtered_data.iloc[i][col], style={
                    'height': '62px',  # Set the height of the row
                    'border-bottom': '0.5px solid #999'  # Add border-bottom style
                }) for col in filtered_data.columns
            ]) for i in range(len(filtered_data))
        ])
    ], style={'width': '100%'})  # Set the width of the table to 100%

    return fig, table