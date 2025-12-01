import pandas as pd
import numpy as np
from src.strategies import BaseStrategy
try:
    from src.cpp import bridge
except ImportError:
    bridge = None

class CppStrategy(BaseStrategy):
    """
    A strategy that uses C++ accelerated indicators.
    """
    def __init__(self, rsi_window=14, ma_window=50, vol_window=20):
        super().__init__()
        self.rsi_window = rsi_window
        self.ma_window = ma_window
        self.vol_window = vol_window

    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        print("--- Creating C++ Strategy Features ---")

        bridge.load_library()

        close_prices = df['Close'].values

        # 1. Calculate SMA using C++
        df['SMA_Cpp'] = bridge.calculate_sma(close_prices, self.ma_window)

        # 2. Calculate EMA using C++ (using same window for demo)
        df['EMA_Cpp'] = bridge.calculate_ema(close_prices, self.ma_window)

        # 3. Calculate RSI using C++
        df['RSI_Cpp'] = bridge.calculate_rsi(close_prices, self.rsi_window)

        # 4. Calculate Volatility (StdDev) using C++
        df['Vol_Cpp'] = bridge.calculate_stddev(close_prices, self.vol_window)

        # 5. Calculate Max Drawdown (Running) using C++
        df['DD_Cpp'] = bridge.calculate_max_drawdown(close_prices)

        print("--- C++ Strategy Features Created ---")
        return df

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        print("--- Creating C++ Strategy Signals ---")

        df['Signal'] = 0

        # Buy signal
        df.loc[df['RSI_Cpp'] < 30, 'Signal'] = 1

        # Sell signal
        df.loc[df['RSI_Cpp'] > 70, 'Signal'] = -1

        # Filter out NaN signals (from beginning of data)
        df['Signal'] = df['Signal'].fillna(0)

        print("--- C++ Strategy Signals Created ---")
        return df

    def __str__(self):
        return f"CppStrategy(RSI={self.rsi_window}, MA={self.ma_window})"
