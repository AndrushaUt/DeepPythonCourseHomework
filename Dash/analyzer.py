from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px

app = Dash(__name__)

df = pd.read_csv("crimedata.csv")
df.reset_index(drop=True, inplace=True)
df["ViolentCrimes"] = df["ViolentCrimesPerPop"] * df["population"] / 100000
df["nonViolentCrimes"] = df["nonViolPerPop"] * df["population"] / 100000
df["TotalCrimes"] = df["ViolentCrimes"] + df["nonViolentCrimes"] / 100000
df["TotalCrimesPerPop"] = df["TotalCrimes"] / df["population"] / 100000

df_total_crime = df.groupby(['state']).agg(
    {"TotalCrimes": "sum", "population": "sum"}).reset_index()
df_total_crime["TotalCrimesPerPop"] = df_total_crime["TotalCrimes"] / \
                                      df_total_crime["population"] * 100000

fig_total_crime = px.bar(df_total_crime, x="state", y="TotalCrimesPerPop")
fig_total_crime.update_layout(title={"text": "Amount of crimes by state", },
                              xaxis_title="State",
                              yaxis_title="Amount of crimes by state per 100k pop",
                              height=500
                              )

df_race = df
df_race["TotalRaceBlack"] = df_race["racepctblack"] / 100 * df_race[
    "population"]
df_race["TotalRaceWhite"] = df_race["racePctWhite"] / 100 * df_race[
    "population"]
df_race["TotalRaceAsian"] = df_race["racePctAsian"] / 100 * df_race[
    "population"]
df_race["TotalRaceHisp"] = df_race["racePctHisp"] / 100 * df_race["population"]
df_race = df_race.groupby("state").agg(
    {"population": "sum", "TotalRaceBlack": "sum", "TotalRaceWhite": "sum",
     "TotalRaceAsian": "sum", "TotalRaceHisp": "sum"}).reset_index()

df_nation_wage = df
df_nation_wage = df_nation_wage.groupby('state').agg(
    {'communityName': 'nunique', 'whitePerCap': 'sum',
     'blackPerCap': 'sum', 'indianPerCap': 'sum',
     'AsianPerCap': 'sum', 'OtherPerCap': 'sum',
     'HispPerCap': 'sum'}).reset_index()
df_nation_wage['whitePerCapState'] = df_nation_wage['whitePerCap'] / \
                                     df_nation_wage['communityName']
df_nation_wage['blackPerCapState'] = df_nation_wage['blackPerCap'] / \
                                     df_nation_wage['communityName']
df_nation_wage['indianPerCapState'] = df_nation_wage['indianPerCap'] / \
                                      df_nation_wage['communityName']
df_nation_wage['AsianPerCapState'] = df_nation_wage['AsianPerCap'] / \
                                     df_nation_wage['communityName']
df_nation_wage['OtherPerCapState'] = df_nation_wage['OtherPerCap'] / \
                                     df_nation_wage['communityName']
df_nation_wage['HispPerCapState'] = df_nation_wage['HispPerCap'] / \
                                    df_nation_wage['communityName']

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Graph(
                id='crime_rate_by_state',
                figure=fig_total_crime)
        ],
            style={'width': '70%', 'margin': 'auto'}),

        html.Div([
            dcc.Dropdown(
                df.sort_values('state')['state'].unique(),
                'AK',
                id='state_dropdown'
            ),
            dcc.Graph(
                id='race_by_state_graph'
            ),
        ],
            style={'width': '49%', 'margin': 'auto'}),
        html.Div([
            dcc.RadioItems(
                ['White People',
                 'Black People',
                 'Indian Pople',
                 'Asian People',
                 'Hisp People',
                 'Other People'],
                'White People',
                inline=True,
                id='nation'
            ),
            dcc.Graph(
                id='nation_graph'
            )
        ],
            style={'width': '49%', 'margin': 'auto'})
    ])
])


@app.callback(
    Output('race_by_state_graph', 'figure'),
    Input('state_dropdown', 'value'))
def race(state):
    rasa = df_race[df_race["state"] == state].reset_index(drop=True)
    rasa_of_state = rasa.drop(["population", "state"], axis=1).iloc[0]
    fig_rasa = px.pie(rasa, names=["Black", "White", "Asian", "Hisp"],
                      values=rasa_of_state)
    fig_rasa.update_layout(title={"text": "Race in state"}, height=400)
    return fig_rasa


@app.callback(
    Output('nation_graph', 'figure'),
    Input('nation', 'value'))
def nation_wage(nation):
    d = {
        'White People': 'whitePerCapState',
        'Black People': 'blackPerCapState',
        'Indian People': 'indianPerCapState',
        'Asian People': 'AsianPerCapState',
        'Hisp People': 'HispPerCapState',
        'Other People': 'OtherPerCapState'
    }
    fig_nation_wage = px.line(df_nation_wage, x='state', y=d[nation])
    fig_nation_wage.update_layout(
        title={
            "text": f"Per {nation.split()[0].lower()} person income for each state", },
        xaxis_title="State",
        yaxis_title="income",
        height=500
    )
    return fig_nation_wage


if __name__ == '__main__':
    app.run_server()
