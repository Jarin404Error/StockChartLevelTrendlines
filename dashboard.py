import streamlit as st
import yfinance as yf
import pandas as pd
import datetime as dt
import pytz
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import time  # For the auto-refresh
from gemini import get_gemini_analysis

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Intraday Levels Dashboard",
    page_icon="⚡",
    layout="wide"
)

# --- Initialize session_state for ticker ---
if 'ticker' not in st.session_state:
    st.session_state.ticker = 'TSLA' # Set a default ticker

# --- 2. Configuration ---
MARKET_TZ = "America/New_York"  # NYSE Timezone

# --- US Market Times in ET ---
PREMARKET_OPEN = dt.time(4, 0)
MARKET_OPEN = dt.time(9, 30)
ORB_5_END = dt.time(9, 35)
ORB_15_END = dt.time(9, 45)  # 9:30 + 15 mins
MARKET_CLOSE = dt.time(16, 0)

# --- 3. Helper Functions ---

def get_level_colors():
    """Returns a consistent color mapping for levels."""
    return {
        "PM_High": "red",
        "PM_Low": "red",
        "ORB_5_High": "blue",
        "ORB_5_Low": "blue",
        "ORB_15_High": "green",
        "ORB_15_Low": "green",
        "PDH": "gray",  # Previous Day High
        "PDL": "gray",  # Previous Day Low
        "ORB_5/15_High": "cyan",
        "ORB_5/15_Low": "cyan",
    }

@st.cache_data(ttl=300) # Cache data for 5 minutes (300 seconds)
def fetch_data(ticker):
    """Fetches the last 7 days of 5-min data for a ticker."""
    print(f"Fetching {ticker} data...") # This will print to your terminal
    try:
        data = yf.Ticker(ticker).history(
            period="7d",  # <-- CHANGED to 7d for robust PDH/PDL
            interval="5m", 
            prepost=True,
            auto_adjust=False, 
            back_adjust=False  
        )
        if not data.empty:
            data.index = data.index.tz_convert(MARKET_TZ)
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame() # Return empty dataframe on error

def calculate_levels(df_7day):
    """Calculates all key levels from the 7-day dataframe."""
    levels = {}

    # --- Robust Date Calculation ---
    all_dates = sorted(np.unique(df_7day.index.date))
    
    if len(all_dates) == 0:
        print("No dates found in data.")
        return {}
    
    today_date = all_dates[-1]
    
    # --- NEW: Find last valid trading day (PDH/PDL) ---
    pdh_found = False
    # Loop backwards from the day *before* today
    for prev_date in reversed(all_dates[:-1]): 
        try:
            df_prev_day = df_7day[df_7day.index.date == prev_date]
            # Check for Regular Trading Hours (RTH) data
            df_prev_day_rth = df_prev_day.between_time(MARKET_OPEN, MARKET_CLOSE)
            
            if not df_prev_day_rth.empty:
                # This was a valid trading day!
                levels["PDH"] = df_prev_day_rth['High'].max()
                levels["PDL"] = df_prev_day_rth['Low'].min()
                pdh_found = True
                print(f"Found valid PDH/PDL on: {prev_date}")
                break # Stop the loop, we are done
        except Exception as e:
            print(f"Error processing date {prev_date} for PDH/PDL: {e}")

    if not pdh_found:
        print(f"Warning: Could not find previous trading day in the last {len(all_dates)-1} days.")
    # --- END: New PDH/PDL logic ---


    # --- Calculations for TODAY_DATE ---

    # 3. Pre-Market Levels (Today)
    df_premarket = df_7day.between_time(PREMARKET_OPEN, MARKET_OPEN)
    if not df_premarket.empty:
        df_premarket = df_premarket[df_premarket.index.date == today_date]
        if not df_premarket.empty:
            levels["PM_High"] = df_premarket['High'].max()
            levels["PM_Low"] = df_premarket['Low'].min()

    # 4. 5-min ORB Levels (Today)
    df_orb5 = df_7day.between_time(MARKET_OPEN, ORB_5_END)
    if not df_orb5.empty:
        df_orb5 = df_orb5[df_orb5.index.date == today_date]
        if not df_orb5.empty:
            levels["ORB_5_High"] = df_orb5['High'].max()
            levels["ORB_5_Low"] = df_orb5['Low'].min()

    # 5. 15-min ORB Levels (Today)
    df_orb15 = df_7day.between_time(MARKET_OPEN, ORB_15_END)
    if not df_orb15.empty:
        df_orb15 = df_orb15[df_orb15.index.date == today_date]
        if not df_orb15.empty:
            levels["ORB_15_High"] = df_orb15['High'].max()
            levels["ORB_15_Low"] = df_orb15['Low'].min()
            
    return levels

