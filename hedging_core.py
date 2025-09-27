import numpy as np
import pandas as pd
from scipy.stats import norm
from dataclasses import dataclass

TRADING_DAYS = 252
CONTRACT_MULTIPLIER = 100  # shares per option contract

# ---------- Helpers ----------
def _ensure_close_column(df: pd.DataFrame) -> pd.DataFrame:
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
        elif "close" in out.columns:
            out["Close"] = out["close"]
        elif out.shape[1] == 1:
            out.columns = ["Close"]
        else:
            raise KeyError("No 'Close' or 'Adj Close' in price DataFrame.")

    out.index = pd.to_datetime(out.index)
    out = out.sort_index()
    return out

def _safe_time_to_expiry(current_date, expiry_date):
    dt_days = (expiry_date - current_date).days
    return max(dt_days / 365.0, 1e-6)

def _bs_d1(S, K, T, r, sigma):
    return (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))

def bs_price(S, K, T, r, sigma, option_type="call"):
    T = max(T, 1e-12); sigma = max(sigma, 1e-8)
    d1 = _bs_d1(S, K, T, r, sigma)
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

def bs_delta(S, K, T, r, sigma, option_type="call"):
    T = max(T, 1e-12); sigma = max(sigma, 1e-8)
    d1 = _bs_d1(S, K, T, r, sigma)
    return norm.cdf(d1) if option_type == "call" else norm.cdf(d1) - 1.0

@dataclass
class CostModel:
    fee_per_share: float = 0.0
    slippage_bps: float = 0.0

def realized_vol(close_prices: pd.Series, lookback: int = 20) -> float:
    rets = np.log(close_prices).diff().dropna()
    return float(rets.tail(lookback).std() * np.sqrt(TRADING_DAYS)) if len(rets) else 0.2

def round_to_lot(qty: float, lot: int) -> int:
    return int(np.round(qty / lot) * lot) if lot > 1 else int(np.round(qty))

# ---------- Backtest ----------
def delta_hedge_backtest(
    df_prices: pd.DataFrame,
    strike: float,
    expiry: pd.Timestamp,
    r: float,
    sigma: float,
    option_type: str = "call",
    contracts: int = 1,
    band_shares: float = 0.0,
    lot_size: int = 1,
    cooldown_days: int = 0,
    cost_model: CostModel = CostModel(),
):
    df = _ensure_close_column(df_prices).copy()
    df = df.dropna(subset=["Close"])
    if df.empty:
        return pd.DataFrame()

    df["Date"] = pd.to_datetime(df.index).tz_localize(None)
    df["T"] = df["Date"].apply(lambda d: _safe_time_to_expiry(d, pd.to_datetime(expiry)))
    df["S"] = df["Close"].astype(float)
    df["OptionPrice"] = df.apply(lambda r0: bs_price(r0["S"], strike, r0["T"], r, sigma, option_type), axis=1)
    df["Delta"] = df.apply(lambda r0: bs_delta(r0["S"], strike, r0["T"], r, sigma, option_type), axis=1)
    df["DeltaSharesTarget"] = df["Delta"] * contracts * CONTRACT_MULTIPLIER

    held_shares, cash = 0.0, float(df["OptionPrice"].iloc[0] * contracts * CONTRACT_MULTIPLIER)
    last_trade_idx = -10_000
    rows = []

    for i, row in enumerate(df.itertuples()):
        cash *= (1.0 + r / TRADING_DAYS)

        target = row.DeltaSharesTarget
        diff = target - held_shares
        trade_qty, exec_px = 0, row.S

        if abs(diff) > band_shares and (i - last_trade_idx) >= cooldown_days:
            trade_qty = round_to_lot(diff, lot_size)
            if trade_qty > 0:  # buy
                exec_px = row.S * (1.0 + cost_model.slippage_bps / 10_000.0)
            elif trade_qty < 0:  # sell
                exec_px = row.S * (1.0 - cost_model.slippage_bps / 10_000.0)
            trade_cost = trade_qty * exec_px + abs(trade_qty) * cost_model.fee_per_share
            cash -= trade_cost
            held_shares += trade_qty
            last_trade_idx = i

        V = held_shares * row.S + cash
        C = row.OptionPrice * contracts * CONTRACT_MULTIPLIER
        rows.append({
            "Date": row.Date,
            "S": row.S,
            "OptionPrice": row.OptionPrice,
            "Delta": row.Delta,
            "DeltaSharesTarget": target,
            "HeldShares": held_shares,
            "TradeQty": trade_qty,
            "ExecPx": exec_px if trade_qty != 0 else np.nan,
            "Cash": cash,
            "ReplicatingV": V,
            "OptionValue": C,
            "HedgingError": V - C
        })

    return pd.DataFrame(rows).set_index("Date")
