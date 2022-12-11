import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import os
import webbrowser
import easygui as g


pitch_colors = {
    '4 Seam Fastball': '#636EFA',
    '2 Seam Fastball': '#EF553B',
    'Cutter': '#00CC96',
    'Curveball': '#AB63FA',
    'Slider': '#FFA15A',
    'Changeup': '#19D3F3',
    'Splitter': '#FF6692',
    'Knuckleball': '#B6E880',
    'Other': '#FF97FF'
}


baseball_cols = [
    'Date',
    'Athlete_Name',
    'MPH',
    'Spin_Direction',
    'Gyro_Degree',
    'Vertical_Break_Inches',
    'Horizontal_Break_Inches',
    'Total_Spin',
    'Spin_Efficiency',
    'True_Spin',
    'Release_Angle',
    'Release_Height',
    'Horizontal_Angle',
    'Release_Size',
    'Pitch_Count',
    'Pitch_Type',
    'Strike',
    'pitch_horizontal_offset',
    'pitch_vertical_offset'
]


def blank_graph(error_message: str) -> go.Figure:
    res = {
        "layout": {
            "xaxis": {
                "visible": False
            },
            "yaxis": {
                "visible": False
            },
            "annotations": [
                {
                    "text": error_message,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ],
            'template': 'flatly'
        }
    }

    return res


def validate_data(df: pd.DataFrame) -> bool:
    if not all_equal(df.columns, baseball_cols):
        return False

    return True


def get_data() -> (pd.DataFrame, pd.DataFrame):
    filename = "C:\\Users\\eamas\\source\\ML_Datasets\\Rapsodo\\test.csv"
    if filename == "":
        return None

    data = pd.read_csv(filename)
    if not validate_data(data):
        return None

    return clean_data(data)


def clean_data(df: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    df = calculated_columns(df)

    return df


def calculated_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["pitch_start_y"] = df["pitch_vertical_offset"] + df['Vertical_Break_Inches']
    df["pitch_start_x"] = df["pitch_horizontal_offset"] + df['Horizontal_Break_Inches']

    return df


def var_stat(df: pd.DataFrame, col: str) -> pd.DataFrame:
    tmp = (
        df
        .groupby(['Date', 'Athlete_Name', 'Pitch_Type'])
        .agg(
            avg=(col, 'mean'),
            min=(col, 'min'),
            q25=(col, lambda x: x.quantile(.25)),
            median=(col, lambda x: x.quantile(.5)),
            q75=(col, lambda x: x.quantile(.75)),
            max=(col, 'max')
        )
        .rename(columns={
            'avg': col + '_avg',
            'min': col + '_min',
            'q25': col + '_q25',
            'median': col + '_median',
            'q75': col + '_q75',
            'max': col + '_max'
        })
    )

    return tmp


def all_equal(a: list, b: list) -> bool:
    if len(a) != len(b):
        return False

    for i in range(len(a)):
        if a[i] != b[i]:
            return False

    return True


def plot_break_graph(df: pd.DataFrame, pitches_selected, agg_method, agg_label, template: str = "flatly") -> go.Figure:

    if pitches_selected is None or len(pitches_selected) == 0:
        return blank_graph("Select a Pitch Type")

    if agg_method is None:
        return blank_graph("Select Aggregation Statistic")

    pitches_selected = sorted(pitches_selected)

    tmp_df = (
        df
        .loc[df['Pitch_Type'].isin(pitches_selected), :]
        .groupby(['Date', 'Pitch_Type', 'Athlete_Name'])
        .agg(
            hoz_use_val = ('Horizontal_Break_Inches', agg_method),
            vert_use_val = ('Vertical_Break_Inches', agg_method),
        )
        .rename(columns={'hoz_use_val': f'{agg_label} Horizontal Break'})
        .rename(columns={'vert_use_val': f'{agg_label} Vertical Break'})
        .reset_index()
    )

    fig = go.Figure()

    for i in range(len(pitches_selected)):
        tmp_dfs = tmp_df.loc[tmp_df['Pitch_Type'] == pitches_selected[i], :]

        one = tmp_dfs['Date'].tolist()
        two = tmp_dfs['Athlete_Name'].tolist()
        three = tmp_dfs['Pitch_Type'].tolist()

        cust_dat = np.empty((len(tmp_dfs.index), 3, 1), dtype='object')
        cust_dat[:, 0] = np.array(one).reshape(-1, 1)
        cust_dat[:, 1] = np.array(two).reshape(-1, 1)
        cust_dat[:, 2] = np.array(three).reshape(-1, 1)

        fig.add_scatter(
            x=tmp_dfs[f'{agg_label} Horizontal Break'],
            y=tmp_dfs[f'{agg_label} Vertical Break'],
            showlegend=True,
            name=pitches_selected[i],
            customdata=cust_dat,
            marker={'color': pitch_colors[pitches_selected[i]]},
            mode="markers",
            hoverinfo='skip',
            hovertemplate='<br>Date: %{customdata[0]}<br>Athlete: %{customdata[1]}<br>Pitch Type: %{customdata[2]}'
        )

    fig.add_hline(y=0)
    fig.add_vline(x=0)

    fig.update_layout(
        xaxis_range=[-30, 30],
        yaxis_range=[-30, 30],
        title=f"Session {agg_label}",
        xaxis_title=f'{agg_label} Horizontal Break\n(Inches)',
        yaxis_title=f"{agg_label} Vertical Break\n(Inches)",
        legend_title="Pitch Types",
        template=template
    )
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
    fig.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')

    return fig


def highlight_plot_break(df: pd.DataFrame, pitches_selected, cust_data=None, template: str = "flatly") -> go.Figure:

    if pitches_selected is None or len(pitches_selected) == 0:
        return blank_graph("Select a Pitch Type")

    pitches_selected = sorted(pitches_selected)

    tmp_dfs_yes_dates = {}
    tmp_dfs_no_dates = {}

    if cust_data is None:
        tmp_dfs_yes_dates = df.loc[(df['Pitch_Type'].isin(pitches_selected)), :]

        tmp_dfs_lst = [tmp_dfs_yes_dates]
    else:
        date_selected = cust_data[0]
        pitch_type_selected = cust_data[2]

        tmp_dfs_yes_dates = df.loc[
                               (df['Pitch_Type'].isin(pitches_selected)) &
                               (
                                   (df['Date'] == date_selected) &
                                   (df['Pitch_Type'] == pitch_type_selected)
                               )
        , :]

        tmp_dfs_no_dates = df.loc[
                               (df['Pitch_Type'].isin(pitches_selected)) &
                               ~(
                                   (df['Date'] == date_selected) &
                                   (df['Pitch_Type'] == pitch_type_selected)
                               )
        , :]

        tmp_dfs_lst = [tmp_dfs_yes_dates, tmp_dfs_no_dates]

    fig = go.Figure()

    for i in range(len(pitches_selected)):
        for j in range(len(tmp_dfs_lst)):
            tmp_dfs = tmp_dfs_lst[j].loc[tmp_dfs_lst[j]['Pitch_Type'] == pitches_selected[i], :]

            one = tmp_dfs['Date'].tolist()
            two = tmp_dfs['Athlete_Name'].tolist()
            three = tmp_dfs['Pitch_Type'].tolist()

            cust_dat = np.empty((len(tmp_dfs.index), 3, 1), dtype='object')
            cust_dat[:, 0] = np.array(one).reshape(-1, 1)
            cust_dat[:, 1] = np.array(two).reshape(-1, 1)
            cust_dat[:, 2] = np.array(three).reshape(-1, 1)

            if len(tmp_dfs_lst) == 1:
                opacity = 1
            else:
                if j == 0:
                    opacity = 1
                else:
                    opacity = 0.25

            fig.add_scatter(
                x=tmp_dfs['Horizontal_Break_Inches'],
                y=tmp_dfs['Vertical_Break_Inches'],
                showlegend=True,
                name=pitches_selected[i],
                opacity=opacity,
                customdata=cust_dat,
                marker={'color': pitch_colors[pitches_selected[i]]},
                mode="markers",
                hoverinfo='skip',
                hovertemplate='<br>Date: %{customdata[0]}<br>Athlete: %{customdata[1]}<br>Pitch Type: %{customdata[2]}'
            )

    fig.add_hline(y=0)
    fig.add_vline(x=0)

    fig.update_layout(
        xaxis_range=[-30, 30],
        yaxis_range=[-30, 30],
        title="All Pitches",
        xaxis_title="Horizontal Break\n(Inches)",
        yaxis_title="Vertical Break\n(Inches)",
        legend_title="Pitch Types",
        template=template
    )
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
    fig.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')

    return fig


def plot_avg_velo(df, pitch_types, agg_method, agg_label, template: str = "flatly"):

    if pitch_types is None:
        return blank_graph("Select a Pitch Type")

    if agg_method is None:
        return blank_graph("Select a Aggregation Statistic")

    tmp_data = (
        df.loc[df['Pitch_Type'].isin(pitch_types), :]
        .groupby(['Pitch_Type', 'Date', 'Athlete_Name'])
        .agg(
            mph_use=('MPH', agg_method),
        )
        .rename(columns={'mph_use': f'{agg_label} MPH'})
        .reset_index()
    )

    fig = px.line(
        tmp_data,
        x='Date',
        y=f'{agg_label} MPH',
        color='Pitch_Type',
        markers=True,
        custom_data=['Date', 'Athlete_Name', 'Pitch_Type']
    )

    fig.update_layout(
        title=f"Session {agg_label} MPH",
        xaxis_title="Session Date",
        yaxis_title="MPH",
        legend_title="Pitch Types",
        template=template
    )

    return fig


def velo_highlight_plot(df: pd.DataFrame, pitches_selected, cust_data=None, template: str = "flatly") -> go.Figure:

    if pitches_selected is None or cust_data is None:
        return blank_graph("Select a Pitch Type")

    pitches_selected = sorted(pitches_selected)

    date_selected = cust_data[0]
    pitch_type_selected = cust_data[2]

    tmp_df = df.loc[
                           (
                               (df['Pitch_Type'].isin(pitches_selected)) &
                               (df['Date'] == date_selected)
                           )
    , :]

    fig = px.strip(tmp_df, y='Pitch_Type', x='MPH', color='Pitch_Type')

    fig.update_layout(
        title=f"Session MPH",
        xaxis_title="Pitch MPH",
        yaxis_title="Pitch Type",
        legend_title="Pitch Types",
        template=template
    )

    return fig


def open_browser():
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new('http://127.0.0.1:1222/')


def flatten_list(_2d_list):
    flat_list = []
    # Iterate through the outer list
    for element in _2d_list:
        if type(element) is list:
            # If the element is of type list, iterate through the sublist
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list


def plot_tot_spin(df, pitch_types, agg_method, agg_label, template: str = "flatly"):

    if pitch_types is None:
        return blank_graph("Select a Pitch Type")

    if agg_method is None:
        return blank_graph("Select a Aggregation Statistic")

    tmp_data = (
        df.loc[df['Pitch_Type'].isin(pitch_types), :]
        .groupby(['Pitch_Type', 'Date', 'Athlete_Name'])
        .agg(
            spin_use=('Total_Spin', agg_method),
        )
        .rename(columns={'spin_use': f'{agg_label} Total Spin'})
        .reset_index()
    )

    fig = px.line(
        tmp_data,
        x='Date',
        y=f'{agg_label} Total Spin',
        color='Pitch_Type',
        markers=True,
        custom_data=['Date', 'Athlete_Name', 'Pitch_Type']
    )

    fig.update_layout(
        title=f"Session {agg_label} Total Spin",
        xaxis_title="Session Date",
        yaxis_title="Total Spin",
        legend_title="Pitch Types",
        template=template
    )

    return fig

def plot_true_spin(df, pitch_types, agg_method, agg_label, template: str = "flatly"):

    if pitch_types is None:
        return blank_graph("Select a Pitch Type")

    if agg_method is None:
        return blank_graph("Select a Aggregation Statistic")

    tmp_data = (
        df.loc[df['Pitch_Type'].isin(pitch_types), :]
        .groupby(['Pitch_Type', 'Date', 'Athlete_Name'])
        .agg(
            spin_use=('True_Spin', agg_method),
        )
        .rename(columns={'spin_use': f'{agg_label} True Spin'})
        .reset_index()
    )

    fig = px.line(
        tmp_data,
        x='Date',
        y=f'{agg_label} True Spin',
        color='Pitch_Type',
        markers=True,
        custom_data=['Date', 'Athlete_Name', 'Pitch_Type']
    )

    fig.update_layout(
        title=f"Session {agg_label} True Spin",
        xaxis_title="Session Date",
        yaxis_title="True Spin",
        legend_title="Pitch Types",
        template=template
    )

    return fig


def plot_eff_spin(df, pitch_types, agg_method, agg_label, template: str = "flatly"):

    if pitch_types is None:
        return blank_graph("Select a Pitch Type")

    if agg_method is None:
        return blank_graph("Select a Aggregation Statistic")

    tmp_data = (
        df.loc[df['Pitch_Type'].isin(pitch_types), :]
        .groupby(['Pitch_Type', 'Date', 'Athlete_Name'])
        .agg(
            spin_use=('Spin_Efficiency', agg_method),
        )
        .rename(columns={'spin_use': f'{agg_label} Spin Efficiency'})
        .reset_index()
    )

    fig = px.line(
        tmp_data,
        x='Date',
        y=f'{agg_label} Spin Efficiency',
        color='Pitch_Type',
        markers=True,
        custom_data=['Date', 'Athlete_Name', 'Pitch_Type']
    )

    fig.update_layout(
        title=f"Session {agg_label} Spin Efficiency",
        xaxis_title="Session Date",
        yaxis_title="Spin Efficiency\n(%)",
        legend_title="Pitch Types",
        template=template
    )

    return fig
