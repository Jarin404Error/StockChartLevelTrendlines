"""
UI components module for the Intraday Levels Dashboard.

This module contains all Streamlit UI helper functions for rendering
and updating the dashboard interface.
"""

import datetime as dt
import pytz
import streamlit as st

from config import MARKET_TZ, DEFAULT_TICKER
from gemini import get_gemini_analysis


def render_sidebar() -> tuple:
    """
    Renders the sidebar with ticker input and info placeholders.
    
    Creates the sidebar interface including:
    - Ticker symbol input
    - Current ticker display
    - Placeholders for dynamic price, time, and levels info
    
    Returns:
        Tuple of (active_ticker, price_placeholder, time_placeholder, levels_placeholder)
        
    Example:
        >>> ticker, price_ph, time_ph, levels_ph = render_sidebar()
        >>> price_ph.write("Price: $150.00")
    """
    with st.sidebar:
        st.header("Dashboard Controls")
        
        # Ticker input field
        user_ticker = st.text_input(
            "Enter Ticker Symbol", 
            value=st.session_state.ticker
        ).upper()
        
        # Update session state if ticker changed
        if user_ticker != st.session_state.ticker:
            st.session_state.ticker = user_ticker
        
        active_ticker = st.session_state.ticker
        st.write(f"**Current Ticker:** {active_ticker}")
        
        # Create placeholders for dynamic content
        price_placeholder = st.empty()
        time_placeholder = st.empty()
        st.markdown("---")  # Visual divider
        levels_placeholder = st.empty()
    
    return active_ticker, price_placeholder, time_placeholder, levels_placeholder


def update_sidebar_info(price_placeholder, time_placeholder, levels_placeholder, 
                       current_price: float, processed_levels: dict):
    """
    Updates the sidebar with current price and levels information.
    
    Args:
        price_placeholder: Streamlit placeholder for price display
        time_placeholder: Streamlit placeholder for timestamp
        levels_placeholder: Streamlit placeholder for levels list
        current_price: Current stock price
        processed_levels: Dictionary of level names to prices
    """
    # Display current price
    price_placeholder.write(f"**Current Price: ${current_price:.2f}**")
    
    # Display last update timestamp
    current_time = dt.datetime.now(pytz.timezone(MARKET_TZ))
    time_placeholder.write(f"Last update: {current_time.strftime('%I:%M:%S %p ET')}")
    
    # Display sorted levels list
    with levels_placeholder.container():
        st.subheader("Calculated Levels")
        
        # Sort levels by price (highest to lowest)
        sorted_levels = sorted(
            [(name, price) for name, price in processed_levels.items() if price is not None], 
            key=lambda item: item[1], 
            reverse=True
        )
        
        if sorted_levels:
            for name, price in sorted_levels:
                st.write(f"**{name}:** {price:.2f}")
        else:
            st.write("No levels calculated yet.")


def display_ai_analysis_section(processed_levels: dict, current_price: float, ticker: str):
    """
    Displays the AI analysis section with button and results.
    
    Creates an interactive section where users can request AI-powered
    market analysis of the current levels and price action.
    
    Args:
        processed_levels: Dictionary of levels for analysis
        current_price: Current stock price
        ticker: Stock symbol
    """
    st.markdown("---")
    st.subheader("🤖 AI Market Analysis")
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        get_ai_feedback = st.button(
            "Get AI Feedback", 
            type="primary", 
            use_container_width=True
        )
    
    with col2:
        if get_ai_feedback:
            with st.spinner("Analyzing market data with Gemini AI..."):
                ai_analysis = get_gemini_analysis(
                    processed_levels, 
                    current_price, 
                    ticker
                )
                st.markdown(ai_analysis)
        else:
            st.info("Click 'Get AI Feedback' to get an AI-powered analysis of the current market levels.")


def handle_no_data_state(price_placeholder, time_placeholder, levels_placeholder, ticker: str):
    """
    Handles the UI state when no data is available for the ticker.
    
    Displays appropriate error messages and placeholder values when
    data fetching fails completely.
    
    Args:
        price_placeholder: Streamlit placeholder for price display
        time_placeholder: Streamlit placeholder for timestamp
        levels_placeholder: Streamlit placeholder for levels list
        ticker: Stock symbol that failed to load
    """
    st.error(f"No data found for {ticker}. Please check the symbol or try again later.")
    
    # Update sidebar with N/A values
    price_placeholder.write("Current Price: N/A")
    
    current_time = dt.datetime.now(pytz.timezone(MARKET_TZ))
    time_placeholder.write(f"Last update: {current_time.strftime('%I:%M:%S %p ET')}")
    
    levels_placeholder.info("No levels to display.")


def handle_no_today_data_state(price_placeholder, time_placeholder, levels_placeholder, 
                               data):
    """
    Handles the UI state when historical data exists but no today's data yet.
    
    Displays a warning message when the trading session hasn't started yet,
    but still shows the most recent price from historical data.
    
    Args:
        price_placeholder: Streamlit placeholder for price display
        time_placeholder: Streamlit placeholder for timestamp
        levels_placeholder: Streamlit placeholder for levels list
        data: Historical DataFrame with some price data
    """
    st.warning("No data for today's session yet. Waiting for pre-market...")
    
    # Show last available price
    current_price = data['Close'].iloc[-1]
    price_placeholder.write(f"**Current Price: ${current_price:.2f}**")
    
    current_time = dt.datetime.now(pytz.timezone(MARKET_TZ))
    time_placeholder.write(f"Last update: {current_time.strftime('%I:%M:%S %p ET')}")
    
    levels_placeholder.info("Waiting for market open to calculate levels.")


def initialize_session_state():
    """
    Initializes Streamlit session state with default values.
    
    Should be called at the start of the app to ensure required
    session state variables exist.
    """
    if 'ticker' not in st.session_state:
        st.session_state.ticker = DEFAULT_TICKER

