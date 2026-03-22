# Data Generation Pipelines

This folder contains the three pipelines used to **build the training dataset**. These pipelines run before fine-tuning — they produce the data in `dataset/training/`.

> For model fine-tuning, see `fine-tuning/`.
> For evaluating model outputs, see `evaluation/`.

```
pipelines/
├── 1-synthetic-data-pipeline/   # Generate synthetic training data
├── 2-real-world-data-pipeline/  # Collect & validate real-world programs
└── 3-repair-pipeline/           # Iterative code repair during generation
```

---

## 1. Synthetic Data Pipeline

**Purpose:** Automatically generate large-scale compiler-validated C programs for embedded systems.

**Three-stage process:**
1. **Base prompt generation** — specifies functional requirements per sensor/actuator category, target board, and application context
2. **Prompt enrichment** — injects library constraints, error handling requirements, OS compatibility rules
3. **Code synthesis + compiler-in-the-loop validation** — generates via Gemini Flash 2.0, then validates through four stages: C++ keyword filtering → structural verification → library validation → GCC compilation (up to 3 retries with error feedback)

**Key files:**
- `task_generator/task_manager.py` — orchestrates the full pipeline
- `prompts/prompt_generator.py` — builds enriched prompts
- `config/constants_rpi_standard.py` — sensor/actuator categories, Pi models, use contexts
- `validation/` — four-stage validation stack
- `storage/example_saver.py` — saves validated examples to JSON

**Run:**
```bash
cd 1-synthetic-data-pipeline
python task_generator/task_manager.py
```

**Requirements:** Gemini API key in `config/model.py`.

---

## 2. Real-World Data Pipeline

**Purpose:** Collect, validate, and tag real-world embedded C programs from GitHub and educational resources.

**Sources:**
- GitHub repositories via REST API v3 (search for Raspberry Pi C programs)
- Educational resources via Google SerpAPI + manual curation

Applies the same four-stage validation stack as the synthetic pipeline. Task descriptions generated via Gemini Flash 2.0 with paraphrasing augmentation.

**Key files:**
- `prompting_code.py` / `Prompt_Fetch.ipynb` — fetch and process collected files
- `prompts/prompt_generator.py` — generates task descriptions for collected programs
- `validation/` — validation stack
- `raw-files/` — raw `.c` source files from public repositories

**Run:**
```bash
cd 2-real-world-data-pipeline
python prompting_code.py
```

---

## 3. Repair Pipeline

**Purpose:** Iterative repair loop that feeds GCC compiler error messages back into the generation prompt for corrective re-generation.

Used during synthetic data construction to recover programs that failed on the first generation attempt. Allows up to 3 retries per task, appending the GCC error output to the original prompt.

**Run:**
```bash
cd 3-repair-pipeline
python task_generator/task_manager.py
```

---

## Validation Architecture (Data Generation)

The `validation/` subfolder in pipelines 1 and 2 validates code **during dataset construction** — ensuring training data compiles and meets structural requirements. This is distinct from the model evaluation validation in `evaluation/validation-pipeline/`, which scores fine-tuned model outputs across four weighted dimensions including functional relevance and code quality.

**Shared validation files** (identical across pipelines 1, 2, and evaluation/):
- `validate_build_command.py` — detects C++ build commands
- `validate_illegal_libs.py` — blacklist of restricted headers
- `validation_libraries.py` — allowed embedded library definitions

---

## Shared Dependencies

```bash
bash 1-synthetic-data-pipeline/install_all_deps.sh
```

Requirements: Python 3.10+, `google-generativeai`, `openai`, `gcc` (system).
