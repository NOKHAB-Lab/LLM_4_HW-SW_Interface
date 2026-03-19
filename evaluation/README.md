# Evaluation

All post-fine-tuning evaluation assets: the validation pipeline that scores model outputs, and the raw results from all evaluation criteria reported in the paper.

---

## Structure

```
evaluation/
├── validation-pipeline/   ← scripts to validate and score model-generated code
└── results/
    ├── eval1-base-vs-finetuned/   ← Eval 1: pre-trained vs fine-tuned accuracy
    ├── eval2-prompt-variation/    ← Eval 2: prompt variation robustness
    ├── eval3-pass-at-k/           ← Eval 3: Pass@k (k = 1, 3, 5)
    ├── eval4-hardware/            ← Eval 4: hardware-in-the-loop subset
    └── eval5-large-pass-at-k/    ← Eval 5: extended Pass@k (70 × 5 generations)
```

---

## Validation Pipeline

**Location:** `evaluation/validation-pipeline/`

Scores each model-generated C program across four dimensions:

| Dimension | Weight | What is checked |
|-----------|--------|-----------------|
| Structural Validation | 40% | `main()` presence, required libraries, no C++ elements, include directives |
| Compilation Success | 25% | Valid syntax (GCC), successful build |
| Functional Relevance | 25% | Task relevance scored by Gemini Flash 2.0 (10%) + GPT-4o (10%) + reference comparison (2.5% each) |
| Code Quality | 10% | `cppcheck` static analysis (1–5 score), compiler warning count |

### Entry Scripts

| Script | What it runs |
|--------|-------------|
| `execute_validation_Criteria1.py` | Eval 1 — base vs fine-tuned, 70 prompts |
| `execute_validation_Criteria2.py` | Eval 2 — prompt variation robustness |
| `execute_validation_Criteria3.py` | Eval 3 — Pass@k (temperature=0.7, k ∈ {1,3,5}) |
| `execute_validation_GPT_and_Gemini.py` | Functional relevance scoring via GPT-4o + Gemini |

### Setup

```bash
cd evaluation/validation-pipeline
# Set API keys in config/model.py:
#   API_KEY = "YOUR_GEMINI_API_KEY"
#   OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
python execute_validation_Criteria1.py
```

Outputs per run: `*_VALIDATED.json`, accuracy CSV, build/syntax error report.

---

## Results

Each results subfolder contains validated JSON files, accuracy/statistics CSVs, and plots.

### eval1-base-vs-finetuned/
Per-model folders (CodeLlama, Mistral, StarCoder2, DeepSeekCoder, Qwen, GPT, Gemini) with:
- `*_VALIDATED.json` — validation output for each of the 70 test prompts
- `*_Accuracy_Statistics_Combined.csv` — combined accuracy breakdown
- `*_Validation_Statistics_Base/Tuned.csv` — per-criterion scores
- `*_Build_SyntaxErrorReports.txt` — compilation failure logs
- Key figures: `Fig6.png`–`Fig10.png`

### eval2-prompt-variation/
Robustness test: 10 prompts × 3 paraphrases. Models: Mistral, DeepSeekCoder, Qwen.
- `accuracy_variationsvsstandard.csv` — standard vs paraphrased accuracy
- `Fig12.png`

### eval3-pass-at-k/
Pass@k evaluation (k=1,3,5) at temperature=0.7.
- `pass_k_summary_70.csv`
- `Fig14.png`

### eval4-hardware/
Hardware-in-the-loop subset: 15 prompts validated on physical Raspberry Pi devices.
- `hw_validation_prompts.json`, `validation_subset.json`

### eval5-large-pass-at-k/
Extended Pass@k with 70 prompts × 5 generations for all fine-tuned models, GPT-4o, and Gemini Flash 2.0.
- Per-model subfolders (Mistral, DeepSeekCoder, Qwen, GPT, Gemini) with `*_VALIDATED.json` and pass@k CSVs
- `pass_k_summary_finetuned_70.csv` — aggregated pass@k scores for fine-tuned models

---

## Workflow Position

```
fine-tuning/<model>/   →   evaluation/validation-pipeline/   →   evaluation/results/
  (inference outputs)         (score with 4-criterion eval)         (CSV + JSON + plots)
```
