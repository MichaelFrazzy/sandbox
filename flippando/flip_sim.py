# V5

import numpy as np
import random
import plotly.graph_objects as go

# Simulation Parameters
days = 365 * 2  # Total simulation days (2 years)
P_0 = 100  # Initial number of players
K = 1000000  # Carrying capacity (maximum number of players)
r = 0.01  # Growth rate
daily_active_percentage = 0.1  # Average active % of users

# FLIP and NFT Parameters
flip_supply = 10000  # Starting available FLIP supply (unlocked for the sake of simulation realism)
locked_flip = 5000  # Starting Locked FLIP within basic NFTs (for realism)
basic_nfts = {'4x4': 100, '8x8': 50}  # Starting total basic NFTs created by type (for realism)
complex_nfts = 0  # Starting total complex NFTs created (for realism)
total_basic_nfts_created = sum(basic_nfts.values())  # Total number of basic NFTs ever created

# Complex NFT Creation Parameters
complex_nft_creation_percentage = 0.005  # Percentage of players who create complex NFTs each day

# Tracking Arrays
daily_flip_supply = np.zeros(days)
daily_locked_flip = np.zeros(days)  # Tracking locked FLIP
daily_basic_nfts_4x4 = np.zeros(days)
daily_basic_nfts_8x8 = np.zeros(days)
cumulative_basic_nfts_4x4 = np.zeros(days)
cumulative_basic_nfts_8x8 = np.zeros(days)
daily_complex_nfts = np.zeros(days)
daily_players = np.zeros(days)

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

# New function to determine the number of basic NFTs used for a complex NFT
def nfts_used_for_complex(mean, std_dev):
    """Determine number of basic NFTs used for a complex NFT based on normal distribution."""
    nfts_used = int(np.random.normal(mean, std_dev))
    # Ensure the number of NFTs used is at least 1 and not more than the mean + 3*std_dev
    return max(1, min(nfts_used, mean + 3 * std_dev))

# New function to realistically create basic NFTs over time
def create_basic_nfts(day, initial_supply, growth_rate):
    """Realistically create basic NFTs over time."""
    # Assuming a linear increase over time, could be modified for other growth patterns
    return initial_supply + day * growth_rate

# Simulation Loop
for day in range(days):
    # Update players using logistic growth model
    players = logistic_growth(day, P_0, K, r)
    daily_players[day] = players

    # Cumulative basic NFT creation
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

# Show the updated pie chart
pie_fig.show()

# Visualization
# Separate charts for Locked and Unlocked FLIP supply
flip_fig = go.Figure()
flip_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_flip_supply, mode='lines', name='Unlocked FLIP Supply'))
flip_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_locked_flip, mode='lines', name='Locked FLIP'))
flip_fig.update_layout(title='FLIP Supply Over Time', xaxis_title='Day', yaxis_title='Count', legend_title='FLIP Type')
flip_fig.show()

# New separate charts for Unlocked and Locked FLIP supply
unlocked_flip_fig = go.Figure()
unlocked_flip_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_flip_supply, mode='lines', name='Unlocked FLIP Supply'))
unlocked_flip_fig.update_layout(title='Unlocked FLIP Supply Over Time', xaxis_title='Day', yaxis_title='Count')
unlocked_flip_fig.show()

locked_flip_fig = go.Figure()
locked_flip_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_locked_flip, mode='lines', name='Locked FLIP'))
locked_flip_fig.update_layout(title='Locked FLIP Over Time', xaxis_title='Day', yaxis_title='Count')
locked_flip_fig.show()

# Separate chart for basic NFTs
basic_nft_fig = go.Figure()
basic_nft_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_basic_nfts_4x4, mode='lines', name='4x4 Basic NFTs'))
basic_nft_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_basic_nfts_8x8, mode='lines', name='8x8 Basic NFTs'))
basic_nft_fig.update_layout(title='Basic NFT Creation Over Time', xaxis_title='Day', yaxis_title='Count', legend_title='NFT Type')
basic_nft_fig.show()

# Cumulative NFT charts

cumulative_nft_fig = go.Figure()
cumulative_nft_fig.add_trace(go.Scatter(x=np.arange(days), y=cumulative_basic_nfts_4x4, mode='lines', name='Cumulative 4x4 Basic NFTs'))
cumulative_nft_fig.add_trace(go.Scatter(x=np.arange(days), y=cumulative_basic_nfts_8x8, mode='lines', name='Cumulative 8x8 Basic NFTs'))
cumulative_nft_fig.update_layout(title='Cumulative Basic NFT Creation Over Time', xaxis_title='Day', yaxis_title='Count', legend_title='NFT Type')
cumulative_nft_fig.show()

# New separate chart for complex NFTs
complex_nft_fig = go.Figure()
complex_nft_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_complex_nfts, mode='lines', name='Complex NFTs'))
complex_nft_fig.update_layout(title='Complex NFT Creation Over Time', xaxis_title='Day', yaxis_title='Count')
complex_nft_fig.show()

# Separate chart for player growth
player_fig = go.Figure()
player_fig.add_trace(go.Scatter(x=np.arange(days), y=daily_players, mode='lines', name='Player Growth'))
player_fig.update_layout(title='Player Growth Over Time', xaxis_title='Day', yaxis_title='Count', legend_title='Metric')
player_fig.show()
