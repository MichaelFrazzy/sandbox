# V5 w/ Dashboard

import numpy as np
import random
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Simulation Parameters
initial_days = 365 * 2  # Total simulation days
initial_P_0 = 100  # Initial number of players
initial_K = 1000000  # Carrying capacity (max number of players)
initial_r = 0.01  # Player growth rate
initial_daily_active_percentage = 0.1  # Average active % of users

# FLIP and NFT Parameters
initial_flip_supply = 10000  # Starting available FLIP supply
initial_locked_flip = 5000  # Starting Locked FLIP within basic NFTs 
initial_basic_nfts = {'4x4': 100, '8x8': 50}  # Starting total basic NFTs created by type
initial_complex_nfts = 0  # Starting total complex NFTs created 

# Complex NFT Creation Parameters
initial_complex_nft_creation_percentage = 0.005  # Percentage of players who create complex NFTs each day

# Helper Functions
def logistic_growth(t, P_0, K, r):
    """Logistic growth model for player population."""
    return K / (1 + ((K - P_0) / P_0) * np.exp(-r * t))

def mint_flip_tokens(puzzle_type):
    """Mint FLIP tokens based on puzzle type solved."""
    return 1 if puzzle_type == '4x4' else 4

def determine_max_canvas_size(total_basic_nfts):
    """Determine max canvas size based on total basic NFTs created."""
    return '8x8' if total_basic_nfts >= 1000 else '4x4'

def nfts_used_for_complex(mean, std_dev):
    """Determine number of basic NFTs used for a complex NFT based on normal distribution."""
    nfts_used = int(np.random.normal(mean, std_dev))
    # Ensure the number of NFTs used is at least 1 and not more than the mean + 3*std_dev
    return max(1, min(nfts_used, mean + 3 * std_dev))

def create_basic_nfts(day, initial_supply, growth_rate):
    """Realistically create basic NFTs over time."""
    # Assuming a linear increase over time, could be modified for other growth patterns
    return initial_supply + day * growth_rate

def run_simulation(days, P_0, K, r, daily_active_percentage, flip_supply, locked_flip, basic_nfts, complex_nfts, complex_nft_creation_percentage):
    total_basic_nfts_created = sum(basic_nfts.values())  # Total number of basic NFTs ever created

    # Tracking Arrays
    daily_flip_supply = np.zeros(days)
    daily_locked_flip = np.zeros(days)  # Tracking locked FLIP
    daily_basic_nfts_4x4 = np.zeros(days)
    daily_basic_nfts_8x8 = np.zeros(days)
    daily_complex_nfts = np.zeros(days)
    daily_players = np.zeros(days)

    # New tracking arrays for cumulative basic NFTs
    cumulative_basic_nfts_4x4 = np.zeros(days)
    cumulative_basic_nfts_8x8 = np.zeros(days)

    # Simulation Loop
    for day in range(days):
        # Update players using logistic growth model
        players = logistic_growth(day, P_0, K, r)
        daily_players[day] = players

        # New code to update cumulative basic NFTs
        if day == 0:
            cumulative_basic_nfts_4x4[day] = basic_nfts['4x4']
            cumulative_basic_nfts_8x8[day] = basic_nfts['8x8']
        else:
            cumulative_basic_nfts_4x4[day] = cumulative_basic_nfts_4x4[day - 1] + basic_nfts['4x4']
            cumulative_basic_nfts_8x8[day] = cumulative_basic_nfts_8x8[day - 1] + basic_nfts['8x8']

        # Determine the number of active players based on some percentage
        active_players = int(players * daily_active_percentage)

        # Daily puzzle solving and FLIP minting (locked)
        for _ in range(active_players):
            puzzle_type = random.choice(['4x4', '8x8'])
            flip_minted = mint_flip_tokens(puzzle_type)
            basic_nfts[puzzle_type] -= flip_minted
            locked_flip += flip_minted
            total_basic_nfts_created += flip_minted

            # Ensure we don't go negative on the basic NFT counts
            basic_nfts['4x4'] = max(basic_nfts['4x4'], 0)
            basic_nfts['8x8'] = max(basic_nfts['8x8'], 0)

        # Create new basic NFTs realistically over time
        basic_nfts['4x4'] += create_basic_nfts(day, 1, 0.05)  # Example growth rate
        basic_nfts['8x8'] += create_basic_nfts(day, 0.5, 0.025)  # Example growth rate

        # Complex NFT Creation Logic
        complex_nft_creators = int(players * complex_nft_creation_percentage)
        max_canvas_size = determine_max_canvas_size(total_basic_nfts_created)

        for _ in range(complex_nft_creators):
            # Determine the number of basic NFTs used for a complex NFT
            nfts_used = nfts_used_for_complex(32, 10)
            nft_used = '8x8' if max_canvas_size == '8x8' and basic_nfts['8x8'] >= nfts_used else '4x4'

            if basic_nfts[nft_used] >= nfts_used:
                basic_nfts[nft_used] -= nfts_used
                flip_supply += mint_flip_tokens(nft_used) * nfts_used
                locked_flip -= mint_flip_tokens(nft_used) * nfts_used
                complex_nfts += 1  # Increment complex NFT count

        # Prevent negative numbers
        flip_supply = max(flip_supply, 0)
        locked_flip = max(locked_flip, 0)
        complex_nfts = max(complex_nfts, 0)

        # Update daily metrics
        daily_flip_supply[day] = flip_supply
        daily_locked_flip[day] = locked_flip
        daily_basic_nfts_4x4[day] = basic_nfts['4x4']
        daily_basic_nfts_8x8[day] = basic_nfts['8x8']
        daily_complex_nfts[day] = complex_nfts

    return daily_flip_supply, daily_locked_flip, daily_basic_nfts_4x4, daily_basic_nfts_8x8, daily_complex_nfts, daily_players, cumulative_basic_nfts_4x4, cumulative_basic_nfts_8x8

