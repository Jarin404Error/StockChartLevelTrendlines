"""
Level calculation module for the Intraday Levels Dashboard.

This module contains all functions for calculating key trading levels:
- Previous Day High/Low (PDH/PDL)
- Pre-market High/Low
- Opening Range Breakout (ORB) levels
"""

import datetime as dt
import numpy as np
import pandas as pd

from config import MARKET_OPEN, MARKET_CLOSE, PREMARKET_OPEN, ORB_5_END, ORB_15_END


def find_previous_trading_day(df: pd.DataFrame, today_date: dt.date) -> tuple:
    """
    Finds the previous valid trading day's high and low.
    
    Searches backward through historical data to find the most recent day
    with valid regular trading hours (RTH) data, skipping weekends and holidays.
    
    Args:
        df: DataFrame with multiple days of OHLCV data
        today_date: Current trading day to search backward from
        
    Returns:
        Tuple of (PDH, PDL) or (None, None) if no valid trading day found
        
    Example:
        >>> pdh, pdl = find_previous_trading_day(df, dt.date(2024, 1, 15))
        >>> print(f"PDH: {pdh}, PDL: {pdl}")
    """
    all_dates = sorted(np.unique(df.index.date))
    
    # Loop backwards from the day before today
    for prev_date in reversed(all_dates[:-1]): 
        try:
            df_prev_day = df[df.index.date == prev_date]
            
            # Check for Regular Trading Hours (RTH) data only
            df_prev_day_rth = df_prev_day.between_time(MARKET_OPEN, MARKET_CLOSE)
            
            if not df_prev_day_rth.empty:
                # Found a valid trading day
                pdh = df_prev_day_rth['High'].max()
                pdl = df_prev_day_rth['Low'].min()
                print(f"Found valid PDH/PDL on: {prev_date}")
                return pdh, pdl
                
        except Exception as e:
            print(f"Error processing date {prev_date} for PDH/PDL: {e}")
    
    print(f"Warning: Could not find previous trading day in the last {len(all_dates)-1} days.")
    return None, None


def calculate_premarket_levels(df: pd.DataFrame, today_date: dt.date) -> tuple:
    """
    Calculates pre-market high and low for today.
    
    Pre-market is defined as the period between PREMARKET_OPEN and MARKET_OPEN.
    
    Args:
        df: DataFrame with historical OHLCV data
        today_date: Current trading day
        
    Returns:
        Tuple of (PM_High, PM_Low) or (None, None) if no pre-market data found
        
    Example:
        >>> pm_high, pm_low = calculate_premarket_levels(df, dt.date.today())
        >>> print(f"PM High: {pm_high}, PM Low: {pm_low}")
    """
    df_premarket = df.between_time(PREMARKET_OPEN, MARKET_OPEN)
    
    if not df_premarket.empty:
        # Filter for today only
        df_premarket = df_premarket[df_premarket.index.date == today_date]
        
        if not df_premarket.empty:
            pm_high = df_premarket['High'].max()
            pm_low = df_premarket['Low'].min()
            return pm_high, pm_low
    
    return None, None


def calculate_orb_levels(df: pd.DataFrame, today_date: dt.date, 
                        orb_end_time: dt.time, label: str) -> tuple:
    """
    Calculates Opening Range Breakout (ORB) levels.
    
    ORB levels represent the high and low during the first N minutes after
    market open. Common timeframes are 5 minutes and 15 minutes.
    
    Args:
        df: DataFrame with historical OHLCV data
        today_date: Current trading day
        orb_end_time: End time for the ORB period (e.g., 9:35 for 5-min ORB)
        label: Label prefix for logging (e.g., "ORB_5" or "ORB_15")
        
    Returns:
        Tuple of (ORB_High, ORB_Low) or (None, None) if insufficient data
        
    Example:
        >>> orb5_high, orb5_low = calculate_orb_levels(
        ...     df, dt.date.today(), dt.time(9, 35), "ORB_5"
        ... )
    """
    df_orb = df.between_time(MARKET_OPEN, orb_end_time)
    
    if not df_orb.empty:
        # Filter for today only
        df_orb = df_orb[df_orb.index.date == today_date]
        
        if not df_orb.empty:
            orb_high = df_orb['High'].max()
            orb_low = df_orb['Low'].min()
            return orb_high, orb_low
    
    return None, None


