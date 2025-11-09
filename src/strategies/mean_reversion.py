from .base_strategy import BaseStrategy

class MeanReversion(BaseStrategy):
    """
    MeanReversion(strategy)
    
    Simple mean-reversion strategy implemented with two simple moving averages (SMA).
    
    Description:
        This strategy computes a short-term and a long-term simple moving average on the
        'Close' price series and generates discrete trading signals:
          - Signal =  1 : go long (expect reversion up)
          - Signal = -1 : go short (expect reversion down)
          - Signal =  0 : neutral
    Parameters:
        short_window (int, optional): Window length for the short-term SMA. Default: 30.
        long_window  (int, optional): Window length for the long-term SMA. Default: 100.
    Public methods:
        generate_features(df)
            - Computes and appends two columns to df:
                'SMA_{short_window}' : short-term SMA of df['Close']
                'SMA_{long_window}'  : long-term SMA of df['Close']
            - Returns the modified DataFrame.
            - Notes: rolling means introduce NaNs for the initial rows until enough data is available.
        generate_signals(df)
            - Ensures a column 'Signal' exists on df and sets values according to the rule above.
            - Expected behavior: set 1 where Close < SMA_{long_window}, -1 where Close > SMA_{short_window},
              and 0 otherwise.
            - Returns the modified DataFrame.
    Input requirements:
        - df: pandas.DataFrame containing at least a numeric 'Close' column.
        - The method implementations assume time-ordered rows (e.g., datetime index or ascending rows).
    Behavioral notes and caveats:
        - The strategy is non-robust to NaNs produced by rolling computations; care should be taken to
          handle or drop NaNs before using signals for backtesting.
        - Parameters should be chosen with regard to data frequency (e.g., minutes vs days).
        - This class provides signal generation only; execution, risk management, and transaction costs
          must be handled by the caller/backtester.
    Example:
        >>> strategy = MeanReversion(short_window=20, long_window=50)
        >>> df = strategy.generate_features(df)   # adds SMA_20 and SMA_50
        >>> df = strategy.generate_signals(df)    # adds/updates 'Signal' column
    """
    

    def __init__(self, short_window=30, long_window=100):
        self.short_window = short_window
        self.long_window = long_window
        
    def generate_features(self, df):
        df[f'SMA_{self.short_window}'] = df['Close'].rolling(self.short_window).mean()
        df[f'SMA_{self.long_window}'] = df['Close'].rolling(self.long_window).mean()
        
        print("MeanReversion Feature are created...")
        
        return df
    
    def generate_signals(self, df):
        df['Signal'] = 0
        
        df.loc[df['Colse'] < df[f'SAM_{self.long_window}'], 'Signal'] = 1
        df.loc[df['Colse'] > df[f'SAM_{self.short_window}'], 'Signal'] = -1
        
        print("MeanReversion Signals are created...")
        
        return df
    
    def __str__(self):
        print_data = []
        print_data.append("------------------------")
        print_data.append("Mean Reversion Strategy")
        print_data.append("------------------------")
        print_data.append("LONG STRATEGY DESCRIPTION")
        print_data.append("------------------------")

        
        return "\n".join(print_data)