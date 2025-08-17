import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
from pandas_datareader import data as pdr
from datetime import date, timedelta, datetime
import plotly.express as px

from hedging_core import delta_hedge_backtest, realized_vol, CostModel

st.set_page_config(page_title="Delta Hedging Dashboard", layout="wide")

st.title("Delta Hedging Dashboard")
st.caption("Backtest a discrete delta-hedging strategy; compare replicating portfolio vs. option value.")

# ------------------------------------------------------------
# Sidebar inputs
# ------------------------------------------------------------
st.sidebar.title("Parameters")

src = st.sidebar.selectbox(
    "Price source",
    ["Yahoo Finance (online)", "Upload CSV", "Demo (synthetic)"],
    index=0,
)

ticker = st.sidebar.text_input("Ticker", value="AAPL")
today = date.today()
default_start = today - timedelta(days=365)
start_date = st.sidebar.date_input("Start date", value=default_start)
end_date = st.sidebar.date_input("End date", value=today)

option_type = st.sidebar.selectbox("Option type", ["call", "put"], index=0)

vol_mode = st.sidebar.radio("Volatility", ["Manual (const)", "Estimate from returns"], index=0)
sigma_manual = st.sidebar.number_input("σ (annualized) if Manual", min_value=0.0001, max_value=5.0, value=0.25, step=0.01)

r = st.sidebar.number_input("Risk-free r (annual)", min_value=-0.05, max_value=0.2, value=0.05, step=0.005, format="%.4f")
contracts = st.sidebar.number_input("Contracts", min_value=1, step=1, value=1)

st.sidebar.markdown("---")
st.sidebar.subheader("Hedge Controls")
band_shares = st.sidebar.number_input("Re-hedge band (shares)", min_value=0.0, value=25.0, step=5.0)
lot_size = st.sidebar.number_input("Lot size (shares)", min_value=1, value=1, step=1)
cooldown_days = st.sidebar.number_input("Cooldown (days)", min_value=0, value=0, step=1)

st.sidebar.markdown("---")
st.sidebar.subheader("Transaction Costs")
fee_per_share = st.sidebar.number_input("Fee per share ($)", min_value=0.0, value=0.005, step=0.001, format="%.4f")
slippage_bps = st.sidebar.number_input("Slippage (bps)", min_value=0.0, value=2.0, step=0.5)

force_refresh = st.sidebar.checkbox("Force refresh data (clear cache)", value=False)
debug_fetch = st.sidebar.checkbox("Show fetch debug info", value=False)
run_btn = st.sidebar.button("Run Backtest", use_container_width=True)

if force_refresh:
    st.cache_data.clear()

