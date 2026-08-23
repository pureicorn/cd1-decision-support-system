# Power BI dashboard

`CD1_dashboard.pbix` is the supplied Power BI prototype with three business views:

1. management KPIs;
2. client scoring;
3. call-center / queueing analysis.

The screenshots are retained because they document the original project result.

## ML note

The client-scoring page in this PBIX is a snapshot from the original prototype. The original scoring implementation contained target leakage by using the current work stage both to construct the label and as a model feature.

The corrected methodology is implemented separately in:

- `../src/contract_prediction.py`
- `../notebooks/03_contract_prediction_leakage_free.ipynb`

This separation is intentional: the repository does not imply that the old PBIX probabilities were silently recalculated with the new methodology.
