from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Read the spacex data into pandas dataframe
spacex_df =  pd.read_csv('spacex_data3.csv')

# Calculate min and max values for the slider
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

app = Dash(__name__)

app.layout = html.Div([
    html.H1("SpaceX Launch Records Dashboard         ", style={'textAlign': 'center'}),
    
    html.Div([
        dcc.Dropdown(
            id='site-dropdown',
            options=[
                {'label': 'All Sites', 'value': 'ALL'},
                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            ],
            value='ALL',
            placeholder="Select a Launch Site here",
            searchable=True,
            style={'width': '300px'}
        )
    ], style={
        'display': 'flex',
        'justifyContent': 'flex-start',  # Align to left
        'padding': '20px'
    }),
    
    # Add the Graph component with the correct ID
    dcc.Graph(id='success-pie-chart'),

    # Payload mass range slider
    html.Div([
        html.H3("Filter by Payload Mass (kg):"),
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=500,
            marks={
                0: '0 kg',
                2000: '2000 kg',
                4000: '4000 kg',
                6000: '6000 kg',
                8000: '8000 kg',
                10000: '10000 kg'
            },
            value=[min_payload, max_payload]  # Initial range
        )
    ], style={'width': '80%', 'margin': '40px auto', 'padding': '20px'}),
    

   
    # Scatter Plot
    dcc.Graph(id='success-payload-scatter-chart'),
    html.Div(id='output-container', style={'marginTop': 20, 'padding': '20px'})
])

# Callback for Pie Chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_pie_chart(selected_site, payload_range):
    # Filter by payload mass first
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    if selected_site == 'ALL':
        outcome_counts = filtered_df['class'].value_counts()
        fig = px.pie(
            values=outcome_counts.values,
            names=['Successful Launches', 'Failed Launches'],
            title=f'Success Rate (Payload: {payload_range[0]} - {payload_range[1]} kg)',
            color=['Successful Launches', 'Failed Launches'],
            color_discrete_map={'Successful Launches': 'green', 'Failed Launches': 'red'}
        )
        return fig
    else:
        # Filter by site and payload
        site_data = filtered_df[filtered_df['Launch Site'] == selected_site]
        outcome_counts = site_data['class'].value_counts()
        
        names = []
        values = []
        if 1 in outcome_counts.index:
            names.append('Successful Launches')
            values.append(outcome_counts[1])
        if 0 in outcome_counts.index:
            names.append('Failed Launches')
            values.append(outcome_counts[0])
        
        fig = px.pie(
            values=values,
            names=names,
            title=f'Success Rate at {selected_site} (Payload: {payload_range[0]} - {payload_range[1]} kg)',
            color=names,
            color_discrete_map={'Successful Launches': 'green', 'Failed Launches': 'red'}
        )
        return fig

# Callback for Scatter Plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter by payload mass first
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    if selected_site == 'ALL':
        # Render scatter plot for all sites
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version',
            title='Payload vs. Launch Outcome (All Sites)',
            labels={
                'PayloadMass': 'Payload Mass (kg)',
                'class': 'Launch Outcome (1=Success, 0=Failure)',
                'Booster Version': 'Booster Version'
            },
            hover_data=['Launch Site']
        )
    else:
        # Filter by specific site
        site_data = filtered_df[filtered_df['Launch Site'] == selected_site]
        
        fig = px.scatter(
            site_data,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version',
            title=f'Payload vs. Launch Outcome at {selected_site}',
            labels={
                'PayloadMass': 'Payload Mass (kg)',
                'class': 'Launch Outcome (1=Success, 0=Failure)',
                'Booster Version': 'Booster Version'
            }
        )
    
    # Customize the scatter plot
    fig.update_traces(marker=dict(size=12, opacity=0.8))
    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=[0, 1],
            ticktext=['Failure', 'Success']
        ),
        hovermode='closest'
    )
    
    return fig

if __name__ == '__main__':
    app.run(debug=True)