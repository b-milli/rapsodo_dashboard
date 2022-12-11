import dash
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from dash import Dash, html, dcc, Input, Output
from threading import Timer
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from functions import *

template_use = "flatly"
load_figure_template(["flatly"])

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.title = "Baseball Data Analytics Dashboard"

data = get_data()
data = data.reset_index()

agg_meth_dict = {
    'Mean': np.mean,
    'Min': np.min,
    'Max': np.max,
    'Median': np.median,
    None: None
}


@app.callback(
    Output('avg_Horz_Vert', 'figure'),
    Input("pitch_type_select", "value"),
    Input('statistic_select', 'value'),
)
def output_agg_hoz_vert_graph(pitches_selected, agg_label):
    return plot_break_graph(data, pitches_selected, agg_meth_dict[agg_label], agg_label, template_use)


@app.callback(
    Output('Horz_Vert', 'figure'),
    Input("pitch_type_select", "value"),
    Input("avg_Horz_Vert", "hoverData"),
)
def output_hoz_vert_graph(pitches_selected, clicked_info):

    if clicked_info is not None:
        return highlight_plot_break(data, pitches_selected, flatten_list(clicked_info['points'][0]['customdata']), template_use)

    return highlight_plot_break(data, pitches_selected, None, template_use)


@app.callback(
    Output('avg_velo', 'figure'),
    Input("pitch_type_select", "value"),
    Input('statistic_select', 'value'),
)
def output_avg_velo(pitch_types, agg_label):
    return plot_avg_velo(data, pitch_types, agg_meth_dict[agg_label], agg_label)

@app.callback(
    Output('velo', 'figure'),
    Input("pitch_type_select", "value"),
    Input("avg_velo", "hoverData"),
)
def output_hov_velo(pitches_selected, clicked_info):
    if pitches_selected is None:
        return blank_graph("Select a Pitch Type")
    if clicked_info is None:
        return blank_graph('Hover Over Point to see All Pitch Speeds for Date')
    return velo_highlight_plot(data, pitches_selected, flatten_list(clicked_info['points'][0]['customdata']))


@app.callback(
    Output('avg_tot_spin', 'figure'),
    Input("pitch_type_select", "value"),
    Input('statistic_select', 'value'),
)
def output_tot_spin(pitch_types, agg_label):
    return plot_tot_spin(data, pitch_types, agg_meth_dict[agg_label], agg_label)


@app.callback(
    Output('avg_true_spin', 'figure'),
    Input("pitch_type_select", "value"),
    Input('statistic_select', 'value'),
)
def output_true_spin(pitch_types, agg_label):
    return plot_true_spin(data, pitch_types, agg_meth_dict[agg_label], agg_label)


@app.callback(
    Output('avg_spin_eff', 'figure'),
    Input("pitch_type_select", "value"),
    Input('statistic_select', 'value'),
)
def output_eff_spin(pitch_types, agg_label):
    return plot_eff_spin(data, pitch_types, agg_meth_dict[agg_label], agg_label)

break_layout = html.Div(
        [
            dcc.Graph(
                id='avg_Horz_Vert',
                style={'width': '40vw', 'height': '90vh', 'margin': 0, 'display': 'inline-block'},
                clear_on_unhover=True
            ),
            dcc.Graph(
                id='Horz_Vert',
                style={'width': '40vw', 'height': '90vh', 'margin': 0, 'display': 'inline-block'}
            )
        ],
        style={'display': 'flex', 'flex-direction': 'row', 'padding': 5, 'width': 'auto', 'height': '1000'}
)

velo_layout = html.Div(
        [
            dcc.Graph(
                id='avg_velo',
                style={'width': '80vw', 'height': '45vh', 'margin': 0, 'display': 'inline-block'},
                clear_on_unhover=True
            ),
            dcc.Graph(
                id='velo',
                style={'width': '80vw', 'height': '45vh', 'margin': 0, 'display': 'inline-block'}
            )
        ],
        style={'display': 'flex', 'flex-direction': 'column', 'padding': 5, 'width': 'auto', 'height': '1000'}
)

spin_layout = html.Div(
        [
            html.Div(
                [
                    dcc.Graph(
                        id='avg_tot_spin',
                        style={'width': '40vw', 'height': '45vh', 'margin': 0, 'display': 'inline-block'},
                        clear_on_unhover=True
                    ),
                    dcc.Graph(
                        id='avg_true_spin',
                        style={'width': '40vw', 'height': '45vh', 'margin': 0, 'display': 'inline-block'}
                    )
                ],
                style={'display': 'flex', 'flex-direction': 'row', 'padding': 5, 'width': 'auto', 'height': '1000'}
            ),
            html.Div(
                [
                    dcc.Graph(
                        id='avg_spin_eff',
                        style={'width': '40vw', 'height': '45vh', 'margin': 0, 'display': 'inline-block'},
                        clear_on_unhover=True
                    )
                ],
                style={'display': 'flex', 'flex-direction': 'row', 'padding': 5, 'width': 'auto', 'height': '1000'}
            ),
        ],
        style={'display': 'flex', 'flex-direction': 'column', 'padding': 5, 'width': 'auto', 'height': '1000'}
)

app.layout = html.Div(
    [
        html.H1("Rapsodo Data Dashboard"),
        html.Div(
                [
                    html.Div(
                        [
                            html.H6(children="Select Pitch Types:"),
                            dcc.Checklist(
                                id='pitch_type_select',
                                options=data['Pitch_Type'].unique(),
                                inline=False,
                                style={'width': '10vw', 'height': 'auto', 'margin': 10, 'padding': 5},
                                labelStyle={'display': 'block'}
                            ),
                            html.H6(children="Select Aggregation Statistic:"),
                            dcc.Dropdown(
                                id='statistic_select',
                                style={'width': '10vw', 'height': 'auto', 'margin': 10, 'padding': 5},
                                options=[
                                    'Mean',
                                    'Min',
                                    'Max',
                                    'Median',
                                ]
                            )
                        ],
                        style={'padding': 15}
                    ),
                    dcc.Tabs(
                        id='tabs',
                        value='tab_horz_vert',
                        children=[
                            dcc.Tab(
                                label="Horizontal Break vs Vertical Break",
                                value='tab_horz_vert',
                                children=break_layout
                            ),
                            dcc.Tab(
                                label="Pitch Velocity",
                                value='tab_velo',
                                children=velo_layout
                            ),
                            dcc.Tab(
                                label="Spin Metrics",
                                value='tab_spin',
                                children=spin_layout
                            )
                        ],
                        style={'width': '80vw', 'height': '5vh'}
                    )
                ],
                style={'display': 'flex', 'flex-direction': 'row', 'padding': 5, 'width': '100vh', 'height': '1000'}
            )
    ]
)

if __name__ == "__main__":

    Timer(1, open_browser).start()
    app.run_server(debug=True, port=1222)

