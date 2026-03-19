# Necassary library imports
import os
import time
import logging
from tqdm import tqdm
from datetime import datetime
import json

### Importing Modular File Functions ### 
# Import API Test Functions
from api.test import test_gemini_api_connection, test_gpt_api_connection
# Import Accuracy Calculator
from evaluator.accuracy_calculator_base import calculate_code_accuracy_base   
from evaluator.accuracy_calculator_finetuned import calculate_code_accuracy_tuned   
# Task Validation Functions
from task_manager.task_manager_Eval1_Tuned import validate_inferred_example_tuned
from task_manager.task_manager_Eval1_Base import validate_inferred_example_base
# Import Stats Generator
from reports.statistics_generator import compute_validation_statistics_base, compute_validation_statistics_tuned, write_accuracy_distribution_to_csv, write_base_inference_errors_to_txt, write_tuned_inference_errors_to_txt

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
    
# Inference Evaluation Criteria 1 - Base
Model_Name = 'CodeLlama'
logger.info(f"Executing Validation Pipeline for LLM Generated Code Against Validation Criteria 1")
################################################################################################
samples_updated = []
INPUT_JSON = f'CodeLlama_Test_Train_Responses_Evaluation_17thMay2025.json'  # Replace with the actual filename
OUTPUT_JSON = f'CodeLlama_Test_Train_Responses_Evaluation_17thMay2025_VALIDATED.json'  # Replace with the actual filename
data, samples, TOTAL_EXAMPLES = load_samples(INPUT_JSON)
logger.info(f"Starting validation of {TOTAL_EXAMPLES} Raspberry Pi code examples from the file {INPUT_JSON}")

# Current user info for metadata
current_user = os.environ.get("USER", "Unknown")
if not current_user:
    current_user = 'Ali Hassan'
current_datetime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

logger.info(f"Current Date and Time (UTC): {current_datetime}")
logger.info(f"Current User's Login: {current_user}")

# Check for existing output to resume
if os.path.exists(OUTPUT_JSON):
    try:
        with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
            samples_updated = json.load(f)
        start_index = len(samples_updated)
        logger.info(f"Resuming from checkpoint. Already processed {start_index} out of {TOTAL_EXAMPLES} examples.")
    except Exception as e:
        logger.error(f"Error reading checkpoint file {OUTPUT_JSON}: {e}")
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

        logger.info(f"Starting inference validation for example {i+1}/{TOTAL_EXAMPLES}.")
        sample_updated = sample ## Copy sample into anothe object

        ### Base Code Evaluation
        logger.info(f"Starting inference validation for base code of {i+1}/{TOTAL_EXAMPLES}.")
        # Start timing after logger.info
        sample_start_time_base = time.time()
        sample_updated = validate_inferred_example_base(sample_updated, False)
        overall_base, breakdown_base = calculate_code_accuracy_base(sample_updated)
        sample_updated["base_Accuracy_Score"] = overall_base
        sample_updated["base_Accuracy_Breakdown"] = breakdown_base
        # End timing after validate_inferred_example
        sample_end_time_base = time.time()
        sample_execution_time_base = sample_end_time_base - sample_start_time_base
        sample_updated["base_validaiton_criteria_execution_time"] = sample_execution_time_base

        logger.info(f"Ending inference validation for base code of {i+1}/{TOTAL_EXAMPLES}.")

        ### Finedtuned Code Evaluation
        logger.info(f"Starting inference validation for finetuned code of {i+1}/{TOTAL_EXAMPLES}.")
        # Start timing after logger.info
        sample_start_time_fine = time.time()
        sample_updated = validate_inferred_example_tuned(sample_updated, False)
        overall_finetuned, breakdown_finetuned = calculate_code_accuracy_tuned(sample_updated)
        sample_updated["finetuned_Accuracy_Score"] = overall_finetuned
        sample_updated["finetuned_Accuracy_Breakdown"] = breakdown_finetuned
        # End timing after validate_inferred_example
        sample_end_time_fine = time.time()
        sample_execution_time_fine = sample_end_time_fine - sample_start_time_fine
        sample_updated["finetuned_validaiton_criteria_execution_time"] = sample_execution_time_fine

        logger.info(f"Ending inference validation for finetuned code of {i+1}/{TOTAL_EXAMPLES}.")

        sample_updated["validaiton_criteria_execution_timestamp"] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        sample_updated["validation_criteria_execution_device"] = "Raspberry Pi 4 Model B"
        
        samples_updated.append(sample_updated)

        
        # Write samples_updated to OUTPUT_JSON_GPT after each example
        try:
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(samples_updated, f, indent=2)
            logger.debug(f"Saved {i+1} samples to {os.path.abspath(OUTPUT_JSON)}")
        except Exception as e:
            logger.error(f"Error writing to {OUTPUT_JSON} for example {i+1}: {e}")
        
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

    logger.info(f"Writing Base Model Inference Statistics.....")
    compute_validation_statistics_base(samples_updated, f"{Model_Name}_Validation_Statistics_Base.csv")
    time.sleep(5)

    logger.info(f"Writing Tuned Model Inference Statistics.....")
    compute_validation_statistics_tuned(samples_updated, f"{Model_Name}_Validation_Statistics_Tuned.csv")
    time.sleep(5)

    logger.info(f"Writing Combined Models Accuracy Statistics.....")
    write_accuracy_distribution_to_csv(samples_updated, f"{Model_Name}_Accuracy_Statistics_Combined.csv")
    time.sleep(5)

    logger.info(f"Writing Base Models Error Report.....")
    write_base_inference_errors_to_txt(samples_updated, f"{Model_Name}_Base_Build_SyntaxErrorReports.txt")

    logger.info(f"Writing Finetuned Models Error Report.....")
    write_tuned_inference_errors_to_txt(samples_updated, f"{Model_Name}_FineTuned_Build_SyntaxErrorReports.txt")
    pbar.close()

    # Final report
    end_time = time.time()
    total_time = end_time - start_time
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    seconds = int(total_time % 60)

    logger.info(f"Total execution time: {hours}h {minutes}m {seconds}s")
    logger.info(f"Examples saved in {os.path.abspath(OUTPUT_JSON)}")
else:
    logger.error("API connection test failed. Skipping validation.")

logger.info(f"All done for LLM Generated Code Against Validation Criteria 1!!!")