def plot_chart(df, levels, ticker):
    """Creates an interactive Plotly chart with levels."""
    
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03, 
        subplot_titles=(f'{ticker} 5-Min Chart', 'Volume'),
        row_heights=[0.8, 0.2]
    )
    
    if df.empty:
        return fig, {} # Return an empty figure if no data

    chart_date = df.index[0].date()
    
    # --- Add Shaded Pre-Market Region ---
    pm_start_dt = df.index[0] 
    pm_end_dt = pytz.timezone(MARKET_TZ).localize(dt.datetime.combine(chart_date, MARKET_OPEN))

    fig.add_vrect(
        x0=pm_start_dt, x1=pm_end_dt,
        fillcolor="rgba(100, 100, 100, 0.15)",
        layer="below",
        line_width=0,
        row=1, col=1
    )
    
    fig.add_annotation(
        x=pm_start_dt + (pm_end_dt - pm_start_dt) / 2, 
        y=df['High'].max(),
        yanchor="top",
        text="Pre-Market Session",
        showarrow=False,
        font=dict(color="rgba(100, 100, 100, 0.6)"),
        row=1, col=1
    )

    # 1. Candlestick Chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Candles'
        ),
        row=1, col=1
    )

    # 2. Volume Chart
    color_pos = 'rgba(0, 150, 0, 0.5)'
    color_neg = 'rgba(200, 0, 0, 0.5)'
    color_neu = 'rgba(100, 100, 100, 0.5)'
    
    colors = np.where(df['Close'] > df['Open'], color_pos, 
                        np.where(df['Close'] < df['Open'], color_neg, color_neu))

    fig.add_trace(
        go.Bar(
            x=df.index, 
            y=df['Volume'], 
            name='Volume',
            marker_color=colors
        ),
        row=2, col=1
    )

    # 3. Add Level Lines
    plot_levels = levels.copy() 

    orb_5_high = plot_levels.get("ORB_5_High")
    orb_15_high = plot_levels.get("ORB_15_High")
    
    if orb_5_high is not None and orb_15_high is not None and orb_5_high == orb_15_high:
        plot_levels["ORB_5/15_High"] = orb_5_high
        if "ORB_5_High" in plot_levels: del plot_levels["ORB_5_High"]
        if "ORB_15_High" in plot_levels: del plot_levels["ORB_15_High"]


    orb_5_low = plot_levels.get("ORB_5_Low")
    orb_15_low = plot_levels.get("ORB_15_Low")

    if orb_5_low is not None and orb_15_low is not None and orb_5_low == orb_15_low:
        plot_levels["ORB_5/15_Low"] = orb_5_low
        if "ORB_5_Low" in plot_levels: del plot_levels["ORB_5_Low"]
        if "ORB_15_Low" in plot_levels: del plot_levels["ORB_15_Low"]

    colors = get_level_colors()
    
    for level_name, level_price in plot_levels.items(): 
        if level_price is None:
            continue
        
        fig.add_shape(
            type="line",
            x0=df.index[0], y0=level_price,
            x1=df.index[-1], y1=level_price,
            line=dict(
                color=colors.get(level_name, "gray"),
                width=1.5,
                dash="dash",
            ),
            name=f"{level_name} ({level_price:.2f})",
            row=1, col=1
        )
        
        fig.add_annotation(
            x=df.index[0],
            y=level_price,
            text=f"{level_name} ({level_price:.2f})",
            showarrow=False,
            xanchor="left",
            xshift=5,
            yanchor="bottom",
            font=dict(color=colors.get(level_name, "gray"), size=10),
            bgcolor="rgba(255, 255, 255, 0.7)",
            row=1, col=1
        )

    # --- Customize Layout ---
    fig.update_layout(
        title_text=f"{ticker} Levels - {chart_date.strftime('%Y-%m-%d')}",
        xaxis_title="Time",
        yaxis_title="Price",
        height=700,
        showlegend=False,
        xaxis_rangeslider_visible=False,
        xaxis=dict(range=[df.index.min(), df.index.max()]),
        yaxis=dict(autorange=True, fixedrange=False),
        yaxis2=dict(autorange=True, fixedrange=False)
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0, 0, 0, 0.1)')
    
    return fig, plot_levels

