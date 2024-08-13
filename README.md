# Stock Analysis Tool

This Python-based tool fetches stock data, calculates various technical indicators, and generates interactive charts for analysis.

## Features

- Fetch stock data from Yahoo Finance
- Calculate technical indicators (MA50, MA200, MACD, RSI, Bollinger Bands, Ichimoku Cloud)
- Generate interactive charts using Plotly
- Export charts to an HTML dashboard

## Requirements

- Python 3.7+
- pandas
- yfinance
- plotly
- ta (Technical Analysis Library)

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/winningday/stocksdashboard.git
   cd stocksdashboard
   ```
2. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

Run the script from the command line:
```
python stocks.py [-h] [-c CSV_FILE] [-s START_DATE] [-i INDICATORS]
```

Arguments:
- `-h`, `--help`: Show help message and exit
- `-c CSV_FILE`, `--csv_file CSV_FILE`: Path to the CSV file containing stock symbols (default: stocks.csv)
- `-s START_DATE`, `--start_date START_DATE`: Start date for fetching stock data (format: YYYY-MM-DD, default: 2018-01-01)
- `-i INDICATORS`, `--indicators INDICATORS`: Comma-separated list of indicators to add (e.g., MA50,MA200,MACD,RSI,BollingerBands,Ichimoku)

Example:
```
python stocks.py -c my_stocks.csv -s 2022-01-01 -i MA50,RSI,MACD
```

## Output

The script generates an HTML file (`dashboard1.html`) containing interactive charts for each stock in the input CSV file.

## Testing

To run the tests:
```
pytest test_stocks.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original idea based on work by Juan Villamizar
- Adapted and extended by Marc Goodman
