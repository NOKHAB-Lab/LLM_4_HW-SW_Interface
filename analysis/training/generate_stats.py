import json
import os
from collections import Counter, defaultdict

def get_tag_category(tag):
    """
    Categorizes a given tag based on predefined keywords.
    Returns the category name or 'Hardware/Context/Other' if no specific category matches.
    """
    tag_lower = tag.lower()

    # Define keywords for each category (order matters for prioritization)
    categories = {
        "Libraries/Frameworks": [
            'library', 'wiringpi', 'pigpio', 'bcm2835', 'gpiozero',
            'spidev', 'smbus', 'pthread', 'curl', 'openssl', 'lib', 'framework'
        ],
        "Communication": [
            'i2c', 'spi', 'uart', 'serial', 'ethernet', 'wifi', 'bluetooth',
            'mqtt', 'http', 'socket', 'network', 'radio', 'nrf24l01',
            'rs232', 'rs485', 'usb'
        ],
        "Sensors": [
            'sensor', 'dht', 'temperature', 'humidity', 'ir', 'light', 'ldr',
            'ultrasonic', 'button', 'switch', 'encoder', 'adc', 'joystick',
            'camera', 'microphone', 'gas sensor', 'motion sensor', 'accelerometer',
            'gyroscope', 'pressure', 'gps', 'rfid', 'nfc'
        ],
        "Actuators": [
            'actuator', 'led', 'motor', 'servo', 'relay', 'buzzer', 'display',
            '7-segment', 'lcd', 'oled', 'pwm', 'stepper', 'h-bridge', 'fan',
            'valve', 'pump', 'speaker'
        ]
    }

    # Prioritize categories based on typical specificity
    # Check for library/framework keywords first, then comms, then specific hardware types
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in tag_lower:
                return category

    # Default category if no specific match
    return "Hardware/Context/Other"


def analyze_json_tags(filepath):
    """
    Performs statistical analysis on 'tags' in a JSON file,
    counting occurrences, calculating percentages, and categorizing them.

    Args:
        filepath (str): The path to the JSON file.

    Returns:
        dict: A dictionary containing tag counts and percentages,
              categorized breakdown, or None if an error occurs.
    """
    
    # Ensure the file exists
    if not os.path.exists(filepath):
        print(f"Error: The file '{filepath}' was not found.")
        return None
    
    # Ensure the file is not empty
    if os.path.exists(filepath) and os.stat(filepath).st_size == 0:
        print(f"Error: The file '{filepath}' is empty.")
        return None

    all_tags = []
    total_objects = 0
    total_tags_instances = 0

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

            # Ensure data is a list, if not, wrap it in a list
            if not isinstance(data, list):
                data = [data]

            total_objects = len(data)

            for obj in data:
                if 'tags' in obj and isinstance(obj['tags'], list):
                    # Extend the all_tags list with tags from the current object
                    # Convert tags to lowercase for case-insensitive counting
                    cleaned_tags = [tag.strip().lower() for tag in obj['tags'] if isinstance(tag, str)]
                    all_tags.extend(cleaned_tags)
                    total_tags_instances += len(cleaned_tags)

    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filepath}'. Please ensure it's a valid JSON file.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during analysis: {e}")
        return None

    if not all_tags:
        print("No tags found or processed in the file for analysis.")
        return None

    # Count tag occurrences
    tag_counts = Counter(all_tags)

    # Calculate percentages for individual tags
    individual_tag_distribution = {}
    for tag, count in tag_counts.most_common(): # most_common() sorts by frequency
        percentage = (count / total_tags_instances) * 100
        individual_tag_distribution[tag] = {
            "count": count,
            "percentage": f"{percentage:.2f}%"
        }
    
    # Categorize tags and aggregate results
    categorized_distribution = defaultdict(lambda: {"count": 0, "tags": {}})
    for tag, details in individual_tag_distribution.items():
        category = get_tag_category(tag)
        categorized_distribution[category]["count"] += details['count']
        categorized_distribution[category]["tags"][tag] = details # Add individual tag details under its category

    # Convert defaultdict to regular dict for JSON output
    final_categorized_distribution = dict(categorized_distribution)

    # Calculate percentages for categories
    for category, details in final_categorized_distribution.items():
        cat_percentage = (details['count'] / total_tags_instances) * 100
        details['percentage'] = f"{cat_percentage:.2f}%"


    # Prepare the final results dictionary
    overall_stats = {
        "total_objects_processed": total_objects,
        "total_unique_tags": len(tag_counts),
        "total_tag_instances": total_tags_instances,
        "individual_tag_distribution": individual_tag_distribution, # Renamed for clarity
        "categorized_tag_distribution": final_categorized_distribution
    }

    return overall_stats

# --- Main execution ---
if __name__ == "__main__":
    file_path = input("Please enter the name of your JSON file for tag analysis: ")

    analysis_results = analyze_json_tags(file_path)

    if analysis_results:
        # Construct the output filename
        base_name, ext = os.path.splitext(file_path)
        output_filename = f"{base_name}_statistics.json"

        try:
            with open(output_filename, 'w') as outfile:
                json.dump(analysis_results, outfile, indent=2)
            print(f"\nStatistical analysis results with categorization saved to: '{output_filename}'")
        except Exception as e:
            print(f"Error saving analysis results to file: {e}")
    else:
        print("\nTag analysis could not be completed or produced no results.")