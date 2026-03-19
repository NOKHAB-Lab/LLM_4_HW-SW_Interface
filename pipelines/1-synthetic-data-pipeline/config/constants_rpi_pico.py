# config/constants.py
# 🌀 Code Style Variations
CODE_STYLES = [
    "functional"
]

# 📊 Complexity Tiers
COMPLEXITY_LEVELS = ["beginner", "intermediate", "advanced"]

# 🍓 Raspberry Pi Model Targets
PI_MODELS = [
    "Raspberry Pi Pico"
]

# 🔗 Integration Types
INTEGRATION_PATTERNS = [
    "standalone", 
    "with multiple sensors",
    "in distributed system"
]

# 🌎 Real-World Application Contexts
USE_CONTEXTS = [
    "educational setting", "hobbyist project", "professional monitoring system",
    "research application", "industrial automation", "smart agriculture",
    "robotics project", "wearable technology", "interactive art installation",
    "assistive technology", "environmental science", "home automation"
]

# ✅ Phase Progression Order (Pipeline Flow)
PROGRESSION_ORDER = [
    "sensor_reading",
    "actuators",
    "sensor_actuator_combo",
    "file_logging",
    "interrupt_driven"
]

# 📦 Phase Categories and Subcategories
CATEGORIES = {
    # 🌱 Phase 1: Basic Sensor Input (Expanded)
    "sensor_reading": [
        "temperature sensor", "humidity sensor", "pressure sensor", "light sensor",
        "ultrasonic sensor", "PIR sensor", "soil moisture sensor", "IR sensor",
        "sound sensor", "vibration sensor", "gas sensor", "touch sensor",
        "hall effect sensor", "rain sensor", "tilt sensor",
        "flame sensor", "color sensor", "capacitive touch sensor",
        "load cell sensor", "motion sensor", "alcohol sensor",
        "gyroscope sensor", "accelerometer", "magnetometer"
        ],


    # ⚙️ Actuator Options (standalone)
    "actuators": [
        "servo motor", "DC motor", "stepper motor", "relay", "solenoid",
        "LED", "buzzer", "speaker", "vibration motor", "fan",
        "LCD display", "OLED screen", "RGB LED",
        "relay-controlled lamp", "heater", "cooling fan",
        "valve actuator", "electromagnetic lock"
        ],

    # ⚡ Phase 2: Sensor-Actuator Integration (Expanded)
    "sensor_actuator_combo": [
        "temperature sensor controlling a cooling fan",
        "humidity sensor triggering a dehumidifier",
        "PIR motion sensor activating a light or buzzer",
        "ultrasonic sensor controlling servo for parking assist",
        "soil moisture sensor turning on a water pump",
        "gas sensor activating a ventilation fan",
        "IR sensor triggering a relay to open a door",
        "sound sensor activating an alarm",
        "light sensor adjusting brightness of an LED strip",
        "load cell sensor triggering a locking mechanism",
        "time of flight sensor controlling a gate",
        "rain sensor closing a motorized window",
        "flame sensor activating buzzer and LED",
        "capacitive touch sensor toggling a relay"
    ],

    # 💾 Phase 3: File and Data Logging (Expanded)
    "file_logging": [
        "log temperature readings to a CSV file",
        "log motion detection timestamps to a text file",
        "log gas sensor values with timestamps",
        "write ultrasonic distance readings to a file every second",
        "create daily sensor log files for multiple sensors",
        "log light and sound levels with date/time",
        "store sensor threshold breaches to a log file",
        "save sensor calibration values to file",
        "record ADC readings from multiple channels into CSV"
        ],

    # 🚨 Phase 4: Interrupts and Real-Time Logic (Expanded)
    "interrupt_driven": [
        "motion sensor using GPIO interrupt to turn on light",
        "button interrupt to start or stop data logging",
        "vibration sensor triggering a shutdown routine",
        "PIR sensor GPIO interrupt activating buzzer",
        "external interrupt from a tilt switch",
        "IR receiver decoding input via interrupt",
        "hardware timer interrupt for consistent sampling",
        "Hall effect sensor rotation counting with interrupt",
        "ultrasonic trigger using echo pin interrupt"
    ]
}

# Create weighted distribution to favor interesting categories
PHASE_WEIGHTS = {
    "sensor_reading": 0.3,
    "actuators": 0.3,
    "sensor_actuator_combo": 0.2,
    "file_logging": 0.1,
    "interrupt_driven": 0.1
}