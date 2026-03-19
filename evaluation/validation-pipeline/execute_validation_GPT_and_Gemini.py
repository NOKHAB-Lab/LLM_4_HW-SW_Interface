# Necassary library imports
import os
import time
import logging
from tqdm import tqdm
from datetime import datetime
import json

# Importing Modular File Functions
from api.test import test_gemini_api_connection, test_gpt_api_connection
from evaluator.accuracy_calculator import calculate_code_accuracy   
from task_manager.task_manager_GPT_and_Gemini import validate_inferred_example
from evaluator.test_case_evaluator import evaluate_test_cases

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_samples(json_file_path):
    sample_count = 0
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

            if isinstance(data, list):
                samples = data
                sample_count = len(samples)
                logger.info(f"Number of samples: {sample_count}")
                return data, samples, sample_count
            else:
                logger.warning("JSON root is not a list of objects.")
                return [], [], sample_count
    except FileNotFoundError:
        logger.error(f"File not found: {json_file_path}")
        return [], [], sample_count
    except json.JSONDecodeError:
        logger.error("Error decoding JSON. Please check the file format.")
        return [], [], sample_count
    
# Inference GPT Base
logger.info(f"Executing Validation Pipeline for LLM Generated Variations Against Validation Criteria 2")
################################################################################################
samples_updated = []
INPUT_JSON_GPT = 'Gemini_Test_Train_Samples_Count_70by5_LargeSet_Responses.json'  # Replace with the actual filename
OUTPUT_JSON_GPT = 'Gemini_Test_Train_Samples_Count_70by5_LargeSet_Responses_VALIDATED.json'  # Replace with the actual filename
data, samples, TOTAL_EXAMPLES = load_samples(INPUT_JSON_GPT)
logger.info(f"Starting validation of {TOTAL_EXAMPLES} Raspberry Pi code examples from the file {INPUT_JSON_GPT}")

# Current user info for metadata
current_user = os.environ.get("USER", "Unknown")
if not current_user:
    current_user = 'Ali Hassan'
current_datetime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

logger.info(f"Current Date and Time (UTC): {current_datetime}")
logger.info(f"Current User's Login: {current_user}")

# Check for existing output to resume
if os.path.exists(OUTPUT_JSON_GPT):
    try:
        with open(OUTPUT_JSON_GPT, 'r', encoding='utf-8') as f:
            samples_updated = json.load(f)
        start_index = len(samples_updated)
        logger.info(f"Resuming from checkpoint. Already processed {start_index} out of {TOTAL_EXAMPLES} examples.")
    except Exception as e:
        logger.error(f"Error reading checkpoint file {OUTPUT_JSON_GPT}: {e}")
        logger.info("Starting from the beginning.")
        samples_updated = []
        start_index = 0
else:
    logger.info("No checkpoint found. Starting from the beginning.")
    samples_updated = []
    start_index = 0

# First test the API connection
if test_gemini_api_connection and test_gpt_api_connection():

# Initialize progress bar
    pbar = tqdm(total=TOTAL_EXAMPLES, desc="Validating inference examples")

    # Process tasks
    start_time = time.time()
    for i, sample in enumerate(samples[start_index:], start=start_index):
        logger.info(f"Validating inference for example {i+1}/{TOTAL_EXAMPLES}.")
        # Start timing after logger.info
        sample_start_time = time.time()

        sample_updated = validate_inferred_example(sample)
        overall, breakdown = calculate_code_accuracy(sample_updated)
        sample_updated["Accuracy_Score"] = overall
        sample_updated["Accuracy_Breakdown"] = breakdown
        test_cases_validation_details, all_test_cases_validation_status = evaluate_test_cases(sample_updated)
        sample_updated["all_test_cases_execution_details"] = test_cases_validation_details
        sample_updated["all_test_cases_execution_status"] = all_test_cases_validation_status
        # End timing after validate_inferred_example
        sample_end_time = time.time()
        sample_execution_time = sample_end_time - sample_start_time
        sample_updated["evaluation_criteria_execution_timestamp"] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        sample_updated["evaluation_criteria_execution_device"] = "Raspberry Pi 4 Model B"
        sample_updated["evaluation_criteria_execution_time"] = sample_execution_time
        samples_updated.append(sample_updated)
        
        # Write samples_updated to OUTPUT_JSON_GPT after each example
        try:
            with open(OUTPUT_JSON_GPT, 'w', encoding='utf-8') as f:
                json.dump(samples_updated, f, indent=2)
            logger.debug(f"Saved {i+1} samples to {os.path.abspath(OUTPUT_JSON_GPT)}")
        except Exception as e:
            logger.error(f"Error writing to {OUTPUT_JSON_GPT} for example {i+1}: {e}")
        
        # Update progress bar
        pbar.update(1)
        
        # Calculate and display ETA
        elapsed = time.time() - start_time
        avg_time_per_item = elapsed / (i + 1)
        remaining_items = TOTAL_EXAMPLES - (i + 1)
        eta_seconds = avg_time_per_item * remaining_items
        
        if i % 10 == 0 and i > 0:
            eta_hours = int(eta_seconds // 3600)
            eta_minutes = int((eta_seconds % 3600) // 60)
            logger.info(f"Progress: {i+1}/{TOTAL_EXAMPLES} examples. Estimated time remaining: {eta_hours}h {eta_minutes}m")
        
    pbar.close()

    # Final report
    end_time = time.time()
    total_time = end_time - start_time
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    seconds = int(total_time % 60)

    logger.info(f"Total execution time: {hours}h {minutes}m {seconds}s")
    logger.info(f"Examples saved in {os.path.abspath(OUTPUT_JSON_GPT)}")
else:
    logger.error("API connection test failed. Skipping validation.")

logger.info("All done for GPT Generated Code Validation Against Criteria Pass@k!")
