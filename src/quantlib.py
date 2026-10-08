import pandas as pd
import numpy as np

def calculate_returns(df):
    #Calculate simple daily percentage returns.
    df = df.copy()
    df["Return"] = df["Close"].pct_change()
    return df 

#EMA
def calculate_ema(series, span):
    #Calculate Exponential Moving Average.
    return series.ewm(
        span=span,
        adjust=False
    ).mean()

#RSI
def calculate_rsi(close, period=14):

    #Calculate Relative Strength Index.
    
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (
        100 / (1 + rs)
    )
    return rsi

#MACD
def calculate_macd(
    close,
    fast_period=12,
    slow_period=26,
    signal_period=9
):
    
    #Calculate MACD, signal line,and MACD histogram.

    ema_fast = calculate_ema(
        close,
        fast_period
    )

    ema_slow = calculate_ema(
        close,
        slow_period
    )
    macd = ema_fast - ema_slow

    signal = calculate_ema(
        macd,
        signal_period
    )
    histogram = macd - signal
    return macd, signal, histogram

#DMA
def calculate_dma(
    close,
    short_period=20,
    long_period=50
):

    #Calculate short and longsimple moving averages.
    

    short_dma = close.rolling(
        window=short_period
    ).mean()
    long_dma = close.rolling(
        window=long_period
    ).mean()
    return short_dma, long_dma

#ADX
def calculate_adx(df, period=14):
    #Calculate Average Directional Index.

    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    previous_high = high.shift(1)
    previous_low = low.shift(1)
    previous_close = close.shift(1)

    upward_move = high - previous_high
    downward_move = previous_low - low

    plus_dm = pd.Series(
        np.where(
            (upward_move > downward_move) &
            (upward_move > 0),
            upward_move,
            0
        ),
        index=df.index
    )

    minus_dm = pd.Series(
        np.where(
            (downward_move > upward_move) &
            (downward_move > 0),
            downward_move,
            0
        ),
        index=df.index
    )

    tr1 = high - low
    tr2 = abs(high - previous_close)
    tr3 = abs(low - previous_close)

    true_range = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    atr = true_range.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    smoothed_plus_dm = plus_dm.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    smoothed_minus_dm = minus_dm.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    plus_di = (
        100 *
        smoothed_plus_dm /
        atr
    )

    minus_di = (
        100 *
        smoothed_minus_dm /
        atr
    )

    denominator = plus_di + minus_di
    dx = (
        100 *
        abs(plus_di - minus_di) /
        denominator.replace(0, np.nan)
    )

    adx = dx.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()
    return adx

def prepare_indicators(df):

    #Add all indicators required for the trading strategies.

    df = df.copy()

    # Daily returns
    df["Return"] = calculate_returns(df)["Return"]

    # RSI
    df["RSI"] = calculate_rsi(
        df["Close"]
    )

    # MACD
    (
        df["MACD"],
        df["MACD_Signal"],
        df["MACD_Hist"]
    ) = calculate_macd(
        df["Close"]
    )

    # DMA
    (
        df["DMA20"],
        df["DMA50"]
    ) = calculate_dma(
        df["Close"]
    )

    # ADX
    df["ADX"] = calculate_adx(df)

    return df

#building the 4 startegies: 1. RSI Strategy, 2. MACD Strategy, 3. DMA Strategy, 4. ADX Strategy

def rsi_strategy(df, oversold=30, overbought=70):

    #RSI mean-reversion strategy.
    #RSI < 30  -> Long
    #RSI > 70  -> Exit
    #Otherwise -> Hold previous position

    signal = pd.Series(
        np.nan,
        index=df.index
    )
    signal[df["RSI"] < oversold] = 1
    signal[df["RSI"] > overbought] = 0

    signal = signal.ffill().fillna(0)
    return signal

def macd_strategy(df):
    """MACD momentum strategy.
    MACD > Signal -> Long
    MACD < Signal -> Cash"""
    signal = pd.Series(
        0,
        index=df.index
    )

    signal[
        df["MACD"] > df["MACD_Signal"]
    ] = 1

    return signal

