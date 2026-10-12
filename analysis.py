# Importing the necessary libraries
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import math

# Defining a function to format the return values for display
def format_return(value):
    rounded_value = round(value, 2)

    if rounded_value > 0:
        return "+" + str(rounded_value)
    else:
        return str(rounded_value)

# (Yahoo Finance)'s codes for the four banks and our market benchmark (like FTSE Ticker Symbols)
# Lloyds, NatWest, Barclays, HSBC and the FTSE 100
tickers = ["LLOY.L", "NWG.L", "BARC.L", "HSBA.L", "^FTSE"]

# Download daily data including enough history for our volume comparison.
data = yf.download(
    tickers,
    start="2022-12-01",
    end="2025-01-01",
    auto_adjust = False,
    actions = True,
    progress = False
)

# Extract the dividends data from the downloaded data
dividends = data["Dividends"]

# Extract the daily closing prices
prices = data["Close"]

# Display the last five trading days
print("Closing prices:")
last_five_rows = prices.tail(5)
rounded_prices = last_five_rows.round(2)
print(rounded_prices)







# Put the previous trading day's prices alongside todays
previous_prices = prices.shift(1)

# Calculate the percentage change for every column
daily_returns = ((prices / previous_prices) - 1) * 100

# Display returns around the announcement
print("\nDaily returns (%):")
selected_returns = daily_returns.loc["2024-01-29":"2024-02-02"]
formatted_table = selected_returns.to_string(float_format=format_return)
print(formatted_table)






# Choose the announcement date
announcement_date = "2024-02-01"

# Get the FTSEs percentage change on that date
market_return = daily_returns.loc[announcement_date, "^FTSE"]

# List the banks we want to compare with the market
banks = ["LLOY.L", "NWG.L", "BARC.L", "HSBA.L"]

print()
print("Bank returns minus FTSE 100 on", announcement_date)
print("Figures are in percentage points.")

# Repeat the comparison for each bank
for bank in banks:
    bank_return = daily_returns.loc[announcement_date, bank]
    adjusted_return = bank_return - market_return
    print(bank, format_return(adjusted_return))
    
    
    
    
    
# Choose the three-day window around the announcement
window_start = "2024-01-31"
window_end = "2024-02-02"

# Extract the FTSE returns for these three days
market_window = daily_returns.loc[window_start:window_end, "^FTSE"]

print()
print("Three day cumulative abnormal returns (percentage points):")

# Creating an empty list to store the results for each bank
CAR_results = []

for bank in banks:
    # Extract this bank's returns for the same three days
    bank_window = daily_returns.loc[window_start:window_end, bank]

    # Minus the FTSE return on each corresponding date
    abnormal_returns = bank_window - market_window

    # Add the three daily differences together for the Three Day Cumulative Abnormal Return (CAR)
    CAR = abnormal_returns.sum(min_count=3)
    
    CAR_results.append(CAR)
    
    print(bank, format_return(CAR))
    






# Extract daily trading volumes from our existing download
volumes = data["Volume"]

# Calculate a "Last 20 trading days" average for each column
rolling_average = volumes.rolling(20).mean()

# Shift the averages so each date uses only earlier trading days
previous_average = rolling_average.shift(1)

print()
print("Relative trading volume on", announcement_date)
relative_volume_results = []


for bank in banks:
    announcement_volume = volumes.loc[announcement_date, bank]
    average_volume = previous_average.loc[announcement_date, bank]

    relative_volume = announcement_volume / average_volume
    relative_volume_results.append(relative_volume)

    print(bank, round(relative_volume, 2), "x")
    
    
    
    
    
    
    
# Each element in the list contains an announcement date and decision type
decisions = [
    ["2023-02-02", "Hike"],
    ["2023-03-23", "Hike"],
    ["2023-05-11", "Hike"],
    ["2023-06-22", "Hike"],
    ["2023-08-03", "Hike"],
    ["2023-09-21", "Hold"],
    ["2023-11-02", "Hold"],
    ["2023-12-14", "Hold"],
    ["2024-02-01", "Hold"],
    ["2024-03-21", "Hold"],
    ["2024-05-09", "Hold"],
    ["2024-06-20", "Hold"],
    ["2024-08-01", "Cut"],
    ["2024-09-19", "Hold"],
    ["2024-11-07", "Cut"],
    ["2024-12-19", "Hold"]
]







print()
print("MARKET-ADJUSTED RETURNS ACROSS ALL DECISIONS")
print("Figures are in percentage points.")

all_results = []

