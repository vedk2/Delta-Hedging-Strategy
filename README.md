Delta Hedging Strategy
Overview
This project implements a dynamic delta hedging strategy using real-time options data from Yahoo Finance to manage portfolio risk. The strategy involves calculating option deltas using the Black-Scholes model, dynamically adjusting hedge positions, and evaluating performance through backtesting.

Motivation
Options trading involves significant risks due to changes in market conditions. This project aims to develop a systematic approach for minimizing delta risk, ensuring robust risk management for an options portfolio.

Features
Real-Time Data Integration: Fetches real-time stock and options data using the Yahoo Finance API.
Delta Calculation: Uses the Black-Scholes model to calculate delta for various options.
Dynamic Rebalancing: Automatically adjusts hedge positions based on real-time changes in delta.
Backtesting: Compares hedged vs. unhedged positions over historical data.
Machine Learning Enhancements: Incorporates predictive models to optimize rebalancing intervals.
Implementation
Data Collection: Utilizes yfinance to gather real-time stock and options data.
Delta Calculation: Implements the Black-Scholes formula to calculate the delta of options.
Dynamic Rebalancing: Uses the calculated delta to determine the number of shares required to hedge the position.
Backtesting: Analyzes the performance of the strategy over historical data to evaluate its effectiveness.
Optimization with Machine Learning: Applies machine learning models to predict optimal times for re-hedging.
Usage
