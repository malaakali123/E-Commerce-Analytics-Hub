import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Initialize app with a modern theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE], meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
])
server = app.server

# Custom CSS for Glassmorphism and specialized styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Amazon Sales Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            .card {
                border-radius: 15px;
                background: rgba(40, 44, 52, 0.95);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: white;
                margin-bottom: 20px;
            }
            .main-header {
                font-family: 'Inter', sans-serif;
                font-weight: 700;
                color: #fff;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                padding: 20px 0;
            }
            .kpi-value {
                font-size: 2.5rem;
                font-weight: bold;
                background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .kpi-title {
                text-transform: uppercase;
                letter-spacing: 1.5px;
                font-size: 0.85rem;
                opacity: 0.8;
            }
            .control-panel {
                background: rgba(30, 33, 40, 0.9);
                padding: 20px;
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
             .Select-control {
                background-color: #323842 !important;
                border-color: #4e555e !important;
                color: white !important;
            }
            .Select-menu-outer {
                background-color: #323842 !important;
                 color: white !important;
            }
            .Select-value-label {
                 color: white !important;
            }
            body {
                background-color: #1e2126;
                color: #e0e0e0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Load Data
DATA_PATH = os.path.join(os.path.dirname(__file__), 'cleaned_data', 'cleaned_Amazon-Sale-Report.csv')

try:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
except Exception as e:
    print(f"Error loading data: {e}")
    df = pd.DataFrame(columns=['Date', 'Amount', 'Category', 'ship-state', 'Month', 'Status'])

# --- Components ---

def create_card(title, id_value):
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, className="kpi-title"),
            html.P("Loading...", id=id_value, className="kpi-value"),
        ])
    )

# --- Layout ---
app.layout = dbc.Container([
    
    html.Div([
        html.H1("🚀 E-Commerce Analytics Hub", className="text-center main-header"),
        html.P("Interactive Insights & Performance Metrics", className="text-center text-muted", style={'marginBottom': '40px'})
    ]),

    dbc.Tabs([
        # TAB 1: DASHBOARD
        dbc.Tab(label="📊 Live Dashboard", tab_id="tab-dashboard", children=[
            html.Br(),
            # Control Panel
            dbc.Card([
                dbc.CardBody([
                     dbc.Row([
                        dbc.Col([
                            html.Label("📅 Filter by Month", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id='month-dropdown',
                                options=[{'label': m, 'value': m} for m in sorted(df['Month'].dropna().unique())],
                                multi=True,
                                placeholder="All Months",
                                className="black-dropdown"
                            )
                        ], md=3, sm=12),
                        
                        dbc.Col([
                            html.Label("📦 Product Categories", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id='category-dropdown',
                                options=[{'label': c, 'value': c} for c in sorted(df['Category'].dropna().unique())],
                                multi=True,
                                placeholder="All Categories"
                            )
                        ], md=3, sm=12),

                        dbc.Col([
                            html.Label("🌍 Regions (State)", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id='region-dropdown',
                                options=[{'label': r, 'value': r} for r in sorted(df['ship-state'].dropna().unique())],
                                multi=True,
                                placeholder="All States"
                            )
                        ], md=3, sm=12),
                        
                         dbc.Col([
                            html.Label("Apply Filters", className="fw-bold mb-2", style={'visibility': 'hidden'}), # Spacer
                            dbc.Button("Update Dashboard ⚡", id="submit-button", color="primary", className="w-100", size="lg")
                        ], md=3, sm=12, className="d-flex align-items-end")
                    ])
                ])
            ], className="control-panel mb-5"),

            # KPIs
            dbc.Row([
                dbc.Col(create_card("Total Revenue", "total-sales"), md=3, sm=6),
                dbc.Col(create_card("Total Orders", "total-orders"), md=3, sm=6),
                dbc.Col(create_card("Avg. Order Value", "avg-order-value"), md=3, sm=6),
                dbc.Col(create_card("Top Selling Category", "top-category"), md=3, sm=6),
            ], className="mb-4"),

            # Charts Row 1
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Loading(dcc.Graph(id='sales-trend', config={'displayModeBar': False}))), md=8),
                dbc.Col(dbc.Card(dcc.Loading(dcc.Graph(id='status-pie', config={'displayModeBar': False}))), md=4),
            ]),

            # Charts Row 2
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Loading(dcc.Graph(id='category-bar', config={'displayModeBar': False}))), md=6),
                dbc.Col(dbc.Card(dcc.Loading(dcc.Graph(id='region-map', config={'displayModeBar': False}))), md=6),
            ]),
        ]),

        # TAB 2: INSIGHTS REPORT
        dbc.Tab(label="🧠 Business Intelligence Analysis", tab_id="tab-insights", children=[
            html.Br(),
            dbc.Container([
                
                # Section 1: Overall Verdict
                dbc.Alert([
                    html.H4("📉 Overall Trend: Declining (Action Required)", className="alert-heading"),
                    html.P("Sales have peaked in April (~28.8M) and have shown a consistent decline through June (~23.4M). While revenue remains substantial, this -18% drop over 3 months suggests post-season cooling or retention issues."),
                ], color="danger", className="mb-4"),

                dbc.Row([
                    # Section 2: Reasons
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("❓ Why is this happening?", className="bg-warning text-dark fw-bold"),
                            dbc.CardBody([
                                html.Ul([
                                    html.Li([html.Strong("Peak Season End: "), "April was likely the start of a seasonal campaign (Summer Sale), leading to a natural dip in subsequent months."]),
                                    html.Li([html.Strong("High Cancellation Rate (~13%): "), "Over 1/10th of all orders are cancelled. This is a critical revenue leak."]),
                                    html.Li([html.Strong("Logistics Gaps: "), "Long delivery times for Merchant-fulfilled orders are driving cancellations."]),
                                    html.Li([html.Strong("Product Concentration: "), "Revenue is heavily reliable on just 2 categories (Sets & Kurtas)."])
                                ])
                            ])
                        ], className="h-100")
                    ], md=6),

                    # Section 3: Recommendations
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("🚀 Actionable Strategies", className="bg-success text-white fw-bold"),
                            dbc.CardBody([
                                dbc.ListGroup([
                                    dbc.ListGroupItem([
                                        html.Div([
                                            html.H5("1. Fix Cancellations", className="mb-1"),
                                            html.P("Audit size charts and product images. Shift effective inventory to FBA (Fulfilled by Amazon) for faster delivery.", className="mb-1 text-muted small")
                                        ])
                                    ]),
                                    dbc.ListGroupItem([
                                        html.Div([
                                            html.H5("2. Counter-Seasonal Sales", className="mb-1"),
                                            html.P("Launch a 'Mid-Year Clearance' in June/July to flatten the sales curve and clear slow-moving stock.", className="mb-1 text-muted small")
                                        ])
                                    ]),
                                    dbc.ListGroupItem([
                                        html.Div([
                                            html.H5("3. Regional Ad Targeting", className="mb-1"),
                                            html.P("Focus 80% of ad spend on top performing states (Maharashtra, Karnataka) to maximize ROI.", className="mb-1 text-muted small")
                                        ])
                                    ]),
                                ], flush=True)
                            ])
                        ], className="h-100")
                    ], md=6),
                ], className="mb-4"),

                # Section 4: Deep Dive Data
                dbc.Card([
                    dbc.CardHeader("📊 Key Data Points"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([html.H3("13.2%"), html.Small("Cancellation Rate")], className="text-center border-end"),
                            dbc.Col([html.H3("April"), html.Small("Peak Month")], className="text-center border-end"),
                            dbc.Col([html.H3("Sets & Kurtas"), html.Small("Top Categories")], className="text-center"),
                        ])
                    ])
                ])

            ], style={'maxWidth': '1000px'})
        ]),
    ])

], fluid=True, style={'padding': '30px'})


