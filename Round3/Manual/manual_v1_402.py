import numpy as np
import pandas as pd

# Constants
BASE_TREASURE = 7500
EXPEDITION_COSTS = [0, 25000, 75000]

# Define the spots and their respective multipliers and hunters.
spots = {
    "G26": (24, 2), "G27": (70, 4), "G28": (41, 3), "G29": (21, 2), "G30": (60, 4),
    "H26": (47, 3), "H27": (82, 5), "H28": (87, 5), "H29": (80, 5), "H30": (35, 3),
    "I26": (73, 4), "I27": (89, 5), "I28": (100, 8), "I29": (90, 7), "I30": (17, 2),
    "J26": (77, 5), "J27": (83, 5), "J28": (85, 5), "J29": (79, 5), "J30": (55, 4),
    "K26": (12, 2), "K27": (27, 3), "K28": (52, 4), "K29": (15, 2), "K30": (30, 3)
}

# Convert spots into a DataFrame for easier manipulation
spots_df = pd.DataFrame.from_dict(spots, orient='index', columns=['Multiplier', 'Hunters'])

# Function to calculate expected treasure for a single spot
def calculate_expected_treasure(multiplier, hunters, expedition_percentage):
    total_treasure = BASE_TREASURE * multiplier
    split_factor = hunters + (expedition_percentage / 100.0)
    expected_treasure = total_treasure / split_factor
    return expected_treasure

# Simulation of 1000 players' selections
def simulate_selections(spots_df, num_players):
    # Normalizing the choice probability based on the spot's attractiveness (high multiplier, fewer hunters)
    attractiveness = (spots_df['Multiplier'] / spots_df['Hunters'])
    probabilities = attractiveness / attractiveness.sum()
    
    # Simulating player choices
    choices = np.random.choice(spots_df.index, size=num_players, p=probabilities)
    
    # Counting how many times each spot was chosen
    choice_counts = pd.Series(choices).value_counts().reindex(spots_df.index, fill_value=0)
    
    # Calculating the percentage of expeditions that took place at each spot
    expedition_percentages = (choice_counts / num_players) * 100
    
    return expedition_percentages

# Run the simulation
num_players = 1000
expedition_percentages = simulate_selections(spots_df, num_players)
expedition_percentages
# Function to calculate the profit for each spot based on the simulated selections
def calculate_profits(spots_df, expedition_percentages, num_expeditions):
    profits = pd.DataFrame(columns=['Expedition 1', 'Expedition 2', 'Expedition 3'], index=spots_df.index)
    
    # Calculate the profit for each expedition
    for spot in spots_df.index:
        for i in range(num_expeditions):
            expected_treasure = calculate_expected_treasure(spots_df.loc[spot, 'Multiplier'],
                                                            spots_df.loc[spot, 'Hunters'],
                                                            expedition_percentages[spot])
            # Subtract the expedition cost if it's the 2nd or 3rd expedition
            profit = expected_treasure - EXPEDITION_COSTS[i] if i > 0 else expected_treasure
            profits.at[spot, f'Expedition {i + 1}'] = float(profit)
            
    return profits

# # We can calculate profits for up to 3 expeditions (including costs)
# profits = calculate_profits(spots_df, expedition_percentages, 2)

# # Find the best choices for each case
# best_one_expedition = profits['Expedition 1'].astype(float).idxmax()
# best_two_expeditions = profits['Expedition 1'].add(profits['Expedition 2'], fill_value=0).astype(float).idxmax()
# best_three_expeditions = profits['Expedition 1'].add(profits['Expedition 2'], fill_value=0).add(profits['Expedition 3'], fill_value=0).astype(float).idxmax()

# print(profits)

def simulate_selections_normal_distribution(spots_df, num_players, std_dev=5):
    # Calculate the 'mean' score for each spot based on attractiveness
    attractiveness = (spots_df['Multiplier'] / spots_df['Hunters'])
    
    # Generate scores using a normal distribution centered around each spot's attractiveness
    normal_scores = np.random.normal(loc=attractiveness, scale=std_dev, size=(num_players, len(spots_df)))
    
    # Take the mean of scores for each spot across all players
    mean_scores = normal_scores.mean(axis=0)
    
    # Convert scores to probabilities by taking their absolute values and normalizing
    scores_positive = np.abs(mean_scores)  # Ensure all scores are positive
    probabilities = scores_positive / scores_positive.sum()
    
    # Simulating player choices
    choices = np.random.choice(spots_df.index, size=num_players, p=probabilities)
    
    # Counting how many times each spot was chosen
    choice_counts = pd.Series(choices).value_counts().reindex(spots_df.index, fill_value=0)
    
    # Calculating the percentage of expeditions that took place at each spot
    expedition_percentages = (choice_counts / num_players) * 100
    
    return expedition_percentages

# Using the new simulation method with normal distribution
expedition_percentages_normal = simulate_selections_normal_distribution(spots_df, num_players)
print(expedition_percentages_normal)

#######################################################################################################

# Calculate profits using these new expedition percentages
profits_normal = calculate_profits(spots_df, expedition_percentages_normal, 3)

# Find the best choices for each case using the new method
best_one_expedition_normal = profits_normal['Expedition 1'].astype(float).idxmax()
best_two_expeditions_normal = profits_normal['Expedition 1'].add(profits_normal['Expedition 2'], fill_value=0).astype(float).idxmax()
best_three_expeditions_normal = profits_normal['Expedition 1'].add(profits_normal['Expedition 2'], fill_value=0).add(profits_normal['Expedition 3'], fill_value=0).astype(float).idxmax()

# print(best_one_expedition_normal, best_two_expeditions_normal, best_three_expeditions_normal, profits_normal)
print(profits_normal)

#######################################################################################################
profits_normal['Total Profit'] = profits_normal[['Expedition 1', 'Expedition 2', 'Expedition 3']].sum(axis=1)

# Sorting by profit from Expedition 1
sorted_by_expedition1 = profits_normal.sort_values(by='Expedition 1', ascending=False)

# Sorting by profit from Expedition 2
sorted_by_expedition2 = profits_normal.sort_values(by='Expedition 2', ascending=False)

# Sorting by profit from Expedition 3
sorted_by_expedition3 = profits_normal.sort_values(by='Expedition 3', ascending=False)

# Sorting by total profit
sorted_by_total_profit = profits_normal.sort_values(by='Total Profit', ascending=False)

# Output sorted DataFrames
print("Sorted by Expedition 1 Profit:\n", sorted_by_expedition1)
print("Sorted by Expedition 2 Profit:\n", sorted_by_expedition2)
print("Sorted by Expedition 3 Profit:\n", sorted_by_expedition3)
print("Sorted by Total Profit:\n", sorted_by_total_profit)