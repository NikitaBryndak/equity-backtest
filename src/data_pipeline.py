import os
import pandas as pd
import warnings
import yfinance as yf

warnings.filterwarnings('ignore')
class DataLoader:
    
    def load_data(self, ticker: str):   
        print("--- Loading Data... ---")
        # Resolve project root and data directory reliably (file-location based)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        data_dir = os.path.join(base_dir, 'data')
        filepath = os.path.join(data_dir, f"{ticker}.csv")

        # download_data will ensure the directory exists
        if not os.path.exists(filepath):
            self._download_data(ticker, data_dir)

        try:
            df = pd.read_csv(filepath)
        except FileNotFoundError:
            raise FileNotFoundError(f"No file at {filepath}")

        df['Date'] = pd.to_datetime(df['Date'], utc=True)
        df.set_index('Date', inplace=True)
        
        df.sort_index(inplace=True)
            
        # TODO: Make resampling frequency configurable
        df = df.resample('1D').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()    
        
        if df[['Open', 'High', 'Low', 'Close']].isnull().any().any():
            df.fillna(method='ffill', inplace=True)
            
        print("--- Data is loaded ---")
        return df
    
    def _download_data(self, ticker: str, data_dir: str) -> str:
        """Download daily history for *ticker* into *data_dir*."""
        os.makedirs(data_dir, exist_ok=True)
        dest_path = os.path.join(data_dir, f"{ticker}.csv")

        ticker_obj = yf.Ticker(ticker)
        history = ticker_obj.history(period="max", interval="1d")
        if history.empty:
            raise ValueError(f"No price history returned for {ticker}")

        history.to_csv(dest_path)
        return dest_path