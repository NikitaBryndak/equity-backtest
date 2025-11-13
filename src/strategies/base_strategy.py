import pandas as pd

class BaseStrategy:
    """Base template for a trading strategy.

    Subclass and implement the required methods:
      - generate_features(df: pd.DataFrame) -> pd.DataFrame: compute and attach feature columns.
      - generate_signals(df: pd.DataFrame) -> pd.DataFrame: produce trading signals (-1, 0, 1).
        Implementations should return df with signals assigned to them in a 'Signal' column.

    If a subclass does not implement these methods, the base implementations will raise NotImplementedError.

    Example:
        class MyStrategy(BaseStrategy):
            def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
                df['ma10'] = df['close'].rolling(10).mean()
                return df

            def generate_signals(self, df: pd.DataFrame) -> pd.Dataframe:
                df['signal'] = (df['close'] > df['ma10']).astype(int)
                return df
    """

    def __init__(self) -> None:
        pass
    
    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate and return feature columns for df.

        Args:
            df (pandas.DataFrame): Historical asset data.

        Returns:
            pandas.DataFrame: DataFrame with added feature columns.
        """
        print("--- Creating Strategy Features ---")
        print("--- Strategy Features Created ---")
        raise NotImplementedError("Implement generate_features() before using it.")

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate and return trading signals for df.

        Args:
            df (pandas.DataFrame): DataFrame with features computed.

        Returns:
            pandas.DataFrame: Signals indexed like df (e.g. -1, 0, 1) in a 'Signal' column
        """
        print("--- Creating Strategy Signals ---")
        print("--- Strategy Signals Created ---")
        raise NotImplementedError("Implement generate_signals() before using it.")
        
    def __str__(self):
        return "Template Strategy"