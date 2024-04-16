import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import collections

# Sample list of multiple stock tickers
tickers = ["AAPL", "GOOGL", "MSFT"]

grading_metrics = {
    'Valuation': ['Forward PE', 'PEG Ratio', 'Price to Sales', 'Price to Book', 'Price to Free Cash Flow'],
    'Profitability': ['Net Profit Margin', 'Operating Margin', 'Gross Margin', 'Return on Equity', 'Return on Assets'],
    'Growth': ['EPS Growth (YoY)', 'EPS Growth (Next Year)', 'EPS Growth (Next 5 Years)', 'Revenue Growth (YoY)', 'EPS Growth (Quarterly)'],
    'Performance': ['Performance (Month)', 'Performance (Quarter)', 'Performance (Half Year)', 'Performance (Year)', 'Performance (YTD)', 'Volatility (Month)']
}

# Function to fetch stock data for multiple tickers
def fetch_stock_data(tickers):
    data = {}
    for ticker in tickers:
        data[ticker] = yf.Ticker(ticker).info
    return pd.DataFrame(data).T

# Sample function to calculate sector data
def calculate_sector_data(stock_data):
    sector_data = collections.defaultdict(lambda: collections.defaultdict(dict))
    sectors = stock_data['sector'].unique()
    metrics = stock_data.columns[3:]
    for sector in sectors:
        sector_rows = stock_data[stock_data['sector'] == sector]
        for metric in metrics:
            if metric != 'sector':
                sector_data[sector][metric]['Median'] = sector_rows[metric].median()
                sector_data[sector][metric]['10Pct'] = sector_rows[metric].quantile(0.1)
                sector_data[sector][metric]['90Pct'] = sector_rows[metric].quantile(0.9)
                sector_data[sector][metric]['Std'] = np.std(sector_rows[metric]) / 5
    return sector_data

# Sample function to calculate grading for a stock
def calculate_stock_grading(stock_data, sector_data):
    grading = {}
    for ticker, row in stock_data.iterrows():
        sector = row['sector']
        category_grades = {}
        for category, metrics in grading_metrics.items():
            metric_grades = {}
            for metric in metrics:
                val = row[metric]
                grade = get_metric_grade(sector_data[sector][metric], val)
                metric_grades[metric] = grade
            category_grades[category] = metric_grades
        grading[ticker] = category_grades
    return grading

# Sample function to get metric grade
def get_metric_grade(sector_metrics, value):
    if value < sector_metrics['10Pct']:
        return 'A+'
    elif value < sector_metrics['Median']:
        return 'A'
    elif value < sector_metrics['90Pct']:
        return 'B'
    else:
        return 'C'

# Sample function to calculate overall rating for a stock
def calculate_overall_rating(grading):
    overall_ratings = {}
    for ticker, category_grades in grading.items():
        total_score = sum([sum(grade.values()) for grade in category_grades.values()])
        overall_rating = round(total_score / len(grading_metrics), 2)
        overall_ratings[ticker] = overall_rating
    return overall_ratings

# Sample function to export data to CSV
def export_to_csv(stock_data, grading, overall_ratings):
    filename = f"StockRatings.csv"
    stock_data['Overall Rating'] = [overall_ratings[ticker] for ticker in stock_data.index]
    for category in grading_metrics.keys():
        for metric in grading_metrics[category]:
            stock_data[f'{metric} Grade'] = [grading[ticker][category][metric] for ticker in stock_data.index]
    stock_data.to_csv(filename)
    return filename

# Main function to run the Streamlit app
def main():
    st.title("Stock Ratings Analysis")

    # Fetch stock data
    st.write("Fetching stock data...")
    stock_data = fetch_stock_data(tickers)
    st.write("Stock data fetched.")
    st.write(stock_data)

    # Calculate sector data
    st.write("Calculating sector data...")
    sector_data = calculate_sector_data(stock_data)
    st.write("Sector data calculated.")
    st.write(sector_data)

    # Calculate grading for each stock
    st.write("Calculating grading...")
    grading = calculate_stock_grading(stock_data, sector_data)
    st.write("Grading calculated.")
    st.write(grading)

    # Calculate overall ratings
    st.write("Calculating overall ratings...")
    overall_ratings = calculate_overall_rating(grading)
    st.write("Overall ratings calculated.")
    st.write(overall_ratings)

    # Export data to CSV
    st.write("Exporting data to CSV...")
    filename = export_to_csv(stock_data, grading, overall_ratings)
    st.write(f"Data exported to {filename}")

if __name__ == "__main__":
    main()
