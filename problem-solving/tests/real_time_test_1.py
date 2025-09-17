import time
from feed import AthleteState, HydrationFuelEngine, WorkoutData

state = AthleteState(weight_kg=70, pre_fluid_ml=1000, pre_carbs_g=60)
engine = HydrationFuelEngine(state)

# Simulated workout data
workout_data_samples = []

hr = 132
speed = 13.0
temp = 20.0

for i in range(120):
    # Add data point
    workout_data_samples.append(
        WorkoutData(
            heart_rate=hr,
            speed=speed,
            temperature=temp,
            drink_ml=300,
            eat_g=15
        )
    )

    # Increase values gradually in cycles
    hr += 2
    speed += 0.1
    temp += 0.05

    # Loop heart rate back to a realistic range
    if hr > 185:
        hr = 140

    # Loop speed realistically
    if speed > 18:
        speed = 13.5

    # Loop temperature realistically
    if temp > 30:
        temp = 21

# Track response times for generating hydration and carbohydrate advice
response_times = []

for data_point in workout_data_samples:

    start_time = time.time()

    # Process a single workout data point (update state, calculate losses, advice, absorption)
    engine.update(data_point)

    end_time = time.time()
    elapsed = end_time - start_time
    response_times.append(elapsed)

# Convert seconds to milliseconds for readability
response_times_ms = [t * 1000 for t in response_times]

# Print metrics
print("Advice delivery times (ms):", ["{:.2f}".format(t) for t in response_times_ms])
print("Max response time: {:.2f} ms".format(max(response_times_ms)))
print("Average response time: {:.2f} ms".format(sum(response_times_ms)/len(response_times_ms)))