# ------------------------------------------------------------
# Helpers: normalization + fetchers
# ------------------------------------------------------------
def _normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure we have Close; flatten MultiIndex; keep standard columns."""
    out = df.copy()
    if isinstance(out.columns, pd.MultiIndex):
        out.columns = [c[-1] if isinstance(c, tuple) else c for c in out.columns]

    cols = list(map(str, out.columns))
    keep = [c for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"] if c in cols]
    if keep:
        out = out[keep].copy()

    if "Close" not in out.columns:
        if "Adj Close" in out.columns:
            out["Close"] = out["Adj Close"]
        elif out.shape[1] == 1:
            out.columns = ["Close"]
        else:
            raise KeyError(f"No Close/Adj Close found. Columns={list(out.columns)}")

    out.index = pd.to_datetime(out.index)
    out = out.sort_index()
    return out

@st.cache_data(show_spinner=False, ttl=900)
def fetch_prices(ticker: str, start: date, end: date) -> pd.DataFrame:
    """
    Try Yahoo (download), then Yahoo (history), then Stooq.
    Clamp end to today and make it inclusive. Return normalized OHLCV or empty.
    """
    end_clamped = min(end, date.today())
    end_plus = end_clamped + timedelta(days=1)  

    
    try:
        df = yf.download(
            ticker, start=start, end=end_plus,
            interval="1d", auto_adjust=False, progress=False,
            threads=False, group_by="column"
        )
        if df is not None and not df.empty:
            return _normalize_ohlcv(df)
    except Exception as e:
        pass  

    
    try:
        df = yf.Ticker(ticker).history(start=start, end=end_plus, interval="1d", auto_adjust=False)
        if df is not None and not df.empty:
            return _normalize_ohlcv(df)
    except Exception as e:
        pass

    
    try:
        df = pdr.DataReader(ticker, "stooq", start=start, end=end_clamped)
        if df is not None and not df.empty:
            df = df.sort_index()
            
            rename = {c: c.capitalize() for c in df.columns}
            df = df.rename(columns=rename)
            return _normalize_ohlcv(df)
    except Exception as e:
        pass

    return pd.DataFrame()

def load_csv(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    if "Date" in df.columns:
        df = df.set_index("Date")
    elif "date" in df.columns:
        df = df.set_index("date")
    if not np.issubdtype(pd.Index(df.index).dtype, np.datetime64):
        df.index = pd.to_datetime(df.index, errors="coerce")
    df = df.dropna()
    return _normalize_ohlcv(df)

def make_synthetic(start: date, end: date, S0: float = 100.0, mu=0.08, sigma=0.25) -> pd.DataFrame:
    dates = pd.date_range(start=start, end=end, freq="B")
    if len(dates) == 0:
        dates = pd.date_range(end=end, periods=252, freq="B")
    dt = 1.0 / 252.0
    rng = np.random.default_rng(42)
    rets = rng.normal((mu - 0.5 * sigma**2) * dt, sigma * np.sqrt(dt), len(dates))
    S = S0 * np.exp(np.cumsum(rets))
    df = pd.DataFrame({"Close": S}, index=dates)
    df["Open"] = df["Close"].shift(1).fillna(df["Close"])
    df["High"] = df[["Open", "Close"]].max(axis=1)
    df["Low"] = df[["Open", "Close"]].min(axis=1)
    df["Volume"] = 0
    return df[["Open", "High", "Low", "Close", "Volume"]]

# ------------------------------------------------------------
# UI placeholder
# ------------------------------------------------------------
st.info("Set your parameters in the left sidebar and click **Run Backtest**.")

uploaded_file = None
if src == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV with columns: Date, Close (and optionally Open, High, Low, Volume)",
        type=["csv"]
    )

# ------------------------------------------------------------
# Run
# ------------------------------------------------------------
if run_btn:
    with st.spinner("Loading prices…"):
        if src == "Yahoo Finance (online)":
            prices = fetch_prices(ticker, start_date, end_date)
            if prices.empty:
                st.error(
                    "No price data returned from Yahoo/Stooq. "
                    "Try a different ticker (AAPL/MSFT), ensure end ≤ today, or switch to CSV/Demo mode."
                )
                st.stop()
        elif src == "Upload CSV":
            if uploaded_file is None:
                st.error("Please upload a CSV file.")
                st.stop()
            prices = load_csv(uploaded_file)
        else:
            prices = make_synthetic(start_date, end_date, S0=100.0)

    if debug_fetch:
        st.write("Fetched rows:", len(prices), "Columns:", list(prices.columns))
        if not prices.empty:
            st.write(prices.head())

    series_close = prices["Close"]
    if series_close.empty:
        st.error("Loaded data has no rows after normalization.")
        st.stop()

    spot = float(series_close.iloc[-1])

    c1, c2 = st.columns(2)
    with c1:
        strike = st.number_input("Strike", min_value=0.0, value=float(round(spot, 2)))
    with c2:
        expiry = st.date_input("Expiry date", value=min(end_date, today + timedelta(days=30)))

    sigma = float(sigma_manual) if (vol_mode == "Manual (const)") else realized_vol(series_close, lookback=20)
    if vol_mode != "Manual (const)":
        st.write(f"Estimated σ (20d realized): **{sigma:.3f}**")

    with st.spinner("Running backtest…"):
        results = delta_hedge_backtest(
            df_prices=prices,
            strike=float(strike),
            expiry=pd.to_datetime(expiry),
            r=float(r),
            sigma=float(sigma),
            option_type=option_type,
            contracts=int(contracts),
            band_shares=float(band_shares),
            lot_size=int(lot_size),
            cooldown_days=int(cooldown_days),
            cost_model=CostModel(fee_per_share=float(fee_per_share), slippage_bps=float(slippage_bps)),
        )

    if results.empty:
        st.warning("Backtest produced no rows — check the date range and data source.")
        st.stop()

    # --- KPIs (robust against dtype issues) ---
    q = pd.to_numeric(results["TradeQty"], errors="coerce").fillna(0.0)
    fees_paid = float(q.abs().sum() * float(fee_per_share))
    total_trades = int((q != 0).sum())
    avg_trade = float(q[q != 0].abs().mean() if (q != 0).any() else 0.0)

    final_err = float(results["HedgingError"].iloc[-1])
    max_abs_err = float(results["HedgingError"].abs().max())

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total trades", f"{total_trades}")
    k2.metric("Final hedging error ($)", f"{final_err:.2f}")
    k3.metric("Max |hedging error| ($)", f"{max_abs_err:.2f}")
    k4.metric("Fees paid ($)", f"{fees_paid:.2f}")
    k5.metric("Avg trade size (sh)", f"{avg_trade:.1f}")

    # Charts & tables
    tab1, tab2, tab3 = st.tabs(["Charts", "Trades", "Full Data"])
    r2 = results.reset_index()

    with tab1:
        st.plotly_chart(px.line(r2, x="Date", y="S", title="Underlying Price"), use_container_width=True)
        st.plotly_chart(px.line(
            r2, x="Date", y=["OptionValue", "ReplicatingV"],
            title="Option Value vs Replicating Portfolio",
            labels={"value": "Value ($)", "variable": "Series"}
        ), use_container_width=True)
        st.plotly_chart(px.line(r2, x="Date", y="HedgingError", title="Hedging Error (V - C)"),
                        use_container_width=True)
        trades = results[results["TradeQty"] != 0].reset_index()
        if not trades.empty:
            st.plotly_chart(px.bar(trades, x="Date", y="TradeQty", title="Trade Quantities (shares)"),
                            use_container_width=True)

    with tab2:
        st.dataframe(results[results["TradeQty"] != 0][
            ["TradeQty", "ExecPx", "HeldShares", "DeltaSharesTarget"]
        ], use_container_width=True)

    with tab3:
        st.dataframe(results, use_container_width=True)

    st.download_button(
        "Download results (CSV)",
        data=results.to_csv().encode("utf-8"),
        file_name=f"{ticker}_{option_type}_delta_hedge_results.csv",
        mime="text/csv"
    )
