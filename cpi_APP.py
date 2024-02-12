import requests
import pandas as pd
from pandas.tseries.offsets import MonthEnd
from datetime import datetime, timedelta

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'api.truflation.io',
    'Origin': 'https://truflation.com',
    'Referer': 'https://truflation.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

response = requests.get("https://api.truflation.io/dashboard-data", headers=headers)

# Check if the request was successful
if response.status_code == 200:
    json_data = response.json()
    cpi_data = json_data.get('n', {})
    cpi_list = [{'Date': date, 'CPI': cpi_values[0]} for date, cpi_values in cpi_data.items()]
    df = pd.DataFrame(cpi_list)
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values(by='Date', ascending=True, inplace=True)
    df['30D RA'] = df['CPI'].rolling(window=30).mean()

    # User input for report date in "yyyy-mm" format then convert, assuming day as the first of the month
    report_date_input = input("Enter the report year and month (yyyy-mm): ")
    report_date = pd.to_datetime(report_date_input + '-01')

    # User input for previous BLS Official CPI YoY Reading
    bls_cpi_input = input("Previous BLS CPI YoY: ")
    bls_cpi = float(bls_cpi_input)

    # Calculate months
    three_months_prior = (report_date - pd.DateOffset(months=4)).date()
    month_following_three_months_prior = (three_months_prior + pd.DateOffset(months=1)).date()
    next_month = (month_following_three_months_prior + pd.DateOffset(months=1)).date()
    next_next_month = (next_month + pd.DateOffset(months=1)).date()

    eom_three_months_prior = (pd.to_datetime(f'{three_months_prior}') + MonthEnd(0)).date()
    eom_following_month = (pd.to_datetime(f'{month_following_three_months_prior}') + MonthEnd(0)).date()
    eom_next_month = (pd.to_datetime(f'{next_month}') + MonthEnd(0)).date()
    eom_next_next_month = (pd.to_datetime(f'{next_next_month}') + MonthEnd(0)).date()

    three_months_prior_cpi = df[df['Date'].dt.strftime('%Y-%m-%d') == df['Date'].dt.year.astype(str) + '-' + eom_three_months_prior.strftime('%m-%d')]['CPI']
    following_month_ra = df[df['Date'].dt.strftime('%Y-%m-%d') == df['Date'].dt.year.astype(str) + '-' + eom_following_month.strftime('%m-%d')]['30D RA']
    next_month_ra = df[df['Date'].dt.strftime('%Y-%m-%d') == df['Date'].dt.year.astype(str) + '-' + eom_next_month.strftime('%m-%d')]['30D RA']
    next_next_month_ra = df[df['Date'].dt.strftime('%Y-%m-%d') == df['Date'].dt.year.astype(str) + '-' + eom_next_next_month.strftime('%m-%d')]['30D RA']

    # Extract scalar values and round the percent changes
    percent_change = round(((following_month_ra.values[0] - three_months_prior_cpi.values[0]) / three_months_prior_cpi.values[0]) * 100, 2)
    percent_change_next_month = round(((next_month_ra.values[0] - following_month_ra.values[0]) / following_month_ra.values[0]) * 100, 2)
    percent_change_next_next_month = round(((next_next_month_ra.values[0] - next_month_ra.values[0]) / next_month_ra.values[0]) * 100, 2)

    # Convert report date to month name
    report_month_name = report_date.strftime('%B')
    first_day_of_current_month = report_date.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    prev_report_month_name = last_day_of_previous_month.strftime('%B')

    # Calculate expected YoY CPI readings and round them
    next_reading = round(bls_cpi * (1 + (percent_change / 100)), 2)
    next_reading2 = round(next_reading * (1 + (percent_change_next_month / 100)), 2)
    next_reading3 = round(next_reading2 * (1 + (percent_change_next_next_month / 100)), 2)

    # Create result DataFrame
    result_df = pd.DataFrame({
        'Reading Month': [report_month_name],
        f'{prev_report_month_name} BLS CPI': [bls_cpi],
        f'{report_month_name} CPI Forecast': [next_reading],
        f'{(report_date + pd.DateOffset(months=1)).strftime("%B")} CPI Forecast': [next_reading2],
        f'{(report_date + pd.DateOffset(months=2)).strftime("%B")} CPI Forecast': [next_reading3]
    })

    # Display and save the result DataFrame
    print(result_df.to_string(index=False))
    #result_df.to_excel(r'C:\Users\WGelletly\Desktop\cpi_percent_change.xlsx', index=False)