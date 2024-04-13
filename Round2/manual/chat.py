import numpy as np

# The exchange rates matrix as given in the image
# Note: The matrix should be inverted because we want to multiply how many units of currency
# we get for one unit of the base currency, not how many units of base currency we get
# for one unit of the given currency.
exchange_rates = np.array([
    [1,      0.48, 1.52, 0.71],
    [2.05,   1,      3.26, 1.56],
    [0.64,   0.3,   1,      0.46],
    [1.41,   0.61,   2.08,   1]
])

# The number of currencies
n = exchange_rates.shape[0]

# Function to print the arbitrage sequence
def print_arbitrage_sequence(sequence, profit):
    items = ['Pizza Slice', 'Wasabi Root', 'Snowball', 'Shells']
    path = ' -> '.join([items[i] for i in sequence])
    print(f"Arbitrage opportunity: {path} with a profit of {profit - 1:.4f} per unit")



# Function to find the arbitrage opportunities
def find_arbitrage_2(exchange_rates):
    # Use Floyd-Warshall algorithm to find all possible paths
    for k in range(n- 1):
        if exchange_rates[3][k]* exchange_rates[k][3] > 1.0:
            print(k, exchange_rates[3][k]* exchange_rates[k][3])

# Function to find the arbitrage opportunities
def find_arbitrage_3(exchange_rates):
    # Use Floyd-Warshall algorithm to find all possible paths
    for k in range(n- 1):
        for i in range(n - 1):
            if exchange_rates[3][k]* exchange_rates[k][i] * exchange_rates[i][3] > 1.0:
                if i!=k:
                    print(k,i, exchange_rates[3][k]* exchange_rates[k][i] * exchange_rates[i][3])


# Function to find the arbitrage opportunities
def find_arbitrage_4(exchange_rates):
    # Use Floyd-Warshall algorithm to find all possible paths
    for k in range(n - 1):
        for i in range(n - 1):
            for j in range(n - 1):
                if exchange_rates[3][k]*exchange_rates[k][i]*exchange_rates[i][j]*exchange_rates[j][3] > 1.0:
                    if k!=i and k!=j and j!=i:
                        print(k,i,j, exchange_rates[3][k]*exchange_rates[k][i]*exchange_rates[i][j]*exchange_rates[j][3])

# Function to find the arbitrage opportunities
def find_arbitrage_5(exchange_rates):
    # Use Floyd-Warshall algorithm to find all possible paths
    for k in range(n - 1):
        for i in range(n - 1):
            for j in range(n - 1):
                for l in range(n - 1):
                    if exchange_rates[3][k]*exchange_rates[k][i]*exchange_rates[i][j]*exchange_rates[j][l] *exchange_rates[l][3] > 1.0:
                        if k!=i and i!=j and j!=l:
                            print(k,i,j,l,exchange_rates[3][k]*exchange_rates[k][i]*exchange_rates[i][j]*exchange_rates[j][l] *exchange_rates[l][3])



find_arbitrage_2(exchange_rates)
find_arbitrage_3(exchange_rates)
find_arbitrage_4(exchange_rates)
find_arbitrage_5(exchange_rates)