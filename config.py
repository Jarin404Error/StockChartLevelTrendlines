"""
Configuration settings for the Intraday Levels Dashboard.

This module contains all constants, configuration settings, and default values
used throughout the application.
"""

import datetime as dt


# ============================================================================
# MARKET CONFIGURATION
# ============================================================================

# Market timezone (NYSE)
MARKET_TZ = "America/New_York"

# Market hours (Eastern Time)
PREMARKET_OPEN = dt.time(4, 0)
MARKET_OPEN = dt.time(9, 30)
MARKET_CLOSE = dt.time(16, 0)

# Opening Range Breakout (ORB) times
ORB_5_END = dt.time(9, 35)      # First 5 minutes after open
ORB_15_END = dt.time(9, 45)     # First 15 minutes after open

# Global session times (in ET for SPY)
ASIA_SESSION_START = dt.time(18, 0)    # 6:00 PM ET (previous day)
ASIA_SESSION_END = dt.time(2, 0)       # 2:00 AM ET (next day)
LONDON_SESSION_START = dt.time(2, 0)   # 2:00 AM ET
LONDON_SESSION_END = dt.time(9, 30)    # 9:30 AM ET (US market open)


# ============================================================================
# DATA FETCHING CONFIGURATION
# ============================================================================

# Data fetching parameters
DATA_PERIOD = "7d"              # Fetch last 7 days of data
DATA_INTERVAL = "5m"            # 5-minute intervals
CACHE_TTL = 120                 # Cache data for 2 minutes (in seconds)
AUTO_REFRESH_INTERVAL = 120     # Auto-refresh every 2 minutes (in seconds)


# ============================================================================
# UI CONFIGURATION
# ============================================================================

# Page settings
PAGE_TITLE = "Intraday Levels Dashboard"
PAGE_ICON = "📈"
PAGE_LAYOUT = "wide"

# Default ticker symbol
DEFAULT_TICKER = "TSLA"


# ============================================================================
# CHART CONFIGURATION
# ============================================================================

# Chart dimensions
CHART_HEIGHT = 700
CHART_ROW_HEIGHTS = [0.8, 0.2]  # Price chart vs volume chart ratio
CHART_VERTICAL_SPACING = 0.03

# Level colors for visualization
LEVEL_COLORS = {
    "PM_High": "red",
    "PM_Low": "red",
    "ORB_5_High": "blue",
    "ORB_5_Low": "blue",
    "ORB_15_High": "green",
    "ORB_15_Low": "green",
    "PDH": "gray",          # Previous Day High
    "PDL": "gray",          # Previous Day Low
    "ORB_5/15_High": "cyan",
    "ORB_5/15_Low": "cyan",
    "Asia_High": "orange",  # Asia session high
    "Asia_Low": "orange",   # Asia session low
    "London_High": "purple", # London session high
    "London_Low": "purple",  # London session low
}

# Pre-market shading color
PREMARKET_FILL_COLOR = "rgba(100, 100, 100, 0.15)"
PREMARKET_TEXT_COLOR = "rgba(100, 100, 100, 0.6)"

# Volume bar colors
VOLUME_COLOR_POSITIVE = "rgba(0, 150, 0, 0.5)"
VOLUME_COLOR_NEGATIVE = "rgba(200, 0, 0, 0.5)"
VOLUME_COLOR_NEUTRAL = "rgba(100, 100, 100, 0.5)"

# Level line styling
LEVEL_LINE_WIDTH = 1.5
LEVEL_LINE_DASH = "dash"
LEVEL_FONT_SIZE = 10
LEVEL_LABEL_BG_COLOR = "rgba(255, 255, 255, 0.7)"


# ============================================================================
# INDICATOR CONFIGURATION
# ============================================================================

# RSI settings
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# MACD settings
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Indicator colors
RSI_COLOR = "purple"
RSI_OVERBOUGHT_COLOR = "rgba(255, 0, 0, 0.2)"
RSI_OVERSOLD_COLOR = "rgba(0, 255, 0, 0.2)"
VWAP_COLOR = "orange"
MACD_LINE_COLOR = "blue"
MACD_SIGNAL_COLOR = "red"
MACD_HISTOGRAM_POSITIVE = "rgba(0, 150, 0, 0.5)"
MACD_HISTOGRAM_NEGATIVE = "rgba(200, 0, 0, 0.5)"

# Chart layout with indicators
CHART_HEIGHT_WITH_INDICATORS = 1000
CHART_ROW_HEIGHTS_WITH_INDICATORS = [0.5, 0.15, 0.15, 0.2]  # Price, RSI, MACD, Volume
INDICATOR_VERTICAL_SPACING = 0.02
