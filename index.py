import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


trades_df = pd.read_csv("trades_file.csv")
prices_df = pd.read_csv("prices_file.csv")

# Create a dictionary to store position information for each symbol
positions = {}

# Initialize a list to store PNL at each timestamp
pnl_list = []


for index, row in trades_df.iterrows():
    time = row['time']
    symbol = row['symbol']
    trade_size = row['tradeSize']
    trade_price = row['tradePrice']

    # Initialize position for the symbol if not exists
    if symbol not in positions:
        positions[symbol] = {'position': 0, 'prev_price': None}

    # Calculate PNL for the trade
    if trade_size > 0:  # Buy
        positions[symbol]['position'] += trade_size
    else:  # Sell
        positions[symbol]['position'] += trade_size
    if positions[symbol]['position'] == 0:
        pnl = positions[symbol]['position'] * (trade_price - positions[symbol]['prev_price'])
        pnl_list.append({'time': time, 'symbol': symbol, 'pnl': pnl})
    positions[symbol]['prev_price'] = trade_price

# Square off remaining positions at 15:25:00
for symbol, position_info in positions.items():
    if position_info['position'] != 0:
        time = '15:25:00'
        trade_size = -position_info['position']
        trade_price = prices_df[(prices_df['time'] == time) & (prices_df['symbol'] == symbol)]['price'].values[0]
        pnl = trade_size * (trade_price - position_info['prev_price'])
        pnl_list.append({'time': time, 'symbol': symbol, 'pnl': pnl})

# Create a DataFrame to store PNL information
pnl_df = pd.DataFrame(pnl_list)
pnl_df = pnl_df.sort_values(by='time')


# Calculate the total PNL for each symbol
symbol_pnl = pnl_df.groupby('symbol')['pnl'].sum()

# Calculate the maximum and minimum PNL
max_pnl_symbol = symbol_pnl.idxmax()
max_pnl_value = symbol_pnl.max()
min_pnl_symbol = symbol_pnl.idxmin()
min_pnl_value = symbol_pnl.min()

# Calculate the maximum intraday drawdown
cumulative_pnl = pnl_df.groupby('time')['pnl'].sum().cumsum()
max_drawdown = (cumulative_pnl - cumulative_pnl.expanding().max()).min()

# Sort the DataFrame by time and drop duplicates
pnl_df = pnl_df.sort_values(by='time').drop_duplicates(subset=['time'])

# Plot the intraday PNL chart
plt.figure(figsize=(10, 5))
plt.plot(pnl_df['time'], pnl_df.groupby('time')['pnl'].sum().cumsum(), label='Intraday PNL')
plt.xlabel('Time')
plt.ylabel('PNL')
plt.title('Intraday PNL')
plt.legend()
plt.grid()

# Show the symbols with max and min PNL
print(f"Symbol with Max PNL: {max_pnl_symbol}, PNL: {max_pnl_value}")
print(f"Symbol with Min PNL: {min_pnl_symbol}, PNL: {min_pnl_value}")
print(f"Maximum Intraday Drawdown: {max_drawdown}")

# Display the PNL chart
plt.show()
