import numpy as np
import pandas as pd
from scipy.signal import lfilter
from .base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """Momentum strategy using log return smoothing with moving average filtering."""

    def __init__(self, window: int = 11, poly: int = 2, threshold: float = 0.05) -> None:
        if window < 3:
            raise ValueError("window must be at least 3")
        if poly < 1:
            raise ValueError("poly must be positive")
        self.window = int(window)
        self.poly = int(poly)
        self.threshold = float(threshold)

    def _resolve_window(self, length: int) -> int:
        window = min(self.window, max(length, 1))
        if window % 2 == 0:
            window = max(3, window - 1)
        if window <= self.poly:
            window = self.poly + 3
            if window % 2 == 0:
                window += 1
        return window

    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        print("--- Creating Strategy Features ---")
        if "Close" not in df:
            raise KeyError("DataFrame must contain a Close column")

        price_series = df["Close"].astype(float).replace([np.inf, -np.inf], np.nan).ffill().bfill()
        prices = price_series.to_numpy()

        if prices.size == 0:
            empty = np.array([], dtype=float)
            df["LogReturn"] = empty
            df["SmoothedReturn"] = empty
            df["Momentum"] = empty
            print("--- Strategy Features Created ---")
            return df

        safe_prices = np.clip(prices, a_min=1e-8, a_max=None)
        log_prices = np.log(safe_prices)
        log_returns = np.diff(log_prices, prepend=log_prices[0])

        window = self._resolve_window(prices.size)
        if prices.size < 3:
            smoothed = np.zeros_like(log_returns)
        else:
            kernel = np.ones(window, dtype=float) / window
            smoothed = lfilter(kernel, [1.0], log_returns)
            smoothed[: window - 1] = np.nan

        rolling_std = pd.Series(log_returns).rolling(window, min_periods=window).std(ddof=0).to_numpy()
        momentum = np.divide(smoothed, rolling_std + 1e-4)

        df["LogReturn"] = log_returns
        df["SmoothedReturn"] = smoothed
        df["Momentum"] = np.nan_to_num(momentum, nan=0.0, posinf=0.0, neginf=0.0)

        print("--- Strategy Features Created ---")
        return df

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        print("--- Creating Strategy Signals ---")
        if "Momentum" not in df:
            raise KeyError("Missing Momentum column; call generate_features first")

        momentum = np.nan_to_num(df["Momentum"].to_numpy(), nan=0.0)
        signal = np.zeros_like(momentum, dtype=int)
        signal[momentum > self.threshold] = 1
        signal[momentum < -self.threshold] = -1

        df["SignalStrength"] = momentum
        df["Signal"] = signal

        print("--- Strategy Signals Created ---")
        return df

    def __str__(self) -> str:
        return f"Momentum Strategy (window={self.window}, poly={self.poly}, threshold={self.threshold})"
