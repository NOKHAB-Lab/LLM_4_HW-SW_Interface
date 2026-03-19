# Replication Guide

This guide walks you through reproducing all results from the paper **"Domain-Specific Fine-Tuning of Large Language Models for HW/SW Interface Generation: An Empirical Study"** (CAiSE 2026).

There are two paths depending on your goal:

- **Use existing data** — skip dataset generation and fine-tuning, go straight to evaluation and analysis using the provided datasets and results.
- **Full reproduction from scratch** — regenerate the dataset, fine-tune the models, run inference, validate outputs, and generate figures.

---

## Requirements

### System
- Linux (Ubuntu 20.04+ recommended)
- Python 3.10+
- GCC toolchain with embedded libraries: `wiringPi`, `pigpio`, `bcm2835`
- `cppcheck` (for code quality scoring)
- CUDA-capable GPU with 80GB VRAM (for fine-tuning — tested on dual NVIDIA H100)

### Install Python dependencies
```bash
bash pipelines/1-synthetic-data-pipeline/install_all_deps.sh
```

Key packages: `transformers`, `trl`, `peft`, `bitsandbytes`, `accelerate`, `torch`, `google-generativeai`, `openai`, `pandas`, `tqdm`

### API Keys

Set in the relevant `config/model.py` files within each pipeline and the evaluation folder:

```python
# evaluation/validation-pipeline/config/model.py
API_KEY = "YOUR_GEMINI_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# pipelines/1-synthetic-data-pipeline/config/model.py
API_KEYS = ["YOUR_GEMINI_API_KEY"]

# pipelines/2-real-world-data-pipeline/config/model.py
API_KEYS = ["YOUR_GEMINI_API_KEY"]

# pipelines/3-repair-pipeline/config/model.py
API_KEYS = ["YOUR_GEMINI_API_KEY"]
```

---

## Path A — Use Existing Data (Recommended for Reviewers)

All datasets and evaluation results are already provided. You can skip straight to analysis and figure generation.

### Step 1 — Explore the dataset

The training and test data is in `dataset/`:

```
dataset/training/synthetic/Validated_Synthetic_Dataset.json   # 15,886 synthetic programs
dataset/training/real-world/Real_World_Dataset.json            # 1,053 real-world programs
dataset/training/Training_Set_JSONL.jsonl                      # Fine-tuning ready JSONL
dataset/test/test_set_70.json                                  # 70-prompt test set
```

### Step 2 — Explore evaluation results

All validated model outputs are in `evaluation/results/`:

```
evaluation/results/eval1-base-vs-finetuned/   # Pre-trained vs fine-tuned (5 models + GPT + Gemini)
evaluation/results/eval2-prompt-variation/    # Prompt variation robustness
evaluation/results/eval3-pass-at-k/           # Pass@k (k=1,3,5)
evaluation/results/eval4-hardware/            # Hardware-in-the-loop subset
evaluation/results/eval5-large-pass-at-k/     # Extended Pass@k (70 × 5 generations)
```

Each model subfolder contains `*_VALIDATED.json` files with per-example scores.

### Step 3 — Compute accuracy statistics

```bash
cd analysis
python accuracyStats.py     # prompts for a *_VALIDATED.json file
python timeStats.py         # prompts for a *_VALIDATED.json file
python extract_errors.py    # prompts for a *_VALIDATED.json file
```

### Step 4 — Reproduce all paper figures

```bash
cd analysis
jupyter notebook plot_generation.ipynb
```

This generates all figures (Fig4–Fig14) from the pre-computed result CSVs in `evaluation/results/`.

---

## Path B — Full Reproduction from Scratch

### Step 1 — Generate the synthetic training dataset

```bash
cd pipelines/1-synthetic-data-pipeline
# Set your Gemini API key in config/model.py
python task_generator/task_manager.py
```

Output: validated examples saved to JSON in the pipeline directory. Copy to `dataset/training/synthetic/` when complete.

The pipeline runs three stages automatically:
1. Base prompt generation (sensor/actuator category + board + context)
2. Prompt enrichment (library constraints, error handling rules)
3. Code synthesis via Gemini Flash 2.0 + four-stage validation (C++ filter → structural → library → GCC compilation)

Failed examples are automatically sent to the repair pipeline (Step 3).

### Step 2 — Collect real-world training data

```bash
cd pipelines/2-real-world-data-pipeline
# Set your Gemini API key in config/model.py
# Place .c source files in raw-files/
python Prompting_code.py --input-dir "raw-files/"
```

Output: `raspberry_pi_validated_data.json` — programs that passed all four validation stages.

### Step 3 — Repair failed examples (optional, runs automatically from Step 1)

```bash
cd pipelines/3-repair-pipeline
# Set your Gemini API key in config/model.py
python task_generator/task_manager.py
```

This reads failed examples, feeds GCC error messages back into Gemini, and retries up to 3 times.

### Step 4 — Fine-tune the models

Use the notebooks in `fine-tuning/`. Each model has its own subfolder with a training notebook:

