# Synthetic Data Pipeline

Automated pipeline for generating large-scale, compiler-validated C programs for Raspberry Pi embedded systems. Supports both standard Raspberry Pi models (3B+, Zero W, 4B, 5) and Raspberry Pi Pico.

---

## How It Works

The pipeline runs in three stages per example:

**Stage 1 — Base Prompt Generation**
`prompts/prompt_generator.py` calls the Gemini API to generate a natural language task description for a given sensor/actuator category and subcategory, targeting a specific Pi model and use context.

**Stage 2 — Prompt Enrichment**
The base prompt is enriched with library constraints (wiringPi, pigpio, bcm2835, sysfs), error handling requirements, code style, complexity level, and OS compatibility rules (Raspberry Pi OS Bookworm/Bullseye).

**Stage 3 — Code Synthesis + Validation**
The enriched prompt is sent back to Gemini to generate the full C program. The generated code goes through four validation checks before being saved:

| Step | Check |
|---|---|
| 1 | C++ keyword filtering (`class`, `namespace`, `template`, etc.) |
| 2 | Structural verification (`#include`, `main()`, minimum length, comments) |
| 3 | Library validation (whitelist of allowed embedded C libraries) |
| 4 | Build command validation (rejects C++ compiler flags) |

If validation fails, the failure reason is appended to the prompt and the generation retries (up to `MAX_RETRIES` attempts).

---

## File Structure

```
1-synthetic-data-pipeline/
├── task_generator/
│   └── task_manager.py          # Orchestrates the full pipeline
├── prompts/
│   └── prompt_generator.py      # Two-stage prompt generation (base + enrichment)
├── config/
│   ├── constants_rpi_standard.py  # Categories, Pi models, styles for standard Pi
│   ├── constants_rpi_pico.py      # Categories and configs for Raspberry Pi Pico
│   └── model.py                   # API keys, retry config, RPI_PICO flag
├── api/
│   └── gemini_api.py              # Gemini API wrapper with key rotation
├── validation/
│   ├── validate.py                # Unified validation entry point
│   ├── validate_cpp_presence.py   # C++ element detection
│   ├── validate_illegal_libs.py   # Restricted header/library checker
│   ├── validate_build_command.py  # Build command validator
│   ├── validate_build_and_compile.py  # GCC compilation check
│   └── validation_libraries.py    # Allowed library whitelist
├── storage/
│   └── example_saver.py           # Saves validated examples to JSON
├── utils/
│   └── formatting.py              # JSON/code extraction utilities
└── install_all_deps.sh            # Dependency installer
```

---

## Configuration

Edit `config/model.py` before running:

```python
API_KEYS = [
    "YOUR_GEMINI_API_KEY_1",
    "YOUR_GEMINI_API_KEY_2",   # optional, for key rotation
]
RPI_PICO = False   # Set to True to generate Raspberry Pi Pico examples
MAX_RETRIES = 3
```

Edit `config/constants_rpi_standard.py` to control:
- `CATEGORIES` — sensor/actuator subcategory lists
- `PI_MODELS` — target hardware
- `COMPLEXITY_LEVELS`, `CODE_STYLES`, `USE_CONTEXTS` — variation parameters
- `PHASE_WEIGHTS` — category sampling weights

---

## Output Format

Each saved example (JSON) contains:

```json
{
  "category":     "High-level task category",
  "input":        "Natural language task description",
  "output":       "Validated C source code",
  "explanation":  "2-3 line description of the code",
  "tags":         "Raspberry Pi, C, GPIO, ...",
  "file-name":    "suggested_filename.c",
  "build-command": "gcc -o output input.c -lwiringPi"
}
```

For Raspberry Pi Pico, `build-command` is replaced with `cmakelists` (CMakeLists.txt content).

---

## Run

```bash
cd pipelines/1-synthetic-data-pipeline
pip install -r ../install_all_deps.sh   # or: bash install_all_deps.sh
python task_generator/task_manager.py
```

**Requirements:** Gemini API key set in `config/model.py`, Python 3.10+, GCC toolchain.
