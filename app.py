from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from server import app, server

# Import the modules for each page
import compras
import ventas
import inventario
import ecommerce

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#ffffff",
}

CONTENT_STYLE = {
    "margin-left": "16rem",
    "padding": "2rem 0rem",
    "background" : "#F5F5F5", 
}

sidebar = html.Div(
    [
        html.Img(src='assets/Logo_Buy_Pharma.svg', style={'height':'25px', 'width':'auto', 'margin-left':'20px'}),
        dbc.Nav(
            [
                dbc.NavLink([html.Img(src='assets/icons/compras-icon.svg', id='compras-icon', style={'width':'16px'}), " Compras BP"], href="/compras", id="compras-link", className="nav-link", style={"margin-top": "65px", "height": "55px"}),
                dbc.NavLink([html.Img(src='assets/icons/ventas-icon.svg', id='ventas-icon', style={'width':'16px'}), " Ventas"], href="/ventas", id="ventas-link", className="nav-link", style={"height": "55px"}),
                dbc.NavLink([html.Img(src='assets/icons/inventario-icon.svg', id='inventario-icon', style={'width':'16px'}), " Inventario"], href="/inventario", id="inventario-link", className="nav-link", style={"height": "55px"}),
                dbc.NavLink([html.Img(src='assets/icons/ecommerce-icon.svg', id='ecommerce-icon', style={'width':'16px'}), " Ecommerce"], href="/ecommerce", id="ecommerce-link", className="nav-link", style={"height": "55px"}),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)
content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content, html.Link(rel='stylesheet', href='/assets/style.css')], style={"background-color": "#F7F9FA"})

@app.callback(
    [Output(f"{page}-link", "active") for page in ["compras", "ventas", "inventario", "ecommerce"]],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False, False
    return [pathname == f"/{page}" for page in ["compras", "ventas", "inventario", "ecommerce"]]

@app.callback(
    [Output(f"{page}-icon", "src") for page in ["compras", "ventas", "inventario", "ecommerce"]],
    [Input("url", "pathname")],
)
def toggle_icon_src(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return [f"assets/icons/{page}-icon-selected.svg" if page == "compras" else f"assets/icons/{page}-icon.svg" for page in ["compras", "ventas", "inventario", "ecommerce"]]
    return [f"assets/icons/{page}-icon-selected.svg" if pathname == f"/{page}" else f"assets/icons/{page}-icon.svg" for page in ["compras", "ventas", "inventario", "ecommerce"]]

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/compras"]:
        return compras.layout()
    elif pathname == "/ventas":
        return ventas.layout()
    elif pathname == "/inventario":
        return inventario.layout()
    elif pathname == "/ecommerce":
        return ecommerce.layout()
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

if __name__ == "__main__":
    app.run_server(debug=True)
