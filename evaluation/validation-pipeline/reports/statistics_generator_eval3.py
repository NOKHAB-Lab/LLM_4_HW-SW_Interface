import logging
import csv
import pandas as pd
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_final_pass_k_stats_table_base(data, output_csv="pass_k_stats_table_base.csv"):
    """
    Generates a CSV summary with task category, accuracy scores for subid 0-4,
    their average, and count of successful test case executions per category.

    Args:
        data (list of dict): Each dict must contain:
            - 'category', 'subid', 'finetuned_Accuracy_Score'
            - 'finetuned_all_test_cases_execution_status' (bool)
        output_csv (str): Path to save the output CSV.
    """
    grouped = defaultdict(lambda: {
        "accuracy_var_0": None,
        "accuracy_var_1": None,
        "accuracy_var_2": None,
        "accuracy_var_3": None,
        "accuracy_var_4": None,
        "successful_test_cases": 0,
        "counted": 0
    })

    for item in data:
        subid = item.get("subid")
        if subid not in {"0", "1", "2", "3", "4"}:
            continue

        key = item.get("category")
        subid = int(subid)
        score = item.get("base_Accuracy_Score")
        test_case_ok = item.get("base_all_test_cases_execution_status", False)

        if isinstance(score, (int, float)):
            grouped[key][f"accuracy_var_{subid}"] = score

        if test_case_ok:
            grouped[key]["successful_test_cases"] += 1

        grouped[key]["counted"] += 1

    # Prepare final CSV rows
    rows = []
    for category, vals in grouped.items():
        acc_list = [vals[f"accuracy_var_{i}"] for i in range(5) if isinstance(vals[f"accuracy_var_{i}"], (int, float))]
        avg_acc = round(sum(acc_list) / len(acc_list), 2) if acc_list else None

        row = {
            "task": category,
            "avg_accuracy": avg_acc,
            "successful_test_cases": vals["successful_test_cases"]
        }
        for i in range(5):
            row[f"accuracy_var_{i}"] = vals[f"accuracy_var_{i}"]

        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"✅ Summary CSV saved to: {output_csv}")

def generate_final_pass_k_stats_table_tuned(data, output_csv="pass_k_stats_table_finetuned.csv"):
    """
    Generates a CSV summary with task category, accuracy scores for subid 0-4,
    their average, and count of successful test case executions per category.

    Args:
        data (list of dict): Each dict must contain:
            - 'category', 'subid', 'finetuned_Accuracy_Score'
            - 'finetuned_all_test_cases_execution_status' (bool)
        output_csv (str): Path to save the output CSV.
    """
    grouped = defaultdict(lambda: {
        "accuracy_var_0": None,
        "accuracy_var_1": None,
        "accuracy_var_2": None,
        "accuracy_var_3": None,
        "accuracy_var_4": None,
        "successful_test_cases": 0,
        "counted": 0
    })

    for item in data:
        subid = item.get("subid")
        if subid not in {"0", "1", "2", "3", "4"}:
            continue

        key = item.get("category")
        subid = int(subid)
        score = item.get("finetuned_Accuracy_Score")
        test_case_ok = item.get("finetuned_all_test_cases_execution_status", False)

        if isinstance(score, (int, float)):
            grouped[key][f"accuracy_var_{subid}"] = score

        if test_case_ok:
            grouped[key]["successful_test_cases"] += 1

        grouped[key]["counted"] += 1

    # Prepare final CSV rows
    rows = []
    for category, vals in grouped.items():
        acc_list = [vals[f"accuracy_var_{i}"] for i in range(5) if isinstance(vals[f"accuracy_var_{i}"], (int, float))]
        avg_acc = round(sum(acc_list) / len(acc_list), 2) if acc_list else None

        row = {
            "task": category,
            "avg_accuracy": avg_acc,
            "successful_test_cases": vals["successful_test_cases"]
        }
        for i in range(5):
            row[f"accuracy_var_{i}"] = vals[f"accuracy_var_{i}"]

        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"✅ Summary CSV saved to: {output_csv}")