# Dash App
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Simulation Dashboard'),
    html.Div([
        html.Label('Total Simulation Days'),
        dcc.Input(id='days-input', type='number', value=initial_days),
    ]),
    html.Div([
        html.Label('Initial Number of Players'),
        dcc.Input(id='p0-input', type='number', value=initial_P_0),
    ]),
    html.Div([
        html.Label('Carrying Capacity'),
        dcc.Input(id='k-input', type='number', value=initial_K),
    ]),
    html.Div([
        html.Label('Growth Rate'),
        dcc.Input(id='r-input', type='number', value=initial_r),
    ]),
    html.Div([
        html.Label('Average Active % of Users'),
        dcc.Input(id='daily-active-percentage-input', type='number', value=initial_daily_active_percentage),
    ]),
    html.Div([
        html.Label('Starting Available FLIP Supply'),
        dcc.Input(id='flip-supply-input', type='number', value=initial_flip_supply),
    ]),
    html.Div([
        html.Label('Starting Locked FLIP'),
        dcc.Input(id='locked-flip-input', type='number', value=initial_locked_flip),
    ]),
    html.Div([
        html.Label('Starting Total 4x4 Basic NFTs'),
        dcc.Input(id='basic-nfts-4x4-input', type='number', value=initial_basic_nfts['4x4']),
    ]),
    html.Div([
        html.Label('Starting Total 8x8 Basic NFTs'),
        dcc.Input(id='basic-nfts-8x8-input', type='number', value=initial_basic_nfts['8x8']),
    ]),
    html.Div([
        html.Label('Starting Total Complex NFTs'),
        dcc.Input(id='complex-nfts-input', type='number', value=initial_complex_nfts),
    ]),
    html.Div([
        html.Label('Complex NFT Creation Percentage'),
        dcc.Input(id='complex-nft-creation-percentage-input', type='number', value=initial_complex_nft_creation_percentage),
    ]),
    html.Div(id='charts')
])

