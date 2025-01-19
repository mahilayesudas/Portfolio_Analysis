import pandas as pd
import yfinance as yf
import financedatabase as fd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import datetime as dt

# Streamlit page configuration
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# App title
st.title("Comprehensive Portfolio Analysis")

# Load ticker data
@st.cache_data
def load_data():
    ticker_list = pd.concat([
        fd.ETFs().select().reset_index()[['symbol', 'name']],
        fd.Equities().select().reset_index()[['symbol', 'name']]
    ])
    ticker_list = ticker_list[ticker_list.symbol.notna()]
    ticker_list['symbol_name'] = ticker_list.symbol + ' - ' + ticker_list.name
    return ticker_list

ticker_list = load_data()

# Sidebar options
with st.sidebar:
    sel_tickers = st.multiselect('Portfolio Builder', placeholder='Search tickers', options=ticker_list.symbol_name)
    sel_tickers_list = ticker_list[ticker_list.symbol_name.isin(sel_tickers)].symbol
    cols = st.columns(4)

    for i, ticker in enumerate(sel_tickers_list):
        try:
            website = yf.Ticker(ticker).info.get('website', '')
            if website:
                cols[i % 4].image('https://logo.clearbit.com/' + website.replace('https://www.', ''), width=65)
            else:
                cols[i % 4].subheader(ticker)
        except Exception as e:
            cols[i % 4].subheader(ticker)

    cols = st.columns(2)
    sel_dt1 = cols[0].date_input('Start date', value=dt.datetime(2020, 1, 1).date(), format='YYYY-MM-DD')
    sel_dt2 = cols[1].date_input('End date', value=dt.datetime.now().date(), format='YYYY-MM-DD')

    total_investment = st.number_input('Total Investment Amount ($)', min_value=1000, step=100, value=100000)

# Load and process data if tickers are selected
if len(sel_tickers_list) != 0:
    sel_dt1 = dt.datetime.combine(sel_dt1, dt.time.min)
    sel_dt2 = dt.datetime.combine(sel_dt2, dt.time.max)

    yfdata = yf.download(list(sel_tickers_list), start=sel_dt1, end=sel_dt2)['Close']
    if not yfdata.empty:
        yfdata = yfdata.reset_index().melt(id_vars=['Date'], var_name='ticker', value_name='price')
        yfdata['price_start'] = yfdata.groupby('ticker').price.transform('first')
        yfdata['price_pct_daily'] = yfdata.groupby('ticker').price.pct_change()
        yfdata['price_pct'] = (yfdata.price - yfdata.price_start) / yfdata.price_start

# Function to calculate CAGR
def calculate_cagr(start_price, end_price, periods):
    return (end_price / start_price) ** (1 / periods) - 1

# Function to calculate performance metrics
def analyze_performance_and_allocate(df, total_investment):
    analysis = []
    for ticker in df['ticker'].unique():
        ticker_data = df[df['ticker'] == ticker]
        start_price = ticker_data['price'].iloc[0]
        end_price = ticker_data['price'].iloc[-1]
        periods = (ticker_data['Date'].iloc[-1] - ticker_data['Date'].iloc[0]).days / 365.0

        # Calculate metrics
        cagr = calculate_cagr(start_price, end_price, periods)
        volatility = ticker_data['price_pct_daily'].std() * (252 ** 0.5)
        sharpe_ratio = (ticker_data['price_pct_daily'].mean() * 252) / volatility if volatility > 0 else 0
        max_drawdown = ((ticker_data['price'] / ticker_data['price'].cummax()) - 1).min()

        # Project profits
        profit_1yr = total_investment * ((1 + cagr) ** 1 - 1)
        profit_5yr = total_investment * ((1 + cagr) ** 5 - 1)
        profit_10yr = total_investment * ((1 + cagr) ** 10 - 1)

        analysis.append({
            'Ticker': ticker,
            'Start Price': start_price,
            'End Price': end_price,
            'CAGR (%)': round(cagr * 100, 2),
            'Volatility (%)': round(volatility * 100, 2),
            'Sharpe Ratio': round(sharpe_ratio, 2),
            'Max Drawdown (%)': round(max_drawdown * 100, 2),
            'Profit 1 Year ($)': round(profit_1yr, 2),
            'Profit 5 Years ($)': round(profit_5yr, 2),
            'Profit 10 Years ($)': round(profit_10yr, 2)
        })

    performance_df = pd.DataFrame(analysis)
    performance_df['CAGR Weight'] = performance_df['CAGR (%)'] / performance_df['CAGR (%)'].sum()
    performance_df['Investment Allocation ($)'] = performance_df['CAGR Weight'] * total_investment
    return performance_df

# Tabs for visualization
tab1, tab2 = st.tabs(['Portfolio Performance', 'Performance Analysis'])

if len(sel_tickers_list) == 0:
    st.info('Select tickers to view plots')
else:
    st.empty()

    with tab1:
        st.subheader('Portfolio Performance Over Selected Dates')
        if 'yfdata' in locals() and not yfdata.empty:
            fig = px.line(yfdata, x='Date', y='price_pct', color='ticker', markers=True)
            fig.add_hline(y=0, line_dash="dash", line_color="white")
            fig.update_layout(xaxis_title=None, yaxis_title=None)
            fig.update_yaxes(tickformat=',.0%')
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader('Performance Metrics and Investment Allocation')
        if 'yfdata' in locals() and not yfdata.empty:
            performance_df = analyze_performance_and_allocate(yfdata, total_investment)
            st.dataframe(performance_df, use_container_width=True)

            fig = go.Figure()
            for _, row in performance_df.iterrows():
                fig.add_trace(go.Indicator(
                    mode="number+delta",
                    value=row['Investment Allocation ($)'],
                    delta={'reference': 0, 'valueformat': '.2f'},
                    title={'text': f"{row['Ticker']}<br><span style='font-size:0.8em;color:gray'>CAGR: {row['CAGR (%)']}%</span>"},
                    domain={'row': 0, 'column': len(fig.data)}
                ))
            fig.update_layout(grid={'rows': 1, 'columns': len(performance_df)}, margin={'t': 50})
            st.plotly_chart(fig, use_container_width=True)
