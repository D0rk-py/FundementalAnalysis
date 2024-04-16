import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import date

# Function to get stock data for multiple tickers
def get_stock_data(tickers):
    data = {}
    for ticker in tickers:
        data[ticker] = yf.Ticker(ticker).info
    return pd.DataFrame(data).T

# Function to remove outliers from data
def remove_outliers(S, std):    
    s1 = S[~((S-S.mean()).abs() > std * S.std())]
    return s1[~((s1-s1.mean()).abs() > std * s1.std())]

# Function to get sector data
def get_sector_data(allStockData):
    sector_data = {}
    sectors = allStockData['sector'].unique()
    metrics = allStockData.columns[3:]
    for sector in sectors:
        sector_rows = allStockData[allStockData['sector'] == sector]
        sector_data[sector] = {}
        for metric in metrics:
            if metric != 'sector':
                sector_data[sector][metric] = {}
                sector_data[sector][metric]['Median'] = sector_rows[metric].median()
                sector_data[sector][metric]['10Pct'] = sector_rows[metric].quantile(0.1)
                sector_data[sector][metric]['90Pct'] = sector_rows[metric].quantile(0.9)
                sector_data[sector][metric]['Std'] = np.std(sector_rows[metric]) / 5
    return sector_data

# Function to get metric grade
def get_metric_grade(sector_metrics, value):
    if value < sector_metrics['10Pct']:
        return 'A+'
    elif value < sector_metrics['Median']:
        return 'A'
    elif value < sector_metrics['90Pct']:
        return 'B'
    else:
        return 'C'

# Function to get category grades
def get_category_grades(ticker, sector, allStockData, sector_data):
    grading_metrics = {'Valuation': ['Forward PE', 'PEG Ratio', 'Price to Sales', 'Price to Book', 'Price to Free Cash Flow'],
                       'Profitability': ['Net Profit Margin', 'Operating Margin', 'Gross Margin', 'Return on Equity', 'Return on Assets'],
                       'Growth': ['EPS Growth (YoY)', 'EPS Growth (Next Year)', 'EPS Growth (Next 5 Years)', 'Revenue Growth (YoY)', 'EPS Growth (Quarterly)'],
                       'Performance': ['Performance (Month)', 'Performance (Quarter)', 'Performance (Half Year)', 'Performance (Year)', 'Performance (YTD)', 'Volatility (Month)']}
    
    category_grades = {}
    
    for category in grading_metrics:
        metric_grades = {}
        for metric_name in grading_metrics[category]:
            metric_val = allStockData.loc[ticker][metric_name]
            metric_grades[metric_name] = get_metric_grade(sector_data[sector][metric_name], metric_val)
        category_grades[category] = metric_grades
        
    return category_grades

# Function to calculate overall rating for a stock
def calculate_overall_rating(category_grades):
    overall_ratings = {}
    grade_scores = {'A+': 4.3, 'A': 4.0, 'B': 3.0, 'C': 2.0}
    for ticker, grades in category_grades.items():
        total_score = sum([grade_scores[grade] for grade in grades.values()])
        overall_ratings[ticker] = round(total_score / len(grades), 2)
    return overall_ratings

# Function to export data to CSV
def export_to_csv(filename, allStockData, category_grades):
    overall_ratings = calculate_overall_rating(category_grades)
    allStockData['Overall Rating'] = [overall_ratings[ticker] for ticker in allStockData.index]
    allStockData.to_csv(filename)
    st.write(f"Data exported to {filename}")

# Main Streamlit web application
def main():
    st.title('Stock Ratings Analysis')
    
    tickers = st.text_input('Enter stock tickers separated by commas (e.g., AAPL, GOOGL, MSFT):')
    tickers = [ticker.strip() for ticker in tickers.split(',')]

    if st.button('Analyze'):
        st.write('Fetching stock data...')
        try:
            allStockData = get_stock_data(tickers)
            st.write(allStockData)

            st.write('Calculating sector data...')
            sector_data = get_sector_data(allStockData)
            st.write(sector_data)

            category_grades = {}
            for ticker in tickers:
                st.write(f'Calculating grades for {ticker}...')
                sector = allStockData.loc[ticker]['sector']
                category_grades[ticker] = get_category_grades(ticker, sector, allStockData, sector_data)
                st.write(category_grades[ticker])

            filename = f"StockRatings-{date.today().strftime('%m.%d.%y')}.csv"
            export_to_csv(filename, allStockData, category_grades)
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
