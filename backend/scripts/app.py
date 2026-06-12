import requests
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

MATCH_ID = 3890561
URL = f"https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{MATCH_ID}.json"

response = requests.get(URL)
response.raise_for_status()
events = response.json()

shots = [e for e in events if e["type"]["name"] == "Shot"]
teams = sorted({s["team"]["name"] for s in shots})

team_colors = {teams[0]: "blue", teams[1]: "red"}

outcome_symbols = {
    "Goal": "circle",
    "Saved": "triangle-up",
    "Saved to Post": "triangle-up",
    "Blocked": "square",
    "Off T": "x",
    "Wayward": "x",
    "Post": "cross",
}

players_by_team = {
    team: sorted({s["player"]["name"] for s in shots if s["team"]["name"] == team})
    for team in teams
}


def draw_pitch(fig):
    fig.add_shape(type="rect", x0=0, y0=0, x1=120, y1=80, line=dict(width=2))
    fig.add_shape(type="line", x0=60, y0=0, x1=60, y1=80, line=dict(width=1))
    fig.add_shape(type="circle", x0=50, y0=30, x1=70, y1=50, line=dict(width=1))
    fig.add_shape(type="rect", x0=0, y0=18, x1=18, y1=62, line=dict(width=2))
    fig.add_shape(type="rect", x0=102, y0=18, x1=120, y1=62, line=dict(width=2))
    fig.add_shape(type="rect", x0=0, y0=30, x1=6, y1=50, line=dict(width=2))
    fig.add_shape(type="rect", x0=114, y0=30, x1=120, y1=50, line=dict(width=2))
    fig.add_shape(type="circle", x0=11.5, y0=39.5, x1=12.5, y1=40.5, line=dict(width=1))
    fig.add_shape(type="circle", x0=107.5, y0=39.5, x1=108.5, y1=40.5, line=dict(width=1))
    fig.add_shape(type="rect", x0=-2, y0=36, x1=0, y1=44, line=dict(width=2))
    fig.add_shape(type="rect", x0=120, y0=36, x1=122, y1=44, line=dict(width=2))


def filter_shots(selected_players, half, minute_range):
    filtered = []

    for shot in shots:
        player = shot["player"]["name"]
        minute = shot["minute"]
        period = shot["period"]

        if selected_players and player not in selected_players:
            continue
        if half == "First Half" and period != 1:
            continue
        if half == "Second Half" and period != 2:
            continue
        if not (minute_range[0] <= minute <= minute_range[1]):
            continue

        filtered.append(shot)

    return filtered


def build_summary(filtered_shots):
    cards = []

    for team in teams:
        team_shots = [s for s in filtered_shots if s["team"]["name"] == team]
        total_xg = sum(float(s["shot"]["statsbomb_xg"]) for s in team_shots)
        shot_count = len(team_shots)
        avg_xg = total_xg / shot_count if shot_count else 0

        cards.append(
            html.Div(
                [
                    html.H3(team, style={"marginBottom": "6px"}),
                    html.Div(f"{total_xg:.2f} xG", style={"fontSize": "28px", "fontWeight": "bold"}),
                    html.Div(f"{shot_count} shots"),
                    html.Div(f"{avg_xg:.3f} avg xG/shot"),
                ],
                style={
                    "border": f"3px solid {team_colors[team]}",
                    "borderRadius": "10px",
                    "padding": "14px",
                    "width": "45%",
                    "boxSizing": "border-box",
                },
            )
        )

    return html.Div(cards, style={"display": "flex", "gap": "20px", "margin": "20px 0"})


