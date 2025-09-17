import matplotlib.pyplot as plt
import time
import copy

class AthleteState:
    def __init__(self, weight_kg, pre_fluid_ml, pre_carbs_g):
        self.weight_kg = weight_kg

        # Dynamic internal estimates
        self.fluid_level_ml = pre_fluid_ml
        self.carb_level_g = pre_carbs_g

        # Totals (for charts, debugging, recommendations)
        self.total_fluid_loss = 0
        self.total_carb_use = 0

        # Advice on how much the athlete should drink or eat
        self.current_advice = {
            "drink_ml": 0,
            "eat_g": 0
        }

        # History for when the user drank or ate
        self.stomach_ml = 0
        self.absorbed_history = []
        self.hourly_absorbed_ml = 0

        self.stomach_carbs_g = 0
        self.carb_absorbed_history = []
        self.hourly_absorbed_carbs_g = 0
        self.carb_cooldown_remaining = 0

        # Cooldowns for eating/drinking
        self.hydration_cooldown_remaining = 0


class WorkoutData:
    """
    A single point/tick of sensor inputs.
    """
    def __init__(self, heart_rate, speed, temperature, drink_ml=None, eat_g=None):
        self.heart_rate = heart_rate
        self.speed = speed
        self.temperature = temperature
        self.drink_ml = drink_ml
        self.eat_g = eat_g


