import yfinance as yf
from datetime import datetime

portfolio = {
    "NVDA": 0,
    "AAPL": 0,
    "MSFT": 0,
    "GOOGL": 0,
    "TSLA": 0,
    "QQQ": 0,
    "VOO": 0,
}

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "price": info.get("currentPrice", 0),
        "change_pct": info.get("regularMarketChangePercent", 0),
        "week_high": info.get("fiftyTwoWeekHigh", 0),
        "week_low": info.get("fiftyTwoWeekLow", 0),
    }

def main():
    print(f"\n📊 Portfolio Tracker — {datetime.now().strftime('%d %b %Y, %H:%M')}")
    print(f"{'Ticker':<8} {'Price':>10} {'Day %':>8} {'52W High':>10} {'52W Low':>10}")
    print("─" * 52)

    for ticker in portfolio:
        data = get_stock_data(ticker)
        arrow = "▲" if data["change_pct"] > 0 else "▼"
        print(
            f"{ticker:<8} "
            f"${data['price']:>9.2f} "
            f"{arrow}{abs(data['change_pct']):>6.2f}% "
            f"${data['week_high']:>9.2f} "
            f"${data['week_low']:>9.2f}"
        )

if __name__ == "__main__":
    main()