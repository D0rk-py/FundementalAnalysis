import streamlit as st
import pandas as pd
import numpy as np
import collections
from datetime import date

# Function to get stock data (simulated for demonstration)
def get_stock_data(tickers):
    # Simulated stock data
    data = {
        'Ticker': tickers,
        'Market Cap': [1000000, 2000000, 1500000],  # Example market cap data
        'Sector': ['Technology', 'Finance', 'Healthcare']  # Example sector data
    }
    return pd.DataFrame(data)

# Function to remove outliers from data
def remove_outliers(S, std):    
    s1 = S[~((S-S.mean()).abs() > std * S.std())]
    return s1[~((s1-s1.mean()).abs() > std * s1.std())]

# Function to get sector data
def get_sector_data(allStockData):
    sector_data = collections.defaultdict(lambda: collections.defaultdict(dict))
    sectors = allStockData['Sector'].unique()
    metrics = allStockData.columns[7:-3]

    for sector in sectors:
        rows = allStockData.loc[allStockData['Sector'] == sector]
        for metric in metrics:
            rows[metric] = rows[metric].str.rstrip('%')
            rows[metric] = pd.to_numeric(rows[metric], errors='coerce')
            data = remove_outliers(rows[metric], 2)
            
            sector_data[sector][metric]['Median'] = data.median(skipna=True)
            sector_data[sector][metric]['10Pct'] = data.quantile(0.1)
            sector_data[sector][metric]['90Pct'] = data.quantile(0.9)
            sector_data[sector][metric]['Std'] = np.std(data, axis=0) / 5

    return sector_data