for decision in decisions:
    event_date = decision[0]
    decision_type = decision[1]

    # Find the announcement's row number in the returns table
    event_position = daily_returns.index.get_loc(event_date)

    # Select the previous, announcement and following trading days
    event_window = daily_returns.iloc[
        event_position - 1:event_position + 2
    ]

    event_market_return = daily_returns.loc[event_date, "^FTSE"]
    event_market_window = event_window["^FTSE"]

    print()
    print(event_date, decision_type)

    for bank in banks:
        # Announcement day comparison
        event_bank_return = daily_returns.loc[event_date, bank]
        adjusted_return = event_bank_return - event_market_return

        # Three-day CAR.
        event_bank_window = event_window[bank]
        abnormal_returns = event_bank_window - event_market_window
        event_car = abnormal_returns.sum(min_count=3)

        # Relative trading volume.
        event_volume = volumes.loc[event_date, bank]
        average_volume = previous_average.loc[event_date, bank]
        relative_volume = event_volume / average_volume
        
        
        # Check for an ex-dividend date within the three-day window
        dividend_window = dividends.loc[event_window.index, bank]

        if dividend_window.isna().any():
            raise ValueError("Missing dividend data for " + bank + " on " + event_date)

        has_dividend = dividend_window.sum() > 0

        if has_dividend:
            print("Dividend overlap:", event_date, bank)



        # Save the results as one row in our list
        all_results.append([
            event_date,
            decision_type,
            bank,
            adjusted_return,
            event_car,
            relative_volume,
            has_dividend
        ])

        print(
            bank,
            "Adjusted:", format_return(adjusted_return),
            "CAR:", format_return(event_car),
            "Volume:", round(relative_volume, 2), "x"
        )

print()
print("Number of result rows:", len(all_results))








# Column names follow the same order as each row in all_results
column_names = [
    "Date",
    "Decision",
    "Bank",
    "Adjusted return (pp)",
    "CAR (pp)",
    "Relative volume",
    "Dividend overlap"
]

# Stops if any calculated metric is missing or infinite
for result_row in all_results:
    for value in result_row[3:6]:
        if not math.isfinite(value):
            raise ValueError(
                "Missing or invalid result for "
                + result_row[0] + " " + result_row[2]
            )


# Convert our list of result rows into a labelled table.
results = pd.DataFrame(all_results, columns=column_names)

# Select rows without a dividend overlap.
no_dividend_overlap = results["Dividend overlap"] == False
results_without_dividends = results.loc[no_dividend_overlap]

print()
print("All observations:", len(results))
print("Observations without dividend overlaps:", len(results_without_dividends))

# Save all results, including the flags, for the project.
results.to_csv("results.csv", index=False)





# Choose the columns we want to average
metrics = [
    "Adjusted return (pp)",
    "CAR (pp)",
    "Relative volume"
]

# Calculate averages for each decision type
summary_all = results.groupby("Decision")[metrics].mean()

summary_without_dividends = (
    results_without_dividends.groupby("Decision")[metrics].mean()
)

# Count the bank-announcement observations in each category
counts_all = results.groupby("Decision").size()
counts_without_dividends = (
    results_without_dividends.groupby("Decision").size()
)

# Add those counts as a column in each summary
summary_all["Observations"] = counts_all
summary_without_dividends["Observations"] = counts_without_dividends

print()
print("AVERAGES: ALL OBSERVATIONS")
print(summary_all.round(2))

print()
print("AVERAGES: EXCLUDING DIVIDEND OVERLAPS")
print(summary_without_dividends.round(2))





# Put the decisions in a logical order.
decision_order = ["Hike", "Hold", "Cut"]

# Collect both sets of CAR averages in a new table.
car_comparison = pd.DataFrame()

car_comparison["All observations"] = summary_all["CAR (pp)"]

car_comparison["Excluding dividend overlaps"] = (
    summary_without_dividends["CAR (pp)"]
)

# Arrange the rows as Hike, Hold, Cut.
car_comparison = car_comparison.loc[decision_order]

# Draw two bars next to each other for each decision type.
car_comparison.plot(
    kind="bar",
    figsize=(8, 5),
    color=["steelblue", "orange"],
    rot=0
)

plt.axhline(0, color="black", linewidth=1)

plt.title(
    "Average three-day CAR around BoE decisions, 2023–2024\n"
    "5 hikes, 9 holds and 2 cuts"
)

plt.xlabel("BoE decision")
plt.ylabel("Mean CAR versus FTSE 100 (percentage points)")

plt.tight_layout()
plt.savefig("car_by_decision.png", dpi=150)
plt.show()






## Now we can visualize the results of our analysis - CAR and relative trading volume

# Names follow the same order as our banks list
bank_names = ["Lloyds", "NatWest", "Barclays", "HSBC"]


# Visualising the Cumulative Abnormal Return results
plt.figure(figsize=(8, 5))

# Draw one bar for each bank
plt.bar(bank_names, CAR_results, color="steelblue")

# Draw a horizontal line at zero
plt.axhline(0, color="black", linewidth=1)

# Explain what the chart shows
plt.title("UK bank shares around the BoE announcement\n31 January-2 February 2024")
plt.ylabel("Three day CAR versus FTSE 100 (percentage points)")

# Adjusting the spacing and display formatting
plt.tight_layout()
plt.savefig("car_2024-02-01.png", dpi=150)
plt.show()



# Visualising the relative trading volume results
plt.figure(figsize=(8, 5))

plt.bar(bank_names, relative_volume_results, color="steelblue")

# One means trading volume matched its previous 20-day average
plt.axhline(1, color="black", linestyle="--", linewidth=1)

plt.title("UK bank trading activity\nBoE announcement: " + announcement_date)
plt.ylabel("Trading volume / previous 20-day average")

plt.tight_layout()
plt.savefig("relative_volume_2024-02-01.png", dpi=150)
plt.show()