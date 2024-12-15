import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash.dependencies as dd
import numpy as np
# hyperparameter
color_scale = 'Burg'

file_path = "../data/dataset.csv"  # Path to your CSV file
data = pd.read_csv(file_path)
cities = pd.read_csv('../data/cities_with_continents.csv')
# Read the CSV file
csv_file = "../data/dataset2.csv"  # Replace with your CSV file name
df = pd.read_csv(csv_file)


# Initialize Dash app
app = dash.Dash(__name__)


result_new = pd.read_csv('../data/city_temp_extremes.csv')
data = pd.read_csv('../data/dataset.csv')  # Replace with actual weather data CSV

reshaped_data = pd.melt(
    data,
    id_vars=['city_name', 'year', 'mean_annual_temperature'],
    value_vars=['Drizzle', 'Moderate Rain', 'Snow fall'],
    var_name='weather',
    value_name='days'
)

reshaped_data = reshaped_data.reset_index(drop=True)
reshaped_data['year_group'] = (reshaped_data['year'] // 3) * 3
reshaped_data['year_group'] = reshaped_data['year_group'].astype(str) + "-" + (reshaped_data['year_group'] + 2).astype(str)

# Grouped data
grouped_data = reshaped_data.groupby(['city_name', 'year_group', 'weather']).agg({
    'days': 'sum',
    'mean_annual_temperature': 'mean'
}).reset_index()

# Add numerical weather mapping
weather_mapping = {weather: idx for idx, weather in enumerate(grouped_data['weather'].unique())}
grouped_data['weather_num'] = grouped_data['weather'].map(weather_mapping)
grouped_data['mean_annual_temperature'] = grouped_data['mean_annual_temperature'].round(2)




#D2
file_path = "../data/dataset.csv"  # Path to your CSV file
data = pd.read_csv(file_path)
# Read the CSV file
csv_file = "../data/dataset2.csv"  # Replace with your CSV file name
df = pd.read_csv(csv_file)
d_new = pd.read_csv('../data/datasetNEW.csv')
cities = pd.read_csv('../data/cities_with_continents.csv')
merged_df = pd.merge(d_new, cities, on='city_name')


z_min_max = {
    "Precipitation": {
        "min": merged_df['precipitation'].min() * 1000,
        "max": merged_df['precipitation'].max() * 1000
    },
    "shortwave_radiation": {
        "min": merged_df['shortwave_radiation'].min(),
        "max": merged_df['shortwave_radiation'].max()
    },
    "snowfall":{
         "min": merged_df['snowfall'].min(),
        "max": merged_df['snowfall'].max()
    },
    "sunshine":{
         "min": merged_df['sunshine'].min(),
        "max": merged_df['sunshine'].max()
    }
}


app.layout = html.Div([
    html.H1("GLOBAL WARMING DATASET"),
    html.Div([
    dcc.Graph(id='subplot-plot')]),
    html.Div([
        html.Div([
            html.Label("Select City"),
            dcc.Dropdown(
        id='city-dropdown',
        options=[{'label': city, 'value': city} for city in grouped_data['city_name'].unique()],
        value='Houston'
    ),
            dcc.Graph(id='surface-plot', style={"height": "550px"})
        ], style={'width': '49%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Select Metric"),
            dcc.Dropdown(
            id='metric-selector',
            options=[
                {'label': 'Precipitation', 'value': 'Precipitation'},
                {'label': 'Snowfall', 'value': 'snowfall'},
                {'label': 'Sunshine duration', 'value': 'sunshine'},
                {'label': 'Shortwave Radiation', 'value': 'shortwave_radiation'}
            ],
            value='Precipitation',  # Default selection
            clearable=False
        ),
            dcc.Graph(id='heatmap-bar-plot', style={"height": "600px"})
        ], style={'width': '49%', 'display': 'inline-block'})
    ])
])




# Create Surface Plot (Plot 1)
def create_surface_plot(city):
    city_data = df.query(f"city_name == '{city}'")
    city_data['Year'] = city_data['year_month'].str[:4].astype(int)
    city_data['Month'] = pd.to_datetime(city_data['year_month']).dt.month_name().str[:3]

    city_data['Month'] = pd.Categorical(city_data['Month'], categories=[
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], ordered=True)

    pivot_table = city_data.pivot_table(
        index='Year', columns='Month', values='temperature'
    )

    x = pivot_table.columns
    y = pivot_table.index
    z = pivot_table.values

    fig = go.Figure(
        data=[
            go.Surface(
                x=np.arange(len(x)),
                y=y,
                z=z,
                colorscale=color_scale,
                colorbar=dict(title="Temperature (°C)")
            )
        ],
        layout=dict(
        title=dict(
            text=f"3D Surface Plot of Temperature for {city}",
            font=dict(size=16),  # Adjust font size of the title
            x=0.5  # Center the title
        )
    )
    )

    # Update layout to enhance richness
    fig.update_layout(
    scene=dict(
        xaxis=dict(
            title=dict(text='Month', font=dict(size=14)),  # Clear and styled axis title
            tickvals=np.arange(len(x)),
            ticktext=x,
            tickangle=45,
            tickmode='array',
            tickfont=dict(size=12, color='blue'),  # Use color to make ticks stand out
            showgrid=True,
            gridcolor='lightgray',  # Subtle grid lines
            zeroline=False
        ),
        yaxis=dict(
            title=dict(text='Year', font=dict(size=14)),
            tickfont=dict(size=12, color='blue'),
            showgrid=True,
            gridcolor='lightgray',
            zeroline=False
        ),
        zaxis=dict(
            title=dict(text='Temperature (°C)', font=dict(size=14)),
            tickfont=dict(size=12, color='blue'),
            showgrid=True,
            tickangle=20,
            gridcolor='lightgray',
            zeroline=False
        )
    ),
    margin=dict(l=0, r=0, b=0, t=50),
    scene_camera=dict(
        eye=dict(x=1.5, y=1.5, z=1.5)  # Improve perspective
    ),
    )


    return fig

# Create Heatmap and Bar Chart (Plot 3)
def create_heatmap(selected_metric):
    merged_df_sorted = merged_df.sort_values(by=['continent', 'city_name'])
    z = merged_df_sorted[selected_metric.lower()] * (1000 if selected_metric == "Precipitation" else 1)
    dates = merged_df_sorted['year']
    cities = merged_df_sorted['city_name'] + " (" + merged_df_sorted['continent'] + ")"

    yearly_totals = merged_df.groupby('year')[selected_metric.lower()].sum() * (1000 if selected_metric == "Precipitation" else 1)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0,
        row_heights=[0.1, 0.9],
        subplot_titles=(f"{selected_metric} Heatmap", "")
    )

    fig.add_trace(
        go.Bar(
            x=yearly_totals.index,
            y=yearly_totals.values,
            name=f"Total {selected_metric}",
            marker_color='rgba(255, 87, 51, 0.7)',
            opacity=0.6
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Heatmap(
            z=z,
            x=dates,
            y=cities,
            colorscale=color_scale,
            zmin=z_min_max[selected_metric]["min"],
            zmax=z_min_max[selected_metric]["max"],
            colorbar=dict(title=f"{selected_metric} (mm)" if selected_metric == "Precipitation" else f"{selected_metric} (hours)"),
        ),
        row=2, col=1
    )

    fig.update_layout(height=680, showlegend=False)
    return fig




@app.callback(
    [Output('surface-plot', 'figure'),
     Output('heatmap-bar-plot', 'figure')],
    [Input('city-dropdown', 'value'),
     Input('metric-selector','value')
    ]
)
def update_combined_plots(city, selectedmetric):
    # Create Surface Plot
    surface_plot = create_surface_plot(city)
    # Create Heatmap and Bar Plot
    heatmap_bar_plot = create_heatmap(selectedmetric)
    return surface_plot, heatmap_bar_plot

@app.callback(
    Output('subplot-plot', 'figure'),
    [Input('city-dropdown', 'value')]
)
def update_subplot(city):
    # Densitymapbox for PLOT 4
    densitymapbox = go.Densitymapbox(
        lat=result_new['Latitude'],
        lon=result_new['Longitude'],
        z=result_new['TemperatureDifference'],
        radius=12,
        colorscale='thermal'
    )

    # Data for Barpolar and Linepolar (PLOT 2)
    city_data = grouped_data[grouped_data['city_name'] == city]

    barpolar = go.Barpolar(
        r=city_data['days'],
        theta=city_data['year_group'],
        name='Bar Chart',
        marker=dict(
            color=city_data['weather_num'],
            colorscale=color_scale,
        ),
        showlegend=False
    )

    linepolar = go.Scatterpolar(
        r=city_data['mean_annual_temperature'] * 20,
        theta=city_data['year_group'],
        mode='lines+markers+text',
        name='Line Chart',
        line=dict(color='blue', width=1),
        text=city_data['mean_annual_temperature'],
        textposition='top center',
        textfont=dict(
        size=10,  # Set the desired font size
        color='black'  # Optional: change text color for better visibility,
    ),
    showlegend=False
    )

    custom_legend = [
        go.Scatterpolar(
            r=[0],  # Dummy point
            theta=['1980-1982'],
            mode='markers',
            marker=dict(size=10, color=color),
            name=label,
            showlegend=True
        ) for label, color in zip(['Snowfall','Heavy Rain','Light Rain'], ['#8B0000', '#E75454', '#F4C2C2'])
    ]

    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f"","Density Map showing increase in temperature in last 300 years"),
        specs=[[{"type": "polar"},{"type": "mapbox"}]],
        column_widths=[0.4, 0.6]  
    )
    
    fig.update_layout(
    polar=dict(
        radialaxis=dict(
            showticklabels=True,
            tickfont=dict(
                size=6  # Set the font size for the radial axis labels
            )
        ),
    ), 
    legend=dict(
            x=-0.3,  # Move legend to the left
            y=1,     # Align legend to the top
            xanchor='left',
            yanchor='top',
            font=dict(size=10)
        ),
    showlegend=True 
    )
    fig.update_layout(
    title_text=f"Polar Chart for {city}",
    title_font=dict(size=16)  # Adjust font size
    )


    # Add traces to subplots
    fig.add_trace(densitymapbox, row=1, col=2)
    fig.add_trace(barpolar, row=1, col=1)
    fig.add_trace(linepolar, row=1, col=1)

    for trace in custom_legend:
        fig.add_trace(trace, row=1, col=1)

    # Update layout
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lon": 0, "lat": 20},
        mapbox_zoom=1,
        height=500,
        showlegend=True
    )

    return fig


    
if __name__ == '__main__':
    app.run_server(debug=True)