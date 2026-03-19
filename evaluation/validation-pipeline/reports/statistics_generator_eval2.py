import logging
import csv
import pandas as pd
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def compute_validation_statistics(data, output_csv_path: str = "tuned_stats.csv"):
    # Initialize counters and accumulators
    count_keys = [
        "has_main_function",
        "has_include_directives",
        "has_required_libraries",
        "has_no_cpp_indicators",
        "has_no_restricted_headers_and_patterns",
        "inference_has_valid_syntax",
        "inference_has_valid_build"
    ]

    sum_keys = [
        "PercentageTaskRelevance_GEMINI",
        "PercentageCodeRelevanceToReference_GEMINI",
        "PercentageTaskRelevance_GPT",
        "PercentageCodeRelevanceToReference_GPT",
        "inference_warnings",
        "inference_static_code_quality_score",
        "execution_time",
        "Accuracy_Score"
    ]

    # For Accuracy_Breakdown breakdown fields
    breakdown_keys = [
        "Structural_Validation",
        "Compilation_Success",
        "Functional_Relevance",
        "Code_Quality_Check"
    ]

    stats = {k: 0 for k in count_keys}
    stats.update({k: 0.0 for k in sum_keys})
    breakdown_sums = {k: 0.0 for k in breakdown_keys}

    total_count = len(data)

    for item in data:
        for key in count_keys:
            if item.get(key) is True:
                stats[key] += 1

        for key in sum_keys:
            value = item.get(key)
            stats[key] += value if isinstance(value, (int, float)) else 0.0

        breakdown = item.get("Accuracy_Breakdown", {})
        for bk in breakdown_keys:
            val = breakdown.get(bk)
            breakdown_sums[bk] += val if isinstance(val, (int, float)) else 0.0

    # Compute averages
    avg_stats = {
        k: stats[k] / total_count if total_count > 0 else 0 for k in sum_keys
    }
    avg_breakdowns = {
        f"avg_{bk}": breakdown_sums[bk] / total_count if total_count > 0 else 0 for bk in breakdown_keys
    }

    # Merge all stats
    final_stats = {**{k: stats[k] for k in count_keys}, **avg_stats, **avg_breakdowns}

    # Write to CSV
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Metric', 'Value'])
        for key, value in final_stats.items():
            writer.writerow([key, round(value, 2) if isinstance(value, float) else value])

    logging.info(f"✅ Model Stats written to {output_csv_path}")
    
def write_accuracy_distribution_to_csv(data, csv_output_path: str = "accuracy_stats.csv"):

    # Define 10-point bins
    ranges = [(i, i + 10) for i in range(0, 100, 10)]
    bins = {f"{start}-{end}": 0 for start, end in ranges}

    for item in data:
        score = item.get("Accuracy_Score", None)
        if isinstance(score, (int, float)):
            score = min(score, 99.999)  # Ensure 100 goes into the 90–100 bin
            for start, end in ranges:
                if start <= score < end:
                    bins[f"{start}-{end}"] += 1
                    break

    # Write to CSV
    with open(csv_output_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Accuracy Range", "Count"])
        for range_key, count in bins.items():
            writer.writerow([range_key, count])

    logging.info(f"✅ Accuracy distribution saved to: {csv_output_path}")

def write_inference_errors_to_txt(evaluations, output_path="inference_failures_report.txt"):
    """
    Writes syntax and build errors from base and finetuned outputs to a .txt file.
    
    Parameters:
    - evaluations: list of dicts, each dict is a parsed JSON of one evaluated example
    - output_path: output .txt file path
    """
    with open(output_path, "w") as f:
        for example in evaluations:
            f.write(f"ID: {example.get('id', 'N/A')}\n")

            # Base syntax
            if not example.get("inference_has_valid_syntax", True):
                msg = example.get("inference_syntax_check_message", "No syntax message")
                f.write(f"  Inference Syntax Error: {msg}\n")

            # Base build
            if not example.get("inference_has_valid_build", True):
                msg = example.get("inference_build_message", "No build message")
                f.write(f"  Inference Build Error: {msg}\n")

            f.write("-" * 40 + "\n")
    logging.info(f"✅ Inference Failures Report saved to: {output_path}") 

def generate_accuracy_Table(data, output_csv="accuracy_table.csv"):
    """
    Generates a CSV summary with task category, accuracy scores for subid 0/1/2,
    their average, and count of valid builds per category.
    
    Args:
        data (list of dict): List of records, each with fields like 'category', 'subid', 'Accuracy_Score', and 'inference_has_valid_build'.
        output_csv (str): Path to save the output CSV.
    """
    grouped = defaultdict(lambda: {
        "accuracy_var_0": None,
        "accuracy_var_1": None,
        "accuracy_var_2": None,
        "success_builds": 0,
        "counted": 0
    })

    for item in data:
        if item.get("subid") not in {"0", "1", "2"}:
            continue

        key = item.get("category")
        subid = int(item["subid"])
        score = item.get("Accuracy_Score")
        build_ok = item.get("inference_has_valid_build", False)

        if score is not None:
            grouped[key][f"accuracy_var_{subid}"] = score

        if build_ok:
            grouped[key]["success_builds"] += 1
        
        grouped[key]["counted"] += 1

    # Prepare final rows
    rows = []
    for category, vals in grouped.items():
        acc_0 = vals["accuracy_var_0"]
        acc_1 = vals["accuracy_var_1"]
        acc_2 = vals["accuracy_var_2"]

        acc_list = [a for a in [acc_0, acc_1, acc_2] if isinstance(a, (int, float))]
        avg_acc = round(sum(acc_list) / len(acc_list), 2) if acc_list else None

        rows.append({
            "task": category,
            "accuracy_var_0": acc_0,
            "accuracy_var_1": acc_1,
            "accuracy_var_2": acc_2,
            "avg_accuracy": avg_acc,
            "successful_builds": vals["success_builds"]
        })

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"✅ Summary CSV saved to: {output_csv}")