def calculate_levels(df_7day: pd.DataFrame) -> dict:
    """
    Calculates all key trading levels from historical data.
    
    This is the main orchestrator function that calculates:
    - Previous Day High/Low (PDH/PDL)
    - Pre-market High/Low (PM_High/PM_Low)
    - 5-minute ORB levels (ORB_5_High/ORB_5_Low)
    - 15-minute ORB levels (ORB_15_High/ORB_15_Low)
    
    Args:
        df_7day: DataFrame with 7 days of OHLCV data
        
    Returns:
        Dictionary mapping level names to prices. Keys may include:
        'PDH', 'PDL', 'PM_High', 'PM_Low', 'ORB_5_High', 'ORB_5_Low',
        'ORB_15_High', 'ORB_15_Low'
        
    Example:
        >>> levels = calculate_levels(df)
        >>> print(levels)
        {'PDH': 150.25, 'PDL': 148.50, 'PM_High': 149.80, ...}
    """
    levels = {}
    
    # Get all available dates
    all_dates = sorted(np.unique(df_7day.index.date))
    
    if len(all_dates) == 0:
        print("No dates found in data.")
        return {}
    
    today_date = all_dates[-1]
    
    # Calculate Previous Day High/Low
    pdh, pdl = find_previous_trading_day(df_7day, today_date)
    if pdh is not None:
        levels["PDH"] = pdh
        levels["PDL"] = pdl
    
    # Calculate Pre-Market Levels
    pm_high, pm_low = calculate_premarket_levels(df_7day, today_date)
    if pm_high is not None:
        levels["PM_High"] = pm_high
        levels["PM_Low"] = pm_low
    
    # Calculate 5-minute ORB Levels
    orb5_high, orb5_low = calculate_orb_levels(df_7day, today_date, ORB_5_END, "ORB_5")
    if orb5_high is not None:
        levels["ORB_5_High"] = orb5_high
        levels["ORB_5_Low"] = orb5_low
    
    # Calculate 15-minute ORB Levels
    orb15_high, orb15_low = calculate_orb_levels(df_7day, today_date, ORB_15_END, "ORB_15")
    if orb15_high is not None:
        levels["ORB_15_High"] = orb15_high
        levels["ORB_15_Low"] = orb15_low
    
    return levels


def merge_identical_levels(levels: dict) -> dict:
    """
    Merges ORB_5 and ORB_15 levels if they are identical.
    
    When the 5-minute and 15-minute ORB levels are the same (e.g., price
    didn't move during those first 15 minutes), this function combines them
    into single "ORB_5/15" levels for cleaner chart display.
    
    Args:
        levels: Dictionary of level names to prices
        
    Returns:
        Dictionary with merged levels where applicable
        
    Example:
        >>> levels = {'ORB_5_High': 150.0, 'ORB_15_High': 150.0, ...}
        >>> merged = merge_identical_levels(levels)
        >>> print(merged)
        {'ORB_5/15_High': 150.0, ...}
    """
    merged_levels = levels.copy()
    
    # Merge high levels if identical
    orb_5_high = merged_levels.get("ORB_5_High")
    orb_15_high = merged_levels.get("ORB_15_High")
    
    if orb_5_high is not None and orb_15_high is not None and orb_5_high == orb_15_high:
        merged_levels["ORB_5/15_High"] = orb_5_high
        merged_levels.pop("ORB_5_High", None)
        merged_levels.pop("ORB_15_High", None)
    
    # Merge low levels if identical
    orb_5_low = merged_levels.get("ORB_5_Low")
    orb_15_low = merged_levels.get("ORB_15_Low")
    
    if orb_5_low is not None and orb_15_low is not None and orb_5_low == orb_15_low:
        merged_levels["ORB_5/15_Low"] = orb_5_low
        merged_levels.pop("ORB_5_Low", None)
        merged_levels.pop("ORB_15_Low", None)
    
    return merged_levels

