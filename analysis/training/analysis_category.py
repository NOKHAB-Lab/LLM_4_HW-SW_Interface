import json
from collections import Counter

# Expanded keyword sets
sensor_keywords = {
    "sensor", "temperature", "humidity", "ultrasonic", "pressure", "gas", "light",
    "camera", "mic", "microphone", "motion", "ir", "ldr", "adc", "thermistor",
    "photoresistor", "gyroscope", "accelerometer", "hall", "magnetometer",
    "tilt", "sound", "vibration", "proximity", "touch", "color", "uv", "als"
}

actuator_keywords = {
    "actuator", "motor", "servo", "relay", "led", "buzzer", "speaker", "fan",
    "heater", "pump", "solenoid", "valve", "stepper", "driver", "display",
    "lcd", "oled", "vibration_motor"
}

def tokenize_text(text: str):
    """Break input text into lowercase word tokens, stripping punctuation."""
    return set(word.strip(".,()[]{}<>/-_").lower() for word in text.split())

def classify_example(tags, input_field):
    all_tokens = set()

    # Normalize and tokenize tags
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]
    tag_tokens = set(t.lower() for t in tags)

    # Tokenize the input field
    if input_field:
        input_tokens = tokenize_text(input_field)
        all_tokens.update(input_tokens)

    all_tokens.update(tag_tokens)

    found_sensor = any(token in sensor_keywords for token in all_tokens)
    found_actuator = any(token in actuator_keywords for token in all_tokens)

    if found_sensor and found_actuator:
        return "sensor_actuator_combo"
    elif found_sensor:
        return "sensor_only"
    elif found_actuator:
        return "actuator_only"
    else:
        return "uncategorized"

def process_json_file(input_path, output_path="category_analysis.json"):
    with open(input_path, 'r') as f:
        data = json.load(f)

    tag_counts = Counter()
    category_counts = Counter()

    for obj in data:
        tags = obj.get("tags", [])
        input_text = obj.get("input", "")

        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        obj["tags"] = tags  # Normalize

        category = classify_example(tags, input_text)
        obj["category_type"] = category
        category_counts[category] += 1
        tag_counts.update(tags)

    # Write final annotated data
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Annotated data saved to: {output_path}")
    print("\n📊 Tag Frequency Summary:")
    for tag, count in tag_counts.most_common():
        print(f"  - {tag}: {count}")

    print("\n📊 Category Type Distribution:")
    for category, count in category_counts.items():
        print(f"  - {category}: {count}")

    print(f"\n📦 Total examples processed: {len(data)}")
    if sum(category_counts.values()) != len(data):
        print("⚠️ Mismatch in total classification count.")
    else:
        print("🎉 All examples successfully categorized.")

# Entry point
if __name__ == "__main__":
    input_file = input("Enter path to JSON file containing examples: ").strip()
    process_json_file(input_file, output_path="category_analysis.json")
