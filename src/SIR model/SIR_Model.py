import numpy as np
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from scipy import optimize
from scipy import integrate
import matplotlib as mpl

mpl.rcParams['figure.figsize'] = (16, 9)
pd.set_option('display.max_rows', 500)


def SIR_model_t(SIR, t, beta, gamma):
    ''' Simple SIR model
        S: susceptible population
        t: time step, mandatory for integral.odeint
        I: infected people
        R: recovered people
        beta:

        overall condition is that the sum of changes (differnces) sum up to 0
        dS+dI+dR=0
        S+I+R= N (constant size of population)

    '''
    global N0
    S, I, R = SIR
    dS_dt = -beta * S * I / N0  # S*I is the
    dI_dt = beta * S * I / N0 - gamma * I
    dR_dt = gamma * I
    return dS_dt, dI_dt, dR_dt


def fit_odeint(x, beta, gamma):
    '''
    helper function for the integration
    '''
    return integrate.odeint(SIR_model_t, (S0, I0, R0), x, args=(beta, gamma))[:, 1]  # we only would like to get dI


df_analyse = pd.read_csv(r'C:\Users\HP\Desktop\pythonProject/data/processed/COVID_small_flat_table.csv', sep=';')
df_analyse.sort_values('date', ascending=True)

dash.__version__

fig = go.Figure()
app = dash.Dash()
app.layout = html.Div([

    dcc.Markdown('''
        # SIR model for Applied Data Science on COVID-19 dataset
        SIR model was developed for COVID-19 dataset and implemented in this dashboard. 

        '''),
    dcc.Markdown('''
        ## Selection of various countries for visualization purpose
        '''),

    dcc.Dropdown(
        id='countries',
        options=[{'label': each, 'value': each} for each in df_analyse.columns[1:]],
        value=['Germany', 'US', 'Spain'],  # which are pre-selected
        multi=True
    ),

    dcc.Markdown('''
            ## Graphical representation of SIR model
            '''),

    dcc.Graph(figure=fig, id='main_window_slope'),
])


@app.callback(
    Output('main_window_slope', 'figure'),
    [Input('countries', 'value')])
def update_figure(country_list):
    traces = []

    my_yaxis = {'type': "log",
                'title': 'Total population'
                }
    for each in country_list:
        Col = df_analyse[each]
        ydata = np.array(Col[100:200])
        global I0, S0, R0, N0
        N0 = 10000000
        t = np.arange(len(ydata))
        I0 = ydata[0]
        S0 = N0 - I0
        R0 = 0
        ## get the model parameters / fit the model
        popt, pcov = optimize.curve_fit(fit_odeint, t, ydata)
        # get the final fitted curve / predict the outcome
        fitted = fit_odeint(t, *popt)
        traces.append(dict(x=t,
                           y=np.ediff1d(ydata, to_begin=ydata[1] - ydata[0]),
                           mode='markers',
                           opacity=0.9,
                           name=each
                           )
                      )
        traces.append(dict(x=t,
                           y=fitted,
                           mode='lines',
                           opacity=0.9,
                           name=each
                           )
                      )

    return {
        'data': traces,
        'layout': dict(
            width=1280,
            height=720,
            title="SIR Simulation fit curve for selected countries",
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
