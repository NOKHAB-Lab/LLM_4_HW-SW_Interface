# Fine-Tuning Scripts

QLoRA fine-tuning notebooks for all five open-source models evaluated in the paper. Each model folder contains a `training/` subfolder with Jupyter notebooks covering both training and inference.

---

## Models

| Folder | Model | Role in Paper |
|--------|-------|---------------|
| `codellama-7b/` | CodeLLaMA-7B-HF | Evaluated (pre-trained → fine-tuned) |
| `mistral-7b/` | Mistral-7B-Instruct-v0.3 | Evaluated (pre-trained → fine-tuned) |
| `starcoder2-7b/` | StarCoder2-7B | Evaluated (pre-trained → fine-tuned) |
| `deepseek-coder-6.7b/` | DeepSeek-Coder-6.7B-Instruct | Evaluated — best accuracy (90.05%) |
| `qwen2.5-7b/` | Qwen2.5-7B-Instruct | Evaluated (pre-trained → fine-tuned) |

---

## Fine-Tuning Configuration (QLoRA)

All models were fine-tuned using **QLoRA** (4-bit NF4 quantization + BF16 compute) via HuggingFace `SFTTrainer` (TRL + PEFT) on dual **NVIDIA H100 80GB GPUs**.

| Model | LoRA r/α | Learning Rate | Epochs | Optimizer | Scheduler |
|-------|----------|---------------|--------|-----------|-----------|
| CodeLLaMA-7B-HF | 16 / 32 | 2e-4 | 3 | adamw_torch | cosine |
| Mistral-7B-Instruct-v0.3 | 16 / 32 | 2e-5 | 3 | paged_adamw_32bit | cosine |
| StarCoder2-7B | 16 / 32 | 2e-4 | 3 | adamw_torch | cosine |
| DeepSeek-Coder-6.7B-Instruct | 16 / 32 | 2e-5 | 3 | paged_adamw_32bit | linear |
| Qwen2.5-7B-Instruct | 16 / 32 | 1e-4 | 3 | paged_adamw_32bit | cosine |

**Common settings:**
- Sequence length: 6,000 tokens
- Batch size: 2 per device, gradient accumulation: 4 steps
- Validation split: 10% held out; early stopping on validation loss
- Training dataset: `dataset/training/training_set.jsonl`

---

## How to Run

1. Open the notebook for your chosen model in JupyterLab or VS Code.
2. Set your HuggingFace token and model path in the notebook's config cell.
3. Run all cells — the notebook handles training, checkpoint saving, and inference on the test set.
4. The inference output (model responses to the 70-prompt test set) is saved as a JSON file.
5. Pass that JSON file to `evaluation/validation-pipeline/` to score the outputs.

---

## Workflow Position

```
dataset/training/  →  fine-tuning/<model>/training/  →  evaluation/validation-pipeline/
  (training data)        (QLoRA fine-tune + inference)      (score generated code)
```
