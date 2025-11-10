"""
Intraday Levels Dashboard

A Streamlit application that displays real-time stock price data with key trading levels:
- Pre-market High/Low
- Opening Range Breakout (ORB) 5-minute and 15-minute levels
- Previous Day High/Low (PDH/PDL)
- AI-powered market analysis using Gemini API

Usage:
    streamlit run dashboard.py
"""

import datetime as dt
import pytz
import streamlit as st

from config import (
    PAGE_TITLE, PAGE_ICON, PAGE_LAYOUT,
    MARKET_TZ, PREMARKET_OPEN
)
from data_fetcher import fetch_data
from level_calculator import calculate_levels, merge_identical_levels
from chart_builder import plot_chart
from ui_components import (
    initialize_session_state,
    render_sidebar,
    update_sidebar_info,
    display_ai_analysis_section,
    handle_no_data_state,
    handle_no_today_data_state
)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=PAGE_LAYOUT
)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """
    Main application entry point.
    
    Orchestrates the entire dashboard workflow:
    1. Initialize session state
    2. Render sidebar and get ticker selection
    3. Fetch and process data
    4. Calculate trading levels
    5. Display chart and levels
    6. Provide AI analysis option
    """
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar and get components
    active_ticker, price_placeholder, time_placeholder, levels_placeholder = render_sidebar()
    
    # Main page title
    st.title(f"{active_ticker} Intraday Levels Dashboard")
    
    # Fetch historical data
    data = fetch_data(active_ticker)
    
    # Handle case when data fetch fails
    if data.empty:
        handle_no_data_state(
            price_placeholder, 
            time_placeholder, 
            levels_placeholder, 
            active_ticker
        )
        return
    
    # Calculate trading levels from historical data
    levels = calculate_levels(data)
    
    # Filter for today's data only
    today_date = data.index[-1].date()
    today_start_dt = pytz.timezone(MARKET_TZ).localize(
        dt.datetime.combine(today_date, PREMARKET_OPEN)
    )
    data_filtered = data.loc[today_start_dt:]
    
    # Handle case when today's session hasn't started
    if data_filtered.empty:
        handle_no_today_data_state(
            price_placeholder, 
            time_placeholder, 
            levels_placeholder, 
            data
        )
        return
    
    # Get current price
    current_price = data_filtered['Close'].iloc[-1]
    
    # Merge identical ORB levels for cleaner display
    merged_levels = merge_identical_levels(levels)
    
    # Generate chart
    fig, _ = plot_chart(data_filtered, merged_levels, active_ticker)
    
    # Update sidebar with current information
    update_sidebar_info(
        price_placeholder, 
        time_placeholder, 
        levels_placeholder,
        current_price, 
        merged_levels
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Add informational caption
    st.caption(
        "This dashboard fetches 7 days of 5-minute data to calculate "
        "previous day and pre-market levels."
    )
    
    # Display AI analysis section
    display_ai_analysis_section(merged_levels, current_price, active_ticker)
    
    # Note: Auto-refresh is commented out to avoid constant reloading
    # Uncomment the following lines to enable auto-refresh every 5 minutes:
    # import time
    # time.sleep(300)
    # st.rerun()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
