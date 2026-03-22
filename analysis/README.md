# Analysis Scripts

Scripts and notebooks for dataset analysis, test set statistics, and result visualization.

---

## Training Dataset Analysis (`training/`)

| File | Description |
|---|---|
| `data_analysis.ipynb` | Jupyter notebook with full exploratory analysis of the training dataset |
| `perform_statistical_analysis.py` | Computes summary statistics across the full training set |
| `generate_stats.py` | Generates per-category and per-subcategory statistics |
| `analysis_category.py` | Category-level breakdown and distribution analysis |
| `tags_formatting.py` | Normalizes and formats metadata tags across dataset entries |

```bash
cd training/
python perform_statistical_analysis.py
python generate_stats.py
```

---

## Test Set Analysis (`test/`)

| File | Description |
|---|---|
| `perform_statistical_analysis.py` | Statistical summary of test set evaluation results |
| `generate_stats.py` | Per-model accuracy breakdown and Pass@k statistics |

```bash
cd test/
python perform_statistical_analysis.py
python generate_stats.py
```

---

## Evaluation Result Utilities

| File | Description |
|---|---|
| `accuracy_stats.py` | Extracts and summarizes `base_Accuracy_Score` / `finetuned_Accuracy_Score` from validated JSON files |
| `time_stats.py` | Extracts Q1/Q3 execution time stats from `base_execution_time` / `finetuned_execution_time` fields |
| `extract_errors.py` | Extracts build/syntax failure logs for both base and fine-tuned model outputs |
| `plot_generation.ipynb` | Generates all paper figures (accuracy comparison, execution time, breakdown subplots) |

These utilities operate on the validated JSON files produced by `evaluation/validation-pipeline/`.

```bash
python accuracy_stats.py       # prompts for JSON filename
python time_stats.py           # prompts for JSON filename
python extract_errors.py      # prompts for JSON filename
```
