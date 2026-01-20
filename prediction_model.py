from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parent
DATASET_PATH = PROJECT_ROOT / "bus_history.csv"


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def generate_mock_bus_history(
    output_path: Path,
    row_count: int = 600,
    random_seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(random_seed)

    days_in_advance = rng.integers(low=0, high=31, size=row_count)
    is_weekend = rng.integers(low=0, high=2, size=row_count)

    base_price = 650
    price_weekend_markup = 120
    price_short_notice_markup = 220

    price = (
        base_price
        + (is_weekend * price_weekend_markup)
        + (days_in_advance <= 2) * price_short_notice_markup
        + rng.normal(loc=0.0, scale=45.0, size=row_count)
    ).round(0)

    # Business-inspired label generation (mock):
    # - bookings made earlier are more likely to confirm
    # - weekend demand is higher, which can slightly reduce confirmation due to capacity pressure
    # - higher prices reduce confirmation probability
    linear_score = (
        1.1
        + 0.06 * days_in_advance
        - 0.55 * is_weekend
        - 0.0028 * (price - base_price)
        + rng.normal(loc=0.0, scale=0.35, size=row_count)
    )
    confirmation_probability = np.vectorize(_sigmoid)(linear_score)
    confirmed = (rng.random(row_count) < confirmation_probability).astype(int)

    df = pd.DataFrame(
        {
            "days_in_advance": days_in_advance,
            "is_weekend": is_weekend,
            "price": price.astype(int),
            "confirmed": confirmed,
        }
    )

    df.to_csv(output_path, index=False)
    return df


def train_confirmation_model(dataset: pd.DataFrame) -> tuple[StandardScaler, LogisticRegression]:
    features = dataset[["days_in_advance", "is_weekend", "price"]]
    labels = dataset["confirmed"]

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.25,
        random_state=7,
        stratify=labels,
    )

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    model = LogisticRegression(max_iter=800, solver="lbfgs")
    model.fit(x_train_scaled, y_train)

    # Keep output minimal for prototype.
    _ = model.score(x_test_scaled, y_test)

    return scaler, model


def predict_confirmation_probability(
    scaler: StandardScaler,
    model: LogisticRegression,
    days_in_advance: int,
    is_weekend: int,
    price: int,
) -> float:
    input_frame = pd.DataFrame(
        [{"days_in_advance": days_in_advance, "is_weekend": is_weekend, "price": price}]
    )
    input_scaled = scaler.transform(input_frame)
    return float(model.predict_proba(input_scaled)[0, 1])


def main() -> None:
    dataset = generate_mock_bus_history(DATASET_PATH)
    scaler, model = train_confirmation_model(dataset)

    hypothetical_booking = {
        "days_in_advance": 5,
        "is_weekend": 1,
        "price": 820,
    }

    probability = predict_confirmation_probability(
        scaler=scaler,
        model=model,
        days_in_advance=hypothetical_booking["days_in_advance"],
        is_weekend=hypothetical_booking["is_weekend"],
        price=hypothetical_booking["price"],
    )

    print(
        "Confirmation Probability: "
        f"{probability * 100:.1f}% "
        f"(days_in_advance={hypothetical_booking['days_in_advance']}, "
        f"is_weekend={hypothetical_booking['is_weekend']}, "
        f"price={hypothetical_booking['price']})"
    )


if __name__ == "__main__":
    main()
