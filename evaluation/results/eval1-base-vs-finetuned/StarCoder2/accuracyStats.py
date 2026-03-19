import json
import statistics
import numpy as np

def extract_and_analyze(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    base_times = []
    finetuned_times = []

    for item in data:
        if "base_Accuracy_Score" in item:
            base_times.append(item["base_Accuracy_Score"])
        if "finetuned_Accuracy_Score" in item:
            finetuned_times.append(item["finetuned_Accuracy_Score"])

    def summarize(name, values):
        print(f"\n{name} Accuracy Summary:")
        print("-" * 40)
        #print(f"Count   : {len(values)}")
        print(f"Min     : {min(values):.2f}")
        print(f"Q1 (25%) : {np.percentile(values, 25):.2f}")
        print(f"Median  : {statistics.median(values):.2f}")
        print(f"Q3 (75%) : {np.percentile(values, 75):.2f}")
        print(f"Max     : {max(values):.2f}")
        print(f"Mean    : {statistics.mean(values):.2f}")

    if base_times:
        summarize("Base", base_times)
    else:
        print("No base accuracy found.")

    if finetuned_times:
        summarize("Fine-tuned", finetuned_times)
    else:
        print("No fine-tuned accuracy found.")

if __name__ == "__main__":
    filename = input("Enter the JSON filename (e.g., results.json): ").strip()
    extract_and_analyze(filename)
