from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from strategies import BaseStrategy

class Backtester:
    def __init__(self, df: pd.DataFrame, strategies: List[BaseStrategy], initial_capital=10000.0, fee=0.001):
        self.df = df
        self.strategies = strategies
        self.initial_capital = initial_capital
        self.fee = fee
        self.returns = None
        
    def plot_equity(self) -> None:
        if self.returns is None:
            raise "Run .run() first"
        
        plt.figure(figsize=(12,6))
        for strategy in self.strategies:
            strategy_name = strategy.__class__.__name__
            self.returns[f'Strategy_Equity_{strategy_name}'].plot()
            
        plt.legend([s.__class__.__name__ for s in self.strategies])
        plt.title("Equity - For strategies")
        plt.ylabel('Portfolio size ($)')
        plt.xlabel('Date')
        plt.show()
         
    def run(self) -> None:
        print("--- BackTester running ---")
        compiled = pd.DataFrame(index=self.df.index.copy())
        activation_points = []

        for i, strategy in enumerate(self.strategies):
            print(f"--- Running Strategy {i+1}/{len(self.strategies)}: {strategy.__class__.__name__} ---")
            print(strategy)

            strategy_df = strategy.generate_features(self.df.copy())
            strategy_df = strategy.generate_signals(strategy_df)

            strategy_name = strategy.__class__.__name__

            strategy_df[f'Returns_{strategy_name}'] = strategy_df['Close'].pct_change()
            strategy_df[f'Position_{strategy_name}'] = strategy_df['Signal'].shift(1).fillna(0)
            strategy_df[f'Trades_{strategy_name}'] = strategy_df[f'Position_{strategy_name}'].diff().abs()
            
            strategy_df[f'Strategy_Returns_{strategy_name}'] = (
                strategy_df[f'Returns_{strategy_name}'] * strategy_df[f'Position_{strategy_name}']
            ) - (self.fee * strategy_df[f'Trades_{strategy_name}'])
            strategy_df[f'Strategy_Equity_{strategy_name}'] = (
                (1 + strategy_df[f'Strategy_Returns_{strategy_name}']).cumprod() * self.initial_capital
            )

            compiled[f'Returns_{strategy_name}'] = strategy_df[f'Returns_{strategy_name}']
            compiled[f'Position_{strategy_name}'] = strategy_df[f'Position_{strategy_name}']
            compiled[f'Trades_{strategy_name}'] = strategy_df[f'Trades_{strategy_name}']
            compiled[f'Strategy_Returns_{strategy_name}'] = strategy_df[f'Strategy_Returns_{strategy_name}']
            compiled[f'Strategy_Equity_{strategy_name}'] = strategy_df[f'Strategy_Equity_{strategy_name}']

            active_positions = strategy_df[strategy_df[f'Position_{strategy_name}'] != 0]
            if not active_positions.empty:
                activation_points.append(active_positions.index[0])
            else:
                activation_points.append(strategy_df[f'Strategy_Equity_{strategy_name}'].first_valid_index())
            print(activation_points)
            print(f"--- Strategy {i+1} completed ---")


        start_candidates = [idx for idx in activation_points if idx is not None]
        if not start_candidates:
            raise ValueError("No strategy produced valid signals; cannot run backtest.")

        start_index = max(start_candidates)
        compiled = compiled.loc[start_index:].copy()

        for strategy in self.strategies:
            equity_col = f'Strategy_Equity_{strategy.__class__.__name__}'
            if equity_col in compiled.columns and not compiled[equity_col].empty:
                base_val = compiled[equity_col].iloc[0]
                if pd.isna(base_val) or base_val == 0:
                    compiled[equity_col] = compiled[equity_col].fillna(method='bfill')
                    base_val = compiled[equity_col].iloc[0]
                if pd.isna(base_val) or base_val == 0:
                    compiled[equity_col] = self.initial_capital
                else:
                    compiled[equity_col] = (compiled[equity_col] / base_val) * self.initial_capital
        
        print("--- BackTester ended running ---")
        
        self.returns = compiled
        
    def get_metrics(self):
        if self.returns is None:
            raise "Run .run() first"
        stats = {
            "Total Return": [],
            "Annualized Return": [],
            "Annualized Volatility": [],
            "Max Drawdown": [],
            "Sharpe Ratio": []
        }
        self.returns.dropna(inplace=True)
        for strategy in self.strategies:
            strategy_name = strategy.__class__.__name__
            equity = self.returns[f'Strategy_Equity_{strategy_name}']

            total_return = (equity.iloc[-1] / equity.iloc[0]) - 1
            
            peak = equity.cummax()
            
            drawdown = (equity - peak) / peak
            max_drawdown = drawdown.min()
            
            length = (equity.index[-1] - equity.index[0]).days / 365.25
            annualised_return = (1 + total_return) ** (1 / length) - 1
            annualised_volatility = self.returns[f'Strategy_Returns_{strategy_name}'].std() * np.sqrt(365)
            
            sharpe_ratio = annualised_return / annualised_volatility
            stats["Total Return"].append(f"{total_return * 100:.2f}%")
            stats["Annualized Return"].append(f"{annualised_return * 100:.2f}%")
            stats["Annualized Volatility"].append(f"{annualised_volatility * 100:.2f}%")
            stats["Max Drawdown"].append(f"{max_drawdown * 100:.2f}%")
            stats["Sharpe Ratio"].append(f"{sharpe_ratio:.2f}")

        metrics_df = pd.DataFrame(stats, index=[s.__class__.__name__ for s in self.strategies])
        return metrics_df.to_dict(orient='index')