def generate_final_pass_k_stats_base(data, output_csv="final_pass_k_stats_table_base.csv"):
    """
    Generates a CSV summary with task category, pass@1, pass@3, and pass@5 scores.
    A final row provides cumulative averages for these scores.

    pass@1: 1 if the task with subid '0' had all test cases executed successfully, else 0.
    pass@3: 1 if any of the subids '0', '1', or '2' for the task had all test cases
            executed successfully, else 0.
    pass@5: 1 if any of the subids '0', '1', '2', '3', or '4' for the task had all
            test cases executed successfully, else 0.

    Args:
        data (list of dict): Each dict must contain:
            - 'category' (str): The identifier for the task.
            - 'subid' (str): The sub-identifier, expected to be '0'-'4'.
            - 'base_all_test_cases_execution_status' (bool): True if all test cases
            for this category and subid executed successfully, False otherwise.
        output_csv (str): Path to save the output CSV.
    """
    grouped = defaultdict(lambda: [False] * 5)

    for item in data:
        category = item.get("category")
        subid_str = item.get("subid")

        if category is None:
            print(f"Warning: Skipping item due to missing 'category': {item}")
            continue
        if subid_str not in {"0", "1", "2", "3", "4"}:
            continue

        subid_int = int(subid_str)
        test_case_passed = item.get("base_all_test_cases_execution_status", False)

        if test_case_passed:
            grouped[category][subid_int] = True

    rows = []
    total_pass_at_1 = 0
    total_pass_at_3 = 0
    total_pass_at_5 = 0

    if not grouped:
        print("Warning: No data to process after filtering. Output CSV will be empty or have only headers/average row.")
        num_tasks = 0
    else:
        num_tasks = len(grouped)

        for category, pass_statuses in grouped.items():
            pass_at_1 = 1 if pass_statuses[0] else 0
            pass_at_3 = 1 if any(pass_statuses[0:3]) else 0
            pass_at_5 = 1 if any(pass_statuses[0:5]) else 0

            rows.append({
                "task": category,
                "pass@1": pass_at_1,
                "pass@3": pass_at_3,
                "pass@5": pass_at_5
            })

            total_pass_at_1 += pass_at_1
            total_pass_at_3 += pass_at_3
            total_pass_at_5 += pass_at_5

    if num_tasks > 0:
        avg_pass_at_1 = round(total_pass_at_1 / num_tasks, 2)
        avg_pass_at_3 = round(total_pass_at_3 / num_tasks, 2)
        avg_pass_at_5 = round(total_pass_at_5 / num_tasks, 2)
        rows.append({
            "task": "Cumulative Average",
            "pass@1": avg_pass_at_1,
            "pass@3": avg_pass_at_3,
            "pass@5": avg_pass_at_5
        })
    else:
        rows.append({
            "task": "Cumulative Average",
            "pass@1": 0.0,
            "pass@3": 0.0,
            "pass@5": 0.0
        })

    column_order = ['task', 'pass@1', 'pass@3', 'pass@5']
    df = pd.DataFrame(rows, columns=column_order)

    try:
        df.to_csv(output_csv, index=False)
        print(f"✅ Summary CSV saved to: {output_csv}")
    except Exception as e:
        print(f"Error saving CSV to {output_csv}: {e}")

