"""
Chart building module for the Intraday Levels Dashboard.

This module handles all chart creation and visualization using Plotly.
"""

import datetime as dt
import numpy as np
import pandas as pd
import pytz
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import (
    MARKET_TZ, MARKET_OPEN,
    CHART_HEIGHT, CHART_ROW_HEIGHTS, CHART_VERTICAL_SPACING,
    LEVEL_COLORS, PREMARKET_FILL_COLOR, PREMARKET_TEXT_COLOR,
    VOLUME_COLOR_POSITIVE, VOLUME_COLOR_NEGATIVE, VOLUME_COLOR_NEUTRAL,
    LEVEL_LINE_WIDTH, LEVEL_LINE_DASH, LEVEL_FONT_SIZE, LEVEL_LABEL_BG_COLOR
)


def create_chart_figure(ticker: str) -> go.Figure:
    """
    Creates the base Plotly figure with subplots for price and volume.
    
    Args:
        ticker: Stock symbol for chart title
        
    Returns:
        Plotly Figure object with 2 subplots
    """
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=CHART_VERTICAL_SPACING, 
        subplot_titles=(f'{ticker} 5-Min Chart', 'Volume'),
        row_heights=CHART_ROW_HEIGHTS
    )
    return fig


def add_premarket_shading(fig: go.Figure, df: pd.DataFrame, chart_date: dt.date):
    """
    Adds shaded pre-market region to the chart with label.
    
    Args:
        fig: Plotly figure object to modify
        df: DataFrame with chart data
        chart_date: Date being displayed on the chart
    """
    pm_start_dt = df.index[0] 
    pm_end_dt = pytz.timezone(MARKET_TZ).localize(
        dt.datetime.combine(chart_date, MARKET_OPEN)
    )
    
    # Add shaded rectangle for pre-market period
    fig.add_vrect(
        x0=pm_start_dt, 
        x1=pm_end_dt,
        fillcolor=PREMARKET_FILL_COLOR,
        layer="below",
        line_width=0,
        row=1, col=1
    )
    
    # Add "Pre-Market Session" label
    fig.add_annotation(
        x=pm_start_dt + (pm_end_dt - pm_start_dt) / 2, 
        y=df['High'].max(),
        yanchor="top",
        text="Pre-Market Session",
        showarrow=False,
        font=dict(color=PREMARKET_TEXT_COLOR),
        row=1, col=1
    )


def add_candlestick_chart(fig: go.Figure, df: pd.DataFrame):
    """
    Adds candlestick chart trace to the figure.
    
    Args:
        fig: Plotly figure object to modify
        df: DataFrame with OHLCV data
    """
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


def add_volume_chart(fig: go.Figure, df: pd.DataFrame):
    """
    Adds volume chart with color-coded bars based on price direction.
    
    Bars are colored:
    - Green if close > open (bullish)
    - Red if close < open (bearish)
    - Gray if close == open (neutral)
    
    Args:
        fig: Plotly figure object to modify
        df: DataFrame with OHLCV data
    """
    # Determine bar colors based on price movement
    colors = np.where(
        df['Close'] > df['Open'], 
        VOLUME_COLOR_POSITIVE, 
        np.where(
            df['Close'] < df['Open'], 
            VOLUME_COLOR_NEGATIVE, 
            VOLUME_COLOR_NEUTRAL
        )
    )
    
    fig.add_trace(
        go.Bar(
            x=df.index, 
            y=df['Volume'], 
            name='Volume',
            marker_color=colors
        ),
        row=2, col=1
    )


def add_level_lines(fig: go.Figure, df: pd.DataFrame, levels: dict):
    """
    Adds horizontal lines and labels for key trading levels.
    
    Each level gets:
    - A dashed horizontal line across the chart
    - A text label showing the level name and price
    
    Args:
        fig: Plotly figure object to modify
        df: DataFrame with chart data (for time range)
        levels: Dictionary mapping level names to prices
    """
    for level_name, level_price in levels.items(): 
        if level_price is None:
            continue
        
        color = LEVEL_COLORS.get(level_name, "gray")
        
        # Add horizontal line
        fig.add_shape(
            type="line",
            x0=df.index[0], 
            y0=level_price,
            x1=df.index[-1], 
            y1=level_price,
            line=dict(
                color=color,
                width=LEVEL_LINE_WIDTH,
                dash=LEVEL_LINE_DASH,
            ),
            name=f"{level_name} ({level_price:.2f})",
            row=1, col=1
        )
        
        # Add label annotation
        fig.add_annotation(
            x=df.index[0],
            y=level_price,
            text=f"{level_name} ({level_price:.2f})",
            showarrow=False,
            xanchor="left",
            xshift=5,
            yanchor="bottom",
            font=dict(color=color, size=LEVEL_FONT_SIZE),
            bgcolor=LEVEL_LABEL_BG_COLOR,
            row=1, col=1
        )


def configure_chart_layout(fig: go.Figure, df: pd.DataFrame, ticker: str, chart_date: dt.date):
    """
    Configures the overall chart layout and styling.
    
    Args:
        fig: Plotly figure object to modify
        df: DataFrame with chart data
        ticker: Stock symbol
        chart_date: Date being displayed
    """
    fig.update_layout(
        title_text=f"{ticker} Levels - {chart_date.strftime('%Y-%m-%d')}",
        xaxis_title="Time",
        yaxis_title="Price",
        height=CHART_HEIGHT,
        showlegend=False,
        xaxis_rangeslider_visible=False,
        xaxis=dict(range=[df.index.min(), df.index.max()]),
        yaxis=dict(autorange=True, fixedrange=False),
        yaxis2=dict(autorange=True, fixedrange=False)
    )
    
    # Style the grid
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0, 0, 0, 0.1)')


def plot_chart(df: pd.DataFrame, levels: dict, ticker: str) -> tuple:
    """
    Creates a complete interactive Plotly chart with levels and volume.
    
    This is the main orchestrator function that builds the entire chart
    by combining all chart components: candlesticks, volume, level lines,
    and pre-market shading.
    
    Args:
        df: DataFrame with today's OHLCV data
        levels: Dictionary of level names to prices
        ticker: Stock symbol
        
    Returns:
        Tuple of (figure, levels) where figure is the Plotly Figure object
        and levels is the dictionary of levels (unchanged for consistency)
        
    Example:
        >>> fig, levels = plot_chart(today_data, calculated_levels, 'AAPL')
        >>> fig.show()
    """
    # Create base figure
    fig = create_chart_figure(ticker)
    
    if df.empty:
        return fig, {}
    
    chart_date = df.index[0].date()
    
    # Add all chart components
    add_premarket_shading(fig, df, chart_date)
    add_candlestick_chart(fig, df)
    add_volume_chart(fig, df)
    add_level_lines(fig, df, levels)
    
    # Configure layout and styling
    configure_chart_layout(fig, df, ticker, chart_date)
    
    return fig, levels

