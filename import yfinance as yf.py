import yfinance as yf
from datetime import datetime

portfolio = {
    "NVDA": {"shares": 2, "avg_cost": 198.878},
    "AAPL": {"shares": 4, "avg_cost": 253.562},
    "MSFT": {"shares": 4, "avg_cost": 420.807},
    "GOOGL": {"shares": 1, "avg_cost": 338.44},
    "QQQ":  {"shares": 1, "avg_cost": 594.20},
    "VOO":  {"shares": 1, "avg_cost": 613.62},
}

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    price = (
        info.get("currentPrice") or
        info.get("regularMarketPrice") or
        info.get("navPrice") or
        0
    )
    return {
        "price": price,
        "change_pct": info.get("regularMarketChangePercent", 0),
        "name": info.get("longName", ticker),
    }

def show_portfolio():
    print(f"\n📊 Portfolio — {datetime.now().strftime('%d %b %Y, %H:%M')}")
    print(f"\n{'Ticker':<8} {'Bought':>8} {'Shares':>7} {'Price':>9} {'Day %':>7} {'Total %':>8} {'P&L':>10}")
    print("─" * 65)

    total_invested = 0
    total_value = 0

    for ticker, info in portfolio.items():
        data = get_stock_data(ticker)
        shares = info["shares"]
        avg_cost = info["avg_cost"]
        current_price = data["price"]
        day_pct = data["change_pct"]

        cost_basis = shares * avg_cost
        current_value = shares * current_price
        pnl = current_value - cost_basis
        total_pct = ((current_price - avg_cost) / avg_cost * 100) if avg_cost > 0 else 0

        total_invested += cost_basis
        total_value += current_value

        day_arrow = "▲" if day_pct > 0 else "▼"
        total_arrow = "▲" if total_pct > 0 else "▼"
        pnl_sign = "+" if pnl >= 0 else "-"

        print(
            f"{ticker:<8} "
            f"${avg_cost:>7.2f} "
            f"{shares:>7} "
            f"${current_price:>8.2f} "
            f"{day_arrow}{abs(day_pct):>5.2f}% "
            f"{total_arrow}{abs(total_pct):>6.2f}% "
            f"{pnl_sign}${abs(pnl):>8.2f}"
        )

    print("─" * 65)
    total_pnl = total_value - total_invested
    total_return = ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
    pnl_sign = "+" if total_pnl >= 0 else "-"
    print(f"\n💰 Invested:  ${total_invested:,.2f}")
    print(f"📈 Value now: ${total_value:,.2f}")
    print(f"{'▲' if total_pnl >= 0 else '▼'} Total P&L:  {pnl_sign}${abs(total_pnl):,.2f} ({total_return:.2f}%)")

def lookup_stock():
    ticker = input("\nEnter ticker symbol (e.g. NVDA): ").upper()
    try:
        data = get_stock_data(ticker)
        arrow = "▲" if data["change_pct"] > 0 else "▼"
        print(f"\n{data['name']}")
        print(f"Price:  ${data['price']:.2f}")
        print(f"Today:  {arrow}{abs(data['change_pct']):.2f}%")
    except:
        print("Ticker not found. Try again.")

def add_stock():
    ticker = input("\nEnter ticker to add (e.g. NVDA): ").upper()
    try:
        data = get_stock_data(ticker)
        if data["price"] == 0:
            print("Ticker not found. Try again.")
            return
        shares = float(input(f"How many shares of {ticker}? "))
        avg_cost = float(input(f"Average price paid per share? $"))
        portfolio[ticker] = {"shares": shares, "avg_cost": avg_cost}
        print(f"✅ Added {shares} shares of {ticker} at ${avg_cost:.2f}")
    except:
        print("Something went wrong. Check the ticker and try again.")

def remove_stock():
    if not portfolio:
        print("\nPortfolio is empty.")
        return
    print("\nCurrent tickers:", ", ".join(portfolio.keys()))
    ticker = input("Enter ticker to remove: ").upper()
    if ticker in portfolio:
        del portfolio[ticker]
        print(f"✅ Removed {ticker} from portfolio.")
    else:
        print(f"{ticker} not found in portfolio.")

def main():
    while True:
        print("\n─────────────────────")
        print("1  View my portfolio")
        print("2  Look up any stock")
        print("3  Add a stock")
        print("4  Remove a stock")
        print("5  Quit")
        print("─────────────────────")
        choice = input("Choose: ")

        if choice == "1":
            show_portfolio()
        elif choice == "2":
            lookup_stock()
        elif choice == "3":
            add_stock()
        elif choice == "4":
            remove_stock()
        elif choice == "5":
            print("Bye!")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()