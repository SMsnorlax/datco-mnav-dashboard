# DAT.co Indicator Monitoring Report

## 1. Selected Indicator
**Indicator:** proxy mNAV (Modified Net Asset Value) for **Strategy (Nasdaq: MSTR)**.

### Why this indicator?
I chose mNAV because it is one of the most common valuation indicators for digital asset treasury companies (DAT.cos). It measures how the stock market values a company relative to the estimated Bitcoin value on its balance sheet. Compared with simply showing stock price or BTC holdings alone, mNAV is more informative because it reflects whether investors are assigning a premium or discount to the company’s Bitcoin strategy.

## 2. Relationship with Bitcoin (BTC)
mNAV is directly tied to BTC because the denominator of the ratio is based on the company’s Bitcoin net asset value. When BTC price rises, the company’s BTC NAV rises as well. If the company’s stock price rises at the same pace as BTC NAV, mNAV stays relatively stable. If the stock price rises faster than BTC NAV, mNAV increases, which implies that the market is pricing in extra value such as leverage, future BTC accumulation, capital markets access, brand effect, or strategy execution. If the stock price rises more slowly than BTC NAV, mNAV declines, indicating valuation compression.

### Hypotheses about BTC price behavior
1. **BTC bull markets can expand mNAV** because investors may become more optimistic about companies with large BTC exposure.
2. **BTC drawdowns can compress mNAV** because risk appetite weakens and the premium investors are willing to pay often shrinks.
3. **mNAV can act as a sentiment indicator**: when mNAV rises sharply, it may suggest that equity investors are more bullish than spot BTC investors; when mNAV falls, it may suggest declining enthusiasm or reduced confidence in the DAT.co trade.

## 3. Data Collection
This project uses two data sources:

1. **Yahoo Finance (via `yfinance`)** for daily historical prices of:
   - `MSTR` (Strategy stock)
   - `BTC-USD` (Bitcoin spot proxy)
2. **BitcoinTreasuries** for the company’s BTC holdings snapshot.

### Formula used
- BTC NAV per share (proxy) = BTC price × (current BTC holdings / shares outstanding)
- proxy mNAV = stock price / BTC NAV per share (proxy)
- Premium to NAV (proxy) = (proxy mNAV − 1) × 100%

### Why “proxy” mNAV?
A fully point-in-time institutional mNAV series would require historical BTC holdings and share-count changes aligned by date. For a practical student project, this implementation uses a current BTC holdings snapshot and live share count metadata to generate an educational approximation of daily mNAV.

## 4. Website Visualization
The website includes:
- A time-series line chart of proxy mNAV
- A time-series line chart of premium/discount to NAV
- A normalized comparison chart of MSTR vs BTC
- KPI cards showing the latest values
- A short auto-generated text summary

## 5. Deployed Website URL
**Your deployment URL goes here after deployment**

Example format:
`https://your-app-name.streamlit.app`

## 6. Bonus: AI Summary (Optional)
This project includes an automatically generated text summary. In the submitted version, a rule-based summary is implemented so the feature works without API keys. It can be extended with an LLM API such as OpenAI, Gemini, or Claude for richer commentary.

## 7. Conclusion
This project demonstrates how DAT.co indicators can be collected, computed, and visualized in a web-based dashboard. Among the available candidates, mNAV is especially useful because it captures both BTC-linked asset value and the market’s valuation premium. As a result, it serves as a useful bridge between crypto market behavior and equity market sentiment.
