import streamlit as st
import yfinance as yf
import json
import os
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

SAVE_FILE = "portfolio.json"

st.set_page_config(page_title="Portfolio", page_icon="📊", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .stApp {
        background-color: #1a1a1a;
        color: #ffffff;
    }

    p, h1, h2, h3, h4, h5, h6, label, td, th {
        color: #ffffff !important;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    [data-testid="metric-container"] {
        background: #2a2a2a;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        border: 1px solid #333;
        color: #ffffff;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }
    thead tr {
        border-bottom: 2px solid #333;
        color: #888;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    tbody tr {
        border-bottom: 1px solid #2a2a2a;
    }
    tbody tr:hover {
        background: #222;
    }
    td, th {
        padding: 12px 8px;
        text-align: right;
    }
    td:first-child, th:first-child {
        text-align: left;
        font-weight: 600;
    }

    .stButton > button {
        background: #2a2a2a;
        border: 1px solid #555;
        color: #ffffff !important;
        border-radius: 8px;
        font-size: 13px;
        padding: 0.4rem 1rem;
        width: 100%;
    }
    .stButton > button:hover {
        background: #ffffff;
        color: #1a1a1a !important;
    }

    [data-testid="stDownloadButton"] > button {
        background: #2a2a2a !important;
        border: 1px solid #555 !important;
        color: #ffffff !important;
        border-radius: 8px;
        font-size: 13px;
        padding: 0.4rem 1rem;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background: #ffffff !important;
        color: #1a1a1a !important;
    }

    [data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid #ddd;
        border-radius: 12px;
    }
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] label,
    [data-testid="stExpander"] span,
    [data-testid="stExpander"] td,
    [data-testid="stExpander"] th {
        color: #111 !important;
    }
    [data-testid="stExpander"] .stButton > button {
        background: #f5f5f5 !important;
        border: 1px solid #ccc !important;
        color: #111 !important;
        border-radius: 8px;
        width: 100%;
    }
    [data-testid="stExpander"] .stButton > button:hover {
        background: #111 !important;
        color: #ffffff !important;
    }
    [data-testid="stExpander"] .stTextInput > div > div > input,
    [data-testid="stExpander"] .stNumberInput > div > div > input {
        background: #f5f5f5;
        border: 1px solid #ddd;
        color: #111;
        border-radius: 8px;
    }
    [data-testid="stExpander"] .stSelectbox > div > div {
        background: #f5f5f5;
        border: 1px solid #ddd;
        color: #111;
        border-radius: 8px;
    }

    hr {
        border: none;
        border-top: 1px solid #333;
        margin: 1.5rem 0;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: #1a1a1a;
        border-bottom: 1px solid #333;
    }
    .stTabs [data-baseweb="tab"] {
        color: #888;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff;
        border-bottom: 2px solid #ffffff;
    }

    .detail-box {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #ddd;
        margin-top: 1rem;
    }
    .detail-box p,
    .detail-box label,
    .detail-box span {
        color: #111 !important;
    }
</style>
""", unsafe_allow_html=True)


SECTOR_PE = {
    "Technology": 28.0,
    "Financial Services": 13.0,
    "Consumer Cyclical": 22.0,
    "Healthcare": 20.0,
    "Communication Services": 18.0,
    "Consumer Defensive": 21.0,
    "Industrials": 20.0,
    "Energy": 12.0,
    "Utilities": 16.0,
    "Real Estate": 30.0,
    "Basic Materials": 15.0,
}


def load_portfolio():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {
        "NVDA":   {"shares": 2,   "avg_cost": 198.878},
        "AAPL":   {"shares": 4,   "avg_cost": 253.562},
        "MSFT":   {"shares": 4,   "avg_cost": 420.807},
        "GOOGL":  {"shares": 1,   "avg_cost": 338.44},
        "QQQ":    {"shares": 1,   "avg_cost": 594.20},
        "VOO":    {"shares": 1,   "avg_cost": 613.62},
        "O39.SI": {"shares": 100, "avg_cost": 0.00},
    }


def save_portfolio(portfolio):
    with open(SAVE_FILE, "w") as f:
        json.dump(portfolio, f, indent=2)


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


def render_portfolio(tab_portfolio, currency, portfolio):
    symbol = "US$" if currency == "USD" else "S$"
    rows = []
    total_invested = 0
    total_value = 0
    allocation_labels = []
    allocation_values = []

    with st.spinner("Fetching prices..."):
        for ticker, info in tab_portfolio.items():
            data = get_stock_data(ticker)
            shares = info["shares"]
            avg_cost = info["avg_cost"]
            price = data["price"]
            day_pct = data["change_pct"]

            cost_basis = shares * avg_cost
            current_value = shares * price
            pnl = current_value - cost_basis
            total_pct = ((price - avg_cost) / avg_cost * 100) if avg_cost > 0 else 0

            total_invested += cost_basis
            total_value += current_value
            allocation_labels.append(ticker)
            allocation_values.append(current_value)

            day_color = "🟢" if day_pct > 0 else "🔴"
            rows.append({
                "Ticker": ticker,
                "Shares": int(shares) if shares == int(shares) else shares,
                "Avg Cost": f"{symbol}{avg_cost:.2f}",
                "Price": f"{symbol}{price:.2f}",
                "Day": f"{day_color} {abs(day_pct):.2f}%",
                "Total Return": f"{'▲' if total_pct > 0 else '▼'} {abs(total_pct):.2f}%",
                "P&L": f"{'+'if pnl >= 0 else '-'}{symbol}{abs(pnl):.2f}",
            })

    total_pnl = total_value - total_invested
    total_return = (total_pnl / total_invested * 100) if total_invested > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Invested", f"{symbol}{total_invested:,.2f}")
    col2.metric("Current Value", f"{symbol}{total_value:,.2f}")
    col3.metric("Total P&L", f"{symbol}{total_pnl:+,.2f}", f"{total_return:.2f}%")

    st.markdown("---")

    col_table, col_pie = st.columns([3, 2])

    with col_table:
        st.markdown("#### Holdings")
        st.table(rows)
        df = pd.DataFrame(rows)
        csv = df.to_csv(index=False)
        st.download_button(
            label="📤 Export to CSV",
            data=csv,
            file_name=f"portfolio_{currency}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key=f"export_{currency}"
        )

    with col_pie:
        st.markdown("#### Allocation")
        if allocation_values and sum(allocation_values) > 0:
            colors = ['#4C9BE8', '#E8834C', '#4CE8A0', '#E8E04C', '#C44CE8', '#4CE8D8', '#E84C6B']
            fig = go.Figure(data=[go.Pie(
                labels=allocation_labels,
                values=allocation_values,
                hole=0.55,
                textinfo='label+percent',
                textfont=dict(size=12, color='white'),
                marker=dict(
                    colors=colors,
                    line=dict(color='#1a1a1a', width=3)
                ),
                hovertemplate="<b>%{label}</b><br>Value: %{value:,.2f}<br>Share: %{percent}<extra></extra>",
            )])
            fig.update_layout(
                showlegend=True,
                legend=dict(
                    font=dict(color='white', size=12),
                    bgcolor='rgba(0,0,0,0)',
                    orientation='v',
                    x=1.0,
                    y=0.5,
                ),
                margin=dict(t=20, b=20, l=10, r=80),
                paper_bgcolor='#1a1a1a',
                plot_bgcolor='#1a1a1a',
                font=dict(color='white'),
                height=340,
                annotations=[dict(
                    text=f"<b>{len(allocation_labels)}<br>stocks</b>",
                    x=0.38, y=0.5,
                    font=dict(size=14, color='white'),
                    showarrow=False
                )]
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.markdown("#### Stock Details")
    selected_ticker = st.selectbox(
        "Select a stock",
        list(tab_portfolio.keys()),
        key=f"detail_{currency}",
        label_visibility="visible"
    )

    if selected_ticker:
        stock = yf.Ticker(selected_ticker)
        info = stock.info

        st.markdown('<div class="detail-box">', unsafe_allow_html=True)

        pe = info.get('trailingPE')
        sector = info.get('sector', '')
        sector_avg_pe = SECTOR_PE.get(sector)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Market Cap", f"{symbol}{info.get('marketCap', 0)/1e9:.1f}B" if info.get('marketCap') else "N/A")
        col3.metric("52W High", f"{symbol}{info.get('fiftyTwoWeekHigh', 0):.2f}")
        col4.metric("Analyst Target", f"{symbol}{info.get('targetMeanPrice', 0):.2f}" if info.get('targetMeanPrice') else "N/A")

        if pe and sector_avg_pe:
            pe_diff = pe - sector_avg_pe
            pe_label = "🔴 Expensive" if pe_diff > 5 else ("🟢 Cheap" if pe_diff < -5 else "🟡 Fair")
            col2.metric(f"P/E ({pe_label})", f"{pe:.1f}", f"Sector avg: {sector_avg_pe:.1f}", delta_color="off")
            if pe_diff > 5:
                pe_note = f"P/E of **{pe:.1f}** — investors pay ${pe:.0f} per $1 of earnings. Above the {sector} sector average of {sector_avg_pe:.1f}, priced for high growth."
            elif pe_diff < -5:
                pe_note = f"P/E of **{pe:.1f}** — investors pay ${pe:.0f} per $1 of earnings. Below the {sector} sector average of {sector_avg_pe:.1f}, may be undervalued."
            else:
                pe_note = f"P/E of **{pe:.1f}** is roughly in line with the {sector} sector average of {sector_avg_pe:.1f} — fairly valued."
            st.info(pe_note)
        else:
            col2.metric("P/E Ratio", f"{pe:.1f}" if pe else "N/A")

        st.markdown("")
        st.markdown("**📈 Price Chart**")
        period_options = {"1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y"}
        selected_period = st.radio(
            "Period",
            list(period_options.keys()),
            horizontal=True,
            key=f"period_{currency}"
        )

        hist = stock.history(period=period_options[selected_period])
        if not hist.empty:
            vol_colors = ['#26a69a' if c >= o else '#ef5350'
                          for c, o in zip(hist['Close'], hist['Open'])]

            fig2 = go.Figure()

            fig2.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                increasing=dict(line=dict(color='#26a69a', width=1), fillcolor='#26a69a'),
                decreasing=dict(line=dict(color='#ef5350', width=1), fillcolor='#ef5350'),
                name='Price',
                yaxis='y'
            ))

            fig2.add_trace(go.Bar(
                x=hist.index,
                y=hist['Volume'],
                marker_color=vol_colors,
                opacity=0.25,
                name='Volume',
                yaxis='y2'
            ))

            fig2.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='#0d1117',
                plot_bgcolor='#0d1117',
                font=dict(color='#aaaaaa'),
                xaxis=dict(
                    showgrid=False,
                    color='#aaaaaa',
                    rangeslider=dict(visible=False),
                    type='date',
                    rangebreaks=[dict(bounds=["sat", "mon"])]
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#1e2a35',
                    color='#aaaaaa',
                    side='right',
                    domain=[0.2, 1.0]
                ),
                yaxis2=dict(
                    overlaying=None,
                    side='left',
                    showgrid=False,
                    showticklabels=False,
                    domain=[0.0, 0.18]
                ),
                height=360,
                showlegend=False,
                hovermode='x unified',
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📅 Upcoming Events**")
            earnings = info.get('earningsTimestamp')
            ex_div = info.get('exDividendDate')
            if earnings:
                st.write(f"🗓 Earnings: {datetime.fromtimestamp(earnings).strftime('%d %b %Y')}")
            else:
                st.write("🗓 Earnings: N/A")
            if ex_div:
                st.write(f"💵 Ex-Dividend: {datetime.fromtimestamp(ex_div).strftime('%d %b %Y')}")
            else:
                st.write("💵 Ex-Dividend: N/A")

        with col2:
            st.markdown("**📊 Analyst Rating**")
            recommendation = info.get('recommendationKey', 'N/A').upper()
            num_analysts = info.get('numberOfAnalystOpinions', 'N/A')
            st.write(f"Consensus: **{recommendation}**")
            st.write(f"Analysts: {num_analysts}")

        st.markdown("")
        st.markdown("**📰 Latest News**")
        news = stock.news
        if news:
            for article in news[:5]:
                title = article.get('content', {}).get('title', 'No title')
                link = article.get('content', {}).get('canonicalUrl', {}).get('url', '#')
                publisher = article.get('content', {}).get('provider', {}).get('displayName', '')
                pub_date = article.get('content', {}).get('pubDate', '')
                if pub_date:
                    try:
                        pub_date = datetime.strptime(pub_date[:10], '%Y-%m-%d').strftime('%d %b %Y')
                    except:
                        pub_date = ''
                st.markdown(f"• **[{title}]({link})** — *{publisher} · {pub_date}*")
        else:
            st.write("No recent news found.")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    with st.expander("Manage Portfolio"):
        st.markdown("**Add Stock**")
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        with col1:
            new_ticker = st.text_input("Ticker", placeholder="e.g. NVDA", key=f"new_ticker_{currency}").upper()
        with col2:
            new_shares = st.number_input("Shares", min_value=0.0, step=1.0, key=f"new_shares_{currency}")
        with col3:
            new_cost = st.number_input(f"Avg Cost ({symbol})", min_value=0.0, step=0.01, key=f"new_cost_{currency}")
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Add", key=f"add_stock_{currency}"):
                if new_ticker:
                    portfolio[new_ticker] = {"shares": new_shares, "avg_cost": new_cost}
                    save_portfolio(portfolio)
                    st.success(f"✅ Added {new_ticker}")
                    st.rerun()

        st.markdown("---")
        st.markdown("**Remove Stock**")
        col1, col2 = st.columns([3, 1])
        with col1:
            remove_ticker = st.selectbox("Select ticker", list(tab_portfolio.keys()), key=f"remove_select_{currency}")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Remove", key=f"remove_stock_{currency}"):
                del portfolio[remove_ticker]
                save_portfolio(portfolio)
                st.success(f"✅ Removed {remove_ticker}")
                st.rerun()


portfolio = load_portfolio()
us_portfolio = {k: v for k, v in portfolio.items() if not k.endswith(".SI")}
sg_portfolio = {k: v for k, v in portfolio.items() if k.endswith(".SI")}

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("## Portfolio")
    st.caption(f"{datetime.now().strftime('%A, %d %B %Y · %H:%M')}")
with col2:
    st.write("")
    st.write("")
    if st.button("↻ Refresh", key="refresh"):
        st.rerun()

st.markdown("---")

tab1, tab2 = st.tabs(["🇺🇸 US Stocks", "🇸🇬 SG Stocks"])

with tab1:
    render_portfolio(us_portfolio, "USD", portfolio)

with tab2:
    render_portfolio(sg_portfolio, "SGD", portfolio)