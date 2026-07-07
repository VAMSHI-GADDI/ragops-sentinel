from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
from typing import Any

from ragops.fine_tuning.failure_router_dataset import (
    load_failure_router_dataset,
    to_instruction_tuning_record,
)


@dataclass(frozen=True)
class LoRATrainingConfig:
    base_model: str = "distilgpt2"
    dataset_path: str = "data/fine_tuning/failure_router_train.jsonl"
    output_dir: str = "models/failure_router_lora"
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    learning_rate: float = 2e-4
    num_train_epochs: int = 1
    per_device_train_batch_size: int = 1
    max_length: int = 512


def prepare_instruction_records(dataset_path: str | Path) -> list[dict[str, str]]:
    examples = load_failure_router_dataset(dataset_path)
    return [to_instruction_tuning_record(example) for example in examples]


def write_instruction_records(
    *,
    dataset_path: str | Path,
    output_path: str | Path,
) -> Path:
    records = prepare_instruction_records(dataset_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    return output


def build_training_plan(config: LoRATrainingConfig) -> dict[str, Any]:
    records = prepare_instruction_records(config.dataset_path)

    return {
        "milestone": "M15_LORA_PEFT_FINE_TUNING_READY_WORKFLOW",
        "base_model": config.base_model,
        "dataset_path": config.dataset_path,
        "output_dir": config.output_dir,
        "example_count": len(records),
        "method": "LoRA / PEFT",
        "lora_config": {
            "r": config.lora_r,
            "lora_alpha": config.lora_alpha,
            "lora_dropout": config.lora_dropout,
            "target_modules": ["c_attn", "c_proj"],
        },
        "training_arguments": {
            "learning_rate": config.learning_rate,
            "num_train_epochs": config.num_train_epochs,
            "per_device_train_batch_size": config.per_device_train_batch_size,
            "max_length": config.max_length,
        },
        "ci_safe": True,
        "live_training_executed": False,
    }


def train_lora_failure_router(config: LoRATrainingConfig) -> dict[str, Any]:
    """Run LoRA/PEFT fine-tuning.

    This function is intentionally isolated from CI. It imports heavy optional
    dependencies only when called. The default repository validation checks the
    dataset and training plan, but does not train a model.
    """
    try:
        from datasets import Dataset
        from peft import LoraConfig, TaskType, get_peft_model
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            DataCollatorForLanguageModeling,
            Trainer,
            TrainingArguments,
        )
    except ImportError as exc:
        raise RuntimeError(
            "Fine-tuning requires optional dependencies from requirements-finetuning.txt"
        ) from exc

    records = prepare_instruction_records(config.dataset_path)
    dataset = Dataset.from_list(
        [
            {
                "text": f"Instruction:\n{record['instruction']}\n\nResponse:\n{record['response']}"
            }
            for record in records
        ]
    )

    tokenizer = AutoTokenizer.from_pretrained(config.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def tokenize(batch: dict[str, list[str]]) -> dict[str, Any]:
        return tokenizer(
            batch["text"],
            truncation=True,
            padding="max_length",
            max_length=config.max_length,
        )

    tokenized = dataset.map(tokenize, batched=True)

    model = AutoModelForCausalLM.from_pretrained(config.base_model)

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=["c_attn", "c_proj"],
    )

    model = get_peft_model(model, lora_config)

    training_args = TrainingArguments(
        output_dir=config.output_dir,
        learning_rate=config.learning_rate,
        num_train_epochs=config.num_train_epochs,
        per_device_train_batch_size=config.per_device_train_batch_size,
        logging_steps=1,
        save_strategy="epoch",
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
    )

    trainer.train()
    model.save_pretrained(config.output_dir)
    tokenizer.save_pretrained(config.output_dir)

    return {
        **build_training_plan(config),
        "live_training_executed": True,
        "adapter_saved": True,
    }


def write_training_plan(
    *,
    config: LoRATrainingConfig,
    output_path: str | Path,
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build_training_plan(config), indent=2), encoding="utf-8")
    return output


def config_to_dict(config: LoRATrainingConfig) -> dict[str, Any]:
    return asdict(config)
