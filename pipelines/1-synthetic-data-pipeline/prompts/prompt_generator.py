# Necassary imports
import logging
from api.gemini_api import call_gemini_api

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_prompt_template(category, subcategory, pi_model):
    """
    Generate a base template to instruct the model to write a Raspberry Pi C code prompt.
    """
    return f"""
    You are a specialized prompt engineer for Raspberry Pi pico programming. Create a detailed, creative coding prompt for a C program that uses the {subcategory} {category} on a {pi_model}.

    The prompt should be specific, technical, and highly detailed. Include:
    1. The exact type of {subcategory} {category} hardware (e.g., brand name, sensor name, sensor type)
    2. Specific C libraries for Raspberry Pi or system calls to use (e.g., wiringPi, pigpio, bcm2835, sysfs)
    3. Clearly specify what communication protocol the sensors uses (GPIO simple, I2C, SPI, UART, 1-Wire) based on your knowlesge of the sensor
    4. Specify that the code should simply read data periodically (even time intervals) and log values to console.
    5. Error handling for failed reads or GPIO init or I2C or SPI Communication
    6. File format for saving results if applicable (only for an example with saving data)
    7. Specify if its an analog/digital sensor and needs to read data through an ADC or DAC.
    8. Specifically designed for {pi_model}

    🔹 Example Format to Follow:
    Write a C program for {pi_model} to read data from a DHT11 sensor connected to GPIO7 and write the readings to a CSV file named 'sensor_log.csv'.
    
    Further requirements:
    Make your prompt interesting, technically accurate, and include an innovative approach or twist that would make this code example stand out.
    Avoid buzzwords, over-explaining, or adding advanced goals. Just give a natural developer-style prompt.
    Try to keep this prompt direct, minimum with only relevant information and maximum two lines. The prompt shouldn't be more than 2 lines and you should be able to explain in 2 lines.
    
    Provide ONLY the prompt in plain text, formatted as a direct instruction to a C developer. Do not include any meta-commentary or notes about the prompt itself.
    """.strip()


def generate_ai_prompt(category, subcategory, complexity, style, pi_model, integration, context):
    """
    Two-stage AI prompt generation:
    1. Generate a base prompt for a C program on Raspberry Pi.
    2. Enrich it with specific design and variation parameters.
    """
    base_template = generate_prompt_template(category, subcategory, pi_model)
    base_prompt = call_gemini_api(base_template, temperature=0.8)

    if not base_prompt:
        logger.error("Failed to generate base prompt. Using fallback.")
        base_prompt = f"Write a C program for {pi_model} that uses {subcategory} ({category})."

    enrichment_instruction = f"""
    Enhance the following prompt with specific implementation details:

    Original prompt: "{base_prompt}"
    
    Add these requirements:
    1. Code should strictly be in C language and use libraries that support C programming.
    2. Donot use dummy libraries or non-standard libraries (such as sensor.h) etc.
    3. Donot refer to any C++ libraries in the code which cannot be used in a C program.
    4. Use modern and supported libraries like wiringPi, pigpio, bcm2835, or sysfs for accessing GPIO, I2C, SPI, and UART. Avoid old or deprecated libraries — they break on newer Raspberry Pi OS versions.
    5. Use only standard Raspberry Pi and Linux-compatible C libraries that can be installed via sudo apt-get or are commonly available on Raspberry Pi OS (Bookworm/Bullseye). Avoid proprietary or obscure libraries.
    6. Avoid deprecated libraries or functions. Ensure all APIs or commands used are compatible with modern Raspberry Pi OS (Bookworm/Bullseye).
    7. Target hardware should be {pi_model}.
    8. Program should be self sufficient and buildable using standard packages in raspberry pi and not some custom libraries.
  
    
    Format your final output like this example (structure only, not content):

    Write a C program for Raspberry Pi 'version' using the pigpio library to read a digital PIR motion sensor connected to GPIO17. When motion is detected, the program should log the timestamp to a file and blink an LED connected to GPIO27 for 1 second. The program should use procedural programming style, target Raspberry Pi 3 Model B+, and be suitable for a home security system in a smart home setup. It should include proper signal handling for graceful shutdown and validate sensor readings before acting.

    Make the prompt cohesive, technical, and detailed. Ensure it specifies exact libraries, functions, and implementation details.
    Format as a direct instruction to a developer. Return ONLY the final enhanced prompt.
    """.strip()

    enriched_prompt = call_gemini_api(enrichment_instruction, temperature=0.7)

    if not enriched_prompt:
        logger.warning("Prompt enrichment failed. Falling back to base prompt with added details.")
        enriched_prompt = (
            f"{base_prompt}\n\n"
            f"Additional requirements:\n"
            f"- Use {style} style\n"
            f"- Target: {pi_model}\n"
            f"- Integration: {integration}\n"
            f"- Context: {context}"
        )

    return base_prompt, enriched_prompt
