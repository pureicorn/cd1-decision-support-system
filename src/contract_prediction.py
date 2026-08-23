"""Leakage-free client contract scoring for the CD1 portfolio project.

The original prototype used the client's current work stage both to define the
label and as a model feature. This module deliberately excludes the work stage
from the feature set and requires a target column that is defined at the
prediction point.

For the portfolio demo, ``make_synthetic_modeling_data`` creates a synthetic
lead-level dataset where the contract outcome is generated from pre-outcome
client characteristics. This makes the example reproducible without claiming
that the supplied historical workbook contains real predictive labels.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


FEATURE_COLUMNS = [
    "Тип компании",
    "Прибыль компании-клиента",
    "Постоянный или новый клиент",
    "Потребность клиента в товаре",
]
CATEGORICAL_COLUMNS = [
    "Тип компании",
    "Постоянный или новый клиент",
    "Потребность клиента в товаре",
]
NUMERIC_COLUMNS = ["Прибыль компании-клиента"]


@dataclass(frozen=True)
class ModelResult:
    """Container for a trained model and hold-out evaluation metrics."""

    pipeline: Pipeline
    metrics: dict[str, float]
    feature_columns: list[str]


def _sigmoid(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, -30, 30)
    return 1.0 / (1.0 + np.exp(-x))


def make_synthetic_modeling_data(n_clients: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Create a clean synthetic lead-scoring dataset.

    The target is generated from variables that are available before the
    contract outcome. ``Стадия работы с клиентом`` is generated afterwards
    and is intentionally *not* used as a model feature.
    """

    if n_clients < 100:
        raise ValueError("n_clients must be at least 100")

    rng = np.random.default_rng(seed)
    company_types = np.array(
        ["Маркетинг", "Строительство", "Финансы", "Продажи", "Консалтинг", "Торговля", "Ритейл"]
    )
    client_statuses = np.array(["Постоянный", "Новый"])
    needs = np.array(
        ["Нет потребности", "Низкая потребность", "Средняя потребность", "Высокая потребность", "Срочная потребность"]
    )

    company = rng.choice(company_types, n_clients)
    status = rng.choice(client_statuses, n_clients, p=[0.78, 0.22])
    profit = rng.integers(150_000, 20_000_000, n_clients)
    need = rng.choice(needs, n_clients, p=[0.08, 0.14, 0.27, 0.32, 0.19])

    company_effect = {
        "Маркетинг": 0.00,
        "Строительство": 0.40,
        "Финансы": 0.10,
        "Продажи": 0.25,
        "Консалтинг": -0.05,
        "Торговля": 0.35,
        "Ритейл": 0.50,
    }
    need_effect = {
        "Нет потребности": -1.80,
        "Низкая потребность": -0.70,
        "Средняя потребность": 0.00,
        "Высокая потребность": 0.85,
        "Срочная потребность": 1.25,
    }

    logit = (
        -1.70
        + np.array([company_effect[x] for x in company])
        + np.array([need_effect[x] for x in need])
        + np.where(status == "Постоянный", 0.85, -0.10)
        + np.clip((profit - 5_000_000) / 8_000_000, -0.7, 1.2)
        + rng.normal(0, 0.45, n_clients)
    )
    probability = _sigmoid(logit)
    outcome = rng.binomial(1, probability)

    # Post-outcome field: intentionally excluded from the feature set.
    stage = np.where(
        outcome == 1,
        "Договор заключен",
        rng.choice(["Холодный звонок", "Работа над договором", "Договор расторгнут"], n_clients, p=[0.45, 0.40, 0.15]),
    )

    return pd.DataFrame(
        {
            "ID клиента": np.arange(1, n_clients + 1),
            "Тип компании": company,
            "Прибыль компании-клиента": profit,
            "Постоянный или новый клиент": status,
            "Потребность клиента в товаре": need,
            "Договор_заключен": outcome,
            "Стадия работы с клиентом": stage,
        }
    )


