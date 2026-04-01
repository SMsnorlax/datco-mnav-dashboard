import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="DAT.co mNAV Dashboard", layout="wide")

COMPANY_NAME = "Strategy (MSTR)"
STOCK_TICKER = "MSTR"
BTC_TICKER = "BTC-USD"
CURRENT_BTC_HOLDINGS = 762_099
FALLBACK_BASIC_SHARES_OUTSTANDING = 283_552_947


@st.cache_data(ttl=60 * 60)
def load_price_data(period: str = "1y") -> pd.DataFrame:
    data = yf.download(
        [STOCK_TICKER, BTC_TICKER],
        period=period,
        interval="1d",
        auto_adjust=True,
        progress=False,
        group_by="column",
        threads=False,
    )

    if data is None or data.empty:
        return pd.DataFrame(columns=["date", "stock_close", "btc_close"])

    try:
        if isinstance(data.columns, pd.MultiIndex):
            stock_close = data[("Close", STOCK_TICKER)].rename("stock_close")
            btc_close = data[("Close", BTC_TICKER)].rename("btc_close")
        else:
            if "Close" in data.columns:
                # Single-ticker fallback shape; not expected here but safe.
                return pd.DataFrame(columns=["date", "stock_close", "btc_close"])
            stock_col = f"Close_{STOCK_TICKER}"
            btc_col = f"Close_{BTC_TICKER}"
            if stock_col not in data.columns or btc_col not in data.columns:
                return pd.DataFrame(columns=["date", "stock_close", "btc_close"])
            stock_close = data[stock_col].rename("stock_close")
            btc_close = data[btc_col].rename("btc_close")
    except Exception:
        return pd.DataFrame(columns=["date", "stock_close", "btc_close"])

    df = pd.concat([stock_close, btc_close], axis=1).dropna().reset_index()
    if df.empty:
        return pd.DataFrame(columns=["date", "stock_close", "btc_close"])

    first_col = df.columns[0]
    df = df.rename(columns={first_col: "date"})
    return df[["date", "stock_close", "btc_close"]]


@st.cache_data(ttl=60 * 60)
def get_shares_outstanding() -> float:
    ticker = yf.Ticker(STOCK_TICKER)
    info = {}
    try:
        info = ticker.info or {}
    except Exception:
        info = {}

    shares = info.get("sharesOutstanding")
    if shares and shares > 0:
        return float(shares)

    try:
        hist = ticker.history(period="5d", auto_adjust=True)
    except Exception:
        hist = pd.DataFrame()

    if not hist.empty and "Close" in hist.columns and not hist["Close"].dropna().empty:
        price = float(hist["Close"].dropna().iloc[-1])
        market_cap = info.get("marketCap")
        if market_cap and price > 0:
            return float(market_cap) / price

    return float(FALLBACK_BASIC_SHARES_OUTSTANDING)


def compute_indicator(df: pd.DataFrame, shares_outstanding: float) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    out = df.copy()
    out["btc_per_share"] = CURRENT_BTC_HOLDINGS / shares_outstanding
    out["nav_per_share_proxy"] = out["btc_close"] * out["btc_per_share"]
    out["mnav_proxy"] = out["stock_close"] / out["nav_per_share_proxy"]
    out["premium_to_nav_proxy_pct"] = (out["mnav_proxy"] - 1.0) * 100
    out["btc_return_30d_pct"] = out["btc_close"].pct_change(30) * 100
    out["mnav_change_30d_pct"] = out["mnav_proxy"].pct_change(30) * 100
    return out


