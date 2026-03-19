# Dataset

This folder contains all training and test data used in the paper.

## Structure

```
dataset/
├── training/
│   ├── synthetic/
│   │   └── Validated_Synthetic_Dataset.json     # Compiler-validated synthetic dataset
│   ├── real-world/
│   │   ├── Real_World_Dataset.json                          # 1,053 real-world programs
│   │   └── real_world_stats.json                            # Real-world statistics
│   └── Training_Set_JSONL.jsonl                       # Fine-tuning ready JSONL (15,886 entries)
└── test/
    ├── test_set_70.json                                     # 70-prompt test set + evaluation responses
    └── test_set_70_statistics.json                          # Test set statistics
```

---

## Training Data

### Synthetic Dataset (`training/synthetic/`)

**~16K compiler-validated C programs** (15,886) generated via an automated three-stage pipeline (Gemini Flash 2.0 + GCC compiler-in-the-loop). Each program passed four validation stages:

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

**~1K validated C programs** (1,053) collected from:
- GitHub repositories (public embedded systems projects)
- Educational resources (tutorials, programming books)

Validated for `main()`, standard platform library usage (`wiringPi`, `bcm2835`), and successful GCC compilation. Task descriptions generated and paraphrased using Gemini Flash 2.0.

### Fine-Tuning JSONL (`training/Training_Set_JSONL.jsonl`)

The **~16K-entry JSONL** (15,886 entries) is ready for direct use with HuggingFace `transformers`/`trl` fine-tuning pipelines. Format: `{"prompt": "...", "completion": "..."}` instruction-response pairs.

---

## Test Data (`test/`)

**70 representative prompts** covering the full range of embedded task categories. Used for:
- **Eval 1** — Pre-trained vs. fine-tuned accuracy comparison (70 prompts)
- **Eval 2** — Prompt variation robustness (10 prompts × 3 paraphrases)
- **Eval 3** — Pass@k evaluation (k ∈ {1, 3, 5})

`test_set_70.json` includes the reference C code, model responses (base and fine-tuned), build results, and evaluation scores.

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
