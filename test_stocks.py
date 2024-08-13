import pytest
import pandas as pd
from datetime import datetime
from stocks import (
    parse_arguments,
    get_stocks,
    create_df,
    add_indicator,
    plot,
    generate_html
)

@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    dates = pd.date_range(start='2023-01-01', end='2023-01-10')
    data = {
        'Open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'High': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
        'Low': [98, 99, 100, 101, 102, 103, 104, 105, 106, 107],
        'Close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        'Volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
    }
    return pd.DataFrame(data, index=dates)

def test_parse_arguments():
    args = parse_arguments([])  # Pass an empty list to simulate no command-line arguments
    assert hasattr(args, 'csv_file')
    assert hasattr(args, 'start_date')
    assert hasattr(args, 'indicators')

def test_get_stocks(tmp_path):
    csv_file = tmp_path / "test_stocks.csv"
    csv_file.write_text("AAPL\nGOOG\nMSFT")
    stocks = get_stocks(str(csv_file))
    assert stocks == ['AAPL', 'GOOG', 'MSFT']

def test_create_df(mocker, sample_df):
    mocker.patch('yfinance.download', return_value=sample_df)
    df = create_df('AAPL', datetime(2023, 1, 1), cache_dir='test_cache')
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 10

def test_add_indicator(sample_df):
    indicators = 'MA50,RSI'
    df_with_indicators = add_indicator(sample_df, indicators)
    assert 'MA50' in df_with_indicators.columns
    assert 'RSI' in df_with_indicators.columns

def test_plot(sample_df):
    sample_df_with_indicators = add_indicator(sample_df, 'MA50,RSI')
    fig = plot('AAPL', sample_df_with_indicators, 'MA50,RSI')
    assert fig.layout.title.text == 'AAPL historical price chart'

def test_generate_html(tmp_path, mocker):
    mocker.patch('plotly.offline.plot')
    all_figs = [mocker.Mock(), mocker.Mock()]
    output_file = tmp_path / "dashboard1.html"
    
    mock_open = mocker.mock_open()
    mocker.patch('builtins.open', mock_open)
    
    generate_html(all_figs)
    
    mock_open.assert_called_once_with("dashboard1.html", 'w')
    handle = mock_open()
    handle.write.assert_any_call("<html><head></head><body>\n")
    handle.write.assert_any_call("</body></html>")