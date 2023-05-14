# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites = spacex_df['Launch Site'].unique()


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] + [{'label': 'All Sites (Success)', 'value': 'SUCCESS'}] + [{'label': 'All Sites (Failures)', 'value': 'FAILURE'}] + [{'label': site, 'value': site} for site in launch_sites],
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', 
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                marks={
                                                    0: '0',
                                                    100: '100'
                                                },
                                                value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(
    dash.dependencies.Output('success-pie-chart', 'figure'),
    [dash.dependencies.Input('site-dropdown', 'value')]
)

def get_pie_chart(entered_site):

    total_success = len(spacex_df[spacex_df['class'] == 1])
    total_failures = len(spacex_df[spacex_df['class'] == 0])
    site_data = spacex_df[spacex_df['Launch Site'] == entered_site]
    success = len(site_data[site_data['class'] == 1])
    failures = len(site_data[site_data['class'] == 0])
    site_success = []
    site_names = []
    site_failure = []

    if entered_site == 'ALL':
        #Render pie chart for all sites
        labels = ['Success', 'Failures']
        values = [total_success, total_failures]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_layout(title='All Sites Combined Success and Failure')

    elif entered_site == 'SUCCESS':
        for site in launch_sites:
            site_data = spacex_df[spacex_df['Launch Site'] == site]
            success = len(site_data[site_data['class'] == 1])
            site_success.append(success)
            site_names.append(site)
        
        fig = go.Figure(data=[go.Pie(labels=site_names, values=site_success)])
        fig.update_layout(title='Success Launches by Site')

    elif entered_site == 'FAILURE':
        for site in launch_sites:
            site_data = spacex_df[spacex_df['Launch Site'] == site]
            failures = len(site_data[site_data['class'] == 0])
            site_failure.append(failures)
            site_names.append(site)
        
        fig = go.Figure(data=[go.Pie(labels=site_names, values=site_failure)])
        fig.update_layout(title='Failure Launches by Site')

    else:
        #Filter data for selected site
        labels = ['Success', 'Failures']
        values = [success, failures]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_layout(title=entered_site + " Launch Site")

    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(entered_site, payload_range):
    if entered_site == 'ALL':
        # Render scatter plot for all sites
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category')
        fig.update_layout(title='Payload vs. Launch Outcome for All Sites')
    else:
        # Filter data for selected site
        site_data = spacex_df[spacex_df['Launch Site'] == entered_site]
        filtered_df = site_data[(site_data['Payload Mass (kg)'] >= payload_range[0]) & (site_data['Payload Mass (kg)'] <= payload_range[1])]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category')
        fig.update_layout(title=f'Payload vs. Launch Outcome for {entered_site} Launch Site')

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
