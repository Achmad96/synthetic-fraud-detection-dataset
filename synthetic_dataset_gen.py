import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

from faker import Faker
from faker.providers import company

OUTPUT_FOLDER = 'frauds_dataset'
RANDOM_SEED = 42
N_TRANSACTIONS = 10 
N_CUSTOMERS = 3 
N_ITEMS = 25
AGE_MIN = 18
AGE_MAX = 80
PRICE_MIN = 10000
PRICE_MAX = 200000
CART_SIZE_MIN = 1
CART_SIZE_MAX = 10
QUANTITY_MIN = 1
QUANTITY_MAX = 50
USER_HISTORY_MIN = 50000
USER_HISTORY_MAX = 150000
FRAUD_MULTIPLIERS = [1.11, 1.5, 0.8]
FRAUD_MULTIPLIER_PROBS = [0.80, 0.10, 0.10]
FRAUD_THRESHOLD = 0.75
TIMEZONE = 'Asia/Jakarta'

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
np.random.seed(RANDOM_SEED)

scaler = MinMaxScaler()

fake = Faker()
fake.add_provider(company)

# Users
customer_ids = np.arange(1000, 1000 + N_CUSTOMERS)
df_users = pd.DataFrame({
    'UserID': customer_ids,
    'Name': [fake.name() for _ in customer_ids],
    'Age': np.random.randint(AGE_MIN, AGE_MAX, size=N_CUSTOMERS)
})

# Items
item_ids = np.arange(500, 500 + N_ITEMS)
item_prices = np.random.randint(PRICE_MIN, PRICE_MAX, size=N_ITEMS)
item_price_map = dict(zip(item_ids, item_prices))
df_items = pd.DataFrame({
    'ItemID': item_ids,
    'ItemName': [fake.random_company_product() for _ in item_ids],
    'Price': item_prices
})

# Transactions
np.random.seed(None)
transaction_ids = np.arange(1, N_TRANSACTIONS + 1)
transaction_user_ids = np.random.choice(customer_ids, size=N_TRANSACTIONS)
timestamps = pd.date_range(start='2024-01-01', end='2026-01-01', periods=N_TRANSACTIONS).tz_localize(TIMEZONE)
df_transactions = pd.DataFrame({
    'TransactionID': transaction_ids,
    'UserID': transaction_user_ids,
    'Timestamp': timestamps
})

# Purchased Items
n_items_in_cart = np.random.randint(CART_SIZE_MIN, CART_SIZE_MAX, size=N_TRANSACTIONS)
cart_transaction_ids = np.repeat(transaction_ids, n_items_in_cart)
cart_item_ids = np.concatenate([
    np.random.choice(item_ids, size=n, replace=False) for n in n_items_in_cart
])
cart_quantities = np.random.randint(QUANTITY_MIN, QUANTITY_MAX, size=cart_item_ids.shape[0])
df_purchased_items = pd.DataFrame({
    'TransactionID': cart_transaction_ids,
    'ItemID': cart_item_ids,
    'Quantity': cart_quantities
})

df_purchased_items['LineTotal'] = (
    df_purchased_items['ItemID'].map(item_price_map) * df_purchased_items['Quantity'] # type: ignore
)
true_amounts = (
    df_purchased_items.groupby('TransactionID')['LineTotal']
    .values
    .sum()
    .reindex(list(transaction_ids), fill_value=0).astype(float)
)
billed_amounts = true_amounts * np.random.choice(
    FRAUD_MULTIPLIERS, size=N_TRANSACTIONS, p=FRAUD_MULTIPLIER_PROBS
)

user_freq = pd.Series(transaction_user_ids).value_counts()
user_history_avg = np.random.uniform(USER_HISTORY_MIN, USER_HISTORY_MAX, size=N_CUSTOMERS)
user_history_avg_map = dict(zip(customer_ids, user_history_avg))
freq_scores = np.array([user_freq.get(uid, 0) for uid in transaction_user_ids])
spikes = np.array([
    billed_amounts[i] / user_history_avg_map[transaction_user_ids[i]]
    for i in range(N_TRANSACTIONS)
])

# Fraud Calculation
# Calculate fraud probability based on billing anomaly, frequency, and spending spike
billing_anomaly = (billed_amounts != true_amounts * FRAUD_MULTIPLIERS[0]) * 0.4
frequency_score = scaler.fit_transform(freq_scores.reshape(-1, 1)).flatten() * 0.3
spike_score = np.clip(spikes / 5, 0, 1) * 0.3
fraud_prob = billing_anomaly + frequency_score + spike_score
fraud_prob = np.clip(fraud_prob + np.random.normal(0, 0.05, N_TRANSACTIONS), 0, 1)
fraud_indicators = (fraud_prob > FRAUD_THRESHOLD).astype(int)

df_fraud_patterns = pd.DataFrame({
    'TransactionID': transaction_ids,
    'FraudIndicator': fraud_indicators,
    'RiskScore': fraud_prob
})

df_transaction_amounts = pd.DataFrame({
    'TransactionID': transaction_ids,
    'TotalAmount': billed_amounts
})

dataframes_and_files = [
    (df_users, 'users.csv'),
    (df_items, 'items.csv'),
    (df_transactions, 'transactions.csv'),
    (df_transaction_amounts, 'transaction_amounts.csv'),
    (df_purchased_items, 'purchased_items.csv'),
    (df_fraud_patterns, 'fraud_patterns.csv'),
]

for df, filename in dataframes_and_files:
    df.to_csv(os.path.join(OUTPUT_FOLDER, filename), index=False)

fraud_rate = fraud_indicators.mean()
print(f"Dataset Built! Fraud Rate: {fraud_rate:.2%}")
