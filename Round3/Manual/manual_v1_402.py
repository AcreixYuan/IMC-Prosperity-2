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



result:
G26    3.7
G27    5.6
G28    4.3
G29    3.4
G30    4.6
H26    4.9
H27    3.6
H28    5.1
H29    4.1
H30    2.9
I26    5.3
I27    4.7
I28    4.0
I29    4.9
I30    3.3
J26    3.8
J27    4.1
J28    5.0
J29    4.2
J30    3.8
K26    2.0
K27    2.6
K28    3.7
K29    3.1
K30    3.3
Name: count, dtype: float64
      Expedition 1   Expedition 2  Expedition 3
G26   88365.243004   63365.243004  13365.243004
G27  129437.869822  104437.869822  54437.869822
G28  101051.593822   76051.593822  26051.593822
G29   77433.628319   52433.628319   2433.628319
G30  111220.958972   86220.958972  36220.958972
H26  115611.675959   90611.675959  40611.675959
H27  122120.730739   97120.730739  47120.730739
H28  129182.340131  104182.340131  54182.340131
H29  119024.003174   94024.003174  44024.003174
H30   86662.264774   61662.264774  11662.264774
I26  135085.122132  110085.122132  60085.122132
I27   132256.78621   107256.78621   57256.78621
I28    93283.58209    68283.58209   18283.58209
I29   95758.263583   70758.263583  20758.263583
I30   62715.199213   37715.199213 -12284.800787
J26  114628.820961   89628.820961  39628.820961
J27  123487.403293   98487.403293  48487.403293
J28  126237.623762  101237.623762  51237.623762
J29   117512.89171    92512.89171   42512.89171
J30  102154.531947   77154.531947  27154.531947
K26   44554.455446   19554.455446 -30445.544554
K27   66920.026438   41920.026438  -8079.973562
K28   96606.390884   71606.390884  21606.390884
K29   55391.432792   30391.432792 -19608.567208
K30   74183.976261   49183.976261   -816.023739
Sorted by Expedition 1 Profit:
       Expedition 1   Expedition 2  Expedition 3   Total Profit
I26  135085.122132  110085.122132  60085.122132  305255.366395
I27   132256.78621   107256.78621   57256.78621  296770.358629
G27  129437.869822  104437.869822  54437.869822  288313.609467
H28  129182.340131  104182.340131  54182.340131  287547.020392
J28  126237.623762  101237.623762  51237.623762  278712.871287
J27  123487.403293   98487.403293  48487.403293  270462.209879
H27  122120.730739   97120.730739  47120.730739  266362.192216
H29  119024.003174   94024.003174  44024.003174  257072.009522
J29   117512.89171    92512.89171   42512.89171  252538.675129
H26  115611.675959   90611.675959  40611.675959  246835.027878
J26  114628.820961   89628.820961  39628.820961  243886.462882
G30  111220.958972   86220.958972  36220.958972  233662.876915
J30  102154.531947   77154.531947  27154.531947   206463.59584
G28  101051.593822   76051.593822  26051.593822  203154.781466
K28   96606.390884   71606.390884  21606.390884  189819.172653
I29   95758.263583   70758.263583  20758.263583   187274.79075
I28    93283.58209    68283.58209   18283.58209  179850.746269
G26   88365.243004   63365.243004  13365.243004  165095.729013
H30   86662.264774   61662.264774  11662.264774  159986.794322
G29   77433.628319   52433.628319   2433.628319  132300.884956
K30   74183.976261   49183.976261   -816.023739  122551.928783
K27   66920.026438   41920.026438  -8079.973562  100760.079313
I30   62715.199213   37715.199213 -12284.800787   88145.597639
K29   55391.432792   30391.432792 -19608.567208   66174.298375
K26   44554.455446   19554.455446 -30445.544554   33663.366337
Sorted by Expedition 2 Profit:
       Expedition 1   Expedition 2  Expedition 3   Total Profit