# --- Callbacks ---
@app.callback(
    [Output('total-sales', 'children'),
     Output('total-orders', 'children'),
     Output('avg-order-value', 'children'),
     Output('top-category', 'children'),
     Output('sales-trend', 'figure'),
     Output('category-bar', 'figure'),
     Output('status-pie', 'figure'),
     Output('region-map', 'figure')],
    [Input('submit-button', 'n_clicks')],
    [State('month-dropdown', 'value'),
     State('category-dropdown', 'value'),
     State('region-dropdown', 'value')]
)
def update_dashboard(n_clicks, selected_months, selected_categories, selected_regions):
    # Default to showing everything on first load
    # Triggers on load because n_clicks is None (or 0) initially? 
    # Actually Dash triggers initial call with None.
    
    filtered_df = df.copy()
    
    if selected_months:
        filtered_df = filtered_df[filtered_df['Month'].isin(selected_months)]
    if selected_categories:
        filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]
    if selected_regions:
        filtered_df = filtered_df[filtered_df['ship-state'].isin(selected_regions)]
        
    # KPIs
    total_sales = filtered_df['Amount'].sum()
    total_orders = len(filtered_df)
    avg_order = total_sales / total_orders if total_orders > 0 else 0
    top_cat = filtered_df['Category'].mode()[0] if not filtered_df.empty else "N/A"
    
    # Common Template
    template = "plotly_dark"

    # 1. Sales Trend
    if not filtered_df.empty:
        daily_sales = filtered_df.groupby('Date')['Amount'].sum().reset_index()
        fig_trend = px.line(daily_sales, x='Date', y='Amount', title='Daily Sales Trend', template=template)
        fig_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        fig_trend.update_traces(line=dict(color='#00d2ff', width=3))
    else:
        fig_trend = px.line(title='No Data', template=template)

    # 2. Category Bar
    if not filtered_df.empty:
        cat_sales = filtered_df.groupby('Category')['Amount'].sum().reset_index().sort_values('Amount', ascending=False)
        fig_cat = px.bar(cat_sales, x='Category', y='Amount', title='Sales by Category', template=template)
        fig_cat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        fig_cat.update_traces(marker_color='#3a7bd5')
    else:
        fig_cat = px.bar(title='No Data', template=template)
        
    # 3. Status Pie
    if not filtered_df.empty:
        status_counts = filtered_df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig_pie = px.pie(status_counts, values='Count', names='Status', title='Order Status Distribution', template=template)
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    else:
        fig_pie = px.pie(title='No Data', template=template)
        
    # 4. Region Map (Top 10 States Horizontal Bar)
    if not filtered_df.empty:
        state_sales = filtered_df.groupby('ship-state')['Amount'].sum().reset_index().sort_values('Amount', ascending=False).head(10)
        fig_map = px.bar(state_sales, x='Amount', y='ship-state', orientation='h', title='Top 10 States by Revenue', template=template)
        fig_map.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), yaxis=dict(autorange="reversed"))
        fig_map.update_traces(marker_color='#00d2ff')
    else:
        fig_map = px.bar(title='No Data', template=template)

    return (
        f"${total_sales:,.0f}",
        f"{total_orders:,}",
        f"${avg_order:,.0f}",
        str(top_cat),
        fig_trend,
        fig_cat,
        fig_pie,
        fig_map
    )

if __name__ == '__main__':
    app.run(debug=True, port=8050)
