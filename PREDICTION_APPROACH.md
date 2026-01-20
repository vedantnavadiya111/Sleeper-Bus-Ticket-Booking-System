# Confirmation Prediction (Mock)

## Goal
Estimate the probability that a booking attempt becomes **confirmed** based on a small set of operational features.

## Dataset
`bus_history.csv` is generated locally for prototyping and contains:
- `days_in_advance` (int): number of days before departure when the booking is attempted
- `is_weekend` (0/1): whether the travel date is a weekend
- `price` (int): seat price at the time of booking
- `confirmed` (0/1): synthetic label indicating whether the booking confirmed

Example rows (sample):

| days_in_advance | is_weekend | price | confirmed |
|---:|---:|---:|---:|
| 12 | 0 | 662 | 1 |
| 1 | 1 | 959 | 0 |
| 6 | 0 | 705 | 1 |

## Feature/Label Design
The label is produced from a logistic-style rule with noise to emulate real-world variability:
- higher `days_in_advance` increases confirmation likelihood
- `is_weekend=1` slightly decreases confirmation likelihood due to capacity pressure
- higher `price` decreases confirmation likelihood

This is intentionally simple and is meant to validate the end-to-end pipeline (data generation → model training → probability output).

## Model
- Algorithm: `sklearn.linear_model.LogisticRegression`
- Preprocessing: `StandardScaler` on numeric features
- Train/test split: stratified split to keep class balance stable

## Inference
A single hypothetical booking is converted into a 1-row feature frame, scaled using the fitted scaler, and passed to `predict_proba`. The printed value is the positive-class probability (confirmed=1) expressed as a percentage.

Example output:

`Confirmation Probability: 67.6% (days_in_advance=5, is_weekend=1, price=820)`
