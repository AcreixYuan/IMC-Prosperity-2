# Constants
base_treasure = 7500
second_expedition_cost = 25000
third_expedition_cost = 75000

# Data for each spot extracted from the image: (multiplier, hunters)
spots = {
    "G26": (24, 2), "G27": (70, 4), "G28": (41, 3), "G29": (21, 2), "G30": (60, 4),
    "H26": (47, 3), "H27": (82, 5), "H28": (87, 5), "H29": (80, 5), "H30": (35, 3),
    "I26": (73, 4), "I27": (89, 5), "I28": (100, 8), "I29": (90, 7), "I30": (17, 2),
    "J26": (77, 5), "J27": (83, 5), "J28": (85, 5), "J29": (79, 5), "J30": (55, 4),
    "K26": (12, 2), "K27": (27, 3), "K28": (52, 4), "K29": (15, 2), "K30": (30, 3)
}

# For each spot calculate the profit without considering the expedition costs first
# This will give us an idea of which spots are intrinsically the most valuable.
profits = {}
max_multiplier = max([multiplier for multiplier, _ in spots.values()])

for spot, (multiplier, hunters) in spots.items():
    # Popularity is inversely proportional to profit, more popular spots will have their profit divided by a larger number
    popularity_factor = multiplier / max_multiplier  # Between 0 and 1
    total_hunters = hunters + popularity_factor  # Number of hunters adjusted with popularity
    total_treasure = base_treasure * multiplier
    profit = total_treasure / total_hunters
    profits[spot] = profit

# Now let's sort the spots by profit
sorted_profits = sorted(profits.items(), key=lambda item: item[1], reverse=True)

# Displaying the top 5 profitable spots
sorted_profits[:5]
