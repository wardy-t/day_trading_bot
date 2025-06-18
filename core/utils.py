import pandas as pd
from ta.momentum import RSIIndicator
from ta.volume import VolumeWeightedAveragePrice

def calculate_rsi(close_series, period=14):
    rsi_indicator = RSIIndicator(close=close_series, window=period)
    return rsi_indicator.rsi().iloc[-1]

def calculate_vwap(bars: pd.DataFrame):
    vwap = VolumeWeightedAveragePrice(
        high=bars['high'],
        low=bars['low'],
        close=bars['close'],
        volume=bars['volume']
    )
    return vwap.vwap().iloc[-1]