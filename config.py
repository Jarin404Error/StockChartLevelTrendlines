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


# ============================================================================
# DATA FETCHING CONFIGURATION
# ============================================================================

# Data fetching parameters
DATA_PERIOD = "7d"              # Fetch last 7 days of data
DATA_INTERVAL = "5m"            # 5-minute intervals
CACHE_TTL = 300                 # Cache data for 5 minutes (in seconds)


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

