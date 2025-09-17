import copy
from feed import AthleteState, HydrationFuelEngine, WorkoutData, create_very_nice_plot

state = AthleteState(weight_kg=70, pre_fluid_ml=1000, pre_carbs_g=60)
engine = HydrationFuelEngine(state)

# Simulated workout data
workout_data_samples = [
    WorkoutData(heart_rate=132, speed=13.0, temperature=20.0),
WorkoutData(heart_rate=136, speed=13.3, temperature=20.5),
WorkoutData(heart_rate=140, speed=13.6, temperature=21.0),
WorkoutData(heart_rate=144, speed=13.9, temperature=21.5),
WorkoutData(heart_rate=148, speed=14.2, temperature=22.0),
WorkoutData(heart_rate=152, speed=14.5, temperature=22.5),
WorkoutData(heart_rate=154, speed=14.7, temperature=23.0),
WorkoutData(heart_rate=156, speed=14.9, temperature=23.5),
WorkoutData(heart_rate=158, speed=15.1, temperature=24.0),
WorkoutData(heart_rate=160, speed=15.3, temperature=24.5),
WorkoutData(heart_rate=162, speed=15.5, temperature=25.0),
WorkoutData(heart_rate=164, speed=15.7, temperature=25.5),
WorkoutData(heart_rate=166, speed=15.9, temperature=26.0),
WorkoutData(heart_rate=168, speed=16.1, temperature=26.5),
WorkoutData(heart_rate=170, speed=16.3, temperature=27.0),
WorkoutData(heart_rate=172, speed=16.5, temperature=27.5),
WorkoutData(heart_rate=174, speed=16.7, temperature=28.0),
WorkoutData(heart_rate=176, speed=16.9, temperature=28.5),
WorkoutData(heart_rate=178, speed=17.1, temperature=29.0),
WorkoutData(heart_rate=180, speed=17.3, temperature=29.5),
WorkoutData(heart_rate=180, speed=18.0, temperature=30.0),
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
