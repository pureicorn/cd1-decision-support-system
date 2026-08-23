# Portfolio notes

## What to say in an interview

**Business problem:** management needs an integrated view of financial / sales performance, service capacity and client prioritization.

**What I built:** a prototype decision-support pipeline combining a Data Mart, queueing simulation, linear optimization, leakage-free Random Forest scoring and Power BI.

**Why the queueing model matters:** it converts operational call-center data into a staffing recommendation instead of showing only descriptive charts.

**Why the ML block matters:** it adds a prioritization layer for sales work using only information available before the outcome.

**Why the Data Mart matters:** it turns raw operational records into consistent business indicators that can feed dashboards and downstream analytical models.

## How to discuss the original implementation

The repository preserves the original Colab exports in `legacy/` for traceability. The original ML prototype had target leakage because the current work stage was used to define the label and was also included as a feature. The portfolio version fixes the methodology in `src/contract_prediction.py`.

## Claims to avoid

Do not describe the synthetic data as company data.

Do not describe the synthetic benchmark metrics as validated production performance.

Do not claim that the supplied PBIX has been recalculated with the corrected ML model.

## Strong portfolio keywords

Business Analysis · Data Analytics · Data Mart · KPI Design · Queueing Theory · Operations Research · Linear Programming · Machine Learning · Random Forest · Power BI · Process Automation · Decision Support System
