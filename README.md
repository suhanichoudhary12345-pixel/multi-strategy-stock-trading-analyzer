# Multi-Strategy Stock Trading Analyzer

A quantitative trading analysis project that backtests multiple technical-analysis strategies across four major equity indices and investigates market behavior across Bull and Bear regimes using statistical hypothesis testing.

## Overview

This project evaluates four rule-based trading strategies across:

- Dow Jones Industrial Average (DJIA)
- NASDAQ Composite
- Nikkei 225
- S&P/BMV IPC

The project combines technical indicators, systematic backtesting, performance evaluation, market-regime analysis, and statistical testing.

The objective is not to predict the market, but to evaluate whether commonly used technical strategies and regime characteristics show meaningful historical patterns.

---

## Project Pipeline

Historical Market Data
        ↓
Data Cleaning & Returns
        ↓
Technical Indicators
        ↓
Trading Signals
        ↓
Backtesting
        ↓
Performance Metrics
        ↓
Bull/Bear Regime Classification
        ↓
Statistical Analysis
        ↓
Risk & Market Regime Insights

## Strategies

Four long/cash trading strategies were implemented:

### 1. RSI Mean Reversion

Uses the Relative Strength Index (RSI).

- RSI < 30 → enter/hold a long position
- RSI > 70 → exit
- Otherwise → maintain the previous position

The strategy attempts to capture reversals following oversold conditions.

### 2. MACD Momentum

Uses the Moving Average Convergence Divergence (MACD).

- MACD > Signal Line → long
- MACD ≤ Signal Line → cash

This strategy attempts to capture upward momentum.

### 3. DMA Trend Following

Uses 20-day and 50-day moving averages.

- 20-DMA > 50-DMA → long
- 20-DMA ≤ 50-DMA → cash

This strategy follows medium-term price trends.

### 4. ADX + DMA

Combines trend strength and trend direction.

- ADX > 25
- 20-DMA > 50-DMA

When both conditions are satisfied, the strategy takes a long position.

---

## Backtesting Framework

Each strategy was backtested across all four indices, resulting in:

**4 strategies × 4 indices = 16 backtests**

The backtesting framework calculates:

- Total Return
- Annualized Return
- Annualized Volatility
- Sharpe Ratio
- Maximum Drawdown
- Win Rate

To avoid look-ahead bias, trading signals generated using the current day's information are applied to the following day's return.

---

## Statistical Analysis

The project investigates whether market behavior differs between Bull and Bear regimes.

### Regime Definition

Market regimes are defined using moving-average relationships:
```
20-DMA > 50-DMA → Bull Regime
20-DMA < 50-DMA → Bear Regime
```

For each regime, the project evaluates:

- Mean return
- Median return
- Daily volatility
- Annualized volatility
- Excess kurtosis
- 1% return quantile
- Number of observations

### Statistical Tests

#### Welch's t-test

Used to evaluate whether the mean daily returns of Bull and Bear regimes differ significantly without assuming equal variances.

#### Permutation Test

A 10,000-iteration permutation test is used to evaluate the observed difference in mean returns without relying on a parametric distributional assumption.

#### Hartigan's Dip Test

Used to investigate whether return distributions show evidence against unimodality.

---

## Key Findings

### 1. Bear regimes were consistently more volatile

Bear-to-Bull volatility ratios were:

| Index  | Bear/Bull Volatility |
| ------ | -------------------- |
| DJIA   | 1.81×                |
| NASDAQ | 1.71×                |
| NIKKEI | 1.35×                |
| IPC    | 1.22×                |

Thus, Bear regimes exhibited higher volatility across **all four indices**.

### 2. Mean returns were not statistically different

Welch's t-test produced p-values above 0.05 for all four indices.

Similarly, the 10,000-iteration permutation tests did not find statistically significant differences in mean daily returns between Bull and Bear regimes.

This suggests that the strongest regime difference observed in the analysis was related to **risk/volatility rather than average daily return**.

### 3. Heavier tails were observed in most indices during Bear regimes

Bear regimes exhibited higher excess kurtosis for:

- DJIA
- NASDAQ
- IPC

Nikkei was an exception, where the Bull regime showed higher excess kurtosis.

Therefore, the project does not claim universally heavier-tailed Bear distributions.

### 4. Strategy performance varied across markets

Some of the strongest Sharpe ratios observed were:

| Index  | Strategy | Sharpe Ratio |
| ------ | -------- | ------------ |
| DJIA   | MACD     | 0.657        |
| NASDAQ | DMA      | 0.610        |
| NIKKEI | MACD     | 0.537        |
| IPC    | MACD     | 0.407        |

Performance varied substantially across both strategy and market, highlighting that no single technical strategy consistently dominated across all indices.

Technologies Used
- Python
- Pandas
- NumPy
- SciPy
- Matplotlib
- Seaborn
- yfinance
- diptest
- Jupyter Notebook

Installation :
-Clone the repository
-Create a virtual environment
-Activate it on windows
-Install dependencies

Running the Project:
-Open Jupyter notebook then open notebooks/01_multi_strategy_analyer.ipynb and run the notebook from top to bottom.

Reproducibility :
-Historical market data is downloaded programmatically using yfinance.
-The repository does not require the local Python virtual environment or downloaded raw market data to be committed to Git.
-Running the notebook downloads the required historical data again.

Limitations :
This project is a historical backtesting and statistical-analysis exercise and should not be interpreted as investment advice.
Important limitations include:
- Transaction costs and slippage are not modeled.
- Strategies are long/cash and do not take short positions.
- Technical indicators are based only on historical price information.
- Historical backtest performance does not guarantee future performance.
- Market regime observations are descriptive and do not establish causality.
- The statistical tests should be interpreted within their underlying assumptions and the time-series nature of financial returns.

Conclusion :
-The analysis demonstrates that technical trading strategy performance can vary considerably across markets and that Bear regimes were consistently associated with higher volatility across the four indices studied.
-The statistical tests did not provide evidence of significant differences in mean daily returns between Bull and Bear regimes, suggesting that the most robust regime-related pattern in this analysis was increased risk rather than a systematic difference in average return.
