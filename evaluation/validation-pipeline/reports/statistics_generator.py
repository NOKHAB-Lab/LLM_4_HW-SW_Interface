import logging
import csv


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def compute_validation_statistics_base(data, output_csv_path: str = "base_stats.csv"):
    # Initialize counters and accumulators
    count_keys = [
        "base_has_main_function",
        "base_has_include_directives",
        "base_has_required_libraries",
        "base_has_no_cpp_indicators",
        "base_has_no_restricted_headers_and_patterns",
        "base_inference_has_valid_syntax",
        "base_inference_has_valid_build"
    ]

    sum_keys = [
        "base_PercentageTaskRelevance_GEMINI",
        "base_PercentageCodeRelevanceToReference_GEMINI",
        "base_PercentageTaskRelevance_GPT",
        "base_PercentageCodeRelevanceToReference_GPT",
        "base_inference_warnings",
        "base_inference_static_code_quality_score",
        "base_execution_time",
        "base_Accuracy_Score"
    ]

    # For finetuned_Accuracy_Breakdown breakdown fields
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

        breakdown = item.get("base_Accuracy_Breakdown", {})
        for bk in breakdown_keys:
            val = breakdown.get(bk)
            breakdown_sums[bk] += val if isinstance(val, (int, float)) else 0.0

    # Compute averages
    avg_stats = {
        k: stats[k] / total_count if total_count > 0 else 0 for k in sum_keys
    }
    avg_breakdowns = {
        f"base_avg_{bk}": breakdown_sums[bk] / total_count if total_count > 0 else 0 for bk in breakdown_keys
    }

    # Merge all stats
    final_stats = {**{k: stats[k] for k in count_keys}, **avg_stats, **avg_breakdowns}

    # Write to CSV
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Metric', 'Value'])
        for key, value in final_stats.items():
            writer.writerow([key, round(value, 2) if isinstance(value, float) else value])

    logging.info(f"✅ Base Stats written to {output_csv_path}")

def compute_validation_statistics_tuned(data, output_csv_path: str = "tuned_stats.csv"):
    # Initialize counters and accumulators
    count_keys = [
        "finetuned_has_main_function",
        "finetuned_has_include_directives",
        "finetuned_has_required_libraries",
        "finetuned_has_no_cpp_indicators",
        "finetuned_has_no_restricted_headers_and_patterns",
        "finetuned_inference_has_valid_syntax",
        "finetuned_inference_has_valid_build"
    ]

    sum_keys = [
        "finetuned_PercentageTaskRelevance_GEMINI",
        "finetuned_PercentageCodeRelevanceToReference_GEMINI",
        "finetuned_PercentageTaskRelevance_GPT",
        "finetuned_PercentageCodeRelevanceToReference_GPT",
        "finetuned_inference_warnings",
        "finetuned_inference_static_code_quality_score",
        "finetuned_execution_time",
        "finetuned_Accuracy_Score"
    ]

    # For finetuned_Accuracy_Breakdown breakdown fields
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

        breakdown = item.get("finetuned_Accuracy_Breakdown", {})
        for bk in breakdown_keys:
            val = breakdown.get(bk)
            breakdown_sums[bk] += val if isinstance(val, (int, float)) else 0.0

    # Compute averages
    avg_stats = {
        k: stats[k] / total_count if total_count > 0 else 0 for k in sum_keys
    }
    avg_breakdowns = {
        f"finetuned_avg_{bk}": breakdown_sums[bk] / total_count if total_count > 0 else 0 for bk in breakdown_keys
    }

    # Merge all stats
    final_stats = {**{k: stats[k] for k in count_keys}, **avg_stats, **avg_breakdowns}

    # Write to CSV
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Metric', 'Value'])
        for key, value in final_stats.items():
            writer.writerow([key, round(value, 2) if isinstance(value, float) else value])

    logging.info(f"✅ Finetuned Stats written to {output_csv_path}")
    
def write_accuracy_distribution_to_csv(data, csv_output_path: str = "combined_accuracy_stats.csv"):

    # Initialize range bins: 0–10, 10–20, ..., 90–100
    ranges = [(i, i + 10) for i in range(0, 100, 10)]
    bins = {f"{start}-{end}": {"base": 0, "finetuned": 0} for start, end in ranges}

    for item in data:
        # Get base and finetuned scores safely
        base_score = item.get("base_Accuracy_Score", None)
        finetuned_score = item.get("finetuned_Accuracy_Score", None)

        for score, label in [(base_score, "base"), (finetuned_score, "finetuned")]:
            if isinstance(score, (int, float)):
                # Clamp to 99.99 to fall into 90–100 instead of a 100–110 bucket
                score = min(score, 99.999)
                for start, end in ranges:
                    if start <= score < end:
                        range_key = f"{start}-{end}"
                        bins[range_key][label] += 1
                        break

    # Write to CSV
    with open(csv_output_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Accuracy Range", "Base Count", "Finetuned Count"])
        for range_key in bins:
            writer.writerow([range_key, bins[range_key]["base"], bins[range_key]["finetuned"]])

    logging.info(f"✅ Accuracy distribution saved to: {csv_output_path}")

def write_base_inference_errors_to_txt(evaluations, output_path="inference_failures_report_base.txt"):
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
            if not example.get("base_inference_has_valid_syntax", True):
                msg = example.get("base_inference_syntax_check_message", "No syntax message")
                f.write(f"  Base Syntax Error: {msg}\n")

            # Base build
            if not example.get("base_inference_has_valid_build", True):
                msg = example.get("base_inference_build_message", "No build message")
                f.write(f"  Base Build Error: {msg}\n")

            f.write("-" * 40 + "\n")
    logging.info(f"✅ Inference Failures Report saved to: {output_path}") 

def write_tuned_inference_errors_to_txt(evaluations, output_path="inference_failures_report_tuned.txt"):
    """
    Writes syntax and build errors from finetuned outputs to a .txt file.

    Parameters:
    - evaluations: list of dicts, each dict is a parsed JSON of one evaluated example
    - output_path: output .txt file path
    """
    with open(output_path, "w") as f:
        for example in evaluations:
            f.write(f"ID: {example.get('id', 'N/A')}\n")
            f.write(f"SUBID: {example.get('subid', 'N/A')}\n")

            # Finetuned syntax
            if not example.get("finetuned_inference_has_valid_syntax", True):
                msg = example.get("finetuned_inference_syntax_check_message", "No syntax message")
                f.write(f"  Finetuned Syntax Error: {msg}\n")

            # Finetuned build
            if not example.get("finetuned_inference_has_valid_build", True):
                msg = example.get("finetuned_inference_build_message", "No build message")
                f.write(f"  Finetuned Build Error: {msg}\n")

            f.write("-" * 40 + "\n")
    logging.info(f"✅ Inference Failures Report saved to: {output_path}")