def build_match_dna(filtered_shots):
    cards = []

    for team in teams:
        team_shots = [s for s in filtered_shots if s["team"]["name"] == team]

        total_xg = sum(float(s["shot"]["statsbomb_xg"]) for s in team_shots)
        shot_count = len(team_shots)
        avg_xg = total_xg / shot_count if shot_count else 0
        goals = sum(1 for s in team_shots if s["shot"]["outcome"]["name"] == "Goal")
        big_chances = sum(1 for s in team_shots if float(s["shot"]["statsbomb_xg"]) >= 0.25)

        box_shots = 0
        outside_box_shots = 0

        for shot in team_shots:
            x, y = shot["location"]

            if team == teams[1]:
                x = 120 - x
                y = 80 - y

            if x >= 102 and 18 <= y <= 62:
                box_shots += 1
            else:
                outside_box_shots += 1

        cards.append(
            html.Div(
                [
                    html.H3(team),
                    html.Div(f"Goals: {goals}"),
                    html.Div(f"Total xG: {total_xg:.2f}"),
                    html.Div(f"Shots: {shot_count}"),
                    html.Div(f"Avg xG/shot: {avg_xg:.3f}"),
                    html.Div(f"Big chances: {big_chances}"),
                    html.Div(f"Box shots: {box_shots}"),
                    html.Div(f"Outside box shots: {outside_box_shots}"),
                ],
                style={
                    "border": f"3px solid {team_colors[team]}",
                    "borderRadius": "10px",
                    "padding": "14px",
                    "width": "45%",
                    "boxSizing": "border-box",
                    "lineHeight": "1.7",
                },
            )
        )

    return html.Div(cards, style={"display": "flex", "gap": "20px", "margin": "20px 0"})


def build_shot_map(selected_players, half, minute_range):
    filtered_shots = filter_shots(selected_players, half, minute_range)
    fig = go.Figure()
    draw_pitch(fig)

    for team in teams:
        x_vals, y_vals, sizes, symbols, hover = [], [], [], [], []

        for shot in filtered_shots:
            if shot["team"]["name"] != team:
                continue

            x, y = shot["location"]

            if team == teams[1]:
                x = 120 - x
                y = 80 - y

            xg = float(shot["shot"]["statsbomb_xg"])
            player = shot["player"]["name"]
            minute = shot["minute"]
            outcome = shot["shot"]["outcome"]["name"]

            x_vals.append(x)
            y_vals.append(y)
            sizes.append(max(xg * 55, 7))
            symbols.append(outcome_symbols.get(outcome, "diamond"))
            hover.append(
                f"<b>{player}</b><br>"
                f"Team: {team}<br>"
                f"Minute: {minute}'<br>"
                f"xG: {xg:.3f}<br>"
                f"Outcome: {outcome}"
            )

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="markers",
                marker=dict(
                    size=sizes,
                    color=team_colors[team],
                    symbol=symbols,
                    opacity=0.75,
                    line=dict(width=1, color="black"),
                ),
                text=hover,
                hoverinfo="text",
                name=team,
            )
        )

    fig.update_layout(
        title=f"Match Lens - {teams[0]} vs {teams[1]}",
        width=1100,
        height=750,
        plot_bgcolor="white",
        showlegend=True,
        xaxis=dict(range=[-3, 123], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-2, 82], showgrid=False, zeroline=False, visible=False, scaleanchor="x", scaleratio=1),
    )

    return fig


def build_xg_timeline(filtered_shots):
    fig = go.Figure()

    top_team = teams[0]
    bottom_team = teams[1]

    for team in teams:
        team_shots = sorted([s for s in filtered_shots if s["team"]["name"] == team], key=lambda x: x["minute"])

        minutes, xg_values, hover = [], [], []

        for shot in team_shots:
            player = shot["player"]["name"]
            minute = shot["minute"]
            xg = float(shot["shot"]["statsbomb_xg"])
            outcome = shot["shot"]["outcome"]["name"]
            y_value = xg if team == top_team else -xg

            minutes.append(minute)
            xg_values.append(y_value)
            hover.append(
                f"<b>{team}</b><br>{player}<br>Minute: {minute}'<br>xG: {xg:.3f}<br>Outcome: {outcome}"
            )

        fig.add_trace(
            go.Bar(
                x=minutes,
                y=xg_values,
                name=team,
                marker_color=team_colors[team],
                opacity=0.75,
                text=hover,
                hoverinfo="text",
            )
        )

    fig.add_hline(y=0, line_width=2, line_color="black")

    fig.update_layout(
        title=f"Chance Quality Timeline: {top_team} ↑ / {bottom_team} ↓",
        height=300,
        barmode="overlay",
        bargap=0.15,
        plot_bgcolor="white",
        margin=dict(l=50, r=20, t=60, b=45),
        showlegend=True,
        legend=dict(orientation="h", y=1.18),
        xaxis=dict(title="Minute", range=[0, 100], showgrid=True, zeroline=False),
        yaxis=dict(
            title="xG",
            range=[-1, 1],
            showgrid=True,
            zeroline=False,
            tickvals=[-1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1],
            ticktext=["1.00", "0.75", "0.50", "0.25", "0", "0.25", "0.50", "0.75", "1.00"],
        ),
    )

    return fig


