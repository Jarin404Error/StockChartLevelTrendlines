"""
Data fetching module for the Intraday Levels Dashboard.

This module handles all data retrieval operations from Yahoo Finance.
"""

import pandas as pd
import streamlit as st
import yfinance as yf

from config import MARKET_TZ, DATA_PERIOD, DATA_INTERVAL, CACHE_TTL


@st.cache_data(ttl=CACHE_TTL)
def fetch_data(ticker: str) -> pd.DataFrame:
    """
    Fetches historical stock data for a given ticker.
    
    Retrieves the last 7 days of 5-minute OHLCV data including pre-market
    and after-hours trading data. Results are cached for 5 minutes to
    reduce API calls.
    
    Args:
        ticker: Stock symbol to fetch data for (e.g., 'AAPL', 'TSLA')
        
    Returns:
        DataFrame with OHLCV data indexed by datetime in market timezone.
        Returns empty DataFrame if fetch fails.
        
    Example:
        >>> df = fetch_data('AAPL')
        >>> print(df.head())
    """
    print(f"Fetching {ticker} data...")
    
    try:
        data = yf.Ticker(ticker).history(
            period=DATA_PERIOD,
            interval=DATA_INTERVAL, 
            prepost=True,           # Include pre-market and after-hours
            auto_adjust=False,      # Don't adjust OHLC automatically
            back_adjust=False       # Don't back-adjust for splits
        )
        
        if not data.empty:
            # Convert timezone to market timezone for consistency
            data.index = data.index.tz_convert(MARKET_TZ)
            print(f"Successfully fetched {len(data)} rows for {ticker}")
        else:
            print(f"No data returned for {ticker}")
            
        return data
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()


def get_current_price(df: pd.DataFrame) -> float:
    """
    Extracts the most recent closing price from the dataframe.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        Most recent close price, or 0.0 if dataframe is empty
    """
    if df.empty:
        return 0.0
    
    return df['Close'].iloc[-1]


def filter_today_data(df: pd.DataFrame, today_date, premarket_open_dt) -> pd.DataFrame:
    """
    Filters the dataframe to include only today's data starting from pre-market.
    
    Args:
        df: DataFrame with historical OHLCV data
        today_date: Date object for today
        premarket_open_dt: Datetime object for pre-market open time
        
    Returns:
        Filtered DataFrame containing only today's data
    """
    return df.loc[premarket_open_dt:]