def generate_rule_based_summary(df: pd.DataFrame) -> str:
    if df.empty:
        return "No data is available right now. Please try another time range or refresh the app later."

    latest = df.iloc[-1]
    lookback = df.tail(min(30, len(df)))
    avg_30 = lookback["mnav_proxy"].mean()
    trend = "higher" if latest["mnav_proxy"] > avg_30 else "lower"

    btc_return = latest.get("btc_return_30d_pct", float("nan"))
    mnav_change = latest.get("mnav_change_30d_pct", float("nan"))

    if pd.isna(btc_return):
        btc_phrase = "Bitcoin 30-day return is not yet available"
    else:
        btc_trend = "up" if btc_return > 0 else "down"
        btc_phrase = f"Bitcoin is {btc_trend} {abs(btc_return):.1f}% over the last 30 trading days"

    if pd.isna(mnav_change):
        mnav_phrase = "proxy mNAV 30-day change is not yet available"
    else:
        mnav_phrase = f"proxy mNAV changed {mnav_change:+.1f}%"

    premium_state = "premium" if latest["premium_to_nav_proxy_pct"] >= 0 else "discount"

    return (
        f"The latest proxy mNAV for {COMPANY_NAME} is {latest['mnav_proxy']:.2f}x, which implies the stock is trading "
        f"at a {premium_state} of {latest['premium_to_nav_proxy_pct']:.1f}% relative to its Bitcoin NAV proxy. "
        f"Compared with the recent 30-day average ({avg_30:.2f}x), today's reading is {trend}. "
        f"{btc_phrase}, while {mnav_phrase}. "
        f"A rising mNAV typically suggests equity investors are assigning additional strategic, leverage, or optionality value beyond spot BTC exposure; a falling mNAV suggests that premium is compressing."
    )


st.title("DAT.co Indicator Dashboard")
st.subheader("Strategy (MSTR) proxy mNAV monitor")

st.markdown(
    """
This dashboard tracks a **DAT.co-related indicator: proxy mNAV (Modified Net Asset Value)** for **Strategy (MSTR)**.

**Definition used in this project**
- **BTC NAV per share (proxy)** = BTC price × (current BTC holdings / shares outstanding)
- **proxy mNAV** = stock price / BTC NAV per share (proxy)
- **Premium to NAV (proxy)** = (proxy mNAV − 1) × 100%

This is a practical educational implementation designed for assignment use.
    """
)

period_label = st.selectbox("Time range", ["6mo", "1y", "2y", "5y"], index=1)

try:
    raw = load_price_data(period_label)
    shares_outstanding = get_shares_outstanding()
    df = compute_indicator(raw, shares_outstanding)
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

if df.empty:
    st.warning(
        "No market data was returned for the selected range. This usually means Yahoo Finance temporarily returned an empty response. Please refresh the page or try another time range."
    )
    st.stop()

latest = df.iloc[-1]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest proxy mNAV", f"{latest['mnav_proxy']:.2f}x")
col2.metric("Premium to NAV (proxy)", f"{latest['premium_to_nav_proxy_pct']:.1f}%")
col3.metric("BTC price", f"${latest['btc_close']:,.0f}")
col4.metric("MSTR price", f"${latest['stock_close']:,.2f}")

fig1 = px.line(df, x="date", y="mnav_proxy", title="Strategy proxy mNAV over time")
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(df, x="date", y="premium_to_nav_proxy_pct", title="Premium / Discount to NAV (proxy, %) over time")
st.plotly_chart(fig2, use_container_width=True)

norm = df[["date", "stock_close", "btc_close"]].copy()
for c in ["stock_close", "btc_close"]:
    norm[c] = norm[c] / norm[c].iloc[0]
fig3 = px.line(norm, x="date", y=["stock_close", "btc_close"], title="Normalized price paths: MSTR vs BTC")
fig3.update_layout(legend_title_text="Series")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("### Summary")
st.write(generate_rule_based_summary(df))

with st.expander("Show raw data"):
    st.dataframe(df.tail(120), use_container_width=True)

with st.expander("Methodology and limitations"):
    st.markdown(
        f"""
- This project uses **Yahoo Finance data via yfinance** for daily adjusted close prices of **{STOCK_TICKER}** and **{BTC_TICKER}**.
- It uses a **current BTC holdings snapshot of {CURRENT_BTC_HOLDINGS:,} BTC** for Strategy.
- Shares outstanding are pulled from Yahoo Finance company metadata when available; if Yahoo metadata is unavailable, the app falls back to a recent filing-based snapshot.
- Therefore, this implementation is a **proxy mNAV** series rather than a fully point-in-time institutional dataset.
- If you want a more exact production version, replace the constant holdings assumption with a dated holdings history table from company filings or a treasury data vendor.
        """
    )
