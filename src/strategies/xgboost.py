import pandas as pd
from xgboost import XGBClassifier

# TODO: Add hyperparameter tunning for XGBoost model
class XGBoostStrategy:
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

    def __init__(self, lookahead_minutes = 15, train_ratio = 0.8, modelPath = None) -> None:
        self.lookahead_minutes = lookahead_minutes
        self.train_ratio = train_ratio
        self.modelPath = modelPath
        self.model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
        self.features = []
        
    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate and return feature columns for df.

        Args:
            df (pandas.DataFrame): Historical asset data.

        Returns:
            pandas.DataFrame: DataFrame with added feature columns.
        """
        print("--- Creating Strategy Features ---")
        
        # Bollinger Bands
        N = 20
        k = 2
        df[f'SMA_{N}'] = df['Close'].rolling(window=N).mean()
        df[f'STD_{N}'] = df['Close'].rolling(window=N).std()
        df[f'BBU_{N}_2.0'] = df[f'SMA_{N}'] + (k * df[f'STD_{N}'])
        df[f'BBL_{N}_2.0'] = df[f'SMA_{N}'] - (k * df[f'STD_{N}'])
        
        # MACD
        MACD_N_fast = 12
        MACD_N_slow = 26
        MACD_N_signal = 9
        df['EMA_fast'] = df['Close'].ewm(span=MACD_N_fast, adjust=False).mean()
        df['EMA_slow'] = df['Close'].ewm(span=MACD_N_slow, adjust=False).mean()
        df['MACD_Line'] = df['EMA_fast'] - df['EMA_slow']
        df['Signal_Line'] = df['MACD_Line'].ewm(span=MACD_N_signal, adjust=False).mean()
        df[f'MACDh_{MACD_N_fast}_{MACD_N_slow}_{MACD_N_signal}'] = df['MACD_Line'] - df['Signal_Line']
        
        # RSI (EMA)
        RSI_N = 14
        df['Change'] = df['Close'].diff()
        df['Gain'] = df['Change'].clip(lower=0)
        df['Loss'] = -df['Change'].clip(upper=0)
        
        df['Avg_Gain'] = df['Gain'].ewm(com=RSI_N-1, adjust=False).mean()
        df['Avg_Loss'] = df['Loss'].ewm(com=RSI_N-1, adjust=False).mean()
        
        df['RS'] = df['Avg_Gain'] / df['Avg_Loss']
        df[f'RSI_{RSI_N}'] = 100 - (100 / (1 + df['RS']))
        
        # Ptc Rolling Returns
        df['Return_5m'] = df['Close'].pct_change(5)
        df['Return_15m'] = df['Close'].pct_change(15)
        
        self.features = [
            f'BBU_{N}_2.0', f'BBL_{N}_2.0',
            f'MACDh_{MACD_N_fast}_{MACD_N_slow}_{MACD_N_signal}',
            f'RSI_{RSI_N}',
            'Return_5m', 
            'Return_15m'
        ]
        
        df['Target_Close'] = df['Close'].shift(-self.lookahead_minutes)
        df['Y_Target'] = (df['Target_Close'] > df['Close']).astype(int)
        
        print("--- Strategy Features Created ---")
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate and return trading signals for df.

        Args:
            df (pandas.DataFrame): DataFrame with features computed.

        Returns:
            pandas.DataFrame: Signals indexed like df (e.g. -1, 0, 1) in a 'Signal' column
        """
        print("--- Creating Strategy Signals ---")
        
        df = df.dropna()
        
        split_index = int(len(df) * self.train_ratio)
        if split_index <= 0 or split_index >= len(df):
            raise ValueError("Train/test split produced empty dataset; adjust train_ratio or ensure sufficient data")

        df_train = df.iloc[:split_index]
        df_test = df.iloc[split_index:]
        self._train(df_train)

        df['Signal'] = 0
        signals = self._predict(df_test)
        df.loc[signals.index, 'Signal'] = signals
        
        print("--- Strategy Signals Created ---")
        return df
    
    def _train(self, df_train) -> None | str:
        print(f"Training XGBoost. Dataset Length - {len(df_train)}")
        
        X_train = df_train[self.features]
        Y_train = df_train['Y_Target']
        
        self.model.fit(X_train, Y_train)
        
        print("Training finished")
        return
                  
    def _predict(self, df_predict):
        print(f"Creating Predictions...")
        
        X_predict = df_predict[self.features]
        
        predictions = self.model.predict(X_predict)
        
        signals = pd.Series(predictions, index=X_predict.index)
        signals = signals.replace(0, -1)
        
        return signals              
     
    def __str__(self):
        return "XGBoost Strategy"