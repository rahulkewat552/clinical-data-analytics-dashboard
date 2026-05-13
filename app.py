import dash
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, html
import plotly.express as px
import os
import base64
import sqlite3
from contextlib import contextmanager


# DATABASE CONNECTION MANAGER

@contextmanager
def get_db_connection():
    """Context manager for database connections (auto-closes)"""
    conn = sqlite3.connect('data/healthcare.db')
    try:
        yield conn
    finally:
        conn.close()

def load_data_from_sql():
    """
    Load initial data from SQLite database
    Returns DataFrame with same structure as before
    """
    with get_db_connection() as conn:
        # Read entire dataset (same as CSV approach)
        df = pd.read_sql_query("SELECT * FROM healthcare", conn)
        
        # Convert date columns back to datetime (SQLite stores as strings)
        df["Date of Admission"] = pd.to_datetime(df["Date of Admission"])
        df["Discharge Date"] = pd.to_datetime(df["Discharge Date"], errors='coerce')
        
        # Ensure YearMonth is in Period format (matching original)
        df["YearMonth"] = pd.PeriodIndex(df["YearMonth"], freq='M')
        
        return df

# Load initial data
data = load_data_from_sql()

# Calculate metrics using SQL (more efficient than pandas)
def get_metrics():
    """Get aggregated metrics using SQL queries"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total records
        cursor.execute("SELECT COUNT(*) FROM healthcare")
        num_records = cursor.fetchone()[0]
        
        # Average billing amount
        cursor.execute("SELECT AVG(\"Billing Amount\") FROM healthcare")
        avg_billing = cursor.fetchone()[0] or 0
        
        return num_records, avg_billing

num_records, avg_billing = get_metrics()


# DASH APP INITIALIZATION


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "assets/style.css"])


# APP LAYOUT 


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Healthcare Dashboard"), width=12, className="text-center my-5")
    ]),
    dbc.Row([
        dbc.Col(html.Div(f"Total Patient Records: {num_records}", className="text-center my-3 top-text"), width=12),
        dbc.Col(html.Div(f"Average Billing Amount: {avg_billing:,.2f}", className="text-center my-3 top-text"), width=12)
    ], className="mb-5"),

    # showing age distribution based gender
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Patient Demographics", className="card-title"),
                    dcc.Dropdown(
                        options=[{"label": gender, "value": gender} for gender in data["Gender"].unique()], 
                        value=None, 
                        placeholder="Select a Gender", 
                        id="gender-filter"
                    ),
                    dcc.Graph(id="age-distribution")
                ])
            ])
        ], width=6),

        # showing medical condition percentages (pie chart)
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H4("Medical Condition Distribution", className="card-title"),
                    dcc.Graph(id="condition-distribution")
                ]),
                className="special-card"
            )
        ], width=6)  
    ]),
 
    # added Graph to show Insurance Provider Data
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Insurance Provider Comparison", className="card-title"),
                    dcc.Graph(id="insurance-comparison")
                ])
            ])
        ], width=12)
    ]),
    
    # graph to show billing amount distribution with a slider
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Billing Amount Distribution", className="card-title"),
                    dcc.Slider(
                        id="billing-slider", 
                        min=data["Billing Amount"].min(), 
                        max=data["Billing Amount"].max(), 
                        value=data["Billing Amount"].median(), 
                        marks={int(value): f"${int(value):,}" for value in data["Billing Amount"].quantile([0,0.25,0.5,0.75,1]).values}, 
                        step=100
                    ),
                    dcc.Graph(id="billing-distribution")
                ])
            ])
        ], width=12)
    ]),
    
    ## graph to display the trends in admission
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Trends in Admission", className="card-title"),
                    dcc.RadioItems(
                        options=[{"label": "Line Chart", 'value': 'line'}, {"label": "Bar Chart", 'value': 'bar'}], 
                        value='line', 
                        inline=True, 
                        className='mb-4 my-radio', 
                        id="chart-type"
                    ),
                    dcc.Dropdown(
                        id="condition-filter", 
                        options=[{'label': condition, 'value': condition} for condition in data["Medical Condition"].unique()], 
                        value=None, 
                        placeholder="Select a Medical Condition"
                    ),
                    dcc.Graph(id="admission-trends")
                ])
            ])
        ], width=12)
    ]),
    
    ## File upload section ( CSV upload feature)
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-data', 
                children=html.Div(['Drag and Drop or', html.A('Select Files')]), 
                style={
                    'width': 'auto', 'height': '100px', 'lineHeight': '100px', 
                    'borderWidth': '1px', 'borderStyle': 'dashed', 
                    'textAlign': 'center', 'margin': '10px'
                }, 
                multiple=False
            ),
            html.Div(id='output-data')
        ])
    ])
], fluid=True)


## CALLBACK

@app.callback(
    Output(component_id="age-distribution", component_property="figure"),
    Input(component_id="gender-filter", component_property="value")
)
def update_distribution(selected_gender):
    """Show age distribution by gender using SQL filtering"""
    with get_db_connection() as conn:
        if selected_gender:
            # Use parameterized query to prevent SQL injection
            query = "SELECT Age, Gender FROM healthcare WHERE Gender = ?"
            filtered_df = pd.read_sql_query(query, conn, params=[selected_gender])
        else:
            query = "SELECT Age, Gender FROM healthcare"
            filtered_df = pd.read_sql_query(query, conn)
    
    if filtered_df.empty:
        return {}
    
    fig = px.histogram(
        filtered_df, 
        x="Age", 
        color="Gender", 
        title="Age Distribution by Gender", 
        color_discrete_sequence=["#636EFA", "#EF553B"]
    )
    return fig

@app.callback(
    Output(component_id="condition-distribution", component_property="figure"),
    Input(component_id="gender-filter", component_property="value")
)
def update_medical_condition(selected_gender):
    """Show medical condition distribution using SQL"""
    with get_db_connection() as conn:
        if selected_gender:
            query = "SELECT \"Medical Condition\" FROM healthcare WHERE Gender = ?"
            filtered_df = pd.read_sql_query(query, conn, params=[selected_gender])
        else:
            query = "SELECT \"Medical Condition\" FROM healthcare"
            filtered_df = pd.read_sql_query(query, conn)
    
    fig = px.pie(
        filtered_df, 
        names="Medical Condition", 
        title="Medical Condition Distribution"
    )
    return fig

@app.callback(
    Output(component_id="insurance-comparison", component_property="figure"),
    Input(component_id="gender-filter", component_property="value")
)
def update_insurance(selected_gender):
    """Show insurance provider comparison using SQL aggregation"""
    with get_db_connection() as conn:
        if selected_gender:
            query = """
                SELECT "Insurance Provider", "Medical Condition", "Billing Amount" 
                FROM healthcare 
                WHERE Gender = ?
            """
            filtered_df = pd.read_sql_query(query, conn, params=[selected_gender])
        else:
            query = """
                SELECT "Insurance Provider", "Medical Condition", "Billing Amount" 
                FROM healthcare
            """
            filtered_df = pd.read_sql_query(query, conn)
    
    fig = px.bar(
        filtered_df, 
        x="Insurance Provider", 
        y="Billing Amount", 
        color="Medical Condition", 
        barmode="group", 
        title="Insurance Provided Price Comparison", 
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    return fig

@app.callback(
    Output(component_id="billing-distribution", component_property="figure"),
    Input(component_id="gender-filter", component_property="value"),
    Input(component_id="billing-slider", component_property="value")
)
def update_billing(selected_gender, slider_value):
    """Show billing distribution with amount filter using SQL"""
    with get_db_connection() as conn:
        if selected_gender:
            query = """
                SELECT "Billing Amount" 
                FROM healthcare 
                WHERE Gender = ? AND "Billing Amount" <= ?
            """
            filtered_df = pd.read_sql_query(query, conn, params=[selected_gender, slider_value])
        else:
            query = 'SELECT "Billing Amount" FROM healthcare WHERE "Billing Amount" <= ?'
            filtered_df = pd.read_sql_query(query, conn, params=[slider_value])
    
    fig = px.histogram(
        filtered_df, 
        x="Billing Amount", 
        nbins=10, 
        title="Billing Amount Distribution"
    )
    return fig

@app.callback(
    Output(component_id="admission-trends", component_property="figure"),
    Input(component_id="chart-type", component_property="value"),
    Input(component_id="condition-filter", component_property="value")
)
def update_admission_trends(chart_type, selected_condition):
    """
    Show admission trends using SQL GROUP BY for aggregation
    This is more efficient than pandas groupby for large datasets
    """
    with get_db_connection() as conn:
        if selected_condition:
            query = """
                SELECT YearMonth, COUNT(*) as Count 
                FROM healthcare 
                WHERE "Medical Condition" = ?
                GROUP BY YearMonth 
                ORDER BY YearMonth
            """
            trend_df = pd.read_sql_query(query, conn, params=[selected_condition])
        else:
            query = """
                SELECT YearMonth, COUNT(*) as Count 
                FROM healthcare 
                GROUP BY YearMonth 
                ORDER BY YearMonth
            """
            trend_df = pd.read_sql_query(query, conn)
    
    if trend_df.empty:
        return {}
    
    if chart_type == "line":
        fig = px.line(
            trend_df, 
            x="YearMonth", 
            y="Count", 
            title="Admission Trends over Time"
        )
    else:
        fig = px.bar(
            trend_df, 
            x="YearMonth", 
            y="Count", 
            title="Admission Trends over Time"
        )
    
    return fig

## File upload callback 
@app.callback(
    Output(component_id="output-data", component_property="children"),
    Input(component_id="upload-data", component_property="contents"),
    Input(component_id="upload-data", component_property="filename")
)
def save_file(contents, filename):
    """Handle CSV file upload (kept original functionality)"""
    if contents is None:
        return "No file uploaded yet."
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    upload_folder = os.path.join(os.getcwd(), "assets")
    os.makedirs(upload_folder, exist_ok=True)
    
    save_to_path = os.path.join(upload_folder, filename)
    with open(save_to_path, "wb") as f:
        f.write(decoded)
    
    return f"File '{filename}' uploaded and saved successfully in {os.getcwd()}!"

if __name__ == '__main__':
    app.run(debug=True)