def genFinal_pass_k_stats_base(data, output_csv="finalPass@kBase.csv"):
        """
        Generates a CSV summary with task category, pass@1, pass@3, and pass@5 scores.
        A final row provides cumulative averages for these scores.

        pass@1: 1 if the task with subid '0' had all test cases executed successfully, else 0.
        pass@3: 1 if any of the subids '0', '1', or '2' for the task had all test cases
                executed successfully, else 0.
        pass@5: 1 if any of the subids '0', '1', '2', '3', or '4' for the task had all
                test cases executed successfully, else 0.

        Args:
            data (list of dict): Each dict must contain:
                - 'category' (str): The identifier for the task.
                - 'subid' (str): The sub-identifier, expected to be '0'-'4'.
                - 'base_all_test_cases_execution_status' (bool): True if all test cases
                for this category and subid executed successfully, False otherwise.
            output_csv (str): Path to save the output CSV.
        """
        # grouped stores pass status for subids 0-4 for each category
        # e.g., grouped['TaskA'] = [True, False, True, False, False]
        # (status for subid 0, 1, 2, 3, 4 respectively)
        grouped = defaultdict(lambda: [False] * 5)

        for item in data:
            category = item.get("category")
            subid_str = item.get("subid")
            
            # Ensure category is present and subid is valid
            if category is None:
                print(f"Warning: Skipping item due to missing 'category': {item}")
                continue
            if subid_str not in {"0", "1", "2", "3", "4"}:
                # print(f"Warning: Skipping item with invalid 'subid' {subid_str} for category {category}: {item}")
                continue

            subid_int = int(subid_str)
            test_case_passed = item.get("base_all_test_cases_execution_status", False)

            if test_case_passed:
                grouped[category][subid_int] = True

        # Prepare final CSV rows
        rows = []
        total_pass_at_1 = 0
        total_pass_at_3 = 0
        total_pass_at_5 = 0
        
        # Check if grouped is empty before proceeding
        if not grouped:
            print("Warning: No data to process after filtering. Output CSV will be empty or have only headers/average row.")
            num_tasks = 0
        else:
            num_tasks = len(grouped)

            for category, pass_statuses in grouped.items():
                # pass_statuses is a list of 5 booleans for subids 0-4
                
                # pass@1: Check if subid 0 passed
                pass_at_1 = 1 if pass_statuses[0] else 0
                
                # pass@3: Check if any of subids 0, 1, or 2 passed
                pass_at_3 = 1 if any(pass_statuses[0:3]) else 0
                
                # pass@5: Check if any of subids 0, 1, 2, 3, or 4 passed
                pass_at_5 = 1 if any(pass_statuses[0:5]) else 0
                
                rows.append({
                    "task": category,
                    "pass@1": pass_at_1,
                    "pass@3": pass_at_3,
                    "pass@5": pass_at_5
                })
                
                total_pass_at_1 += pass_at_1
                total_pass_at_3 += pass_at_3
                total_pass_at_5 += pass_at_5

        # Add cumulative average row
        if num_tasks > 0:
            avg_pass_at_1 = round(total_pass_at_1 / num_tasks, 2)
            avg_pass_at_3 = round(total_pass_at_3 / num_tasks, 2)
            avg_pass_at_5 = round(total_pass_at_5 / num_tasks, 2)
            
            rows.append({
                "task": "Cumulative Average",
                "pass@1": avg_pass_at_1,
                "pass@3": avg_pass_at_3,
                "pass@5": avg_pass_at_5
            })
        else:
            # Append an empty average row if there were no tasks
            rows.append({
                "task": "Cumulative Average",
                "pass@1": 0.0,
                "pass@3": 0.0,
                "pass@5": 0.0
            })

        # Define column order for the DataFrame
        column_order = ['task', 'pass@1', 'pass@3', 'pass@5']
        df = pd.DataFrame(rows, columns=column_order)
        
        try:
            df.to_csv(output_csv, index=False)
            print(f"✅ Summary CSV saved to: {output_csv}")
        except Exception as e:
            print(f"Error saving CSV to {output_csv}: {e}")

