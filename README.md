# DAT.co mNAV Dashboard

A simple assignment-ready web dashboard that monitors a DAT.co-related indicator: **proxy mNAV for Strategy (MSTR)**.

## What this project does
- Downloads daily price data for **MSTR** and **BTC-USD** using `yfinance`
- Uses a current BTC holdings snapshot for Strategy
- Computes:
  - BTC NAV per share (proxy)
  - proxy mNAV
  - Premium / Discount to NAV (proxy)
- Displays charts and a short summary in a Streamlit app

## Quick start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment (recommended)
This project is easiest to deploy on **Streamlit Community Cloud**:
1. Push these files to a GitHub repository.
2. Go to Streamlit Community Cloud.
3. Create a new app from your repo.
4. Set `app.py` as the main file.
5. Deploy.

## Notes
This project uses a **proxy** version of mNAV. For a more precise production implementation, you should replace the constant BTC holdings assumption with dated holdings history from company filings or a treasury dataset provider.
