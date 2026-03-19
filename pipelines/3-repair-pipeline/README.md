# Repair Pipeline

Iterative code repair loop that takes generated C programs which failed validation, feeds the GCC compiler error messages back to Gemini, and re-generates corrected code. Used during synthetic data construction to recover examples that failed on the first generation attempt.

---

## How It Works

For each failed example, the pipeline:

1. **Packages the failure context** — bundles the original prompt, the broken code, the syntax error, and the build error into a JSON object
2. **Sends to Gemini with repair instructions** — asks the model to fix the code while respecting the same library and language constraints as generation (C only, standard Pi libraries, no deprecated APIs)
3. **Validates the repaired code** — applies the same four-stage validation stack as the synthetic pipeline
4. **Corrects headers** — `validation/correct_headers.py` replaces any incorrect or deprecated include directives
5. **Retries on failure** — up to `MAX_RETRIES` attempts, with the updated failure reason appended each time

---

## File Structure

```
4-repair-pipeline/
├── task_generator/
│   └── task_manager.py          # Orchestrates the repair loop
├── api/
│   └── gemini_api.py            # Gemini API wrapper with key rotation
├── config/
│   └── model.py                 # API keys, retry config, RPI_PICO flag
├── validation/
│   ├── validate.py              # Unified validation entry point
│   ├── correct_headers.py       # Replaces incorrect/deprecated headers
│   ├── validate_cpp_presence.py
│   ├── validate_illegal_libs.py
│   ├── validate_build_command.py
│   ├── validate_build_and_compile.py
│   └── validation_libraries.py
├── storage/
│   └── example_saver.py         # Saves repaired examples to JSON
├── utils/
│   └── formatting.py
└── Prompt_Fetch.ipynb           # Notebook version
```

---

## Input Format

The pipeline expects a JSON array of failed examples, each containing:

```json
{
  "id":           "example identifier",
  "input":        "original natural language prompt",
  "output":       "broken C source code",
  "file-name":    "suggested filename",
  "build-command": "gcc compile command",
  "syntax_error": "syntax check error message",
  "build_error":  "GCC build error message"
}
```

---

## Configuration

Edit `config/model.py`:

```python
API_KEYS = [
    "YOUR_GEMINI_API_KEY_1",
    "YOUR_GEMINI_API_KEY_2",   # optional
]
RPI_PICO   = False   # Set True for Raspberry Pi Pico examples
MAX_RETRIES = 3
```

---

## Run

```bash
cd pipelines/4-repair-pipeline
python task_generator/task_manager.py
```

**Requirements:** Gemini API key in `config/model.py`, Python 3.10+, GCC toolchain.