def genFinal_pass_k_stats_tuned(data, output_csv="finalPass@kTuned.csv"):
        """
        Generates a CSV summary with task category, pass@1, pass@3, and pass@5 scores.
        A final row provides cumulative averages for these scores.

        pass@1: 1 if the task with subid '0' had all test cases executed successfully, else 0.
        pass@3: 1 if any of the subids '0', '1', or '2' for the task had all test cases
                executed successfully, else 0.
        pass@5: 1 if any of the subids '0', '1', '2', '3', or '4' for the task had all
                test cases executed successfully, else 0.

        Args:
            data (list of dict): Each dict must contain:
                - 'category' (str): The identifier for the task.
                - 'subid' (str): The sub-identifier, expected to be '0'-'4'.
                - 'base_all_test_cases_execution_status' (bool): True if all test cases
                for this category and subid executed successfully, False otherwise.
            output_csv (str): Path to save the output CSV.
        """
        # grouped stores pass status for subids 0-4 for each category
        # e.g., grouped['TaskA'] = [True, False, True, False, False]
        # (status for subid 0, 1, 2, 3, 4 respectively)
        grouped = defaultdict(lambda: [False] * 5)

        for item in data:
            category = item.get("category")
            subid_str = item.get("subid")
            
            # Ensure category is present and subid is valid
            if category is None:
                print(f"Warning: Skipping item due to missing 'category': {item}")
                continue
            if subid_str not in {"0", "1", "2", "3", "4"}:
                # print(f"Warning: Skipping item with invalid 'subid' {subid_str} for category {category}: {item}")
                continue

            subid_int = int(subid_str)
            test_case_passed = item.get("finetuned_all_test_cases_execution_status", False)

            if test_case_passed:
                grouped[category][subid_int] = True

        # Prepare final CSV rows
        rows = []
        total_pass_at_1 = 0
        total_pass_at_3 = 0
        total_pass_at_5 = 0
        
        # Check if grouped is empty before proceeding
        if not grouped:
            print("Warning: No data to process after filtering. Output CSV will be empty or have only headers/average row.")
            num_tasks = 0
        else:
            num_tasks = len(grouped)

            for category, pass_statuses in grouped.items():
                # pass_statuses is a list of 5 booleans for subids 0-4
                
                # pass@1: Check if subid 0 passed
                pass_at_1 = 1 if pass_statuses[0] else 0
                
                # pass@3: Check if any of subids 0, 1, or 2 passed
                pass_at_3 = 1 if any(pass_statuses[0:3]) else 0
                
                # pass@5: Check if any of subids 0, 1, 2, 3, or 4 passed
                pass_at_5 = 1 if any(pass_statuses[0:5]) else 0
                
                rows.append({
                    "task": category,
                    "pass@1": pass_at_1,
                    "pass@3": pass_at_3,
                    "pass@5": pass_at_5
                })
                
                total_pass_at_1 += pass_at_1
                total_pass_at_3 += pass_at_3
                total_pass_at_5 += pass_at_5

        # Add cumulative average row
        if num_tasks > 0:
            avg_pass_at_1 = round(total_pass_at_1 / num_tasks, 2)
            avg_pass_at_3 = round(total_pass_at_3 / num_tasks, 2)
            avg_pass_at_5 = round(total_pass_at_5 / num_tasks, 2)
            
            rows.append({
                "task": "Cumulative Average",
                "pass@1": avg_pass_at_1,
                "pass@3": avg_pass_at_3,
                "pass@5": avg_pass_at_5
            })
        else:
            # Append an empty average row if there were no tasks
            rows.append({
                "task": "Cumulative Average",
                "pass@1": 0.0,
                "pass@3": 0.0,
                "pass@5": 0.0
            })

        # Define column order for the DataFrame
        column_order = ['task', 'pass@1', 'pass@3', 'pass@5']
        df = pd.DataFrame(rows, columns=column_order)
        
        try:
            df.to_csv(output_csv, index=False)
            print(f"✅ Summary CSV saved to: {output_csv}")
        except Exception as e:
            print(f"Error saving CSV to {output_csv}: {e}")