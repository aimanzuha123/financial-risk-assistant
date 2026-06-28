# API Reference Documentation

Base URL: `http://localhost:8000/api`

Interactive Swagger Docs: `http://localhost:8000/docs`

---

## Datasets

### `POST /datasets/upload`
Upload a CSV portfolio file.

**Request:** `multipart/form-data` with `file` field (CSV only).

**Response:**
```json
{
  "id": 1,
  "name": "sample_portfolio",
  "rows": 253,
  "columns": 10,
  "numerical_columns": ["age", "income", "credit_score"],
  "categorical_columns": ["gender", "marital_status"],
  "target_column": "delinquent",
  "status": "uploaded"
}
```

### `GET /datasets`
List all uploaded datasets.

### `GET /datasets/{id}`
Get full metadata of a single dataset.

### `GET /datasets/{id}/preview?rows=20`
Return first N rows of the dataset for UI preview.

### `PUT /datasets/{id}/target?target_column=delinquent`
Set the delinquency/default target column.

### `DELETE /datasets/{id}`
Delete dataset and its file.

---

## EDA

### `POST /eda/{dataset_id}`
Run full automated EDA pipeline.

**Response:** JSON with fields:
- `summary` – row/column/memory counts
- `missing_values` – per-column missing details and imputation recommendations
- `duplicates` – count and percentage
- `outliers` – IQR bounds and outlier counts per column
- `correlation` – matrix and strong correlations list
- `distributions` – stats per column (mean, std, skew, kurtosis, normality)
- `risk_profile` – target class distribution and imbalance indicator
- `charts` – base64 encoded PNG images (keyed by chart type)
- `business_insights` – automated text insights list

---

## Predictions

### `POST /predictions/{dataset_id}/train`
Train Logistic Regression, Decision Tree, and Random Forest. Auto-selects best model.

**Response:**
```json
{
  "best_model": "random_forest",
  "best_model_name": "Random Forest",
  "best_score": 0.8423,
  "models": {
    "random_forest": {
      "model_name": "Random Forest",
      "metrics": { "accuracy": 0.84, "f1": 0.8423, "roc_auc": 0.91 },
      "feature_importance": { "credit_score": 0.32, "debt_to_income": 0.28 },
      "explanations": [...]
    }
  }
}
```

### `GET /predictions/{dataset_id}/results`
Retrieve stored prediction results.

---

## Reports

### `POST /reports/{dataset_id}/generate`
Generate executive business report with insights, segmentation, recommendations, and PDF.

**Response:**
```json
{
  "executive_summary": "...",
  "business_insights": "...",
  "recommendations": ["...", "..."],
  "financial_impact": "...",
  "pdf_path": "/path/to/report.pdf",
  "pdf_filename": "report_1_20260628.pdf"
}
```

### `GET /reports/{dataset_id}/download?pdf_path=...`
Download the generated PDF report.

---

## Collections Strategy

### `POST /collections/{dataset_id}/generate`
Generate AI-recommended collection actions for the entire portfolio.

### `GET /collections/{dataset_id}/actions`
Retrieve all collection actions for a dataset.

### `POST /collections/actions/{action_id}/approve?approved_by=analyst`
Approve a high-risk action that requires human review.

### `POST /collections/actions/{action_id}/feedback`
Submit collector interaction feedback — triggers the Agentic AI workflow.

**Request Body:**
```json
{
  "payment_amount": 500.00,
  "promise_to_pay": true,
  "notes": "Customer agreed to pay next Friday."
}
```

**Response:**
```json
{
  "action_id": 42,
  "old_risk_level": "high",
  "new_risk_level": "medium",
  "old_action": "phone_call",
  "new_action": "payment_plan",
  "new_risk_score": 0.45
}
```

---

## AI Chat Assistant

### `POST /chat`
Ask the AI assistant a natural language question with optional dataset context.

**Request Body:**
```json
{
  "message": "Why is customer CUST_00003 high risk?",
  "dataset_id": 1
}
```

**Response:**
```json
{
  "reply": "### Risk Explanation for Customer: CUST_00003\n...",
  "used_openai": false
}
```

---

## Settings & Responsible AI

### `GET /settings/sensitive-attributes/{dataset_id}`
Detect columns that could represent sensitive/protected attributes.

### `POST /settings/bias-check/{dataset_id}?sensitive_column=gender&privileged_group=Male&unprivileged_group=Female`
Compute fairness metrics (DIR, SPD, EOD) across protected groups.

**Response:**
```json
{
  "disparate_impact_ratio": 0.94,
  "statistical_parity_difference": -0.04,
  "equal_opportunity_difference": 0.02,
  "has_bias": false,
  "status": "fair",
  "interpretation": "Fair prediction output: Metrics fall within compliant thresholds."
}
```

### `GET /settings/audit-logs?dataset_id=1`
Retrieve all system audit trail entries.

---

## Health Check

### `GET /health`
Returns system status, app name, and version.
