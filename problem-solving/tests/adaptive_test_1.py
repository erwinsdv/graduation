import copy
from feed import AthleteState, HydrationFuelEngine, WorkoutData, create_very_nice_plot

# Athlete state (switch manually)
state = AthleteState(weight_kg=70, pre_fluid_ml=1000, pre_carbs_g=60) # Average athlete, properly hydrated/fueled
# state = AthleteState(weight_kg=70, pre_fluid_ml=100, pre_carbs_g=5) # Average athlete, badly hydrated/fueled
# state = AthleteState(weight_kg=195, pre_fluid_ml=1000, pre_carbs_g=60) # Eddie Hall, "properly" hydrated/fueled

engine = HydrationFuelEngine(state)

# Generate workout data for all phases (switch manually)
workout_data_samples = []

# =================================================
# BASELINE WORKOUT (20 min)
# =================================================

for i in range(20):
    workout_data_samples.append(
        WorkoutData(
            heart_rate=135,
            speed=12.0,
            temperature=20.0
        )
    )


# =================================================
# HEAT ADAPTATION WORKOUT (20 min)
# =================================================

# temp = 20.0
# for i in range(20):
#     temp += 0.5
#     workout_data_samples.append(
#         WorkoutData(
#             heart_rate=135,
#             speed=12.0,
#             temperature=temp
#         )
#     )


# =================================================
# HEART RATE ADAPTATION WORKOUT (20 min)
# =================================================

# hr = 135
# for i in range(20):
#     hr += 2
#     workout_data_samples.append(
#         WorkoutData(
#             heart_rate=hr,
#             speed=12.0,
#             temperature=20.0
#         )
#     )


# =================================================
# SPEED ADAPTATION WORKOUT (20 min)
# =================================================

# speed = 12.0
# for i in range(20):
#     speed += 0.3
#     workout_data_samples.append(
#         WorkoutData(
#             heart_rate=135,
#             speed=speed,
#             temperature=20.0
#         )
#     )


# =================================================
# INTAKE DURING WORKOUT (20 min)
# =================================================

# for i in range(20):
#     workout_data_samples.append(
#         WorkoutData(
#             heart_rate=135,
#             speed=12.0,
#             temperature=20.0,
#             drink_ml=300 if i == 10 else 0,
#             eat_g=15 if i == 10 else 0
#         )
#     )

# =================================================
# MUCH LOWER INTAKE DURING WORKOUT (20 min)
# =================================================

# for i in range(20):
#     workout_data_samples.append(
#         WorkoutData(
#             heart_rate=135,
#             speed=12.0,
#             temperature=20.0,
#             drink_ml=100 if i == 10 else 0,
#             eat_g=5 if i == 10 else 0
#         )
#     )

engine_history = []
sweat_losses = []
carb_losses = []
hydration_advice_list = []
carb_advice_list = []

# Simulate workout
for data_point in workout_data_samples:
    # Process a single workout data point (update state, calculate losses, advice, absorption)
    engine.update(data_point)

    # Store the calculated values for the graph
    sweat_losses.append(engine.estimate_sweat_loss(data_point.heart_rate, data_point.temperature))
    carb_losses.append(engine.estimate_carb_burn(data_point.heart_rate, data_point.speed))
    hydration_advice_list.append(engine.state.current_advice.get('drink_ml', 0))
    carb_advice_list.append(engine.state.current_advice.get('eat_g', 0))
    engine_history.append(copy.deepcopy(engine))

create_very_nice_plot(engine_history, sweat_losses, carb_losses, hydration_advice_list, carb_advice_list, workout_data_samples)
