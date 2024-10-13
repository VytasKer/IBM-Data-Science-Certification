# Import required libraries
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df =  pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv')
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites = []
launch_sites.append({'label': 'All', 'value': 'All'})
all_launch_sites = spacex_df['Launch Site'].unique().tolist()
for launch_site in all_launch_sites:
    launch_sites.append({'label': launch_site, 'value': launch_site})

"""
filtered_df = spacex_df[spacex_df['Launch Site'] == 'VAFB SLC-4E']
print(filtered_df.head())
success_rate = filtered_df['class'].mean()
print('Success rate: ', success_rate)

var_names=['Successful Launches', 'Unsuccessful Launches']

fig = px.pie(filtered_df, values=[success_rate, 1 - success_rate], 
            names=var_names, 
            title='Success Rate for Selected Site')

print(fig)
"""

# Create a dash application
app = dash.Dash(__name__)

# Build dash app layout
app.layout = html.Div([
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 35}),
    html.P("Select a Launch Site:", style={'textAlign': 'left', 'color': '#503D36', 'font-size': 30}),
    dcc.Dropdown(id='site-dropdown', 
                 options=launch_sites,
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True),
    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.P("Select Payload range (Kg):", style={'textAlign': 'left', 'color': '#503D36', 'font-size': 30}),
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={i: {'label': str(i), 'style': {'font-size': '18px'}} for i in range(0, 10001, 1000)},
                    value=[min_payload, max_payload]),
    html.Br(),
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
], style={'display': 'flex', 'flex-direction': 'column'})


# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class', 
                     names='Launch Site', 
                     title='Total Success Launches for All Sites')
        return fig
    else:
        # return the outcomes piechart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

        filtered_df=filtered_df.groupby(['Launch Site','class']).size().reset_index(name='class count')

        fig = px.pie(filtered_df,values='class count',
                     names='class',
                     title=f"Total Success Launches for site {entered_site}")

    return fig

@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])

def get_scatter_chart(entered_site, payload_range):
    # Filter data by payload range
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color="Booster Version Category", 
                         title='Correlation between Payload and Success for All Sites')
        return fig
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) & 
                                 (spacex_df['Payload Mass (kg)'] >= low) & 
                                 (spacex_df['Payload Mass (kg)'] <= high)]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color="Booster Version Category",
                         title='Correlation between Payload and Success for Selected Site')

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)