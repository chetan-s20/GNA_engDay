"""Data validation, cleaning, feature derivation, and filtering pipeline."""

import os
import pandas as pd
import numpy as np
import streamlit as st

REQUIRED_COLUMNS = [
    "id",
    "name",
    "host_id",
    "host_name",
    "neighbourhood_group",
    "neighbourhood",
    "latitude",
    "longitude",
    "room_type",
    "price",
    "minimum_nights",
    "number_of_reviews",
    "last_review",
    "reviews_per_month",
    "calculated_host_listings_count",
    "availability_365",
]

NUMERIC_COLUMNS = [
    "id",
    "host_id",
    "latitude",
    "longitude",
    "price",
    "minimum_nights",
    "number_of_reviews",
    "reviews_per_month",
    "calculated_host_listings_count",
    "availability_365",
]


def validate_columns(df: pd.DataFrame) -> None:
    """Validate that all required columns are present in the dataframe."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"Dataset validation failed. Missing required column(s): {', '.join(missing)}"
        )


def assign_host_category(count: int | float) -> str:
    """Categorize host by portfolio size according to PRD specs:
    1: Single-listing host
    2-5: Small portfolio
    6+: Professional host
    """
    if pd.isna(count) or count <= 1:
        return "Single-listing host"
    elif 2 <= count <= 5:
        return "Small portfolio"
    else:
        return "Professional host"


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich raw NYC Airbnb listings data according to PRD Section 10."""
    validate_columns(df)
    clean_df = df.copy()

    # 1. Normalize text fields & whitespace
    for col in ["neighbourhood_group", "neighbourhood", "room_type"]:
        if col in clean_df.columns:
            clean_df[col] = clean_df[col].astype(str).str.strip()

    # 2. Convert numeric fields safely
    for col in NUMERIC_COLUMNS:
        if col in clean_df.columns:
            clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce")

    # 3. Convert dates
    clean_df["last_review"] = pd.to_datetime(clean_df["last_review"], errors="coerce")

    # 4. Drop records with missing key geographic / market identifiers
    critical_cols = ["latitude", "longitude", "price", "neighbourhood_group", "room_type"]
    clean_df = clean_df.dropna(subset=critical_cols)

    # 5. Exclude invalid non-positive prices
    clean_df = clean_df[clean_df["price"] > 0].copy()

    # 6. Fill missing reviews_per_month in a separate analysis column (preserve original raw column)
    clean_df["reviews_per_month_filled"] = clean_df["reviews_per_month"].fillna(0.0)

    # 7. Derived field: log_price
    clean_df["log_price"] = np.log1p(clean_df["price"])

    # 8. Derived field: price_tier based on quartiles
    if len(clean_df) > 0:
        q1 = clean_df["price"].quantile(0.25)
        q2 = clean_df["price"].quantile(0.50)
        q3 = clean_df["price"].quantile(0.75)

        def get_price_tier(p):
            if p <= q1:
                return "Budget"
            elif p <= q2:
                return "Mid-range"
            elif p <= q3:
                return "Premium"
            else:
                return "Luxury"

        clean_df["price_tier"] = clean_df["price"].apply(get_price_tier)
    else:
        clean_df["price_tier"] = pd.Series(dtype="object")

    # 9. Derived field: host_category
    clean_df["host_category"] = clean_df["calculated_host_listings_count"].apply(
        assign_host_category
    )

    # 10. Derived field: has_reviews
    clean_df["has_reviews"] = clean_df["number_of_reviews"] > 0

    # 11. Derived field: review_activity (Low / Moderate / High based on non-null reviews_per_month)
    valid_rpm = clean_df.loc[clean_df["reviews_per_month"] > 0, "reviews_per_month"]
    if len(valid_rpm) >= 3:
        rpm_t1 = valid_rpm.quantile(0.333)
        rpm_t2 = valid_rpm.quantile(0.667)

        def get_activity(r):
            if pd.isna(r) or r == 0:
                return "None / Inactive"
            elif r <= rpm_t1:
                return "Low"
            elif r <= rpm_t2:
                return "Moderate"
            else:
                return "High"

        clean_df["review_activity"] = clean_df["reviews_per_month_filled"].apply(get_activity)
    else:
        clean_df["review_activity"] = "Moderate"

    return clean_df


@st.cache_data(show_spinner="Loading and preparing NYC Airbnb dataset...")
def load_and_prepare_data(filepath: str = "data/AB_NYC_2019.csv") -> pd.DataFrame:
    """Load source CSV and execute preparation pipeline with Streamlit caching."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Source file not found at: {filepath}")
    raw_df = pd.read_csv(filepath)
    return prepare_data(raw_df)


def filter_data(
    df: pd.DataFrame,
    selected_boroughs: list[str] | None = None,
    selected_room_types: list[str] | None = None,
    price_min: float = 0.0,
    price_max: float = 10000.0,
    min_reviews: int = 0,
    min_availability: int = 0,
) -> pd.DataFrame:
    """Apply interactive sidebar filters across the cleaned dataset."""
    filtered = df.copy()

    if selected_boroughs:
        filtered = filtered[filtered["neighbourhood_group"].isin(selected_boroughs)]

    if selected_room_types:
        filtered = filtered[filtered["room_type"].isin(selected_room_types)]

    filtered = filtered[
        (filtered["price"] >= price_min) & (filtered["price"] <= price_max)
    ]

    if min_reviews > 0:
        filtered = filtered[filtered["number_of_reviews"] >= min_reviews]

    if min_availability > 0:
        filtered = filtered[filtered["availability_365"] >= min_availability]

    return filtered


def compute_neighborhood_aggregates(
    df: pd.DataFrame, min_listings: int = 20
) -> pd.DataFrame:
    """Aggregate neighborhood metrics according to PRD Section 11.5, including Relative Value Signal."""
    if df.empty:
        return pd.DataFrame()

    def get_mode_room(series):
        mode_val = series.mode()
        return mode_val.iloc[0] if not mode_val.empty else "N/A"

    grouped = (
        df.groupby(["neighbourhood_group", "neighbourhood"])
        .agg(
            listings=("id", "count"),
            median_price=("price", "median"),
            median_reviews_per_month=("reviews_per_month_filled", "median"),
            median_availability=("availability_365", "median"),
            dominant_room_type=("room_type", get_mode_room),
            lat=("latitude", "mean"),
            lon=("longitude", "mean"),
        )
        .reset_index()
    )

    # Filter to threshold
    grouped = grouped[grouped["listings"] >= min_listings].copy()

    if grouped.empty:
        return grouped

    # Relative Value Signal:
    # Standardize median price (lower is better -> invert) and median reviews/month (higher is better)
    # Scaled to 0-100 for intuitive interpretation
    price_series = grouped["median_price"]
    review_series = grouped["median_reviews_per_month"]

    price_min, price_max = price_series.min(), price_series.max()
    rev_min, rev_max = review_series.min(), review_series.max()

    price_norm = (
        1.0 - (price_series - price_min) / (price_max - price_min)
        if price_max > price_min
        else 0.5
    )
    rev_norm = (
        (review_series - rev_min) / (rev_max - rev_min)
        if rev_max > rev_min
        else 0.5
    )

    # Relative value = 50% lower price score + 50% higher activity score
    grouped["relative_value_score"] = np.round((0.5 * price_norm + 0.5 * rev_norm) * 100, 1)

    return grouped.sort_values(by="median_price", ascending=False)
