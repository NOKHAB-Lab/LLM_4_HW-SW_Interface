# Dataset

This folder contains all training and test data used in the paper.

## Structure

```
dataset/
├── training/
│   ├── synthetic/
│   │   └── validated_synthetic_dataset.json     # Compiler-validated synthetic dataset
│   ├── real-world/
│   │   ├── real_world_dataset.json              # ~1,000 real-world programs
│   │   └── real_world_stats.json                # Real-world statistics
│   └── training_set.jsonl                       # Fine-tuning ready JSONL (~16,000 entries)
└── test/
    ├── test_set_70_responses.json                # 70-prompt test set + model responses + evaluation scores
    ├── test_set_70_prompts_template.json         # 70 prompts only — use to run your own model
    └── test_set_70_statistics.json               # Test set statistics
```

---

## Training Data

### Synthetic Dataset (`training/synthetic/`)

**~16,000 compiler-validated C programs** generated via an automated three-stage pipeline (Gemini Flash 2.0 + GCC compiler-in-the-loop). Each program passed four validation stages:

1. C++ keyword filtering (`class`, `namespace`, `template`)
2. Structural verification (`#include`, `main()`)
3. Library validation (standard embedded libraries only)
4. GCC compilation check

**Category distribution:**

| Category | Count | % |
|---|---|---|
| Combined sensor-actuator | ~6,784 | 42.4% |
| Sensor integration | ~6,272 | 39.2% |
| Actuator control | ~2,944 | 18.4% |

### Real-World Dataset (`training/real-world/`)

**~1,000 validated C programs** collected from:
- GitHub repositories (public embedded systems projects)
- Educational resources (tutorials, programming books)

Validated for `main()`, standard platform library usage (`wiringPi`, `bcm2835`), and successful GCC compilation. Task descriptions generated and paraphrased using Gemini Flash 2.0.

### Fine-Tuning JSONL (`training/training_set.jsonl`)

The **~16,000-entry JSONL** is ready for direct use with HuggingFace `transformers`/`trl` fine-tuning pipelines. Format: `{"prompt": "...", "completion": "..."}` instruction-response pairs.

---

## Test Data (`test/`)

**70 representative prompts** covering the full range of embedded task categories. Used for:
- **Eval 1** — Pre-trained vs. fine-tuned accuracy comparison (70 prompts)
- **Eval 2** — Prompt variation robustness (10 prompts × 3 paraphrases)
- **Eval 3** — Pass@k evaluation (k ∈ {1, 3, 5})

`test_set_70_responses.json` includes the reference C code, model responses (base and fine-tuned), build results, and evaluation scores.

`test_set_70_prompts_template.json` is a **clean prompt-only version** for evaluating your own model. It contains only: `id`, `task`, `category`, `complexity`, `tags`, `input`, `prompt`, `file-name`, `build-command` — no reference outputs or evaluation data.

---

## Data Schema

```json
{
  "category":    "string  — high-level task category",
  "input":       "string  — natural language task description (prompt)",
  "output":      "string  — validated C source code",
  "explanation": "string  — 2-3 line description of what the code does",
  "tags":        "string  — comma-separated tags (sensor type, library, board, etc.)",
  "file-name":   "string  — suggested .c filename",
  "build-command": "string — GCC command to compile the code"
}
```

The fine-tuning JSONL uses a simplified format:
```json
{"prompt": "Write a C program for...", "completion": "#include <wiringPi.h>..."}
```
