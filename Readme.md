# Synthetic Fraud Dataset Generator

This project generates a synthetic transactional dataset for fraud detection research and model development. The generated data simulates realistic user, item, and transaction behaviors, including fraudulent activity.

## Overview

The main script, `synthetic_dataset_gen.py`, creates several CSV files representing users, items, transactions, purchased items, transaction amounts, and fraud patterns. The data is designed to support feature engineering and machine learning experiments for fraud detection.

## Data Generation Logic

- **Users**: Each user has a unique ID, name, and age, randomly assigned within a realistic range.
- **Items**: Each item/product has a unique ID, name, and price, with prices sampled from a specified range.
- **Transactions**: Each transaction is linked to a user and timestamped within a two-year period.
- **Purchased Items**: For each transaction, a random set of items and quantities is selected to simulate a shopping cart.
- **Amounts**: The true amount for each transaction is calculated as the sum of item prices times quantities. The billed amount may be altered by a fraud multiplier to simulate over- or under-charging.
- **Fraud & Behavioral Logic**:
  - Fraud is simulated by randomly applying multipliers to the billed amount.
  - User behavior is modeled by assigning each user a historical average spending value and tracking transaction frequency.
  - Anomaly scores are computed based on billing anomalies, transaction frequency, and spending spikes.
- **Fraud Calculation**: Each transaction receives a fraud probability score based on the above features. Transactions with a score above a configurable threshold are labeled as fraudulent.

## Output Files

All generated CSVs are saved in the `frauds_dataset` folder:
- `users.csv`: List of users with demographic info.
- `items.csv`: List of items/products with prices.
- `transactions.csv`: Transaction records with user and timestamp.
- `purchased_items.csv`: Junction table of items and quantities per transaction.
- `transaction_amounts.csv`: True and billed amounts per transaction.
- `fraud_patterns.csv`: Fraud indicator and risk score per transaction.

## Customization

You can adjust dataset size, fraud rates, price ranges, and other parameters by editing the constants at the top of `synthetic_dataset_gen.py`.

## Usage

1. Install Python dependencies:
   ```
   pip install pandas numpy scikit-learn
   ```
2. Run the generator:
   ```
   python synthetic_dataset_gen.py
   ```
3. The generated CSVs will be available in the `frauds_dataset` directory.

## Next Steps

- Use the generated CSVs for feature engineering and model training in a separate notebook or script.
- See the code comments in `synthetic_dataset_gen.py` for detailed explanations of each step.

---
This generator is intended for research, prototyping, and educational purposes.
