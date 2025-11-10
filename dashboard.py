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
import time

from config import (
    PAGE_TITLE, PAGE_ICON, PAGE_LAYOUT,
    MARKET_TZ, PREMARKET_OPEN
)
from data_fetcher import fetch_data
from level_calculator import calculate_levels, merge_identical_levels
from chart_builder import plot_chart
from indicators import calculate_all_indicators, get_indicator_signals
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
    4. Calculate trading levels and indicators
    5. Display chart with indicators
    6. Provide AI analysis option
    """
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar and get components
    active_ticker, price_placeholder, time_placeholder, levels_placeholder = render_sidebar()
    
    # Main page title
    st.title(f"{active_ticker} Intraday Levels Dashboard")
    
    # Add toggle for indicators in sidebar
    with st.sidebar:
        st.markdown("---")
        show_indicators = st.checkbox("Show Technical Indicators", value=True)
    
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
    # Pass ticker to enable SPY-specific global session levels
    levels = calculate_levels(data, ticker=active_ticker)
    
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
    
    # Calculate technical indicators if enabled
    indicators = None
    if show_indicators:
        indicators = calculate_all_indicators(data_filtered)
        
        # Display indicator signals in sidebar
        signals = get_indicator_signals(indicators)
        if signals:
            with st.sidebar:
                st.markdown("---")
                st.subheader("Indicator Signals")
                
                # RSI signal
                if 'rsi_signal' in signals:
                    rsi_color = {
                        'Overbought': '🔴',
                        'Oversold': '🟢',
                        'Neutral': '⚪'
                    }.get(signals['rsi_signal'], '⚪')
                    st.write(f"{rsi_color} **RSI ({signals['rsi_value']:.1f}):** {signals['rsi_signal']}")
                
                # MACD signal
                if 'macd_signal' in signals:
                    macd_color = {
                        'Bullish': '🟢',
                        'Bearish': '🔴',
                        'Neutral': '⚪'
                    }.get(signals['macd_signal'], '⚪')
                    st.write(f"{macd_color} **MACD:** {signals['macd_signal']}")
                
                # VWAP
                if 'vwap_value' in signals:
                    vwap_vs_price = "Above" if current_price > signals['vwap_value'] else "Below"
                    st.write(f"📊 **Price vs VWAP:** {vwap_vs_price}")
                    st.write(f"   VWAP: ${signals['vwap_value']:.2f}")
    
    # Generate chart with or without indicators
    fig, _ = plot_chart(data_filtered, merged_levels, active_ticker, indicators=indicators)
    
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
    caption_text = "This dashboard fetches 7 days of 5-minute data to calculate previous day and pre-market levels."
    if show_indicators:
        caption_text += " Technical indicators: RSI (14), VWAP, and MACD (12,26,9)."
    st.caption(caption_text)
    
    # Display AI analysis section
    display_ai_analysis_section(merged_levels, current_price, active_ticker)
    
    # Simple market hours check: 4 AM - 8 PM ET, Monday-Friday
    now_et = dt.datetime.now(pytz.timezone(MARKET_TZ))
    is_weekday = now_et.weekday() < 5  # Monday=0, Friday=4
    is_trading_hours = dt.time(4, 0) <= now_et.time() <= dt.time(20, 0)
    
    if is_weekday and is_trading_hours:
        # Market is open - auto-refresh every 2 minutes
        time.sleep(120)
        st.rerun()
    # else: Market closed - no auto-refresh


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
