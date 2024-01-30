import vectorbtpro as vbt
import pandas as pd
import numpy as np

vbt.settings.set_theme("dark")

symbols = [
    "NASDAQ:META",
    "NASDAQ:AMZN",
    "NASDAQ:AAPL",
    "NASDAQ:NFLX",
    "NASDAQ:GOOG",
]

data = vbt.TVData.pull(symbols, timeframe="hourly")

data = data.xloc["2020":None]

price = data.hlc3

bullish_patterns = {
    "double_bottom": [5, 1, 3, 1, 5],
    "exp_triangle": [3, 4, 2, 5, 1, 6],
    "asc_triangle": [1, 5, 2, 5, 3, 6],
    "symm_triangle": [1, 6, 2, 5, 3, 6],
    "pennant": [6, 1, 5, 2, 4, 3, 6]
}
bearish_patterns = {
    "head_and_shoulders": [1, 4, 2, 6, 2, 4, 1],
    "double_top": [1, 5, 3, 5, 1],
    "desc_triangle": [6, 2, 5, 2, 4, 1],
    "symm_triangle": [6, 1, 5, 2, 4, 1],
    "pennant": [1, 6, 2, 5, 3, 4, 1]
}

pd.Series(bullish_patterns["double_bottom"]).vbt.plot().show()

min_window = 24
max_window = 24 * 30

def detect_patterns(patterns):
    return vbt.PatternRanges.from_pattern_search(
        price,
        open=data.open,  # OHLC for plotting
        high=data.high,
        low=data.low,
        close=data.close,
        pattern=patterns,
        window=min_window,
        max_window=max_window,
        execute_kwargs=dict(  # multithreading
            engine="threadpool", 
            chunk_len="auto", 
            show_progress=True
        )
    )

bullish_matches = detect_patterns(
    vbt.Param(
        bullish_patterns, 
        name="bullish_pattern"
    )
)
bearish_matches = detect_patterns(
    vbt.Param(
        bearish_patterns, 
        name="bearish_pattern"
    )
)

vbt.settings.plotting.auto_rangebreaks = True  # for stocks

display_column = bullish_matches.count().idxmax()

bullish_matches.plot(column=display_column, fit_ranges=True).show()

# zoom on particular areas

display_match = 3

bullish_matches.plot(
    column=display_column, 
    fit_ranges=display_match
).show()

entries = bullish_matches.last_pd_mask
exits = bearish_matches.last_pd_mask

entries, exits = entries.vbt.x(exits)

# Establish Portfolio

pf = vbt.Portfolio.from_signals(data, entries, exits)

mean_total_return.vbt.heatmap(
    x_level="bearish_pattern", 
    y_level="bullish_pattern"
).show()