```
fine-tuning/codellama-7b/training/Fine_Tuning_Script_CodeLlama_v2.ipynb
fine-tuning/mistral-7b/training/Fine_Tuning_Script_Mistral_7B_v2.ipynb
fine-tuning/starcoder2-7b/training/Fine_Tuning_Script_StarCoder2_7B_v1.ipynb
fine-tuning/deepseek-coder-6.7b/training/Fine_Tuning_Script_DeepSeekCoder_6.7B_v1.ipynb
fine-tuning/qwen2.5-7b/training/Fine_Tuning_Script_Qwen2.5_7B_v1.ipynb
```

All notebooks use:
- Input: `dataset/training/Training_Set_JSONL.jsonl`
- Method: QLoRA (4-bit NF4 + BF16, LoRA r=16 α=32)
- Framework: HuggingFace SFTTrainer (TRL) + PEFT
- Hardware: dual NVIDIA H100 80GB

After fine-tuning, run inference on the 70-prompt test set and save responses as a JSON file with fields `base_code`, `base_build-command`, `finetuned_code`, `finetuned_build-command`.

### Step 5 — Run the evaluation pipeline

The evaluation is a **two-step process**. Run step 5a first, then 5b.

#### Step 5a — Structural + compilation validation (Eval 1)

```bash
cd evaluation/validation-pipeline
# Edit execute_validation_Criteria1.py:
#   INPUT_JSON  = 'YourModel_Responses.json'
#   OUTPUT_JSON = 'YourModel_Responses_VALIDATED.json'
#   Model_Name  = 'YourModelName'
python execute_validation_Criteria1.py
```

This scores each example on:
- Structural Validation (40%): `main()`, includes, libraries, C++ checks
- Compilation Success (25%): GCC syntax check + full build
- Code Quality (10%): `cppcheck` static analysis + compiler warnings
- Functional Relevance (25%): set to 0 here — scored separately in Step 5b

Output: `*_VALIDATED.json` + accuracy CSVs + error report.

#### Step 5b — Functional relevance scoring

```bash
cd evaluation/validation-pipeline
# Edit execute_validation_GPT_and_Gemini.py:
#   INPUT_JSON_GPT  = 'YourModel_Responses.json'
#   OUTPUT_JSON_GPT = 'YourModel_Responses_FR_VALIDATED.json'
# Set API keys in config/model.py (both Gemini and OpenAI required)
python execute_validation_GPT_and_Gemini.py
```

This adds functional relevance scores (Gemini Flash 2.0 + GPT-4o) to the validated JSON. The final `Accuracy_Score` combining all four dimensions is recomputed.

#### Step 5c — Prompt variation robustness (Eval 2)

```bash
cd evaluation/validation-pipeline
# Edit execute_validation_Criteria2.py with your input/output filenames
python execute_validation_Criteria2.py
```

#### Step 5d — Pass@k evaluation (Eval 3)

```bash
cd evaluation/validation-pipeline
# Edit execute_validation_Criteria3.py with your input/output filenames
# Input must contain 5 responses per prompt (subid 0–4)
python execute_validation_Criteria3.py
```

### Step 6 — Compute statistics and generate figures

```bash
cd analysis
python accuracyStats.py
python timeStats.py
python extract_errors.py
jupyter notebook plot_generation.ipynb
```

---

## Evaluation Scoring Reference

| Dimension | Weight | Criteria |
|---|---|---|
| Structural Validation | **40%** | `main()` (10%), required libraries (10%), no restricted headers (10%), no C++ elements (5%), include directives (5%) |
| Compilation Success | **25%** | Valid syntax (10%), successful GCC build (15%) |
| Functional Relevance | **25%** | Task relevance Gemini (10%) + GPT-4o (10%), reference relevance both (2.5% each) |
| Code Quality | **10%** | `cppcheck` rating 1–5 (5%), compiler warnings (5%) |

---

## Repository Structure Quick Reference

```
HW-SW-Interface-LLM-Dataset/
├── dataset/                          # Training (15,886 + 1,053) and test (70) data
├── pipelines/
│   ├── 1-synthetic-data-pipeline/    # Step 1: generate synthetic training data
│   ├── 2-real-world-data-pipeline/   # Step 2: collect real-world training data
│   └── 3-repair-pipeline/            # Step 3: iterative code repair
├── fine-tuning/                      # Step 4: QLoRA fine-tuning notebooks (5 models)
├── evaluation/
│   ├── validation-pipeline/          # Step 5: score model outputs
│   └── results/                      # All raw results (CSV, JSON, plots)
├── analysis/                         # Step 6: statistics and figure generation
└── figures/                          # All paper figures (Fig4–Fig14)
```

---

## Notes

- All evaluation scripts support **checkpointing** — if interrupted, they resume from the last saved example.
- The evaluation pipeline requires GCC and `cppcheck` installed on the system.
- Functional relevance scoring (Step 5b) requires both a Gemini API key and an OpenAI API key.
- For fine-tuning, use the `v2` notebook where available — it contains the final hyperparameter configuration used in the paper.
