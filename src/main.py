from data_pipeline import DataLoader 
from engine.backtester import Backtester
from strategies import (
    BuyAndHoldStrategy,
    MeanReversionStrategy,
    NumpyMomentumStrategy,
    TrendFollowingStrategy,
    XGBoostStrategy,
)

if __name__ == "__main__":    
    data = DataLoader.load_data()
    
    if data.empty:
        raise ValueError("No data loaded. Exiting.")
    else:

        backtester = Backtester(
            df=data, 
            strategies=[
                MeanReversionStrategy(),
                BuyAndHoldStrategy(), 
                TrendFollowingStrategy(short_window=20, long_window=50),
                NumpyMomentumStrategy(),
                XGBoostStrategy()
                ], 
            initial_capital=10000.0, 
            fee=0.001 
        )
        
        backtester.run()
        
        metrics = backtester.get_metrics()
        print("\n--- Metrics ---")
        for key, value in metrics.items():
            print(f"{key:<25}: {value}")
            
        backtester.plot_equity()
        
