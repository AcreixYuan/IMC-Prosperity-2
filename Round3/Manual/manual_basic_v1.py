# Constants
base_treasure = 7500
second_expedition_cost = 25000
third_expedition_cost = 75000

# Data for each spot extracted from the image: (multiplier, hunters)
spots = {
    "G26": (24, 2), "G27": (70, 4), "G28": (41, 3), "G29": (21, 2), "G30": (60, 4),
    "H47": (47, 3), "H82": (82, 5), "H87": (87, 5), "H80": (80, 5), "H35": (35, 3),
    "I73": (73, 4), "I89": (89, 5), "I100": (100, 8), "I90": (90, 7), "I17": (17, 2),
    "J77": (77, 5), "J83": (83, 5), "J85": (85, 5), "J79": (79, 5), "J55": (55, 4),
    "K12": (12, 2), "K27": (27, 3), "K52": (52, 4), "K15": (15, 2), "K30": (30, 3)
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
