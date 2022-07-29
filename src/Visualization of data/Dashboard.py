import pandas as pd
import numpy as np
import dash
from dash import dcc
from dash import html

from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import os

dash.__version__

print(os.getcwd())
df_input_large = pd.read_csv('../../data/processed/COVID_final_set.csv', sep=';')

fig = go.Figure()
app = dash.Dash()
app.layout = html.Div([

    dcc.Markdown('''
    #  Applied Data Science on COVID-19 dataset
    This dashboard is being implemented to demonstrate the understanding and knowledge gained during the data science 
    course. This will show different aspects of data science such as automated data scrapping, data filtration and 
    machine learning concepts.

    '''),
    dcc.Markdown('''
    ## Selection of various countries for visualization purpose
    '''),

    dcc.Dropdown(
        id='countries',
        options=[{'label': each, 'value': each} for each in df_input_large['country'].unique()],
        value=['India', 'Germany', 'Poland'],  # which are pre-selected
        multi=True
    ),

    dcc.Markdown('''
        ## Selection for Timeline of confirmed COVID-19 cases or the approximated doubling time
        '''),

    dcc.Dropdown(
        id='doubling_time',
        options=[
            {'label': 'Timeline Confirmed ', 'value': 'confirmed'},
            {'label': 'Timeline Confirmed Filtered', 'value': 'confirmed_filtered'},
            {'label': 'Timeline Doubling Rate', 'value': 'confirmed_DR'},
            {'label': 'Timeline Doubling Rate Filtered', 'value': 'confirmed_filtered_DR'},
        ],
        value='confirmed',
        multi=False
    ),

    dcc.Graph(figure=fig, id='main_window_slope'),
])


@app.callback(
    Output('main_window_slope', 'figure'),
    [Input('countries', 'value'),
     Input('doubling_time', 'value')])
def update_figure(country_list, show_doubling):
    if 'doubling_rate' in show_doubling:
        my_yaxis = {'type': "log",
                    'title': 'Approximated doubling rate over 3 days (larger numbers are better #stayathome)'
                    }
    else:
        my_yaxis = {'type': "log",
                    'title': 'Logarithmic scaled Confirmed infected people (source johns hopkins csse)'
                    }

    traces = []
    for each in country_list:

        df_plot = df_input_large[df_input_large['country'] == each]

        if show_doubling == 'doubling_rate_filtered':
            df_plot = df_plot[
                ['state', 'country', 'confirmed', 'confirmed_filtered', 'confirmed_DR', 'confirmed_filtered_DR',
                 'date']].groupby(['country', 'date']).agg(np.mean).reset_index()
        else:
            df_plot = df_plot[
                ['state', 'country', 'confirmed', 'confirmed_filtered', 'confirmed_DR', 'confirmed_filtered_DR',
                 'date']].groupby(['country', 'date']).agg(np.sum).reset_index()

        traces.append(dict(x=df_plot.date,
                           y=df_plot[show_doubling],
                           mode='markers+lines',
                           opacity=0.9,
                           name=each
                           )
                      )
    return {
        'data': traces,
        'layout': dict(
            width=1280,
            height=720,

            xaxis={'title': 'Timeline',
                   'tickangle': -45,
                   'nticks': 20,
                   'tickfont': dict(size=14, color="#7f7f7f"),
                   },

            yaxis=my_yaxis
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
