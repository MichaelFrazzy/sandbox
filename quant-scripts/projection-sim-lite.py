import plotly.io as pio
pio.renderers.default = "jupyterlab"
import vectorbtpro as vbt
vbt.settings.set_theme("dark")

SYMBOL = "BTC-USD"
TIMEFRAME = "1 hour"
START = "one year ago"

LAST_N_BARS = 66
PRED_N_BARS = 12

GIF_FNAME = "projections.gif"
GIF_N_BARS = 72
GIF_FPS = 4
GIF_PAD = 0.01

data = vbt.YFData.pull(SYMBOL, timeframe=TIMEFRAME, start=START)

def find_patterns(data):
    price = data.hlc3
    pattern = price.values[-LAST_N_BARS:]
    pattern_ranges = price.vbt.find_pattern(
        pattern=pattern,
        rescale_mode="rebase",
        overlap_mode="allow",
        wrapper_kwargs=dict(freq=TIMEFRAME)
    )
    pattern_ranges = pattern_ranges.status_closed
    return pattern_ranges

pattern_ranges = find_patterns(data)

def plot_projections(data, pattern_ranges, **kwargs):
    projection_ranges = pattern_ranges.with_delta(
        PRED_N_BARS,
        open=data.open,
        high=data.high,
        low=data.low,
        close=data.close,
    )
    projection_ranges = projection_ranges.status_closed
    return projection_ranges.plot_projections(
        plot_past_period=LAST_N_BARS, 
        **kwargs,
    )

plot_projections(data, pattern_ranges, plot_bands=True).show()

def plot_frame(frame_index, **kwargs):
    sub_data = data.loc[:frame_index[-1]]
    pattern_ranges = find_patterns(sub_data)
    if pattern_ranges.count() < 3:
        return None
    return plot_projections(sub_data, pattern_ranges, **kwargs)

vbt.save_animation(
    GIF_FNAME,
    data.index[-GIF_N_BARS:],
    plot_frame,
    plot_projections=False,
    delta=1,
    fps=GIF_FPS,
    writer_kwargs=dict(loop=0),
    yaxis_range=[
        data.low.iloc[-GIF_N_BARS:].min() * (1 - GIF_PAD), 
        data.high.iloc[-GIF_N_BARS:].max() * (1 + GIF_PAD)
    ],
)
