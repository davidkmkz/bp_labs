import pandas as pd
from datetime import datetime as dt, timedelta
from dash import dcc, html, Dash
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px


from server import app  # Import the app from server.py

#custom_color_scale = ["#effbff", "#def5ff", "#b6efff","#75e5ff","#2cd8ff","#00beef","#009ed4","#007eab","#006a8d","#065874","#04384d"]
custom_color_scale = ["#f1f8fe","#e1f1fd","#bde2fa","#82cbf7","#26a6ee","#1797e0","#0a77bf","#0a5f9a","#0c5180","#10446a","#0b2b46"]

# Load the data
data = pd.read_csv('Asofarma.csv')
data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')  # Adjust the format as per your data

def layout():
    global data
    min_date = data['date'].min()
    max_date = data['date'].max()

    today = dt.today()
    one_month_ago = today - timedelta(days=30)

    return html.Div([
        html.Link(href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css', rel='stylesheet'),
        html.Div([
            dcc.Dropdown(
                id='product-dropdown',
                options=[{'label': 'Todos los medicamentos', 'value': 'all'}] + sorted([{'label': i, 'value': i} for i in data['nombre'].unique()], key=lambda x: x['label']),
                value='all',
            ),
            dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                start_date=one_month_ago,
                end_date=today,
                display_format='DD/MM/YYYY',
            ),
            dbc.ButtonGroup([
                dbc.Button("Mes", id="btn-month", color="primary"),
                dbc.Button("Quincena", id="btn-fortnight", color="primary"),
                dbc.Button("Semana", id="btn-week", color="primary"),
                dbc.Button("Día", id="btn-day", color="primary"),
            ], className="mr-1"),
        ], id='dropdown-date-picker'),
        html.Div([
            html.Div([
                html.P('Ingresos generados durante el periodo', style={'margin-left':'24px', 'margin-top':'24px', 'color':'#2C2C2C', 'font-family':'Lato', 'font-size':'22px', 'font-weight':'700'}),
                html.I(id='income-period-info', className='fas fa-info-circle fa-2x', style={'font-size': '1.2em', 'position': 'absolute', 'right': '0', 'bottom': '0'}),
                dbc.Tooltip(
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque nec placerat tellus. Nulla ultrices, sem at blandit maximus, eros massa scelerisque orci, et porta orci lacus non sem.",
                    target='income-period-info',  # The id of the element the tooltip is for
                    placement='left'
                ),
                dcc.Graph(
                    id='line-chart',
                    style={'height': '80%', 'width': '94%', 'margin-left': '24px', 'margin-right': '24px'}
                ),
            ], id='line-chart-container', style={'position': 'relative'}),
            html.Div([
                html.Div([
                    html.Img(src='assets/ventas_icons/ingresos.svg', style={'height':'44px', 'width':'44px', 'margin-top':'24px', 'margin-left':'24px'}),
                    html.P('Ingresos totales', style={'margin-left':'24px', 'margin-top':'16px', 'color':'#2C2C2C', 'font-family':'Lato', 'font-size':'16px', 'font-weight':'600'}),
                    html.P(id='total-precio-lab', style={'margin-left':'24px', 'margin-top':'24px', 'color':'#2C2C2C', 'font-family':'Lato', 'font-size':'20px', 'font-weight':'800'}),
                    html.I(id='circle-info', className='fas fa-info-circle fa-2x', style={'font-size': '1.2em', 'position': 'absolute', 'right': '0', 'bottom': '0'}),
                ], id='div1', style={'position': 'relative'}),
                dbc.Tooltip(
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque nec placerat tellus. Nulla ultrices, sem at blandit maximus, eros massa scelerisque orci, et porta orci lacus non sem.",
                    target='circle-info',  # The id of the element the tooltip is for
                    placement='left'
                ),

                html.Div([
                    html.Img(src='assets/ventas_icons/ordenes.svg', style={'height':'44px', 'width':'44px', 'margin-top':'24px', 'margin-left':'24px'}),
                    html.P('Ordenes totales', style={'margin-left':'24px', 'margin-top':'16px', 'color':'#2C2C2C', 'font-family':'Lato', 'font-size':'16px', 'font-weight':'600'}),
                    html.P(id='total-order', style={'margin-left':'24px', 'margin-top':'24px', 'color':'#2C2C2C', 'font-family':'Lato', 'font-size':'20px', 'font-weight':'800'}),
                    html.I(id='orders-info', className='fas fa-info-circle fa-2x', style={'font-size': '1.2em', 'position': 'absolute', 'right': '0', 'bottom': '0'}),
                ], id='div2', style={'position': 'relative'}),
                dbc.Tooltip(
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque nec placerat tellus. Nulla ultrices, sem at blandit maximus, eros massa scelerisque orci, et porta orci lacus non sem.",
                    target='orders-info',  # The id of the element the tooltip is for
                    placement='left'
                ),
                
                html.Div([
                    html.Img(src='assets/ventas_icons/carrito.svg', style={'height':'44px', 'width':'44px', 'margin-top':'24px', 'margin-left':'24px'}),
                    html.P('Veces agregardo al carrito', style={'margin-left':'24px', 'margin-top':'16px', 'color':'#2C2C2C', 'font-family':'Lato', 'font-size':'16px', 'font-weight':'600'}),
                    html.P(id='total-basket', style={'margin-left':'24px', 'margin-top':'24px', 'color':'#2C2C2C', 'font-family':'Lato', 'font-size':'20px', 'font-weight':'800'}),
                    html.I(id='basket-info', className='fas fa-info-circle fa-2x', style={'font-size': '1.2em', 'position': 'absolute', 'right': '0', 'bottom': '0'}),
                ], id='div3', style={'position': 'relative'}),

                dbc.Tooltip(
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque nec placerat tellus. Nulla ultrices, sem at blandit maximus, eros massa scelerisque orci, et porta orci lacus non sem.",
                    target='basket-info',  # The id of the element the tooltip is for
                    placement='left'
                ),

                html.Div([
                    html.Img(src='assets/ventas_icons/clicks.svg', style={'height':'44px', 'width':'44px', 'margin-top':'24px', 'margin-left':'24px'}),
                    html.P('Clicks en producto', style={'margin-left':'24px', 'margin-top':'16px', 'color':'#2C2C2C', 'font-family':'Lato', 'font-size':'16px', 'font-weight':'600'}),
                    html.P(id='total-click', style={'margin-left':'24px', 'margin-top':'24px', 'color':'#2C2C2C', 'font-family':'Lato', 'font-size':'20px', 'font-weight':'800'}),
                    html.I(id='clicks-info', className='fas fa-info-circle fa-2x', style={'font-size': '1.2em', 'position': 'absolute', 'right': '0', 'bottom': '0'}),
                ], id='div4', style={'position': 'relative'}),

                dbc.Tooltip(
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque nec placerat tellus. Nulla ultrices, sem at blandit maximus, eros massa scelerisque orci, et porta orci lacus non sem.",
                    target='clicks-info',  # The id of the element the tooltip is for
                    placement='left'
                ),
            ], id='div-container')
        ], id='graph-div-container'),
        html.Div([
            html.Div([
                dcc.Graph(
                    id='map',
                ),
                html.I(id='map-info', className='fas fa-info-circle fa-2x', style={'font-size': '1.2em', 'position': 'absolute', 'right': '0', 'bottom': '0'}),
                dbc.Button("Abrir mapa", id="open-map-button", className="mt-2"),  # Add a button
            ], id='map-container', style={'position': 'relative'}),

            dbc.Modal(  # Add a modal
                [
                    dbc.ModalHeader("Map"),
                    dbc.ModalBody(dcc.Graph(id='map-popup', style={'height': '80%', 'width': '100%'})),
                    dbc.ModalFooter(
                        dbc.Button("Cerrar", id="close-map-button", className="ml-auto")
                    ),
                ],
                id="map-modal",
                className="large-modal",  # Set the size of the modal
                centered=True,  # Center the modal vertically in the page
            ),

            dbc.Tooltip(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque nec placerat tellus. Nulla ultrices, sem at blandit maximus, eros massa scelerisque orci, et porta orci lacus non sem.",
                target='map-info',  # The id of the element the tooltip is for
                placement='left',
            ),
            html.Div([
                dash_table.DataTable(
                    id='zona-order-table',
                    columns=[{"name": "#", "id": "position"}, {"name": "Ubicación", "id": "zona"}, {"name": "Ordenes", "id": "ordenes"}],
                    style_table={'overflowX': 'auto', 'maxHeight': '390px', 'overflowY': 'auto'},
                    style_data={
                        'height': '42px',  # Adjust the height here
                        'borderBottom': '1px solid #E1E1E1'  # Add a border to the bottom of each cell
                    },
                    style_cell={
                        'minWidth': '50px', 
                        'width': '50px', 
                        'maxWidth': '50px', 
                        'whiteSpace': 'normal',
                        'border': 'none',  # Remove the lines around the table
                        'font-size': '14px',  # Set the font size
                        'font-family': 'Lato'  # Set the font family
                    },
                    style_header={
                        'border': 'none',  # Remove the column lines
                        'backgroundColor': 'white',  # Set the background color to white
                    },
                    style_cell_conditional=[
                        {'if': {'column_id': 'position'}, 'width': '10%', 'textAlign': 'center', 'margin-right': '10px'},  # Adjust the width here
                        {'if': {'column_id': 'zona'}, 'width': '70%', 'textAlign': 'left', 'padding-left': '30px'},  # Add padding to the left side of the "zona" column
                        {'if': {'column_id': 'ordenes'}, 'width': '20%', 'textAlign': 'center'}
                    ],
                    style_data_conditional=[
                        {
                            'if': {'column_id': 'position'},
                            'color': '{color}'
                        },
                        {
                            'if': {
                                'filter_query': '{position} lt 5'  # Change the number as per your requirement
                            },
                            'color': 'white'
                        }
                    ],
                    css=[{
                        'selector': '.dash-cell div.dash-cell-value',
                        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                    }],
                ), 
            ], id='empty-div', style={'padding': '24px'}),
        ], id='map-empty-div-container'),
        html.Div([
            dcc.Graph(
                id='new-line-chart',
            ),
        ], id='new-row'),
    ], className='my-layout')

