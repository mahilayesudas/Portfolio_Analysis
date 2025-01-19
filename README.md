# Portfolio_Analysis

# Overview

 The Portfolio Analysis application is designed to help clients efficiently allocate their investment across a selection of stocks based on their historical performance. By analyzing data such as Compound Annual Growth Rate (CAGR), volatility, Sharpe ratio, and maximum drawdown, the app provides insightful recommendations on how to distribute an investment across chosen tickers.

# Key Features

- **Data Source**: Stock data fetched from Yahoo Finance and ticker info from a financial database.
- **Performance Metrics**:
  - **CAGR**: Measures long-term growth rate.
  - **Volatility**: Assesses risk.
  - **Sharpe Ratio**: Risk-adjusted return.
  - **Max Drawdown**: Peak-to-trough loss.

- **Investment Allocation**: Allocates total investment based on CAGR of selected stocks.

- **Visualizations**:
  - Portfolio performance over time (line chart).
  - Performance metrics and investment allocation (table and indicators)

## Usage
1. **Select Tickers**: Choose stocks/ETFs for your portfolio.
2. **Set Date Range**: Pick start and end dates for the analysis.
3. **Enter Investment**: Input total investment (e.g., **$100,000**).
4. **View Results**: Get stock performance over time and recommended investment allocation.

## How It Works
- The app calculates daily percentage change, CAGR, volatility, Sharpe ratio, and max drawdown for each selected stock.
- Stocks with higher CAGR are allocated a larger portion of the total investment.

## Output

- **Performance Chart**: Line chart showing stock performance.
- **Metrics Table**: Displays CAGR, volatility, Sharpe ratio, and max drawdown.
- **Investment Allocation**: Breakdown of the recommended investment per stock.