I26  135085.122132  110085.122132  60085.122132  305255.366395
I27   132256.78621   107256.78621   57256.78621  296770.358629
G27  129437.869822  104437.869822  54437.869822  288313.609467
H28  129182.340131  104182.340131  54182.340131  287547.020392
J28  126237.623762  101237.623762  51237.623762  278712.871287
J27  123487.403293   98487.403293  48487.403293  270462.209879
H27  122120.730739   97120.730739  47120.730739  266362.192216
H29  119024.003174   94024.003174  44024.003174  257072.009522
J29   117512.89171    92512.89171   42512.89171  252538.675129
H26  115611.675959   90611.675959  40611.675959  246835.027878
J26  114628.820961   89628.820961  39628.820961  243886.462882
G30  111220.958972   86220.958972  36220.958972  233662.876915
J30  102154.531947   77154.531947  27154.531947   206463.59584
G28  101051.593822   76051.593822  26051.593822  203154.781466
K28   96606.390884   71606.390884  21606.390884  189819.172653
I29   95758.263583   70758.263583  20758.263583   187274.79075
I28    93283.58209    68283.58209   18283.58209  179850.746269
G26   88365.243004   63365.243004  13365.243004  165095.729013
H30   86662.264774   61662.264774  11662.264774  159986.794322
G29   77433.628319   52433.628319   2433.628319  132300.884956
K30   74183.976261   49183.976261   -816.023739  122551.928783
K27   66920.026438   41920.026438  -8079.973562  100760.079313
I30   62715.199213   37715.199213 -12284.800787   88145.597639
K29   55391.432792   30391.432792 -19608.567208   66174.298375
K26   44554.455446   19554.455446 -30445.544554   33663.366337
Sorted by Expedition 3 Profit:
       Expedition 1   Expedition 2  Expedition 3   Total Profit
I26  135085.122132  110085.122132  60085.122132  305255.366395
I27   132256.78621   107256.78621   57256.78621  296770.358629
G27  129437.869822  104437.869822  54437.869822  288313.609467
H28  129182.340131  104182.340131  54182.340131  287547.020392
J28  126237.623762  101237.623762  51237.623762  278712.871287
J27  123487.403293   98487.403293  48487.403293  270462.209879
H27  122120.730739   97120.730739  47120.730739  266362.192216
H29  119024.003174   94024.003174  44024.003174  257072.009522
J29   117512.89171    92512.89171   42512.89171  252538.675129
H26  115611.675959   90611.675959  40611.675959  246835.027878
J26  114628.820961   89628.820961  39628.820961  243886.462882
G30  111220.958972   86220.958972  36220.958972  233662.876915
J30  102154.531947   77154.531947  27154.531947   206463.59584
G28  101051.593822   76051.593822  26051.593822  203154.781466
K28   96606.390884   71606.390884  21606.390884  189819.172653
I29   95758.263583   70758.263583  20758.263583   187274.79075
I28    93283.58209    68283.58209   18283.58209  179850.746269
G26   88365.243004   63365.243004  13365.243004  165095.729013
H30   86662.264774   61662.264774  11662.264774  159986.794322
G29   77433.628319   52433.628319   2433.628319  132300.884956
K30   74183.976261   49183.976261   -816.023739  122551.928783
K27   66920.026438   41920.026438  -8079.973562  100760.079313
I30   62715.199213   37715.199213 -12284.800787   88145.597639
K29   55391.432792   30391.432792 -19608.567208   66174.298375
K26   44554.455446   19554.455446 -30445.544554   33663.366337
Sorted by Total Profit:
       Expedition 1   Expedition 2  Expedition 3   Total Profit
I26  135085.122132  110085.122132  60085.122132  305255.366395
I27   132256.78621   107256.78621   57256.78621  296770.358629
G27  129437.869822  104437.869822  54437.869822  288313.609467
H28  129182.340131  104182.340131  54182.340131  287547.020392
J28  126237.623762  101237.623762  51237.623762  278712.871287
J27  123487.403293   98487.403293  48487.403293  270462.209879
H27  122120.730739   97120.730739  47120.730739  266362.192216
H29  119024.003174   94024.003174  44024.003174  257072.009522
J29   117512.89171    92512.89171   42512.89171  252538.675129
H26  115611.675959   90611.675959  40611.675959  246835.027878
J26  114628.820961   89628.820961  39628.820961  243886.462882
G30  111220.958972   86220.958972  36220.958972  233662.876915
J30  102154.531947   77154.531947  27154.531947   206463.59584
G28  101051.593822   76051.593822  26051.593822  203154.781466
K28   96606.390884   71606.390884  21606.390884  189819.172653
I29   95758.263583   70758.263583  20758.263583   187274.79075
I28    93283.58209    68283.58209   18283.58209  179850.746269
G26   88365.243004   63365.243004  13365.243004  165095.729013
H30   86662.264774   61662.264774  11662.264774  159986.794322
G29   77433.628319   52433.628319   2433.628319  132300.884956
K30   74183.976261   49183.976261   -816.023739  122551.928783
K27   66920.026438   41920.026438  -8079.973562  100760.079313
I30   62715.199213   37715.199213 -12284.800787   88145.597639
K29   55391.432792   30391.432792 -19608.567208   66174.298375
K26   44554.455446   19554.455446 -30445.544554   33663.366337
