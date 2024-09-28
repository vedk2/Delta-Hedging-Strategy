# Delta Hedging Strategy

## Overview
This project implements a dynamic delta hedging strategy using real-time options data from Yahoo Finance to manage portfolio risk. The strategy involves calculating option deltas using the Black-Scholes model, dynamically adjusting hedge positions, and evaluating performance through backtesting.

**Note:** The Jupyter Notebook (`DeltaHedging (1).ipynb`) contains detailed explanations for each part of the strategy, including code, methodology, and visualizations.

## Motivation
Options trading involves significant risks due to changes in market conditions. This project aims to develop a systematic approach for minimizing delta risk, ensuring robust risk management for an options portfolio.

## Features
- **Real-Time Data Integration:** Fetches real-time stock and options data using the Yahoo Finance API.
- **Delta Calculation:** Uses the Black-Scholes model to calculate delta for various options.
- **Dynamic Rebalancing:** Automatically adjusts hedge positions based on real-time changes in delta.
- **Backtesting:** Compares hedged vs. unhedged positions over historical data.
- **Machine Learning Enhancements:** Incorporates predictive models to optimize rebalancing intervals.

## Implementation
1. **Data Collection:** Utilizes `yfinance` to gather real-time stock and options data.
2. **Delta Calculation:** Implements the Black-Scholes formula to calculate the delta of options.
3. **Dynamic Rebalancing:** Uses the calculated delta to determine the number of shares required to hedge the position.
4. **Backtesting:** Analyzes the performance of the strategy over historical data to evaluate its effectiveness.
5. **Optimization with Machine Learning:** Applies machine learning models to predict optimal times for re-hedging.


## How to Use the Delta Hedging Strategy

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/vedk2/Delta-Hedging-Strategy.git
    cd Delta-Hedging-Strategy
    ```



2. **Install Required Libraries**
     Install the necessary Python libraries using the following command:
     ```bash
    pip install numpy pandas yfinance scipy matplotlib
    ```

3. **Run the Jupyter Notebook**:
    Open and run the Jupyter Notebook (`DeltaHedging (1).ipynb`). Modify the parameters in the designated cell, such as `ticker`, `strike_price`, etc., to apply the strategy to any stock of your choice. You can directly use the `delta_hedging_strategy.py` file to implement the delta hedging strategy with any stock symbol of your choice.

4. **Interactive Parameters**:
    - **Ticker Symbol**: Choose any stock ticker (e.g., `AAPL`).
    - **Strike Price**: Set your desired strike price for the option.
    - **Time to Expiration**: Set the time to expiration in days.
    - **Risk-Free Rate**: Default is 0.05, modify as needed.
    - **Volatility**: Estimate or use historical volatility for the stock.

5. **Visualize Results**:
    The notebook will generate visualizations of the hedging strategy's performance, such as delta vs. stock price, hedged vs. unhedged portfolio values, and risk metrics.

6. **Disclaimer**:
    This strategy is for educational purposes only and should not be used for actual trading.


## Results
This project is currently in the development and testing phase, but shows that portfolio value is increasing over time. The results presented here are for educational purposes only and should not be used as the basis for real-world trading. Overall, The backtesting results show promise in reducing portfolio risk compared to an unhedged position, but the strategy is still being refined and has not been validated for live trading environments.

## Future Enhancements
- **Advanced Machine Learning Models:** Incorporate reinforcement learning for more sophisticated hedging strategies.
- **Multi-Asset Hedging:** Extend the strategy to support multi-asset portfolios.
- **Live Deployment:** Develop an automated system for executing the strategy in a live trading environment.

## Contributors
- **Ved Kulkarni**
To connect, email ved.kulkarni628@gmail.com.

