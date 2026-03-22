# Validation Pipeline

Evaluates pre-trained and fine-tuned model outputs using a four-component weighted accuracy framework. Supports three evaluation protocols and functional relevance scoring via GPT-4o and Gemini.

---

## Accuracy Framework

Each generated code sample is scored across four weighted dimensions:

| Dimension | Weight | Criteria |
|---|---|---|
| Structural Validation | **40%** | `main()` presence (10%), required libraries (10%), no restricted headers (10%), no C++ elements (5%), include directives (5%) |
| Compilation Success | **25%** | Valid syntax (10%), successful GCC build (15%) |
| Functional Relevance | **25%** | Task relevance via Gemini (10%) + GPT-4o (10%), reference relevance via both (2.5% each) |
| Code Quality | **10%** | Static analysis rating 1–5 (5%), compiler warnings count (5%) |

---

## Evaluation Scripts

| Script | Protocol | Description |
|---|---|---|
| `execute_validation_criteria1.py` | **Eval 1** | Structural + compilation validation for base (pre-trained) and fine-tuned model outputs on 70 prompts |
| `execute_validation_criteria2.py` | **Eval 2** | Prompt variation robustness — evaluates model outputs on paraphrased prompt variants |
| `execute_validation_criteria3.py` | **Eval 3** | Pass@k evaluation (k ∈ {1, 3, 5}) at temperature 0.7 |
| `execute_validation_gpt_and_gemini.py` | Functional | Functional relevance scoring via GPT-4o and Gemini Flash 2.0 |

Each script reads a JSON file of model responses, runs validation, and writes results to a new JSON file with accuracy scores appended per example.

---

## File Structure

```
3-validation-pipeline/
├── execute_validation_criteria1.py     # Eval 1 entry point
├── execute_validation_criteria2.py     # Eval 2 entry point
├── execute_validation_criteria3.py     # Eval 3 entry point
├── execute_validation_gpt_and_gemini.py # Functional relevance scoring
├── execute.ipynb                        # Notebook version
├── evaluator/
│   ├── accuracy_calculator.py           # Weighted accuracy computation
│   ├── accuracy_calculator_base.py      # Accuracy for pre-trained model outputs
│   ├── accuracy_calculator_finetuned.py # Accuracy for fine-tuned model outputs
│   ├── test_case_evaluator.py           # Individual test case evaluation
│   ├── test_case_evaluator_base.py
│   └── test_case_evaluator_finetuned.py
├── task_manager/
│   ├── task_manager_eval1_base.py       # Manages inference for base models
│   ├── task_manager_eval1_tuned.py      # Manages inference for fine-tuned models
│   └── task_manager_gpt_and_gemini.py   # Manages GPT-4o + Gemini calls
├── reports/
│   ├── statistics_generator.py          # Summary statistics and CSV reports
│   ├── statistics_generator_eval2.py
│   ├── statistics_generator_eval3.py
│   └── statistics_generator_gpt.py
├── validation/
│   ├── validate.py
│   ├── validate_build_and_compile.py
│   ├── validate_build_command.py
│   ├── validate_cpp_presence.py
│   ├── validate_illegal_libs.py
│   ├── validate_static_code_quality.py  # Static analysis scoring
│   ├── validation_task_accuracy_gemini.py
│   ├── validation_task_accuracy_gpt.py
│   └── validation_libraries.py
├── api/
│   ├── gemini_api.py
│   ├── gpt_api.py
│   └── test.py                          # API connection tests
├── config/
│   ├── constants_rpi_standard.py
│   ├── constants_rpi_pico.py
│   └── model.py                         # API keys
├── GPT_Test_Train_Samples_Count_70by5_LargeSet_Responses.json
└── Gemini_Test_Train_Samples_Count_70by5_LargeSet_Responses.json
```

---

## Configuration

Edit `config/model.py`:

```python
API_KEY = "YOUR_GEMINI_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
```

In each evaluation script, set the input/output file paths:

```python
INPUT_JSON  = 'YourModel_Responses.json'
OUTPUT_JSON = 'YourModel_Responses_VALIDATED.json'
Model_Name  = 'YourModelName'
```

---

## Run

```bash
cd evaluation/validation-pipeline

# Eval 1: structural + compilation validation
python execute_validation_criteria1.py

# Eval 2: prompt variation robustness
python execute_validation_criteria2.py

# Eval 3: Pass@k
python execute_validation_criteria3.py

# Functional relevance scoring (run after Eval 1 — requires Gemini + OpenAI API keys)
python execute_validation_gpt_and_gemini.py
```

Each script supports **checkpointing** — if interrupted, it resumes from the last saved example.

**Requirements:** Gemini and OpenAI API keys in `config/model.py`, Python 3.10+, GCC toolchain.
