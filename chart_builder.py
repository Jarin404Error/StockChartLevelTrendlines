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
    CHART_HEIGHT_WITH_INDICATORS, CHART_ROW_HEIGHTS_WITH_INDICATORS, INDICATOR_VERTICAL_SPACING,
    LEVEL_COLORS, PREMARKET_FILL_COLOR, PREMARKET_TEXT_COLOR,
    VOLUME_COLOR_POSITIVE, VOLUME_COLOR_NEGATIVE, VOLUME_COLOR_NEUTRAL,
    LEVEL_LINE_WIDTH, LEVEL_LINE_DASH, LEVEL_FONT_SIZE, LEVEL_LABEL_BG_COLOR,
    RSI_COLOR, RSI_OVERBOUGHT, RSI_OVERSOLD, RSI_OVERBOUGHT_COLOR, RSI_OVERSOLD_COLOR,
    VWAP_COLOR, MACD_LINE_COLOR, MACD_SIGNAL_COLOR, 
    MACD_HISTOGRAM_POSITIVE, MACD_HISTOGRAM_NEGATIVE
)


def create_chart_figure(ticker: str, with_indicators: bool = False) -> go.Figure:
    """
    Creates the base Plotly figure with subplots.
    
    Args:
        ticker: Stock symbol for chart title
        with_indicators: If True, creates 4 subplots (Price, RSI, MACD, Volume)
                        If False, creates 2 subplots (Price, Volume)
        
    Returns:
        Plotly Figure object with subplots
    """
    if with_indicators:
        fig = make_subplots(
            rows=4, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=INDICATOR_VERTICAL_SPACING, 
            subplot_titles=(f'{ticker} 5-Min Chart', 'RSI', 'MACD', 'Volume'),
            row_heights=CHART_ROW_HEIGHTS_WITH_INDICATORS,
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": False}],
                   [{"secondary_y": False}],
                   [{"secondary_y": False}]]
        )
    else:
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
            name='Price',
            showlegend=False
        ),
        row=1, col=1
    )


def add_vwap_line(fig: go.Figure, df: pd.DataFrame, vwap: pd.Series):
    """
    Adds VWAP line to the price chart.
    
    Args:
        fig: Plotly figure object to modify
        df: DataFrame with chart data
        vwap: Series with VWAP values
    """
    if vwap.empty or vwap.isna().all():
        return
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=vwap,
            mode='lines',
            name='VWAP',
            line=dict(color=VWAP_COLOR, width=2),
            showlegend=True
        ),
        row=1, col=1
    )