def build_cumulative_xg_race(filtered_shots):
    fig = go.Figure()

    for team in teams:
        team_shots = sorted([s for s in filtered_shots if s["team"]["name"] == team], key=lambda x: x["minute"])

        minutes = [0]
        cumulative_xg = [0]
        running_total = 0

        for shot in team_shots:
            minute = shot["minute"]
            xg = float(shot["shot"]["statsbomb_xg"])
            running_total += xg
            minutes.append(minute)
            cumulative_xg.append(running_total)

        fig.add_trace(
            go.Scatter(
                x=minutes,
                y=cumulative_xg,
                mode="lines+markers",
                name=team,
                line=dict(color=team_colors[team], width=3),
                marker=dict(size=6),
            )
        )

    fig.update_layout(
        title="Cumulative xG Race",
        height=300,
        plot_bgcolor="white",
        margin=dict(l=50, r=20, t=60, b=45),
        showlegend=True,
        legend=dict(orientation="h", y=1.18),
        xaxis=dict(title="Minute", range=[0, 100], showgrid=True, zeroline=False),
        yaxis=dict(title="Cumulative xG", showgrid=True, zeroline=False),
    )

    return fig


all_player_options = []
for team in teams:
    for player in players_by_team[team]:
        all_player_options.append({"label": f"{team} — {player}", "value": player})


app = Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Match Lens"),

        html.Label("Players"),
        dcc.Dropdown(
            id="player-filter",
            options=all_player_options,
            value=[],
            multi=True,
            placeholder="Select players, or leave blank for all",
        ),

        html.Br(),

        html.Label("Half"),
        dcc.RadioItems(
            id="half-filter",
            options=["Full Match", "First Half", "Second Half"],
            value="Full Match",
            inline=True,
        ),

        html.Br(),

        html.Label("Minute Range"),
        dcc.RangeSlider(
            id="minute-slider",
            min=0,
            max=100,
            step=1,
            value=[0, 100],
            marks={0: "0", 15: "15", 30: "30", 45: "45", 60: "60", 75: "75", 90: "90", 100: "100"},
        ),

        html.Div(id="summary-panel"),
        dcc.Graph(id="xg-timeline"),
        dcc.Graph(id="cumulative-xg-race"),
        html.Div(id="match-dna-panel"),
        dcc.Graph(id="shot-map"),
    ],
    style={"maxWidth": "1200px", "margin": "0 auto", "fontFamily": "Arial"},
)


@app.callback(
    Output("minute-slider", "value"),
    Input("half-filter", "value"),
)
def sync_minute_slider_with_half(half):
    if half == "First Half":
        return [0, 45]
    if half == "Second Half":
        return [45, 100]
    return [0, 100]


@app.callback(
    Output("shot-map", "figure"),
    Output("summary-panel", "children"),
    Output("xg-timeline", "figure"),
    Output("cumulative-xg-race", "figure"),
    Output("match-dna-panel", "children"),
    Input("player-filter", "value"),
    Input("half-filter", "value"),
    Input("minute-slider", "value"),
)
def update_dashboard(selected_players, half, minute_range):
    filtered_shots = filter_shots(selected_players, half, minute_range)

    return (
        build_shot_map(selected_players, half, minute_range),
        build_summary(filtered_shots),
        build_xg_timeline(filtered_shots),
        build_cumulative_xg_race(filtered_shots),
        build_match_dna(filtered_shots),
    )


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)