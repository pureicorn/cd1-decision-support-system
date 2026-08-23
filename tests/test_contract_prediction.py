import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from contract_prediction import (  # noqa: E402
    FEATURE_COLUMNS,
    make_synthetic_modeling_data,
    out_of_fold_scores,
    train_and_evaluate,
)


def test_post_outcome_stage_is_not_a_feature():
    assert "Стадия работы с клиентом" not in FEATURE_COLUMNS


def test_model_trains_without_leakage():
    df = make_synthetic_modeling_data(400, seed=7)
    result = train_and_evaluate(df)
    assert 0.5 <= result.metrics["roc_auc"] <= 1.0
    assert set(result.feature_columns) == set(FEATURE_COLUMNS)


def test_out_of_fold_scores_are_between_zero_and_one():
    df = make_synthetic_modeling_data(300, seed=10)
    scores = out_of_fold_scores(df)
    assert len(scores) == len(df)
    assert scores["Вероятность заключения договора"].between(0, 1).all()
