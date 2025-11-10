"""
Technical indicators module for the Intraday Levels Dashboard.

This module calculates common technical indicators:
- RSI (Relative Strength Index)
- VWAP (Volume Weighted Average Price)
- MACD (Moving Average Convergence Divergence)
"""

import pandas as pd
import numpy as np


def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculates the Relative Strength Index (RSI).
    
    RSI measures the speed and magnitude of price changes to identify
    overbought (>70) or oversold (<30) conditions.
    
    Args:
        df: DataFrame with OHLCV data
        period: RSI period (default: 14)
        
    Returns:
        Series with RSI values (0-100 scale)
        
    Example:
        >>> rsi = calculate_rsi(df, period=14)
        >>> print(f"Current RSI: {rsi.iloc[-1]:.2f}")
    """
    if df.empty or 'Close' not in df.columns:
        return pd.Series(dtype=float)
    
    # Calculate price changes
    delta = df['Close'].diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate average gain and loss
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    # Calculate RS (Relative Strength)
    rs = avg_gain / avg_loss
    
    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """
    Calculates the Volume Weighted Average Price (VWAP).
    
    VWAP is the average price weighted by volume, commonly used as a
    benchmark for institutional trading and intraday trend direction.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        Series with VWAP values
        
    Example:
        >>> vwap = calculate_vwap(df)
        >>> print(f"Current VWAP: {vwap.iloc[-1]:.2f}")
    """
    if df.empty or not all(col in df.columns for col in ['High', 'Low', 'Close', 'Volume']):
        return pd.Series(dtype=float)
    
    # Calculate typical price (HLC/3)
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    
    # Calculate cumulative volume * typical price
    cumulative_tp_volume = (typical_price * df['Volume']).cumsum()
    
    # Calculate cumulative volume
    cumulative_volume = df['Volume'].cumsum()
    
    # Calculate VWAP
    vwap = cumulative_tp_volume / cumulative_volume
    
    return vwap


def calculate_macd(df: pd.DataFrame, fast_period: int = 12, 
                   slow_period: int = 26, signal_period: int = 9) -> tuple:
    """
    Calculates the MACD (Moving Average Convergence Divergence).
    
    MACD is a trend-following momentum indicator that shows the relationship
    between two exponential moving averages.
    
    Args:
        df: DataFrame with OHLCV data
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line EMA period (default: 9)
        
    Returns:
        Tuple of (macd_line, signal_line, histogram)
        
    Example:
        >>> macd, signal, histogram = calculate_macd(df)
        >>> if histogram.iloc[-1] > 0:
        ...     print("Bullish MACD crossover")
    """
    if df.empty or 'Close' not in df.columns:
        empty_series = pd.Series(dtype=float)
        return empty_series, empty_series, empty_series
    
    # Calculate EMAs
    ema_fast = df['Close'].ewm(span=fast_period, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=slow_period, adjust=False).mean()
    
    # Calculate MACD line
    macd_line = ema_fast - ema_slow
    
    # Calculate signal line
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # Calculate histogram
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_ema(df: pd.DataFrame, period: int) -> pd.Series:
    """
    Calculates Exponential Moving Average (EMA).
    
    Args:
        df: DataFrame with OHLCV data
        period: EMA period
        
    Returns:
        Series with EMA values
    """
    if df.empty or 'Close' not in df.columns:
        return pd.Series(dtype=float)
    
    return df['Close'].ewm(span=period, adjust=False).mean()


def calculate_all_indicators(df: pd.DataFrame) -> dict:
    """
    Calculates all technical indicators at once.
    
    This is a convenience function that calculates all indicators
    with default parameters.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        Dictionary containing all calculated indicators:
        {
            'rsi': RSI series,
            'vwap': VWAP series,
            'macd': MACD line series,
            'macd_signal': MACD signal line series,
            'macd_histogram': MACD histogram series
        }
        
    Example:
        >>> indicators = calculate_all_indicators(df)
        >>> print(f"RSI: {indicators['rsi'].iloc[-1]:.2f}")
        >>> print(f"VWAP: {indicators['vwap'].iloc[-1]:.2f}")
    """
    indicators = {}
    
    # Calculate RSI
    indicators['rsi'] = calculate_rsi(df)
    
    # Calculate VWAP
    indicators['vwap'] = calculate_vwap(df)
    
    # Calculate MACD
    macd, signal, histogram = calculate_macd(df)
    indicators['macd'] = macd
    indicators['macd_signal'] = signal
    indicators['macd_histogram'] = histogram
    
    return indicators


def get_indicator_signals(indicators: dict) -> dict:
    """
    Generates trading signals from indicators.
    
    Args:
        indicators: Dictionary of calculated indicators
        
    Returns:
        Dictionary with signal interpretations
    """
    signals = {}
    
    if not indicators:
        return signals
    
    # RSI signals
    if 'rsi' in indicators and not indicators['rsi'].empty:
        current_rsi = indicators['rsi'].iloc[-1]
        if not pd.isna(current_rsi):
            if current_rsi > 70:
                signals['rsi_signal'] = "Overbought"
            elif current_rsi < 30:
                signals['rsi_signal'] = "Oversold"
            else:
                signals['rsi_signal'] = "Neutral"
            signals['rsi_value'] = current_rsi
    
    # MACD signals
    if 'macd_histogram' in indicators and not indicators['macd_histogram'].empty:
        current_hist = indicators['macd_histogram'].iloc[-1]
        if not pd.isna(current_hist):
            if current_hist > 0:
                signals['macd_signal'] = "Bullish"
            elif current_hist < 0:
                signals['macd_signal'] = "Bearish"
            else:
                signals['macd_signal'] = "Neutral"
            signals['macd_histogram_value'] = current_hist
    
    # VWAP signals
    if 'vwap' in indicators and not indicators['vwap'].empty:
        vwap_value = indicators['vwap'].iloc[-1]
        if not pd.isna(vwap_value):
            signals['vwap_value'] = vwap_value
    
    return signals