@app.callback(
    Output('charts', 'children'),
    [Input('days-input', 'value'),
     Input('p0-input', 'value'),
     Input('k-input', 'value'),
     Input('r-input', 'value'),
     Input('daily-active-percentage-input', 'value'),
     Input('flip-supply-input', 'value'),
     Input('locked-flip-input', 'value'),
     Input('basic-nfts-4x4-input', 'value'),
     Input('basic-nfts-8x8-input', 'value'),
     Input('complex-nfts-input', 'value'),
     Input('complex-nft-creation-percentage-input', 'value')]
)
def update_charts(days, P_0, K, r, daily_active_percentage, flip_supply, locked_flip,
                  basic_nfts_4x4, basic_nfts_8x8, complex_nfts, complex_nft_creation_percentage):
    basic_nfts = {'4x4': basic_nfts_4x4, '8x8': basic_nfts_8x8}

    daily_flip_supply, daily_locked_flip, daily_basic_nfts_4x4, daily_basic_nfts_8x8, daily_complex_nfts, daily_players, cumulative_basic_nfts_4x4, cumulative_basic_nfts_8x8 = run_simulation(
        days, P_0, K, r, daily_active_percentage, flip_supply, locked_flip, basic_nfts, complex_nfts, complex_nft_creation_percentage
    )

    # Final Day Pie Chart Data
    final_day_unlocked_flip = daily_flip_supply[-1]
    final_day_locked_flip = daily_locked_flip[-1]

    # Pie Chart for Locked vs Unlocked FLIP
    pie_fig = go.Figure(data=[go.Pie(
        labels=['Unlocked', 'Locked'],
        values=[final_day_unlocked_flip, final_day_locked_flip],
        title='Locked vs Unlocked FLIP',
        textinfo='percent+label',
        pull=[0.1, 0],  # Slightly pull out the largest section
        hoverinfo='label+percent',  # Show label and percent on hover
        direction='clockwise',  # Ensure the layout is ordered clockwise
        sort=False,  # Don't sort the values
        insidetextorientation='radial'  # Arrange text to avoid overlap
    )])

    # Update traces to set the text position to outside and add connector lines
    pie_fig.update_traces(
        textposition='outside',
        textfont_size=8,
        marker=dict(line=dict(color='#000000', width=1))
    )

    # Update the layout to adjust the pie chart size, margins, and domain
    pie_fig.update_layout(
        height=600,  # Height of the pie chart
        width=2100,  # Width to match the line graph width
        showlegend=False,  # Hide the legend if needed
        title_y=0.95  # Vertically raise the title by 50 pixels
    )

    # Separate charts for Locked and Unlocked FLIP supply
    flip_fig = go.Figure()
    flip_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_flip_supply, mode='lines', name='Unlocked FLIP Supply'))
    flip_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_locked_flip, mode='lines', name='Locked FLIP'))
    flip_fig.update_layout(title='FLIP Supply Over Time', xaxis_title='Day', yaxis_title='Count', legend_title='FLIP Type')

    # New separate charts for Unlocked and Locked FLIP supply
    unlocked_flip_fig = go.Figure()
    unlocked_flip_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_flip_supply, mode='lines', name='Unlocked FLIP Supply'))
    unlocked_flip_fig.update_layout(title='Unlocked FLIP Supply Over Time', xaxis_title='Day', yaxis_title='Count')

    locked_flip_fig = go.Figure()
    locked_flip_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_locked_flip, mode='lines', name='Locked FLIP'))
    locked_flip_fig.update_layout(title='Locked FLIP Over Time', xaxis_title='Day', yaxis_title='Count')

    # Separate chart for basic NFTs
    basic_nft_fig = go.Figure()
    basic_nft_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_basic_nfts_4x4, mode='lines', name='4x4 Basic NFTs'))
    basic_nft_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_basic_nfts_8x8, mode='lines', name='8x8 Basic NFTs'))
    basic_nft_fig.update_layout(title='Basic NFT Creation Over Time', xaxis_title='Day', yaxis_title='Count', legend_title='NFT Type')

    # New separate chart for complex NFTs
    complex_nft_fig = go.Figure()
    complex_nft_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_complex_nfts, mode='lines', name='Complex NFTs'))
    complex_nft_fig.update_layout(title='Complex NFT Creation Over Time', xaxis_title='Day', yaxis_title='Count')

    player_fig = go.Figure()
    player_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_players, mode='lines', name='Player Growth'))
    player_fig.update_layout(title='Player Growth Over Time', xaxis_title='Day', yaxis_title='Count', legend_title='Metric')

    return [
        dcc.Graph(figure=pie_fig),
        dcc.Graph(figure=flip_fig),
        dcc.Graph(figure=unlocked_flip_fig),
        dcc.Graph(figure=locked_flip_fig),
        dcc.Graph(figure=basic_nft_fig),
        dcc.Graph(figure=complex_nft_fig),
        dcc.Graph(figure=player_fig)
    ]

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
