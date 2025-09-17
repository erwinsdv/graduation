import copy
from feed import AthleteState, HydrationFuelEngine, WorkoutData, create_very_nice_plot

state = AthleteState(weight_kg=70, pre_fluid_ml=1000, pre_carbs_g=60)
engine = HydrationFuelEngine(state)

# Simulated workout data
workout_data_samples = [
WorkoutData(heart_rate=132, speed=10.0, temperature=20.0),
WorkoutData(heart_rate=133, speed=10.1, temperature=20.1),
WorkoutData(heart_rate=134, speed=10.3, temperature=20.2),
WorkoutData(heart_rate=135, speed=10.4, temperature=20.3),
WorkoutData(heart_rate=136, speed=10.6, temperature=20.4),
WorkoutData(heart_rate=137, speed=10.7, temperature=20.5),
WorkoutData(heart_rate=138, speed=10.8, temperature=20.6),
WorkoutData(heart_rate=139, speed=10.9, temperature=20.7),
WorkoutData(heart_rate=140, speed=11.0, temperature=20.8),
WorkoutData(heart_rate=141, speed=11.1, temperature=20.9),
WorkoutData(heart_rate=142, speed=11.2, temperature=21.0),
WorkoutData(heart_rate=143, speed=11.3, temperature=21.1),
WorkoutData(heart_rate=144, speed=11.4, temperature=21.2, drink_ml=300, eat_g=15),
WorkoutData(heart_rate=145, speed=11.5, temperature=21.3),
WorkoutData(heart_rate=145, speed=11.6, temperature=21.4),
WorkoutData(heart_rate=145, speed=11.7, temperature=21.5),
WorkoutData(heart_rate=145, speed=11.8, temperature=21.6),
WorkoutData(heart_rate=145, speed=11.9, temperature=21.7),
WorkoutData(heart_rate=145, speed=12.0, temperature=21.8),
WorkoutData(heart_rate=145, speed=12.0, temperature=21.9),
WorkoutData(heart_rate=145, speed=12.0, temperature=22.0),
WorkoutData(heart_rate=145, speed=12.0, temperature=22.0),
WorkoutData(heart_rate=145, speed=12.0, temperature=22.0),
WorkoutData(heart_rate=145, speed=12.0, temperature=22.0),
WorkoutData(heart_rate=145, speed=12.0, temperature=22.0),
]

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
