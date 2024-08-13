'''
Stock data fetching and visualization tool.

usage: stocks.py [-h] [-c CSV_FILE] [-s START_DATE] [-i INDICATORS]

optional arguments:
  -h, --help            show this help message and exit
  -c CSV_FILE, --csv_file CSV_FILE
                        Path to the CSV file containing stock symbols
  -s START_DATE, --start_date START_DATE
                        Start date for fetching stock data (format: YYYY-MM-DD)
  -i INDICATORS, --indicators INDICATORS
                        Comma-separated list of indicators to add (e.g., MA50,MA200,MACD,RSI,BollingerBands,Ichimoku)

Base Code and original idea from https://www.youtube.com/watch?v=rV0m9U7FLnE written by Juan Villamizar 
Full working code adapted by Marc Goodman
'''

import argparse
import datetime as dt
import os
import json
import time
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as py
import ta


def main():
    """Main function to orchestrate the stock data processing and visualization."""
    args = parse_arguments()
    stocks = get_stocks(args.csv_file)
    start_date = args.start_date
    indicators = args.indicators
    all_figs = []

    for stock in stocks:
        df_stock = create_df(stock, start_date)
        df_indicator = add_indicator(df_stock, indicators)
        fig_stock = plot(stock, df_indicator, indicators)
        all_figs.append(fig_stock)

    generate_html(all_figs)


def parse_arguments(args=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Fetch and plot stock data")
    parser.add_argument(
        '-c', '--csv_file', type=str, default='stocks.csv',
        help='Path to the CSV file containing stock symbols'
    )
    parser.add_argument(
        '-s', '--start_date', type=lambda s: dt.datetime.strptime(s, '%Y-%m-%d'),
        default=dt.datetime(2018, 1, 1),
        help='Start date for fetching stock data (format: YYYY-MM-DD)'
    )
    parser.add_argument(
        '-i', '--indicators', type=str, default='MA50,MA200',
        help='Comma-separated list of indicators to add (e.g., MA50,MA200,MACD,RSI,BollingerBands,Ichimoku)'
    )
    return parser.parse_args(args)


def get_stocks(csv_file):
    """Get stocks from CSV file."""
    with open(csv_file) as file:
        return [line.rstrip().upper() for line in file]


def create_df(symbol, start_date, cache_dir='cache', refresh_interval=10800):
    """Create stock Data Frame for stock."""
    end = datetime.now()
    cache_file = os.path.join(cache_dir, f'{symbol}.json')

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    if os.path.exists(cache_file):
        last_modified_time = os.path.getmtime(cache_file)
        if time.time() - last_modified_time < refresh_interval:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
                df = pd.DataFrame(cached_data)
                df.index = pd.to_datetime(df.index)
                return df

    df = yf.download(symbol, start=start_date, end=end)
    df.to_json(cache_file, date_format='iso')

    return df


def add_indicator(df, indicators):
    """Add indicators to stock data frame."""
    indicators_list = indicators.split(',')
    for indicator in indicators_list:
        if indicator == 'MA50':
            df['MA50'] = df['Close'].rolling(window=50, min_periods=0).mean()
        elif indicator == 'MA200':
            df['MA200'] = df['Close'].rolling(window=200, min_periods=0).mean()
        elif indicator == 'MA20':
            df['MA20'] = df['Close'].rolling(window=20, min_periods=0).mean()
        elif indicator == 'MACD':
            df['MACD'] = ta.trend.macd_diff(df['Close'])
        elif indicator == 'RSI':
            df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        elif indicator == 'BollingerBands':
            bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
            df['BB_upper'] = bb.bollinger_hband()
            df['BB_lower'] = bb.bollinger_lband()
            df['BB_middle'] = bb.bollinger_mavg()
        elif indicator == 'Ichimoku':
            ichimoku = ta.trend.IchimokuIndicator(
                high=df['High'], low=df['Low'], window1=9, window2=26, window3=52
            )
            df['Tenkan_sen'] = ichimoku.ichimoku_conversion_line()
            df['Kijun_sen'] = ichimoku.ichimoku_base_line()
            df['Senkou_span_a'] = ichimoku.ichimoku_a()
            df['Senkou_span_b'] = ichimoku.ichimoku_b()
            df['Chikou_span'] = df['Close'].shift(-26)
    return df


def plot(symbol, df1, indicators):
    """Plot price + volume stock."""
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.1, subplot_titles=(symbol, 'Volume'),
        row_width=[0.2, 0.7]
    )

    fig.add_trace(go.Candlestick(
        x=df1.index, open=df1['Open'], high=df1['High'],
        low=df1['Low'], close=df1['Close'], name='OHLC'
    ), row=1, col=1)

    indicators_list = indicators.split(',')
    for indicator in indicators_list:
        if indicator == 'MA50':
            fig.add_trace(go.Scatter(x=df1.index, y=df1['MA50'], marker_color='green', name='MA50'), row=1, col=1)
        elif indicator == 'MA200':
            fig.add_trace(go.Scatter(x=df1.index, y=df1['MA200'], marker_color='blue', name='MA200'), row=1, col=1)
        elif indicator == 'MA20':
            fig.add_trace(go.Scatter(x=df1.index, y=df1['MA20'], marker_color='red', name='MA20'), row=1, col=1)
        elif indicator == 'MACD':
            fig.add_trace(go.Scatter(x=df1.index, y=df1['MACD'], marker_color='purple', name='MACD'), row=1, col=1)
        elif indicator == 'RSI':
            fig.add_trace(go.Scatter(x=df1.index, y=df1['RSI'], marker_color='orange', name='RSI'), row=1, col=1)
        elif indicator == 'BollingerBands':
            fig.add_trace(go.Scatter(
                x=df1.index, y=df1['BB_upper'], line=dict(color='rgba(0, 0, 255, 0.2)', width=1),
                name='Bollinger Bands Upper', fill=None
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df1.index, y=df1['BB_lower'], line=dict(color='rgba(0, 0, 255, 0.2)', width=1),
                fill='tonexty', fillcolor='rgba(179, 223, 255, 0.3)', name='Bollinger Bands Lower'
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df1.index, y=df1['BB_middle'], line=dict(color='blue', width=1),
                name='Bollinger Bands Middle'
            ), row=1, col=1)
        elif indicator == 'Ichimoku':
            add_ichimoku_traces(fig, df1)

    fig.add_trace(go.Bar(x=df1.index, y=df1['Volume'], marker_color='red', showlegend=False), row=2, col=1)

    fig.update_layout(
        title=f'{symbol} historical price chart',
        xaxis_tickfont_size=12,
        yaxis=dict(
            title='price ($/share)',
            titlefont_size=14,
            tickfont_size=12
        ),
        autosize=False,
        width=560,
        height=420,
        margin=dict(l=50, r=20, b=50, t=80, pad=5),
        paper_bgcolor='LightSteelBlue',
        plot_bgcolor='white'
    )
    fig.update_xaxes(rangeslider_visible=False)

    return fig