# Function to convert numerical value to letter grade
def convert_to_letter_grade(val):
    grade_scores = {'A+': 4.3, 'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7, 
                    'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'D-': 0.7, 'F': 0.0}
    
    for grade in grade_scores:
        if val >= grade_scores[grade]:
            return grade

# Function to get metric grade
def get_metric_grade(sector, metric_name, metric_val, sector_data):
    lessThan = metric_name in ['Fwd P/E', 'PEG', 'P/S', 'P/B', 'P/FCF', 'Volatility M']
    grade_basis = '10Pct' if lessThan else '90Pct'
    start, change = sector_data[sector][metric_name][grade_basis], sector_data[sector][metric_name]['Std']
    grade_map = {'A+': 0, 'A': change, 'A-': change * 2, 'B+': change * 3, 'B': change * 4, 
                 'B-': change * 5, 'C+': change * 6, 'C': change * 7, 'C-': change * 8, 
                 'D+': change * 9, 'D': change * 10, 'D-': change * 11, 'F': change * 12}
    
    for grade, val in grade_map.items():
        comparison = start + val if lessThan else start - val
       
        if lessThan and metric_val < comparison:
            return grade
        
        if not lessThan and metric_val > comparison:
            return grade
            
    return 'C'

# Function to get category grades
def get_category_grades(ticker, sector, allStockData, sector_data):
    grading_metrics = {'Valuation': ['Fwd P/E', 'PEG', 'P/S', 'P/B', 'P/FCF'],
                       'Profitability': ['Profit M', 'Oper M', 'Gross M', 'ROE', 'ROA'],
                       'Growth': ['EPS this Y', 'EPS next Y', 'EPS next 5Y', 'Sales Q/Q', 'EPS Q/Q'],
                       'Performance': ['Perf Month', 'Perf Quart', 'Perf Half', 'Perf Year', 'Perf YTD', 'Volatility M']}
    
    grade_scores = {'A+': 4.3, 'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7, 
                    'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'D-': 0.7, 'F': 0.0}
    
    category_grades = {}
    
    for category in grading_metrics:
        metric_grades = []
        for metric_name in grading_metrics[category]:
            metric_grades.append(get_metric_grade(sector, metric_name, 
                                                  get_metric_val(ticker, metric_name, allStockData), sector_data))
        category_grades[category] = metric_grades
        
    for category in category_grades:
        score = sum(grade_scores[grade] for grade in category_grades[category])
        category_grades[category].append(round(score / len(category_grades[category]), 2))
        
    return category_grades

# Function to get stock rating
def get_stock_rating(category_grades):
    grade_scores = {'A+': 4.3, 'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7, 
                    'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'D-': 0.7, 'F': 0.0}
    
    score = sum(grade_scores[grade] for grade in category_grades['Overall Rating'][:-1])
    return round(score * 6.2, 2)

# Function to get stock rating data
def get_stock_rating_data(tickers, allStockData, sector_data):
    data_to_add = collections.defaultdict(list)
    
    for ticker in tickers:
        category_grades = get_category_grades(ticker, 
                                              allStockData.loc[allStockData['Ticker'] == ticker]['Sector'].values[0], 
                                              allStockData, sector_data)
        stock_rating = get_stock_rating(category_grades)
        data_to_add['Overall Rating'].append(stock_rating)
        data_to_add['Valuation Grade'].append(convert_to_letter_grade(category_grades['Valuation'][-1]))
        data_to_add['Profitability Grade'].append(convert_to_letter_grade(category_grades['Profitability'][-1]))
        data_to_add['Growth Grade'].append(convert_to_letter_grade(category_grades['Growth'][-1]))
        data_to_add['Performance Grade'].append(convert_to_letter_grade(category_grades['Performance'][-1]))
        
    return data_to_add

# Function to export data to CSV
def export_to_csv(filename, allStockData, data_to_add):
    allStockData['Overall Rating'] = data_to_add['Overall Rating']
    allStockData['Valuation Grade'] = data_to_add['Valuation Grade']
    allStockData['Profitability Grade'] = data_to_add['Profitability Grade']
    allStockData['Growth Grade'] = data_to_add['Growth Grade']
    allStockData['Performance Grade'] = data_to_add['Performance Grade']    
    allStockData['Percent Diff'] = (pd.to_numeric(allStockData['Target Price'], errors='coerce') - pd.to_numeric(allStockData['Price'], errors='coerce')) / pd.to_numeric(allStockData['Price'], errors='coerce') * 100

    ordered_columns = 'Ticker, Company, Market Cap, Overall Rating, Sector, Industry, Country, Valuation Grade, Profitability Grade, Growth Grade, Performance Grade, Fwd P/E, PEG, P/S, P/B, P/C, P/FCF, Dividend, Payout Ratio, EPS this Y, EPS next Y, EPS past 5Y, EPS next 5Y, Sales past 5Y, EPS Q/Q, Sales Q/Q, Insider Own, Insider Trans, Inst Own, Inst Trans, Short Ratio, ROA, ROE, ROI, Curr R, Quick R, LTDebt/Eq, Debt/Eq, Gross M, Oper M, Profit M, Perf Month, Perf Quart, Perf Half, Perf Year, Perf YTD, Volatility M, SMA20, SMA50, SMA200, 52W High, 52W Low, RSI, Earnings, Price, Target Price, Percent Diff'

    stock_csv_data = allStockData
    stock_csv_data = allStockData[ordered_columns.replace(', ', ',').split(',')]
    stock_csv_data.to_csv(filename, index=False)
    
    st.write('\nSaved as', f"StockRatings-{today_date}.csv")

# Main Streamlit web application
def main():
    st.title('Stock Ratings Analysis')
    
    tickers = st.text_input('Enter stock tickers separated by commas (e.g., AAPL, GOOGL, MSFT):')
    tickers = [ticker.strip() for ticker in tickers.split(',')]
    
    if st.button('Analyze'):
        # Simulate fetching stock data
        allStockData = get_stock_data(tickers)
        
        # Simulate getting sector data
        sector_data = get_sector_data(allStockData)
        
        # Simulate getting stock rating data
        data_to_add = get_stock_rating_data(tickers, allStockData, sector_data)
        
        # Export data to CSV
        export_to_csv(f"StockRatings-{date.today().strftime('%m.%d.%y')}.csv", allStockData, data_to_add)

if __name__ == '__main__':
    main()