@app.callback(
    Output('date-picker-range', 'start_date'),
    Output('date-picker-range', 'end_date'),
    Input('btn-month', 'n_clicks'),
    Input('btn-fortnight', 'n_clicks'),
    Input('btn-week', 'n_clicks'),
    Input('btn-day', 'n_clicks'),
    prevent_initial_call=True,
)
def update_date_range(n_month, n_fortnight, n_week, n_day):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        today = dt.today()
        if button_id == 'btn-month':
            start_date = today - timedelta(days=30)
        elif button_id == 'btn-fortnight':
            start_date = today - timedelta(days=15)
        elif button_id == 'btn-week':
            start_date = today - timedelta(days=7)
        elif button_id == 'btn-day':
            start_date = today - timedelta(days=1)
        return start_date, today

@app.callback(
    [Output('total-precio-lab', 'children'),
     Output('total-order', 'children'),
     Output('total-basket', 'children'),
     Output('total-click', 'children')],
    [Input('product-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_totals(selected_product, start_date, end_date):
    global data
    if selected_product == 'all':
        filtered_data = data
    else:
        filtered_data = data[data['nombre'] == selected_product]

    # Convert start_date and end_date to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter data based on date range
    filtered_data = filtered_data[(filtered_data['date'] >= start_date) & (filtered_data['date'] <= end_date)]

    total_precio_lab = filtered_data['precio lab'].sum()
    total_order = filtered_data['order'].sum()
    total_basket = filtered_data['basket'].sum()
    total_click = filtered_data['click'].sum()

    return f'$ {total_precio_lab:,.2f}', f'{total_order:,}', f'{total_basket:,}', f'{total_click:,}'

@app.callback(
    Output('map', 'figure'),
    Input('product-dropdown', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)
def update_map(selected_product, start_date, end_date):
    global data
    if selected_product == 'all':
        filtered_data = data
    else:
        filtered_data = data[data['nombre'] == selected_product]

    # Convert start_date and end_date to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter data based on date range
    filtered_data = filtered_data[(filtered_data['date'] >= start_date) & (filtered_data['date'] <= end_date)]

    map_data = filtered_data.groupby(['latitude', 'longitude', 'map_dir'])['order'].sum().reset_index()
    map_fig = px.scatter_mapbox(map_data, lat="latitude", lon="longitude", hover_name="map_dir", size="order", zoom=10, height=425, color="order", color_continuous_scale=custom_color_scale)  # Add the color scale

    # Calculate the mean latitude and longitude
    lat_center = map_data['latitude'].mean()
    lon_center = map_data['longitude'].mean()

    map_fig.update_layout(
        mapbox_style="light", 
        mapbox_accesstoken="pk.eyJ1IjoiZGF2aWRhYW0iLCJhIjoiY2xkaTN0OGlvMHFpbTNvbGhwbzZjc3lmZSJ9.a2DecEMvPiLlurE98EdRWw", 
        mapbox=dict(
            center=dict(lat=lat_center, lon=lon_center),  # Center the map
            zoom=9  # Adjust the zoom level
        ),
        autosize=True, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        margin=dict(l=24, r=24, t=24, b=24)  # Adjust the margins here
    )

    return map_fig

@app.callback(
    Output("map-modal", "is_open"),
    [Input("open-map-button", "n_clicks"), Input("close-map-button", "n_clicks")],
    [State("map-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output('map-popup', 'figure'),
    Input('map-modal', 'is_open'),
    [State('product-dropdown', 'value'),
     State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date')]
)
def update_popup(is_open, selected_product, start_date, end_date):
    if is_open:
        return update_map(selected_product, start_date, end_date)  # Call the function that updates the map
    return dash.no_update

@app.callback(
    Output('zona-order-table', 'data'),
    Input('product-dropdown', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)
def update_table(selected_product, start_date, end_date):
    global data
    if selected_product == 'all':
        filtered_data = data
    else:
        filtered_data = data[data['nombre'] == selected_product]

    # Convert start_date and end_date to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter data based on date range
    filtered_data = filtered_data[(filtered_data['date'] >= start_date) & (filtered_data['date'] <= end_date)]

    # Prepare data for the table
    table_data = filtered_data.groupby('map_dir')['order'].sum().reset_index()
    table_data.columns = ['zona', 'ordenes']

    # Sort the table data from more to less orders
    table_data = table_data.sort_values('ordenes', ascending=False)

    # Limit to top 10
    table_data = table_data.head(10)

    # Add a new column with the position of the zone
    table_data = table_data.reset_index(drop=True)
    table_data['position'] = table_data.index + 1

    return table_data[['position', 'zona', 'ordenes']].to_dict('records')

@app.callback(
    Output('zona-order-table', 'style_data_conditional'),
    Input('zona-order-table', 'data')
)
def update_styles(data):
    reversed_colors = custom_color_scale[::-1]  # Reverse the color list
    styles = []
    for i in range(len(data)):
        color = reversed_colors[i % len(reversed_colors)]
        # Calculate brightness of the color to decide whether to use black or white text
        r, g, b = [int(color[i:i+2], 16) for i in (1, 3, 5)]  # Convert hex color to RGB
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        text_color = '#000000' if brightness > 125 else '#ffffff'  # Black for bright colors, white for dark colors
        style = {
            'if': {'column_id': 'position', 'filter_query': '{{position}} = {pos}'.format(pos=data[i]['position'])},
            'backgroundColor': color,
            'color': text_color,
        }
        styles.append(style)
    return styles

@app.callback(
    Output('line-chart', 'figure'),
    Input('product-dropdown', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)
def update_line_chart(selected_product, start_date, end_date):
    global data
    if selected_product == 'all':
        filtered_data = data
    else:
        filtered_data = data[data['nombre'] == selected_product]

    # Convert start_date and end_date to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter data based on date range
    filtered_data = filtered_data[(filtered_data['date'] >= start_date) & (filtered_data['date'] <= end_date)]

    # Prepare data for the line chart
    line_data = filtered_data.groupby('date')['precio lab'].sum().reset_index()

    line_chart = go.Figure(data=go.Scatter(x=line_data['date'], y=line_data['precio lab'], mode='lines', line_shape='spline', line=dict(color='#26A6EE'), fill='tozeroy', fillcolor='rgba(38, 166, 238, 0.5)'))
    line_chart.update_layout(
        autosize=True, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=24, r=24, t=24, b=24),  # Adjust the margins here
    )
    line_chart.update_yaxes(ticksuffix=" ")
    line_chart.update_layout(margin_pad=8)

    return line_chart

@app.callback(
    Output('new-line-chart', 'figure'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)
def update_new_line_chart(start_date, end_date):
    global data

    # Convert start_date and end_date to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter data based on date range
    filtered_data = data[(data['date'] >= start_date) & (data['date'] <= end_date)]

    # Prepare data for the new line chart
    new_line_data = filtered_data.groupby(['date', 'nombre'])['order'].sum().reset_index()

    # Create a line chart with different colors for each product
    new_line_chart = go.Figure()

    for i, product in enumerate(new_line_data['nombre'].unique()):
        product_data = new_line_data[new_line_data['nombre'] == product]
        # Split the product name into two lines at the middle space
        spaces = [i for i, char in enumerate(product) if char == ' ']
        if spaces:
            middle_space = spaces[len(spaces)//2]
            product_name = product[:middle_space] + '<br>' + product[middle_space+1:]
        else:
            product_name = product
        if i == 0:  # Make the first line visible
            new_line_chart.add_trace(go.Scatter(x=product_data['date'], y=product_data['order'], mode='lines', name=product_name, line_shape='spline'))
        else:  # Make other lines visible only when clicked on in the legend
            new_line_chart.add_trace(go.Scatter(x=product_data['date'], y=product_data['order'], mode='lines', name=product_name, line_shape='spline', visible='legendonly'))

    new_line_chart.update_layout(autosize=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return new_line_chart