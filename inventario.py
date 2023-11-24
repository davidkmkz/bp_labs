import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
from server import app  # assuming server.py is where your Dash app is initialized

# Load your data
df = pd.read_csv('Inventario_Asofarma.csv')

#custom_color_scale = ["#effbff", "#def5ff", "#b6efff","#75e5ff","#2cd8ff","#00beef","#009ed4","#007eab","#006a8d","#065874","#04384d"]
custom_color_scale = ["#f1f8fe","#e1f1fd","#bde2fa","#82cbf7","#26a6ee","#1797e0","#0a77bf","#0a5f9a","#0c5180","#10446a","#0b2b46"]

def layout():
    return html.Div([
        html.Div([
            dcc.Dropdown(
                id='product-dropdown',
                options=[{'label': 'Todos los medicamentos', 'value': 'all'}] + sorted([{'label': i, 'value': i} for i in df['nombre'].unique()], key=lambda x: x['label']),
                value='all',
            ),
        ], style={'marginBottom': '32px', 'marginLeft': '32px'}),  # separation from the heatmap and sidebar
        html.Div([
            html.Div(
                dcc.Graph(id='main-heatmap'),
                style={
                    'height': 'calc(100%)',  # subtract 24px from the height
                    'overflowY': 'scroll',  # make this div scrollable
                }
            )
        ], style={
            'height': 'calc(696px - 48px)',  # subtract 48px from the height
            'width': 'calc(100% - 64px)',  # 100% - 48px (left) - 48px (right)
            'marginLeft': '32px',  # separation from the sidebar
            'marginRight': '32px',  # separation from the end of the page
            'backgroundColor': '#ffffff',  # background color
            'padding': '24px',  # separation from the chart
            'border-radius' : '8px'
        }),
        dcc.Loading(
            id="loading",
            type="circle",
            children=[
                html.Div([
                    html.Div(
                        dcc.Graph(id='filtered-heatmap'),
                        style={
                            'height': 'calc(100%)',  # subtract 24px from the height
                            'overflowY': 'scroll',  # make this div scrollable
                        }
                    )
                ], style={
                    'height': 'calc(300px - 48px)',  # subtract 48px from the height
                    'width': 'calc(100% - 64px)',  # 100% - 48px (left) - 48px (right)
                    'marginLeft': '32px',  # separation from the sidebar
                    'marginRight': '32px',  # separation from the end of the page
                    'marginTop': '32px',  # separation from the first heatmap
                    'backgroundColor': '#ffffff',  # background color
                    'padding': '24px',  # separation from the chart
                    'border-radius' : '8px'
                })
            ]
        )
    ])

@app.callback(
    Output('main-heatmap', 'figure'),
    [Input('product-dropdown', 'value'),
     Input('main-heatmap', 'clickData')]
)
def update_main_heatmap(selected_product, clickData):
    if selected_product == 'all':
        filtered_df = df
    else:
        filtered_df = df[df['nombre'] == selected_product]

    z = filtered_df.pivot_table(values='existencia', index='nombre', columns='caducidad', aggfunc='sum').sort_index(ascending=True)

    # Custom function to split text into multiple lines
    def split_text(text, line_length=20):
        words = text.split(' ')
        lines = ['']
        for word in words:
            if len(lines[-1]) + len(word) > line_length:
                lines.append(word)
            else:
                lines[-1] += ' ' + word
        return '<br>'.join(lines)

    yaxis_labels = [split_text(label) for label in z.index]

    annotations = []
    for n, row in enumerate(yaxis_labels):
        for m, col in enumerate(z.columns):
            val = z.values[n][m]
            if pd.notnull(val):  # only add annotations when the value is not null
                # Use white text for dark cells and black for light cells
                text_color = 'white' if val > z.values.max()/2 else 'black'
                annotations.append(go.layout.Annotation(text=str(val), x=col, y=row, font=dict(color=text_color), showarrow=False))

    fig = go.Figure(data=go.Heatmap(z=z.values, x=z.columns, y=yaxis_labels, hoverinfo='text', colorscale=custom_color_scale, showscale=False, customdata=z.index.to_list()))
    fig_height = max(80*len(yaxis_labels) - 24, 10) if len(yaxis_labels) > 0 else 10  # ensure height is at least 10
    fig.update_layout(
        height=fig_height,
        annotations=annotations,
        xaxis_autorange='reversed',
        xaxis=dict(
            tickmode='array',
            tickvals=z.columns,
            ticktext=z.columns,
            side='top',  # Move x-axis to the top
            fixedrange=True  # Freeze x-axis
        ),
        yaxis=dict(
            autorange='reversed',  # Reverse y-axis
            fixedrange=True  # Freeze y-axis
        ),
        margin=dict(l=0, r=0, b=24, t=0),  # Add 24px bottom margin
        
    )

    fig.update_layout(margin_pad=8)

    return fig

@app.callback(
    Output('filtered-heatmap', 'figure'),
    [Input('main-heatmap', 'clickData')]
)
def update_filtered_heatmap(clickData):
    if clickData is None or 'points' not in clickData or len(clickData['points']) == 0 or 'y' not in clickData['points'][0] or 'x' not in clickData['points'][0]:
        return go.Figure()  # return empty figure if no cell is selected
    else:
        selected_nombre = clickData['points'][0]['y'].replace('<br>', ' ').strip()  # reverse the split_text function
        selected_caducidad = clickData['points'][0]['x']  # get the x-axis value from the main heatmap
        filtered_df = df[(df['nombre'] == selected_nombre) & (df['caducidad'] == selected_caducidad)]
        
        data = []
        for i, row in filtered_df.iterrows():
            color = custom_color_scale[i % len(custom_color_scale)]  # cycle through colors
            text_color = 'white' if i % len(custom_color_scale) > len(custom_color_scale)/2 else 'black'  # use white text for dark bars and black for light bars
            data.append(go.Bar(
                y=[row['almacen']], 
                x=[row['existencia']], 
                orientation='h',
                marker=dict(color=color),
                text=[str(row['existencia'])],
                textposition='auto',
                insidetextanchor='middle',
                textfont=dict(color=text_color)
            ))
        
        fig = go.Figure(data=data)
        fig.update_layout(
            height=max(80*len(filtered_df['almacen'].unique()) - 24, 10) if len(filtered_df['almacen'].unique()) > 0 else 10,  # subtract 24px from the height
            yaxis=dict(
                autorange='reversed',  # Reverse y-axis
                fixedrange=True  # Freeze y-axis
            ),
            margin=dict(l=0, r=0, b=24, t=0),  # Add 24px bottom margin
            plot_bgcolor='rgba(0,0,0,0)',  # Make the border transparent
            showlegend=False
        )        

        fig.update_layout(margin_pad=8)
        
        return fig