def add_ichimoku_traces(fig, df1):
    """Add Ichimoku Cloud traces to the figure."""
    fig.add_trace(go.Scatter(x=df1.index, y=df1['Tenkan_sen'], line=dict(color='blue', width=1), name='Tenkan-sen'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df1.index, y=df1['Kijun_sen'], line=dict(color='red', width=1), name='Kijun-sen'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df1.index, y=df1['Senkou_span_a'], line=dict(color='green', width=1), name='Senkou Span A'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df1.index, y=df1['Senkou_span_b'], line=dict(color='orange', width=1), name='Senkou Span B'), row=1, col=1)

    for i in range(1, len(df1)):
        if df1['Senkou_span_a'][i] > df1['Senkou_span_b'][i] and df1['Senkou_span_a'][i-1] > df1['Senkou_span_b'][i-1]:
            add_cloud_trace(fig, df1, i, 'green')
        elif df1['Senkou_span_a'][i] < df1['Senkou_span_b'][i] and df1['Senkou_span_a'][i-1] < df1['Senkou_span_b'][i-1]:
            add_cloud_trace(fig, df1, i, 'red')

    fig.add_trace(go.Scatter(x=df1.index, y=df1['Chikou_span'], line=dict(color='lightgrey', width=1), name='Chikou Span'), row=1, col=1)


def add_cloud_trace(fig, df1, i, color):
    """Add a cloud trace to the Ichimoku chart."""
    fig.add_trace(go.Scatter(
        x=[df1.index[i-1], df1.index[i]],
        y=[df1['Senkou_span_a'][i-1], df1['Senkou_span_a'][i]],
        fill=None, mode='lines', line=dict(color='rgba(255, 255, 255, 0)'),
        showlegend=False, hoverinfo='skip'
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=[df1.index[i-1], df1.index[i]],
        y=[df1['Senkou_span_b'][i-1], df1['Senkou_span_b'][i]],
        fill='tonexty', fillcolor=f'rgba({"0, 200, 0" if color == "green" else "255, 0, 0"}, 0.2)',
        mode='lines', line=dict(color='rgba(255, 255, 255, 0)'),
        name=f'Cloud {color.capitalize()}'
    ), row=1, col=1)


def generate_html(all_figs):
    """Generate HTML file with all charts."""
    with open("dashboard1.html", 'w') as file_html_graphs:
        file_html_graphs.write("<html><head></head><body>\n")

        for i, fig in enumerate(all_figs):
            py.plot(fig, filename=f'Chart_{i}.html', auto_open=False)
            file_html_graphs.write(f'  <object data="Chart_{i}.html" width="600" height="460"></object>\n')

        file_html_graphs.write("</body></html>")


if __name__ == "__main__":
    main()