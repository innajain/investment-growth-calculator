import wbdata
import yfinance as yf
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

def calculate_annual_return(start_date, num_years, data):
    

    # Find the closest available index for the start date
    start_idx = np.abs((data.index - start_date).total_seconds()).argmin()

    # Calculate the end date as 5 years from the start date
    end_date = start_date + timedelta(days=num_years * 365)
    
    # Find the closest available index for the end date
    end_idx = np.abs((data.index - end_date).total_seconds()).argmin()

    # Get the start and end values from the dataset
    start_value = data.iloc[start_idx]
    end_value = data.iloc[end_idx]

    # Calculate the annual return based on start and end values
    num_yrs = (data.index[end_idx] - data.index[start_idx]).days / 365
    value_ratio = end_value / start_value

    annual_return = (value_ratio ** (1 / num_yrs)) - 1

    return annual_return.item()

def generate_random_dates(start_date, end_of_start_date, num_dates):
    random_dates = []

    for _ in range(num_dates):
        # Random number of days to add to the start date
        random_days = random.randint(0, (end_of_start_date - start_date).days)
        random_date = start_date + timedelta(days=random_days)
        random_dates.append(random_date.strftime('%Y-%m-%d'))

    random_dates = [datetime.strptime(date, "%Y-%m-%d") for date in random_dates]
    return random_dates


def check_standard_deviation_rule(returns_absolute):

    returns = [x*100 for x in returns_absolute]
    average_return = np.mean(returns)
    std_deviation = np.std(returns)

    # Check how many returns fall within each range
    within_68 = sum((returns >= (average_return - std_deviation)) & (returns <= (average_return + std_deviation))) / len(returns)
    within_95 = sum((returns >= (average_return - 2 * std_deviation)) & (returns <= (average_return + 2 * std_deviation))) / len(returns)
    within_997 = sum((returns >= (average_return - 3 * std_deviation)) & (returns <= (average_return + 3 * std_deviation))) / len(returns)

    # Print the results
    print(f"Percentage of simulated returns within 1 Std Dev (68%): {within_68 * 100:.2f}%")
    print(f"Percentage of simulated returns within 2 Std Dev (95%): {within_95 * 100:.2f}%")
    print(f"Percentage of simulated returns within 3 Std Dev (99.7%): {within_997 * 100:.2f}%")

def calculate_avg_inflation_rate(start_date, num_years, data):
    # Find the closest available index for the start date
    start_idx = np.abs((data.index - start_date).total_seconds()).argmin()

    # Calculate the end date as 5 years from the start date
    end_date = start_date + timedelta(days=num_years * 365)
    
    # Find the closest available index for the end date
    end_idx = np.abs((data.index - end_date).total_seconds()).argmin()

    # Get the start and end values from the dataset
    inflation_rates = data.iloc[start_idx:end_idx].values
    
    avg_inflation_rate = np.prod([1 + r/100 for r in inflation_rates])**(1/len(inflation_rates)) - 1
    
    return avg_inflation_rate

def do_simulation(num_years, ticker, num_random_dates):
    # Download data only once
    data = pd.read_csv(f"{ticker}_data.csv", index_col=0, parse_dates=True)

    # Check if there is enough data available for the specified number of years
    start_date = datetime.strptime(data.index[0].strftime('%Y-%m-%d'), '%Y-%m-%d')
    end_of_start_date = datetime(datetime.now().year - num_years, 12, 31)
    if end_of_start_date < start_date:
        print("Error: Not enough data available for the specified number of years")
        return

    # Information about the inflation rate
    indicator = {"FP.CPI.TOTL.ZG": "Inflation (%)"}
    inflation_data = pd.read_csv(f"inflation_data.csv", index_col=0, parse_dates=True)

    # Generate random dates
    random_dates = generate_random_dates(start_date, end_of_start_date, num_random_dates)
    # Calculate the annual return for each random date
    annual_returns = []
    avg_inflation_rates = []
    for date in random_dates:
        annual_return = calculate_annual_return(date, num_years, data)
        annual_returns.append(annual_return)
        avg_inflation_rate = calculate_avg_inflation_rate(date, num_years, inflation_data)
        avg_inflation_rates.append(avg_inflation_rate)

    # Calculate the average annual return
    average_annual_return = np.prod([1 + r for r in annual_returns])**(1/len(annual_returns)) - 1
    print(f"{ticker} Analysis for {num_random_dates} random {num_years} year periods with start date between {start_date.strftime('%Y-%m-%d')} and {end_of_start_date.strftime('%Y-%m-%d')}")
    print(f"Average annual returns (Geometric Mean): {average_annual_return:.2%}")
    standard_deviation = np.std(annual_returns)
    print(f"Standard deviation of returns: {standard_deviation:.2%}")
    print(f"Average inflation rate: {np.mean(avg_inflation_rates):.2%}")
    print(f"Standard deviation of inflation rate: {np.std(avg_inflation_rates):.2%}")

def download_data(ticker):
    if ticker=="inflation":
        indicator = {"FP.CPI.TOTL.ZG": "Inflation (%)"}
        data = wbdata.get_dataframe(indicator, country="IND", parse_dates=True)
        # reverse the data
        data = data.iloc[::-1]
        data.to_csv("inflation_data.csv")
        return
    data = yf.download(ticker, auto_adjust=True, progress=False)
    data = data["Close"]
    data.to_csv(f"{ticker}_data.csv")

def main():
    for ticker in ["^BSESN", "^NSEI"]:
        for period in [5, 10, 15]:
            do_simulation(period, ticker, 1000)

if __name__ == "__main__":
    main()
    # download_data("^BSEMCAP")
