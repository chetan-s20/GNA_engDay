"""Unit tests for statistical narrative generation."""

import pandas as pd
from src.insights import (
    generate_overview_insights,
    generate_price_insights,
    generate_demand_insights,
)


def test_insights_on_sparse_and_single_borough_data():
    """Test 7: Generated insights do not fail when only one borough or room type remains."""
    single_slice = pd.DataFrame(
        {
            "neighbourhood_group": ["Manhattan", "Manhattan"],
            "room_type": ["Entire home/apt", "Entire home/apt"],
            "price": [300, 350],
            "minimum_nights": [3, 4],
            "number_of_reviews": [10, 20],
            "reviews_per_month_filled": [1.5, 2.0],
            "availability_365": [100, 150],
            "price_tier": ["Luxury", "Luxury"],
            "host_category": ["Single-listing host", "Single-listing host"],
        }
    )

    overview_insights = generate_overview_insights(single_slice)
    assert len(overview_insights) >= 1
    assert "Manhattan" in overview_insights[0]

    price_insights = generate_price_insights(single_slice)
    assert isinstance(price_insights, list)

    demand_insights = generate_demand_insights(single_slice)
    assert isinstance(demand_insights, list)


def test_insights_on_empty_df():
    """Insights should return informative messages on empty data without throwing."""
    empty_df = pd.DataFrame()
    res = generate_overview_insights(empty_df)
    assert len(res) == 1
    assert "No listings match" in res[0]


def test_price_insights_respect_display_cap():
    """Narrative medians should match the capped records shown in adjacent charts."""
    frame = pd.DataFrame(
        {
            "room_type": ["Entire home/apt", "Entire home/apt", "Private room"],
            "price": [200, 5000, 100],
            "minimum_nights": [2, 2, 2],
            "price_tier": ["Premium", "Luxury", "Budget"],
        }
    )
    insights = generate_price_insights(frame, price_cap=1000)
    combined = " ".join(insights)
    assert "$200" in combined
    assert "$5,000" not in combined