# --- 4. Main App Logic ---

# --- Sidebar (Placed first to get user input) ---
with st.sidebar:
    st.header("Dashboard Controls")
    
    # --- Ticker Input ---
    user_ticker = st.text_input(
        "Enter Ticker Symbol", 
        value=st.session_state.ticker
    ).upper()
    
    # --- Update Ticker Logic ---
    if user_ticker != st.session_state.ticker:
        st.session_state.ticker = user_ticker
        # When user presses Enter, Streamlit reruns
    
    ACTIVE_TICKER = st.session_state.ticker
    
    st.write(f"**Current Ticker:** {ACTIVE_TICKER}")
    
    # --- Placeholders for dynamic info ---
    price_placeholder = st.empty()
    time_placeholder = st.empty()
    st.markdown("---") # Divider
    levels_placeholder = st.empty() # Placeholder for the levels list


# --- Main Page ---
st.title(f"{ACTIVE_TICKER} Intraday Levels Dashboard")

# Fetch data using the ACTIVE_TICKER from the sidebar
# This uses the 7-day function
data = fetch_data(ACTIVE_TICKER)

if data.empty:
    st.error(f"No data found for {ACTIVE_TICKER}. Please check the symbol or try again later.")
    # Clear sidebar placeholders if data fetch fails
    price_placeholder.write("Current Price: N/A")
    time_placeholder.write(f"Last update: {dt.datetime.now(pytz.timezone(MARKET_TZ)).strftime('%I:%M:%S %p ET')}")
    levels_placeholder.info("No levels to display.")

else:
    # Calculate levels using the 7-day data
    levels = calculate_levels(data)
    
    # Filter for *today's* chart
    today_date = data.index[-1].date()
    today_start_dt = pytz.timezone(MARKET_TZ).localize(dt.datetime.combine(today_date, PREMARKET_OPEN))
    
    # Select only today's data for plotting
    data_filtered = data.loc[today_start_dt:]
    
    if data_filtered.empty:
        st.warning("No data for today's session yet. Waiting for pre-market...")
        # Update time/price even if chart is empty
        current_price = data['Close'].iloc[-1]
        price_placeholder.write(f"**Current Price: ${current_price:.2f}**")
        time_placeholder.write(f"Last update: {dt.datetime.now(pytz.timezone(MARKET_TZ)).strftime('%I:%M:%S %p ET')}")
        levels_placeholder.info("Waiting for market open to calculate levels.")

    else:
        current_price = data_filtered['Close'].iloc[-1]
        
        # --- 5. Generate Chart & Get Processed Levels ---
        fig, processed_levels = plot_chart(data_filtered, levels, ACTIVE_TICKER) 
        
        # --- 6. Update Sidebar Placeholders ---
        price_placeholder.write(f"**Current Price: ${current_price:.2f}**")
        time_placeholder.write(f"Last update: {dt.datetime.now(pytz.timezone(MARKET_TZ)).strftime('%I:%M:%S %p ET')}")
        
        with levels_placeholder.container():
            st.subheader("Calculated Levels")
            sorted_levels_display = sorted(
                [item for item in processed_levels.items() if item[1] is not None], 
                key=lambda item: item[1], 
                reverse=True
            )
            if sorted_levels_display:
                for name, price in sorted_levels_display:
                    st.write(f"**{name}:** {price:.2f}")
            else:
                st.write("No levels calculated yet.")

        # --- 7. Display the Chart ---
        st.plotly_chart(fig, use_container_width=True)

        st.caption("This dashboard fetches 7 days of 5-minute data to calculate previous day and pre-market levels.")
        
        # --- 8. AI Analysis Section ---
        st.markdown("---")  # Divider
        st.subheader("🤖 AI Market Analysis")
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            get_ai_feedback = st.button("Get AI Feedback", type="primary", use_container_width=True)
        
        with col2:
            if get_ai_feedback:
                with st.spinner("Analyzing market data with Gemini AI..."):
                    ai_analysis = get_gemini_analysis(processed_levels, current_price, ACTIVE_TICKER)
                    st.markdown(ai_analysis)
            else:
                st.info("Click 'Get AI Feedback' to get an AI-powered analysis of the current market levels.")
        
        # --- 9. Auto-Refresh Loop ---
        # time.sleep(300)  # Wait 300 seconds (5 minutes)
        # st.rerun()       # Rerun the script