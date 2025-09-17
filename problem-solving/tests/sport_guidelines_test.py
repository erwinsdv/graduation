import copy
from feed import AthleteState, HydrationFuelEngine, WorkoutData, create_very_nice_plot

state = AthleteState(weight_kg=70, pre_fluid_ml=1000, pre_carbs_g=60)
engine = HydrationFuelEngine(state)

# Simulated workout data
workout_data_samples = []

hrate = 165
speed = 15.5
temp = 28.0

for i in range(60):  # 60 minutes
    workout_data_samples.append(
        WorkoutData(
            heart_rate=hrate,
            speed=speed,
            temperature=temp,
            drink_ml=0,
            eat_g=0
        )
    )

    # Keep intensity and heat high
    hrate = min(hrate + 1, 180)
    speed = min(speed + 0.05, 17.0)
    temp = min(temp + 0.05, 32.0)

for i in range(90):  # 90 minutes
    workout_data_samples.append(
        WorkoutData(
            heart_rate=hrate,
            speed=speed,
            temperature=temp,
            drink_ml=750 if i == 0 or i == 30 else 0, # Drink 1500ml (half at minute 60, half at minute 90)
            eat_g=60 if i == 0 or i == 30 else 0 # Eat 120g (half at minute 60, half at minute 90)
        )
    )

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