class HydrationFuelEngine:
    def __init__(self, athlete_state):
        self.state = athlete_state

        # Assume 1 tick = 1 minute.
        self.current_tick = 0

    # Sweat loss model (ml/min)
    def estimate_sweat_loss(self, hr, temp):
        base_sweat = 6  # ml/min baseline

        hr_factor = max(0, hr - 120) * 0.5
        temp_factor = max(0, temp - 15) * 1.2
        weight_factor = (self.state.weight_kg - 70) * 0.2

        return base_sweat + hr_factor + temp_factor + weight_factor

    # Carb burn model (g/min)
    def estimate_carb_burn(self, hr, speed):
        carb_from_hr = max(0, hr - 120) * 0.03
        speed_factor = (speed / 10)
        weight_factor = self.state.weight_kg / 70.0

        return carb_from_hr * speed_factor * weight_factor

    def calculate_hydration_advice(self, sweat_loss, hr, speed, temp):
        if self.state.hourly_absorbed_ml >= 1500 or self.state.stomach_ml > 0:
            return 0

        if self.state.hydration_cooldown_remaining > 0:
            return 0

        current = self.state.fluid_level_ml
        total   = self.state.total_fluid_loss
        weight  = self.state.weight_kg

        optimal_level = 700
        ok_level      = 400
        low_level     = 200

        if current >= optimal_level:
            tank_zone = 0.0
        elif current <= low_level:
            tank_zone = 1.0
        else:
            tank_zone = (optimal_level - current) / (optimal_level - low_level)

        max_safe_loss = weight * 20
        loss_zone = min(1.0, total / max_safe_loss)

        base = sweat_loss
        extra = 150 * tank_zone + 300 * loss_zone
        recommendation = base + extra

        hourly_baseline = 0.02 * weight * 1000 # 2% hydration
        per_min_baseline = hourly_baseline / 60
        recommendation = max(recommendation, per_min_baseline)

        if temp > 20:
            temp_steps = (temp - 20) // 5
            recommendation *= 1 + (0.10 * temp_steps)

        if hr > 160 or speed > 15:
            recommendation *= 1.15

        est_max_hr = 200
        if temp > 30 and hr > 0.85 * est_max_hr:
            recommendation *= 1.15

        recommendation = min(750, recommendation)
        remaining_hourly_capacity = 1500 - self.state.hourly_absorbed_ml
        recommendation = min(recommendation, remaining_hourly_capacity)

        return max(0, recommendation)

    def calculate_carb_advice(self, carb_loss, temperature, hr):
        # Do not advise carbs if cooling down AND last snack has not yet been absorped
        if self.state.carb_cooldown_remaining > 0 and self.state.stomach_carbs_g > 0:
            return 0

        # Hourly absorption cap
        if self.state.hourly_absorbed_carbs_g >= 120:
            return 0

        current = self.state.carb_level_g
        total   = self.state.total_carb_use
        weight  = self.state.weight_kg

        optimal = 60
        ok      = 30
        low     = 15

        # tank emptiness: 0 full → 1 empty
        if current >= optimal:
            tank_zone = 0.0
        elif current <= low:
            tank_zone = 1.0
        else:
            tank_zone = (optimal - current) / (optimal - low)

        # duration / total burn factor
        max_hourly = weight * 2
        burn_zone = min(1.0, total / max_hourly)

        extra = 20 * tank_zone + 40 * burn_zone

        recommendation = carb_loss + extra

        est_max_hr = 200
        if temperature > 30 and hr > 0.85 * est_max_hr:
            recommendation *= 1.15

        return min(60, max(0, recommendation))

    def update_absorption(self):
        absorption_rate = 40  # ml/min

        absorbed = min(absorption_rate, self.state.stomach_ml)
        self.state.stomach_ml -= absorbed

        # Add to internal fluid level
        self.state.fluid_level_ml = min(1500, self.state.fluid_level_ml + absorbed)

        # Track hourly absorption window
        self.state.absorbed_history.append((self.current_tick, absorbed))

        cutoff = self.current_tick - 60
        self.state.absorbed_history = [
            (t, ml) for (t, ml) in self.state.absorbed_history if t > cutoff
        ]

        self.state.hourly_absorbed_ml = sum(ml for (_, ml) in self.state.absorbed_history)

        carb_absorption_rate = 1.5  # g/min typical for gels/chews

        absorbed_carbs = min(carb_absorption_rate, self.state.stomach_carbs_g)
        self.state.stomach_carbs_g -= absorbed_carbs

        # Add to internal carb level
        self.state.carb_level_g = min(200, self.state.carb_level_g + absorbed_carbs)

        # Track 60-minute absorption window (carbs)
        self.state.carb_absorbed_history.append((self.current_tick, absorbed_carbs))

        self.state.carb_absorbed_history = [
            (t, g) for (t, g) in self.state.carb_absorbed_history if t > cutoff
        ]

        self.state.hourly_absorbed_carbs_g = sum(g for (_, g) in self.state.carb_absorbed_history)

    # One tick update
    def update(self, workout_data):

        # 1. Compute losses
        sweat_loss = self.estimate_sweat_loss(
            workout_data.heart_rate,
            workout_data.temperature
        )
        carb_loss = self.estimate_carb_burn(
            workout_data.heart_rate,
            workout_data.speed
        )

        # 2. Update internal state
        self.state.fluid_level_ml = max(0, self.state.fluid_level_ml - sweat_loss)
        self.state.carb_level_g = max(0, self.state.carb_level_g - carb_loss)

        # 3. Calculate advice
        self.state.current_advice = {
            "drink_ml": self.calculate_hydration_advice(sweat_loss, workout_data.heart_rate, workout_data.speed, workout_data.temperature),
            "eat_g": self.calculate_carb_advice(carb_loss, workout_data.temperature, workout_data.heart_rate)
        }

        # 4. Update if the user ate or drank
        if workout_data.drink_ml:
            intake = workout_data.drink_ml
            self.state.stomach_ml += intake

            # Add scaled cooldown
            absorption_rate = 40  # ml/min
            self.state.hydration_cooldown_remaining += intake / absorption_rate
        if workout_data.eat_g:
            intake = workout_data.eat_g
            self.state.stomach_carbs_g += intake

            # Cooldown based on intake
            absorption_rate = 1.5
            self.state.carb_cooldown_remaining += intake / absorption_rate

        # Update cumulative loss over entire workout
        self.state.total_fluid_loss += sweat_loss
        self.state.total_carb_use += carb_loss

        # Advance simulation time and update cooldowns/absorption
        self.current_tick += 1
        self.state.hydration_cooldown_remaining = max(
            0,
            self.state.hydration_cooldown_remaining - 1
        )
        self.state.carb_cooldown_remaining = max(
            0,
            self.state.carb_cooldown_remaining - 1
        )
        self.update_absorption()