def dma_strategy(df):
    """
    Moving-average trend-following strategy.

    20 DMA > 50 DMA -> Long
    20 DMA < 50 DMA -> Cash
    """

    signal = pd.Series(
        0,
        index=df.index
    )
    signal[
        df["DMA20"] > df["DMA50"]
    ] = 1
    return signal

def adx_strategy(df, adx_threshold=25):
    """
    ADX + DMA trend-strength strategy.
    ADX > 25
    AND
    20 DMA > 50 DMA
    -> Long

    Otherwise -> Cash
    """

    signal = pd.Series(
        0,
        index=df.index
    )

    condition = (
        (df["ADX"] > adx_threshold) &
        (df["DMA20"] > df["DMA50"])
    )

    signal[condition] = 1

    return signal

def backtest_strategy(df, signal):
    """
    Backtest a strategy using daily close-to-close returns.

    Signals are shifted by one day to avoid
    look-ahead bias.
    """

    result = df.copy()

    # Shift signal by one day.
    # Today's signal is applied to tomorrow's return.
    result["Position"] = signal.shift(1)

    # Strategy return
    result["Strategy_Return"] = (
        result["Position"] *
        result["Return"]
    )

    # Cumulative wealth
    result["Strategy_Equity"] = (
        1 +
        result["Strategy_Return"].fillna(0)
    ).cumprod()

    # Buy-and-hold benchmark
    result["Benchmark_Equity"] = (
        1 +
        result["Return"].fillna(0)
    ).cumprod()

    return result

#evaluating the backtest
def performance_metrics(strategy_returns):
    """
    Calculate key performance metrics.
    """

    returns = strategy_returns.dropna()

    if len(returns) == 0:
        return {}

    # Cumulative return
    cumulative_return = (
        1 + returns
    ).prod() - 1

    # Number of years
    years = len(returns) / 252

    # Annualized return
    annualized_return = (
        (1 + cumulative_return) ** (1 / years)
        - 1
        if years > 0
        else np.nan
    )

    # Annualized volatility
    annualized_volatility = (
        returns.std() *
        np.sqrt(252)
    )

    # Sharpe ratio
    if returns.std() != 0:
        sharpe_ratio = (
            returns.mean() /
            returns.std()
        ) * np.sqrt(252)
    else:
        sharpe_ratio = np.nan

    # Equity curve
    equity = (
        1 + returns
    ).cumprod()

    # Running maximum
    running_max = equity.cummax()

    # Drawdown
    drawdown = (
        equity - running_max
    ) / running_max

    max_drawdown = drawdown.min()

    # Win rate
    win_rate = (
        (returns > 0).sum() /
        len(returns)
    )

    return {
        "Total Return": cumulative_return,
        "Annualized Return": annualized_return,
        "Annualized Volatility": annualized_volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Maximum Drawdown": max_drawdown,
        "Win Rate": win_rate
    }

def classify_regime(df):
    """
    Classify market regime using 20-day and 50-day
    moving averages.
    20 DMA > 50 DMA -> Bull
    20 DMA < 50 DMA -> Bear
    """
    df = df.copy()
    df["Regime"] = np.where(
        df["DMA20"] > df["DMA50"],
        "Bull",
        "Bear"
    )
    return df

def permutation_test(
    sample1,
    sample2,
    n_permutations=10000,
    seed=42
):
    """
    Two-sided permutation test for difference
    in means.
    """
    rng = np.random.default_rng(seed)

    sample1 = np.asarray(sample1)
    sample2 = np.asarray(sample2)

    observed_difference = (
        sample1.mean()
        - sample2.mean()
    )

    combined = np.concatenate(
        [sample1, sample2]
    )

    n1 = len(sample1)
    permuted_differences = np.empty(
        n_permutations
    )

    for i in range(n_permutations):
        shuffled = rng.permutation(
            combined
        )
        group1 = shuffled[:n1]
        group2 = shuffled[n1:]

        permuted_differences[i] = (
            group1.mean()
            - group2.mean()
        )
    p_value = np.mean(
        np.abs(permuted_differences)
        >= abs(observed_difference)
    )
    return (
        observed_difference,
        p_value,
        permuted_differences
    )