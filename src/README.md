# Source code

## `contract_prediction.py`

Leakage-free Random Forest client scoring.

The module is intentionally independent of Google Colab / Google Sheets so that it can be reproduced locally.

### Main functions

- `make_synthetic_modeling_data()` — reproducible benchmark data;
- `build_pipeline()` — preprocessing + Random Forest;
- `train_and_evaluate()` — hold-out validation;
- `out_of_fold_scores()` — honest client-level score table;
- `score_new_clients()` — scoring of new leads using pre-outcome fields only.

The historical Colab exports remain in `../legacy/` for traceability.
