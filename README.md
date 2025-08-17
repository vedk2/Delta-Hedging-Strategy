# Delta Hedging Strategy  

[![Launch App](https://img.shields.io/badge/Streamlit-Live%20App-brightgreen?logo=streamlit)](https://delta-hedging-strategy-vedk2.streamlit.app/)  

---

## 📌 Overview  
This project implements a **dynamic delta hedging strategy** using real-time options data from Yahoo Finance to manage portfolio risk. The strategy calculates option deltas via the Black-Scholes model, dynamically adjusts hedge positions, and evaluates performance through backtesting.  

👉 **Try it live here:** [Delta Hedging Streamlit App](https://delta-hedging-strategy-vedk2.streamlit.app/)  

---

## 🎯 Motivation  
Options trading carries significant risks due to market volatility. This project provides a systematic framework for minimizing **delta risk**, enabling more robust **risk management** for options portfolios.  

---

## ✨ Features  
- **Interactive Web App** – Run the strategy directly in your browser via Streamlit.  
- **Real-Time Data Integration** – Fetches live stock & options data from Yahoo Finance.  
- **Delta Calculation** – Implements the Black-Scholes model to compute option delta.  
- **Dynamic Rebalancing** – Automatically adjusts hedge positions based on real-time delta changes.  
- **Backtesting** – Compares hedged vs. unhedged positions on historical data.  
- **Machine Learning Enhancements** – Leverages predictive models to optimize rebalancing intervals.  

---

## 🚀 How to Use  

### Option 1 – Use the Web App (Recommended)  
Simply open the app in your browser:  
👉 [Delta Hedging Streamlit App](https://delta-hedging-strategy-vedk2.streamlit.app/)  

### Option 2 – Run Locally  
1. **Clone the repository**:  
   ```bash
   git clone https://github.com/vedk2/Delta-Hedging-Strategy.git
   cd Delta-Hedging-Strategy
2. **Install dependencies
   pip install -r requirements.txt
3. **Run the app locally
   streamlit run streamlit_app.py
   
## 📊 Results
Backtesting shows that the hedged portfolio reduces exposure to market movements compared to an unhedged position. While results are promising, the strategy is still under development and not validated for live trading.

## 🔮 Future Enhancements

1. Reinforcement Learning for adaptive hedging strategies.
2. Multi-Asset Hedging for portfolios with multiple underlying securities.
3. Automated Live Deployment with broker integration.

## Contributors
- **Ved Kulkarni**
To connect, email ved.kulkarni628@gmail.com.