def build_pipeline(random_state: int = 42) -> Pipeline:
    """Build the preprocessing + Random Forest pipeline."""

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLUMNS),
            ("numeric", "passthrough", NUMERIC_COLUMNS),
        ],
        remainder="drop",
    )

    classifier = RandomForestClassifier(
        n_estimators=300,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def validate_dataset(df: pd.DataFrame, target_column: str = "Договор_заключен") -> None:
    """Validate that the modeling dataset contains only pre-outcome features."""

    missing = [column for column in FEATURE_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing modeling columns: {missing}")
    if target_column not in df.columns:
        raise ValueError(
            f"Target column '{target_column}' is missing. Define the outcome at the prediction point; "
            "do not derive it inside the feature matrix from a post-outcome field."
        )
    target = pd.to_numeric(df[target_column], errors="coerce")
    if target.isna().any() or not set(target.astype(int).unique()).issubset({0, 1}):
        raise ValueError(f"Target '{target_column}' must contain only 0/1 values.")
    if "Стадия работы с клиентом" in FEATURE_COLUMNS:
        raise AssertionError("Post-outcome stage must never be a model feature.")


def train_and_evaluate(
    df: pd.DataFrame,
    target_column: str = "Договор_заключен",
    test_size: float = 0.2,
    random_state: int = 42,
) -> ModelResult:
    """Train on a hold-out split and return honest evaluation metrics."""

    validate_dataset(df, target_column)
    X = df[FEATURE_COLUMNS].copy()
    y = pd.to_numeric(df[target_column], errors="raise").astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    pipeline = build_pipeline(random_state)
    pipeline.fit(X_train, y_train)
    probabilities = pipeline.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.50).astype(int)

    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
    }
    return ModelResult(pipeline=pipeline, metrics=metrics, feature_columns=FEATURE_COLUMNS.copy())


def out_of_fold_scores(
    df: pd.DataFrame,
    target_column: str = "Договор_заключен",
    folds: int = 5,
    random_state: int = 42,
) -> pd.DataFrame:
    """Return out-of-fold probabilities for an honest client-level score table."""

    validate_dataset(df, target_column)
    X = df[FEATURE_COLUMNS].copy()
    y = pd.to_numeric(df[target_column], errors="raise").astype(int)
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=random_state)

    model = build_pipeline(random_state)
    probabilities = cross_val_predict(model, X, y, cv=cv, method="predict_proba", n_jobs=1)[:, 1]

    result = df[["ID клиента"]].copy() if "ID клиента" in df.columns else pd.DataFrame(index=df.index)
    result["Вероятность заключения договора"] = probabilities
    result["Вероятность заключения договора, %"] = (probabilities * 100).round(1)
    return result


def score_new_clients(model: Pipeline, df_clients: pd.DataFrame) -> pd.DataFrame:
    """Score new clients using only information available before the outcome."""

    missing = [column for column in FEATURE_COLUMNS if column not in df_clients.columns]
    if missing:
        raise ValueError(f"Missing client scoring columns: {missing}")

    result = df_clients[["ID клиента"]].copy() if "ID клиента" in df_clients.columns else pd.DataFrame(index=df_clients.index)
    probabilities = model.predict_proba(df_clients[FEATURE_COLUMNS])[:, 1]
    result["Вероятность заключения договора"] = probabilities
    result["Вероятность заключения договора, %"] = (probabilities * 100).round(1)
    return result.sort_values("Вероятность заключения договора", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    dataset = make_synthetic_modeling_data(n_clients=1000, seed=42)
    result = train_and_evaluate(dataset)
    print("Leakage-free Random Forest evaluation")
    for name, value in result.metrics.items():
        print(f"{name:>10}: {value:.3f}")
    scores = out_of_fold_scores(dataset)
    print("\nTop 10 clients:")
    print(scores.sort_values("Вероятность заключения договора", ascending=False).head(10).to_string(index=False))