def add_volume_chart(fig: go.Figure, df: pd.DataFrame, volume_row: int = 2):
    """
    Adds volume chart with color-coded bars based on price direction.
    
    Bars are colored:
    - Green if close > open (bullish)
    - Red if close < open (bearish)
    - Gray if close == open (neutral)
    
    Args:
        fig: Plotly figure object to modify
        df: DataFrame with OHLCV data
        volume_row: Row number for volume chart (default: 2)
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
            marker_color=colors,
            showlegend=False
        ),
        row=volume_row, col=1
    )


def add_rsi_chart(fig: go.Figure, df: pd.DataFrame, rsi: pd.Series):
    """
    Adds RSI indicator chart with overbought/oversold zones.
    
    Args:
        fig: Plotly figure object to modify
        df: DataFrame with chart data
        rsi: Series with RSI values
    """
    if rsi.empty or rsi.isna().all():
        return
    
    # Add RSI line
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=rsi,
            mode='lines',
            name='RSI',
            line=dict(color=RSI_COLOR, width=2),
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Add overbought line (70)
    fig.add_hline(
        y=RSI_OVERBOUGHT, 
        line_dash="dash", 
        line_color="red", 
        line_width=1,
        row=2, col=1
    )
    
    # Add oversold line (30)
    fig.add_hline(
        y=RSI_OVERSOLD, 
        line_dash="dash", 
        line_color="green", 
        line_width=1,
        row=2, col=1
    )
    
    # Add shaded regions for overbought/oversold
    fig.add_hrect(
        y0=RSI_OVERBOUGHT, y1=100,
        fillcolor=RSI_OVERBOUGHT_COLOR,
        layer="below",
        line_width=0,
        row=2, col=1
    )
    
    fig.add_hrect(
        y0=0, y1=RSI_OVERSOLD,
        fillcolor=RSI_OVERSOLD_COLOR,
        layer="below",
        line_width=0,
        row=2, col=1
    )


def add_macd_chart(fig: go.Figure, df: pd.DataFrame, macd: pd.Series, 
                   signal: pd.Series, histogram: pd.Series):
    """
    Adds MACD indicator chart with signal line and histogram.
    
    Args:
        fig: Plotly figure object to modify
        df: DataFrame with chart data
        macd: Series with MACD line values
        signal: Series with signal line values
        histogram: Series with histogram values
    """
    if macd.empty or macd.isna().all():
        return
    
    # Add MACD line
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=macd,
            mode='lines',
            name='MACD',
            line=dict(color=MACD_LINE_COLOR, width=2),
            showlegend=False
        ),
        row=3, col=1
    )
    
    # Add signal line
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=signal,
            mode='lines',
            name='Signal',
            line=dict(color=MACD_SIGNAL_COLOR, width=2),
            showlegend=False
        ),
        row=3, col=1
    )
    
    # Add histogram with color coding
    colors = np.where(
        histogram >= 0,
        MACD_HISTOGRAM_POSITIVE,
        MACD_HISTOGRAM_NEGATIVE
    )
    
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=histogram,
            name='Histogram',
            marker_color=colors,
            showlegend=False
        ),
        row=3, col=1
    )
    
    # Add zero line
    fig.add_hline(
        y=0,
        line_dash="solid",
        line_color="gray",
        line_width=1,
        row=3, col=1
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


def configure_chart_layout(fig: go.Figure, df: pd.DataFrame, ticker: str, 
                          chart_date: dt.date, with_indicators: bool = False):
    """
    Configures the overall chart layout and styling.
    
    Args:
        fig: Plotly figure object to modify
        df: DataFrame with chart data
        ticker: Stock symbol
        chart_date: Date being displayed
        with_indicators: Whether indicators are included
    """
    height = CHART_HEIGHT_WITH_INDICATORS if with_indicators else CHART_HEIGHT
    
    fig.update_layout(
        title_text=f"{ticker} Levels - {chart_date.strftime('%Y-%m-%d')}",
        xaxis_title="Time",
        yaxis_title="Price",
        height=height,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis_rangeslider_visible=False,
    )
    
    # Configure x-axis range for all subplots
    fig.update_xaxes(
        range=[df.index.min(), df.index.max()],
        showgrid=False
    )
    
    # Configure y-axes
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0, 0, 0, 0.1)')
    
    # Set RSI y-axis range if indicators are present
    if with_indicators:
        fig.update_yaxes(range=[0, 100], row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        fig.update_yaxes(title_text="Volume", row=4, col=1)
        
        # Add bold white separator line between price chart and RSI
        fig.add_shape(
            type="line",
            xref="paper", yref="paper",
            x0=0, y0=0.65,  # Horizontal line at 65% height (between price and RSI)
            x1=1, y1=0.65,
            line=dict(color="white", width=5),
            layer="above"
        )
        
        # Add separator line between RSI and MACD
        fig.add_shape(
            type="line",
            xref="paper", yref="paper",
            x0=0, y0=0.45,  # Horizontal line at 45% height (between RSI and MACD)
            x1=1, y1=0.45,
            line=dict(color="white", width=5),
            layer="above"
        )
        
        # Add separator line between MACD and Volume
        fig.add_shape(
            type="line",
            xref="paper", yref="paper",
            x0=0, y0=0.25,  # Horizontal line at 25% height (between MACD and Volume)
            x1=1, y1=0.25,
            line=dict(color="white", width=5),
            layer="above"
        )


def plot_chart(df: pd.DataFrame, levels: dict, ticker: str, 
               indicators: dict = None) -> tuple:
    """
    Creates a complete interactive Plotly chart with levels, volume, and indicators.
    
    This is the main orchestrator function that builds the entire chart
    by combining all chart components: candlesticks, volume, level lines,
    pre-market shading, and technical indicators.
    
    Args:
        df: DataFrame with today's OHLCV data
        levels: Dictionary of level names to prices
        ticker: Stock symbol
        indicators: Optional dictionary of calculated indicators
        
    Returns:
        Tuple of (figure, levels) where figure is the Plotly Figure object
        and levels is the dictionary of levels (unchanged for consistency)
        
    Example:
        >>> fig, levels = plot_chart(today_data, calculated_levels, 'AAPL', indicators)
        >>> fig.show()
    """
    # Determine if we're showing indicators
    with_indicators = indicators is not None and len(indicators) > 0
    
    # Create base figure
    fig = create_chart_figure(ticker, with_indicators=with_indicators)
    
    if df.empty:
        return fig, {}
    
    chart_date = df.index[0].date()
    
    # Add price chart components
    add_premarket_shading(fig, df, chart_date)
    add_candlestick_chart(fig, df)
    
    # Add VWAP if indicators are provided
    if with_indicators and 'vwap' in indicators:
        add_vwap_line(fig, df, indicators['vwap'])
    
    # Add level lines
    add_level_lines(fig, df, levels)
    
    # Add indicators if provided
    if with_indicators:
        # Add RSI
        if 'rsi' in indicators:
            add_rsi_chart(fig, df, indicators['rsi'])
        
        # Add MACD
        if 'macd' in indicators:
            add_macd_chart(
                fig, df, 
                indicators['macd'], 
                indicators['macd_signal'], 
                indicators['macd_histogram']
            )
        
        # Add volume to row 4
        add_volume_chart(fig, df, volume_row=4)
    else:
        # Add volume to row 2 (no indicators)
        add_volume_chart(fig, df, volume_row=2)
    
    # Configure layout and styling
    configure_chart_layout(fig, df, ticker, chart_date, with_indicators=with_indicators)
    
    return fig, levels
