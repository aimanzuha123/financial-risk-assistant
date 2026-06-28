"""
Mock Data Generator
Generates a realistic mock credit portfolio CSV dataset with missing values,
imbalanced target, sensitive categories, and outliers for demonstration.
"""
import os
import random
import pandas as pd
import numpy as np

def generate_data(output_path: str, n_samples: int = 250):
    np.random.seed(42)
    random.seed(42)

    data = []
    for i in range(n_samples):
        cust_id = f"CUST_{i+1:05d}"
        
        # Demographic sensitive features
        age = int(np.random.normal(42, 12))
        age = max(18, min(80, age))
        gender = random.choices(["Male", "Female"], weights=[0.48, 0.52])[0]
        marital = random.choices(["Married", "Single", "Divorced"], weights=[0.6, 0.3, 0.1])[0]

        # Financial variables
        income = float(np.random.lognormal(10.8, 0.5))
        income = max(15000.0, min(250000.0, income))
        
        credit_score = int(np.random.normal(680, 75))
        credit_score = max(350, min(850, credit_score))

        # Risk parameters
        debt_to_income = float(np.random.beta(2, 5) * 0.8)
        
        # Delinquency variables
        # Correlate days past due with credit score, DTI
        dpd_prob = 0.05
        if credit_score < 580:
            dpd_prob += 0.35
        if debt_to_income > 0.45:
            dpd_prob += 0.20
            
        dpd = 0
        if random.random() < dpd_prob:
            dpd = int(np.random.exponential(45))
            dpd = min(120, max(1, dpd))

        balance = float(np.random.exponential(12000))
        balance = max(100.0, min(80000.0, balance))

        # Class label: default (1 = delinquent/default, 0 = non-delinquent)
        default_prob = 0.02
        if dpd > 30:
            default_prob += 0.60
        if credit_score < 500:
            default_prob += 0.25
        if debt_to_income > 0.50:
            default_prob += 0.10

        default = 1 if random.random() < default_prob else 0

        # Inject some missing values (PII or standard cols)
        # 3% missing in income
        if random.random() < 0.03:
            income = np.nan
        # 2% missing in credit_score
        if random.random() < 0.02:
            credit_score = np.nan

        data.append({
            "customer_id": cust_id,
            "age": age,
            "gender": gender,
            "marital_status": marital,
            "annual_income": income,
            "credit_score": credit_score,
            "debt_to_income": debt_to_income,
            "days_past_due": dpd,
            "outstanding_balance": balance,
            "delinquent": default
        })

    df = pd.DataFrame(data)
    
    # Introduce 3 duplicate rows
    dups = df.sample(3, random_state=42)
    df = pd.concat([df, dups], ignore_index=True)

    df.to_csv(output_path, index=False)
    print(f"Mock dataset generated successfully with {len(df)} rows at {output_path}")

if __name__ == "__main__":
    dest = os.path.join(os.path.dirname(__file__), "..", "data", "uploads", "sample_portfolio.csv")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    generate_data(dest)
