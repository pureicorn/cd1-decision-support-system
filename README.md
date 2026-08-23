# CD1 — Decision Support System

[![Python CI](https://github.com/pureicorn/cd1-decision-support-system/actions/workflows/python-app.yml/badge.svg)](https://github.com/pureicorn/cd1-decision-support-system/actions/workflows/python-app.yml)

**Business Analytics · Data Mart · Queueing Theory · Optimization · Machine Learning · Power BI**

A portfolio prototype of a **data-driven decision-support system for customer service and sales management**.

The project combines operational analytics, KPI calculation, Data Mart design, queueing simulation, staff optimization, leakage-free client scoring and Power BI reporting into one analytical workflow.

> **Project status:** academic / portfolio prototype. The included business data is synthetic. Google Colab / Google Sheets were used in the original implementation.

---

## What problem does it solve?

The system is designed to help management answer four practical questions:

1. **What is happening with the business?**  
   Profit, sales, contracts and staffing KPIs.

2. **Is the service operation overloaded?**  
   Waiting time, queue length, abandonment and employee utilization.

3. **How many employees are needed?**  
   Simulation-based staffing recommendation.

4. **Which clients deserve priority?**  
   Contract-propensity scoring based only on information available before the outcome.

---

## Tech Stack

**Python · pandas · NumPy · scikit-learn · Jupyter · Power BI · Excel · GitHub Actions**

---

## End-to-end architecture

```text
                    ┌──────────────────────────┐
                    │ Synthetic / source data  │
                    │ Google Sheets / Excel    │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │   Data Mart / KPI layer  │
                    │ profit • sales •         │
                    │ contracts • staffing     │
                    └───────┬─────────┬────────┘
                            │         │
                ┌───────────┘         └──────────────┐
                ▼                                    ▼
     ┌──────────────────────┐             ┌──────────────────────┐
     │ Queueing simulation  │             │ Leakage-free ML      │
     │ M/M/m + patience     │             │ Random Forest        │
     └──────────┬───────────┘             └──────────┬───────────┘
                │                                    │
                ▼                                    ▼
     ┌──────────────────────┐             ┌──────────────────────┐
     │ Staff recommendation │             │ Client prioritizing  │
     │ + service metrics    │             │ / propensity score   │
     └──────────┬───────────┘             └──────────┬───────────┘
                └────────────────┬───────────────────┘
                                 ▼
                       ┌────────────────────────┐
                       │     Power BI report    │
                       │  management decisions  │
                       └────────────────────────┘
```

---

# Project Components

## 1. Data generation and scheduled updates

`legacy/01_data_generation_colab_export.py`

The original script creates the `ЦД1` Google Spreadsheet and populates four business datasets:

- **Деньги** — expenses and sales volume;
- **Сотрудники** — number of active employees and calls per hour;
- **Клиенты** — historical new / completed contracts;
- **Клиенты_компании** — synthetic company-client profiles.

It also configures APScheduler jobs for recurring updates.

The original Colab implementation is preserved under `legacy/` for traceability.

---

## 2. Data Mart and KPI layer

`notebooks/02_queueing_optimization_and_datamart.ipynb`

The notebook contains Data Mart logic, KPI aggregation and an optimization block. The business-logic workbook documents KPI definitions and scoring rules.

### Main modeled outputs

- monthly profit;
- sales volume;
- new and completed contracts;
- current contract count;
- modeled maximum / optimal sales volume;
- modeled maximum profit.

---

## 3. Queueing model and staff optimization

The analytical notebook contains an **M/M/m-style queueing simulation with limited customer patience**.

The model simulates incoming calls, service completion, queueing and customer abandonment across repeated replications.

### Main outputs

- current staffing;
- recommended staffing;
- calls per hour;
- utilization `ρ`;
- average waiting time;
- average queue length;
- abandonment probability;
- lost calls per hour.

The supplied portfolio dashboard contains a recommendation to increase staffing from **3 to 7 employees** under the modeled scenario.

---

# 4. Leakage-Free Client Scoring

`src/contract_prediction.py`

This is the corrected version of the original Random Forest client-scoring block.

The original implementation had a classic target-leakage problem: **`Стадия работы с клиентом`** was used both to define the target and as a model feature.

The corrected model follows a strict pre-outcome feature policy.

### Model features

- **Тип компании**
- **Прибыль компании-клиента**
- **Постоянный или новый клиент**
- **Потребность клиента в товаре**

`Стадия работы с клиентом` is treated as **post-outcome information** and is excluded from the predictive feature matrix.

### ML pipeline

```text
Pre-outcome client attributes
            │
            ▼
    Preprocessing pipeline
            │
            ▼
       Random Forest
            │
            ▼
    Contract propensity
```

### Model functionality

The module provides:

- hold-out evaluation;
- `accuracy`;
- `precision`;
- `recall`;
- `F1`;
- `ROC-AUC`;
- 5-fold out-of-fold scoring;
- scoring of new clients using only pre-outcome fields;
- reproducible synthetic modeling data.

### Synthetic benchmark result

Current local evaluation:

| Metric | Score |
|---|---:|
| Accuracy | 0.615 |
| Precision | 0.600 |
| Recall | 0.667 |
| F1 | 0.632 |
| ROC-AUC | 0.701 |

> These metrics are valid only for the included synthetic benchmark and should not be interpreted as real-world model performance.

A reproducible notebook is available at:

`notebooks/03_contract_prediction_leakage_free.ipynb`

---

# 5. Power BI Reporting

`dashboard/CD1_dashboard.pbix`

The report is represented by three business views:

### Management / CD1
Financial and sales KPIs.

### Client Scoring / CD2
Client contract probabilities and client composition.

### Call Center / CD3
Staffing, queueing, waiting, lost calls and staffing recommendation.

> **Important:** the PBIX file and screenshots are retained as the original visual prototype. The corrected ML methodology is implemented in `src/contract_prediction.py` and `notebooks/03_contract_prediction_leakage_free.ipynb`. The PBIX has not been silently presented as if its historical client scores were recalculated with the corrected methodology.

---

# Business Value

The project demonstrates a complete decision-support loop:

- **KPI analytics** tells management what is happening;
- **queueing theory** explains service-capacity problems;
- **optimization** supports resource decisions;
- **machine learning** supports client prioritization without post-outcome leakage;
- **Power BI** brings the analytical outputs into a management interface.

---

# ML Methodology: What Was Fixed?

The original prototype contained the following leakage pattern:

```text
Стадия работы с клиентом
        │
        ├──> defines target: Договор_заключен
        │
        └──> also used as a model feature
                    ▲
                    │
                 leakage
```

The corrected version uses:

```text
Pre-outcome client attributes
            │
            ▼
       Random Forest
            │
            ▼
      Contract propensity
```

The stage field may still exist in the raw business dataset, but it is explicitly excluded from the predictive feature matrix.

For the portfolio benchmark, the outcome is generated from pre-outcome attributes so that the notebook demonstrates a genuine predictive setup rather than simply learning a post-outcome label.

---

# Testing and CI

The repository includes automated tests and GitHub Actions CI.

Local test suite:

```bash
python -m pytest -q
```

Current test result:

```text
3 passed
```

Every push to `main` triggers the Python CI workflow.

The workflow:

1. checks out the repository;
2. sets up Python;
3. installs dependencies;
4. runs linting;
5. runs tests.

---

# Limitations

## Synthetic data

The supplied business data is generated / simulated rather than real corporate data.

The repository therefore demonstrates **methodology, analytics and engineering**, not real-world model validity.

## Model validation

The corrected notebook uses a hold-out test and out-of-fold predictions.

Reported metrics are only valid for the included synthetic benchmark.

## Google Colab dependency

The original scripts use Google authentication and Google Sheets.

Credentials are not stored in the repository.

## Power BI snapshot

The PBIX file is a portfolio visualization artifact from the original implementation.

Its historical client-scoring page should not be used as evidence of the corrected model's performance.

---

# Data and Artifacts

| Artifact | Purpose |
|---|---|
| `data/sample/CD1_source_data.xlsx` | Sample source dataset with money, staff, contracts and company-client data |
| `data/sample/CD1OV_analytics.xlsx` | Original normalized client data, model-result snapshot and SMO output |
| `data/sample/Data_Mart.xlsx` | Original Data Mart snapshot |
| `data/sample/Data_Mart_business_logic.xlsx` | Business definitions and KPI scoring logic |
| `data/sample/modeling_clients.csv` | Clean synthetic lead-level dataset for the leakage-free ML example |
| `data/sample/contract_scores_oof.csv` | Out-of-fold contract propensity scores |
| `dashboard/CD1_dashboard.pbix` | Power BI report snapshot from the original prototype |
| `dashboard/screenshots/` | Portfolio screenshots of the report |

---

# Power BI Preview

## Management Dashboard

![Management dashboard](dashboard/screenshots/01_management_dashboard.png)

## Client Scoring

![Client scoring dashboard](dashboard/screenshots/02_client_scoring_dashboard.png)

## Queueing / Staffing

![Queueing dashboard](dashboard/screenshots/03_queueing_dashboard.png)

---

# Quick Start

## 1. Clone the repository

```bash
git clone https://github.com/pureicorn/cd1-decision-support-system.git
cd cd1-decision-support-system
```

## 2. Create a virtual environment

```bash
python -m venv .venv
```

## 3. Activate the environment

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
.venv\Scriptsctivate
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Run the ML example

```bash
python src/contract_prediction.py
```

## 6. Run tests

```bash
python -m pytest -q
```

The original Google Colab workflow remains under:

`legacy/`

The queueing / Data Mart notebook remains under:

`notebooks/02_queueing_optimization_and_datamart.ipynb`

---

# Repository Map

```text
cd1-decision-support-system/
│
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
│
├── src/
│   ├── contract_prediction.py
│   └── README.md
│
├── tests/
│   └── test_contract_prediction.py
│
├── legacy/
│   ├── 01_data_generation_colab_export.py
│   └── 03_contract_prediction_colab_export.py
│
├── notebooks/
│   ├── 02_queueing_optimization_and_datamart.ipynb
│   └── 03_contract_prediction_leakage_free.ipynb
│
├── data/
│   └── sample/
│       ├── CD1_source_data.xlsx
│       ├── CD1OV_analytics.xlsx
│       ├── Data_Mart.xlsx
│       ├── Data_Mart_business_logic.xlsx
│       ├── modeling_clients.csv
│       └── contract_scores_oof.csv
│
├── dashboard/
│   ├── CD1_dashboard.pbix
│   └── screenshots/
│       ├── 01_management_dashboard.png
│       ├── 02_client_scoring_dashboard.png
│       └── 03_queueing_dashboard.png
│
└── docs/
    ├── ARCHITECTURE.md
    ├── DATA_DICTIONARY.md
    ├── ML_METHODOLOGY.md
    └── PORTFOLIO_NOTES.md
```

---

# Portfolio Positioning

> **A data-driven decision-support prototype for customer service and sales management, combining Data Mart design, KPI analytics, queueing simulation, optimization, leakage-free machine learning and BI reporting.**

### Relevant roles

**Business Analyst · Data Analyst · BI Analyst · Operations / Decision Science · Junior Data Scientist · Business Transformation Consultant**
