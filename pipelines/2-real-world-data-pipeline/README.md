# Real-World Data Pipeline

Collects, validates, and tags real-world embedded C programs from GitHub repositories and educational resources, then generates natural language task descriptions using Gemini Flash 2.0.

---

## How It Works

**Step 1 — Raw File Collection**
Raw `.c` source files are placed in `raw-files/`. These are collected manually or via the GitHub REST API from public embedded systems repositories.

**Step 2 — Raspberry Pi Relevance Check**
`Prompting_code.py` reads each file and uses Gemini to determine whether the code is specifically designed for Raspberry Pi. Files that fail this check are saved to `raspberry_pi_invalid_data.json` for reference.

**Step 3 — Task Description Generation**
For each validated file, Gemini generates a detailed natural language prompt describing the program — including hardware requirements, software dependencies, and expected behavior.

**Step 4 — Variation Generation**
An improved/variation version of the code is generated with better structure, error handling, commenting, and variable naming. Saved to `raspberry_pi_variations_data.json`.

**Step 5 — Validation**
The same four-stage validation stack used in the synthetic pipeline is applied:

| Step | Check |
|---|---|
| 1 | C++ keyword filtering |
| 2 | Structural verification (`#include`, `main()`) |
| 3 | Library validation (allowed embedded C libraries) |
| 4 | Build command validation |

Validated examples are saved to `raspberry_pi_validated_data.json`.

---

## File Structure

```
2-real-world-data-pipeline/
├── raw-files/              # Raw .c source files collected from GitHub
├── Prompting_code.py              # Main processing script
├── Prompt_Fetch.ipynb             # Jupyter notebook version
├── prompts/
│   └── prompt_generator.py        # Generates task descriptions via Gemini
├── config/
│   ├── constants_rpi_standard.py  # Platform and library constants
│   ├── constants_rpi_pico.py      # Pico-specific constants
│   └── model.py                   # API keys and model config
├── api/
│   └── gemini_api.py              # Gemini API wrapper with key rotation
├── validation/
│   ├── validate.py                # Validation entry point
│   ├── validate_cpp_presence.py
│   ├── validate_illegal_libs.py
│   ├── validate_build_command.py
│   ├── validate_build_and_compile.py
│   └── validation_libraries.py
├── storage/
│   └── example_saver.py
├── utils/
│   └── formatting.py
├── raspberry_pi_validated_data.json    # Programs that passed validation
├── raspberry_pi_invalid_data.json      # Programs that failed (kept for reference)
└── raspberry_pi_variations_data.json   # Improved variation versions
```

---

## Configuration

Edit `config/model.py`:

```python
API_KEYS = [
    "YOUR_GEMINI_API_KEY_1",
    "YOUR_GEMINI_API_KEY_2",   # optional
]
```

---

## Run

```bash
cd pipelines/2-real-world-data-pipeline
python Prompting_code.py --input-dir "raw-files/"
```

Or use the notebook:
```bash
jupyter notebook Prompt_Fetch.ipynb
```

**Requirements:** Gemini API key set in `config/model.py`, Python 3.10+.
