# Delta Hedging Strategy

## Overview
This project implements a dynamic delta hedging strategy using real-time options data from Yahoo Finance to manage portfolio risk. The strategy involves calculating option deltas using the Black-Scholes model, dynamically adjusting hedge positions, and evaluating performance through backtesting.

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

## Usage
1. Clone the repository:
    ```bash
    git clone https://github.com/vedk2/Delta-Hedging-Strategy.git
    ```
2. Navigate to the project directory:
    ```bash
    cd Delta-Hedging-Strategy
    ```
3. Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```
4. Run the Jupyter Notebook `DeltaHedging (1).ipynb` to execute the strategy.

## Results
The backtesting results demonstrate that the dynamic hedging strategy significantly reduces portfolio risk compared to an unhedged position. Various metrics such as Sharpe ratio, maximum drawdown, and volatility are used to assess performance.

## Future Enhancements
- **Advanced Machine Learning Models:** Incorporate reinforcement learning for more sophisticated hedging strategies.
- **Multi-Asset Hedging:** Extend the strategy to support multi-asset portfolios.
- **Live Deployment:** Develop an automated system for executing the strategy in a live trading environment.

## Contributors
- **Ved Kulkarni**

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
