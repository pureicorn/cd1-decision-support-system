# Leakage-free ML methodology

## Problem

Estimate a client's probability of contract conclusion using information available at the moment a lead is being evaluated.

## Previous prototype problem

The previous implementation constructed the label from `Стадия работы с клиентом` and also encoded that column as a model feature. That is target leakage because the feature contains information about the outcome itself. The original code explicitly sets the target from the work stage.

## Corrected feature set

The model uses only:

- `Тип компании`
- `Прибыль компании-клиента`
- `Постоянный или новый клиент`
- `Потребность клиента в товаре`

The current work stage is never used as an input to the classifier.

## Corrected target

For the portfolio benchmark, the target `Договор_заключен` is generated from pre-outcome variables in `make_synthetic_modeling_data`. The raw stage is generated afterwards as a business-state field.

This creates a clean demonstration of the modeling workflow without pretending that the source workbook contains real labels from a prediction point.

## Validation

The module reports:

- Accuracy
- Precision
- Recall
- F1
- ROC-AUC

The repository also includes out-of-fold probabilities, which are preferred over in-sample probabilities when creating a portfolio score table for the benchmark dataset.

## Interpretation rule

The scores are **propensity scores for a synthetic portfolio benchmark**. They are not calibrated probabilities of a real company's future contract conclusion.
