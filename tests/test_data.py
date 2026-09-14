"""Unit tests for data validation, cleaning, and derivation logic."""

import pytest
import pandas as pd
import numpy as np
from src.data import (
    prepare_data,
    validate_columns,
    assign_host_category,
    filter_data,
    compute_neighborhood_aggregates,
    REQUIRED_COLUMNS,
)


@pytest.fixture
def sample_valid_df() -> pd.DataFrame:
    """Fixture providing a miniature valid raw dataframe matching Kaggle AB_NYC_2019 schema."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6, 7],
            "name": ["Cozy Apt", "Studio", "Loft", "Room", "Luxury Suite", "Free Room", "Invalid"],
            "host_id": [101, 102, 103, 104, 105, 106, 107],
            "host_name": ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"],
            "neighbourhood_group": [
                "Manhattan",
                "Brooklyn",
                "Queens",
                "Manhattan",
                "Brooklyn",
                "Manhattan",
                None,  # Should be dropped
            ],
            "neighbourhood": [
                "Midtown",
                "Williamsburg",
                "Astoria",
                "Harlem",
                "Bushwick",
                "Midtown",
                "SoHo",
            ],
            "latitude": [40.75, 40.71, 40.76, 40.81, 40.70, 40.75, None],
            "longitude": [-73.98, -73.95, -73.92, -73.94, -73.93, -73.98, -73.99],
            "room_type": [
                "Entire home/apt",
                "Private room",
                "Private room",
                "Entire home/apt",
                "Entire home/apt",
                "Shared room",
                "Private room",
            ],
            "price": [250, 80, 70, 150, 500, 0, 100],  # 0 should be dropped
            "minimum_nights": [2, 1, 3, 30, 5, 1, 2],
            "number_of_reviews": [25, 0, 42, 110, 5, 0, 10],
            "last_review": [
                "2019-06-15",
                None,
                "2019-05-20",
                "2019-06-30",
                "2018-12-01",
                None,
                "2019-01-01",
            ],
            "reviews_per_month": [1.5, np.nan, 3.2, 5.0, 0.4, np.nan, 0.8],
            "calculated_host_listings_count": [1, 2, 5, 6, 12, 1, 1],
            "availability_365": [120, 0, 240, 365, 50, 0, 180],
        }
    )


def test_missing_required_columns():
    """Test 1: Missing required columns produces a clear validation error."""
    df_missing = pd.DataFrame({"id": [1], "price": [100]})
    with pytest.raises(ValueError) as excinfo:
        validate_columns(df_missing)
    assert "Missing required column(s)" in str(excinfo.value)


def test_invalid_and_zero_prices_removed(sample_valid_df):
    """Test 2: Invalid and zero prices are removed."""
    clean = prepare_data(sample_valid_df)
    assert (clean["price"] <= 0).sum() == 0
    # The record with price 0 (Free Room) should not be in clean
    assert 6 not in clean["id"].values


def test_missing_reviews_per_month_handled(sample_valid_df):
    """Test 3: Missing reviews per month are handled without overwriting the raw column."""
    clean = prepare_data(sample_valid_df)
    # Raw column should still preserve NaN
    bob_record = clean[clean["host_name"] == "Bob"].iloc[0]
    assert pd.isna(bob_record["reviews_per_month"])
    # But filled column should be 0.0
    assert bob_record["reviews_per_month_filled"] == 0.0


def test_host_category_boundaries():
    """Test 4: Host categories are correctly assigned at boundaries 1, 2, 5, and 6."""
    assert assign_host_category(1) == "Single-listing host"
    assert assign_host_category(2) == "Small portfolio"
    assert assign_host_category(5) == "Small portfolio"
    assert assign_host_category(6) == "Professional host"
    assert assign_host_category(100) == "Professional host"
    assert assign_host_category(np.nan) == "Unknown"


def test_price_tiers_assigned(sample_valid_df):
    """Test 5: Price tiers are assigned for valid input."""
    clean = prepare_data(sample_valid_df)
    assert "price_tier" in clean.columns
    assert set(clean["price_tier"].unique()).issubset(
        {"Budget", "Mid-range", "Premium", "Luxury"}
    )


def test_empty_filter_result(sample_valid_df):
    """Test 6: A no-data filter result returns an empty dataframe safely."""
    clean = prepare_data(sample_valid_df)
    empty = filter_data(clean, selected_boroughs=["NonExistentBorough"])
    assert empty.empty
    assert isinstance(empty, pd.DataFrame)


def test_empty_filter_selections_return_no_rows(sample_valid_df):
    """An explicit empty multiselect must not be interpreted as selecting all values."""
    clean = prepare_data(sample_valid_df)
    assert filter_data(clean, selected_boroughs=[]).empty
    assert filter_data(clean, selected_room_types=[]).empty


def test_missing_and_blank_categories_are_removed(sample_valid_df):
    """Missing categorical values must remain null through normalization and be removed."""
    categorical_null = sample_valid_df.iloc[[0]].copy()
    categorical_null["id"] = 99
    categorical_null["neighbourhood_group"] = None
    categorical_null["latitude"] = 40.75

    blank_room = sample_valid_df.iloc[[0]].copy()
    blank_room["id"] = 100
    blank_room["room_type"] = "   "

    clean = prepare_data(pd.concat([sample_valid_df, categorical_null, blank_room], ignore_index=True))
    assert 99 not in clean["id"].values
    assert 100 not in clean["id"].values


def test_outlier_and_review_activity_fields(sample_valid_df):
    """Required derived fields should use stable, documented categories."""
    expensive = sample_valid_df.iloc[[0]].copy()
    expensive["id"] = 101
    expensive["price"] = 1500
    clean = prepare_data(pd.concat([sample_valid_df, expensive], ignore_index=True))

    assert clean.loc[clean["id"] == 101, "is_price_outlier"].item()
    assert set(clean["review_activity"].unique()).issubset({"Low", "Moderate", "High"})
