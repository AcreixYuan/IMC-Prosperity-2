#%%
import numpy as np
import matplotlib.pyplot as plt

def generate_reserve_prices(num_fish, low=900, high=1000):
    """Generate reserve prices for goldfish, linearly more likely towards the high end."""
    # Using a linear distribution: P(x) = 2*(x - low) / (high - low)**2
    scale = (high - low)
    samples = np.random.rand(num_fish)  # Uniform distribution
    reserve_prices = low + scale * np.sqrt(samples)
    return reserve_prices

#%%
def simulate_bids(reserve_prices, bid1, bid2):
    """Simulate trading with two bid prices and calculate the number of sales and profit."""
    sales1 = np.sum(reserve_prices <= bid1)
    sales2 = np.sum((reserve_prices > bid1) & (reserve_prices <= bid2))
    
    total_sales = sales1 + sales2
    total_profit = total_sales * 1000 - (sales1 * bid1 + sales2 * bid2)

    avg_profit = total_profit / len(reserve_prices)
    
    return avg_profit

#%%
num_fish = 100000
reserve_prices = generate_reserve_prices(num_fish)

# loop through all possible bid prices and get best avg_profit
best_profit = -np.inf
best_bid1 = 901
best_bid2 = 902

for bid1 in range(901, 998):
    for bid2 in range(bid1+1, 999):
        avg_profit = simulate_bids(reserve_prices, bid1, bid2)
        if avg_profit > best_profit:
            best_profit = avg_profit
            best_bid1 = bid1
            best_bid2 = bid2

print(f"Best bid prices: {best_bid1}, {best_bid2}")
print(f"Best profit: {best_profit}")
# %%
