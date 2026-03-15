# Synthetic Fraud Dataset Generator

This project generates a synthetic transactional dataset for fraud detection research and model development using NVIDIA NeMo Data Designer.

## Overview

The main workflow is implemented as a Jupyter notebook: `synthetic_dataset_generator.ipynb`. It uses NeMo Data Designer to define a column schema, sampling distributions, and fraud logic.

The generator produces a realistic transactional dataset where fraud is introduced via:

- transaction amount discrepancies (billed vs true amount)
- unusual item quantity patterns compared to recent history
- a judge model that labels transactions as fraudulent or not

## Data Generation Logic

The notebook defines and samples the following columns:

- `timestamp`: realistic datetime distribution
- `transaction_id` / `customer_id`: UUIDs
- `transaction_total`: sampled transaction amount
- `merchant_category`, `payment_method`, `region`: categorical distributions
- `total_quantity`: total items in a transaction
- `anomaly_type`: determines whether to inject fraud types (quantity, total, both, none)
- `total_quantity_7d`: computed based on anomaly type (simulating recent history)
- `reported_transaction_total`: computed with possible fraud modification
- `fraud_analysis`: judged by an LLM judge model and turned into `is_fraud` + `reasoning`

## Output Files

The notebook writes the generated dataset to:

- `synthetic_dataset_output/synthetic_transactions.csv`

It also saves artifacts and analysis output in:

- `synthetic_dataset_output/synthetic_fraud_artifacts/`

## Setup and Usage

1. Create and activate a Python environment (recommended):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install the required dependencies (from the notebook environment):

   ```bash
   pip install -r requirements.txt
   ```

3. Configure required environment variables (example):

   ```powershell
   $env:NEMO_DATADESIGNER_BASE_URL = "https://<your-nemo-endpoint>"
   $env:MODEL_PROVIDER = "nvidia"
   $env:SYSTEM_PROMPT = "<your-system-prompt>"
   $env:STRUCTURE_MODEL_ID = "<structure-model-id>"
   $env:STRUCTURE_MODEL_ALIAS = "structure"
   $env:JUDGE_MODEL_ID = "<judge-model-id>"
   $env:JUDGE_MODEL_ALIAS = "judge"
   ```

4. Run the notebook in Jupyter or VS Code:
   - Open `synthetic_dataset_generator.ipynb`
   - Execute the cells top-to-bottom

## Next Steps

- Use `synthetic_dataset_output/synthetic_transactions.csv` for feature engineering and model training.
- Adjust the notebook’s sampler configurations and judge prompt to tune fraud patterns.

---

This notebook-based generator is intended for research, prototyping, and educational purposes.