def create_very_nice_plot(
        engine_history,
        sweat_losses,
        carb_losses,
        hydration_advice,
        carb_advice,
        workout_data_samples
    ):

    minutes = list(range(1, len(engine_history) + 1))
    heart_rates = [d.heart_rate for d in workout_data_samples]
    speeds = [d.speed for d in workout_data_samples]
    temperatures = [d.temperature for d in workout_data_samples]
    fluid_levels = [engine.state.fluid_level_ml for engine in engine_history]
    carb_levels = [engine.state.carb_level_g for engine in engine_history]

    plt.rcParams.update({'font.size': 20})

    # 7 original + 2 new plots = 9
    fig, axs = plt.subplots(5, 2, figsize=(20, 32))
    axs = axs.flatten()

    line_kwargs = {'linewidth': 4, 'marker': 'o', 'markersize': 10}

    # 9 plots
    axs[0].plot(minutes, heart_rates, color='red', **line_kwargs)
    axs[0].set_title("Heart Rate")
    axs[0].set_ylabel("Heart Rate (bpm)")
    axs[0].grid(True)

    axs[1].plot(minutes, speeds, color='blue', **line_kwargs)
    axs[1].set_title("Speed")
    axs[1].set_ylabel("Speed (km/h)")
    axs[1].grid(True)

    axs[2].plot(minutes, temperatures, color='orange', **line_kwargs)
    axs[2].set_title("Ambient Temperature")
    axs[2].set_ylabel("Temperature (°C)")
    axs[2].grid(True)

    axs[4].plot(minutes, fluid_levels, color='cyan', **line_kwargs)
    axs[4].set_title("Estimated Fluid Level")
    axs[4].set_ylabel("Fluid (ml)")
    axs[4].grid(True)

    axs[5].plot(minutes, carb_levels, color='green', **line_kwargs)
    axs[5].set_title("Estimated Carbohydrate Level")
    axs[5].set_ylabel("Carbs (g)")
    axs[5].grid(True)

    axs[8].plot(minutes, sweat_losses, color='purple', **line_kwargs)
    axs[8].set_title("Sweat Loss per Minute")
    axs[8].set_ylabel("Sweat (ml)")
    axs[8].grid(True)

    axs[9].plot(minutes, carb_losses, color='brown', **line_kwargs)
    axs[9].set_title("Carb Burn per Minute")
    axs[9].set_ylabel("Carbs (g)")
    axs[9].grid(True)

    axs[6].plot(minutes, hydration_advice, color='dodgerblue', **line_kwargs)
    axs[6].set_title("Hydration Recommendation")
    axs[6].set_ylabel("Drink (ml)")
    axs[6].grid(True)

    axs[7].plot(minutes, carb_advice, color='limegreen', **line_kwargs)
    axs[7].set_title("Carb Recommendation")
    axs[7].set_ylabel("Eat (g)")
    axs[7].grid(True)

    # turn off the empty final subplot
    axs[3].axis('off')

    # Label x-axis on all plots
    for ax in axs[:9]:
        ax.set_xlabel("Time (minutes)")

    plt.tight_layout(rect=[0, 0, 1, 0.98], h_pad=4)
    plt.show()


if __name__ == "__main__":
    state = AthleteState(weight_kg=70, pre_fluid_ml=1000, pre_carbs_g=60)
    engine = HydrationFuelEngine(state)

    # Simulate workout data found in test_data.txt
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
    response_times = []

    # Simulate workout
    for i, data in enumerate(workout_data_samples):
        engine.update(data)

        sweat_losses.append(engine.estimate_sweat_loss(data.heart_rate, data.temperature))
        carb_losses.append(engine.estimate_carb_burn(data.heart_rate, data.speed))
        hydration_advice_list.append(engine.state.current_advice.get('drink_ml', 0))
        carb_advice_list.append(engine.state.current_advice.get('eat_g', 0))

        start_time = time.time()
        end_time = time.time()
        elapsed = end_time - start_time
        response_times.append(elapsed)
        engine_history.append(copy.deepcopy(engine))

    create_very_nice_plot(engine_history, sweat_losses, carb_losses, hydration_advice_list, carb_advice_list, workout_data_samples)
    response_times_ms = [t * 1000 for t in response_times]

    print("Advice delivery times (ms):", ["{:.2f}".format(t) for t in response_times_ms])
    print("Max response time: {:.2f} ms".format(max(response_times_ms)))
    print("Average response time: {:.2f} ms".format(sum(response_times_ms)/len(response_times_ms)))


