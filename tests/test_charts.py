"""End-to-end chart rendering integration tests."""

import pytest
import pandas as pd
from src.data import load_and_prepare_data, compute_neighborhood_aggregates
from src.charts import (
    build_borough_supply_chart,
    build_room_type_mix_chart,
    build_price_distribution_chart,
    build_market_map,
    build_supply_vs_price_chart,
    build_price_by_borough_room_chart,
    build_min_nights_vs_price_chart,
    build_price_tier_composition_chart,
    build_reviews_vs_price_chart,
    build_availability_by_borough_chart,
    build_host_portfolio_chart,
    build_neighborhood_ranked_chart,
)


@pytest.fixture(scope="module")
def real_data():
    return load_and_prepare_data("data/AB_NYC_2019.csv")


def test_all_chart_builders_render_without_error(real_data):
    """Verify that every chart function executes cleanly on the full real dataset."""
    sample_slice = real_data.sample(500, random_state=42)

    fig1 = build_borough_supply_chart(sample_slice)
    assert fig1 is not None

    fig2 = build_room_type_mix_chart(sample_slice)
    assert fig2 is not None

    fig3 = build_price_distribution_chart(sample_slice, price_cap=1000.0)
    assert fig3 is not None

    fig4 = build_market_map(sample_slice, metric="Listing Density")
    assert fig4 is not None

    fig4b = build_market_map(sample_slice, metric="Median Price")
    assert fig4b is not None

    fig4c = build_market_map(sample_slice, metric="Review Activity")
    assert fig4c is not None

    fig5 = build_supply_vs_price_chart(sample_slice)
    assert fig5 is not None

    fig6 = build_price_by_borough_room_chart(sample_slice, price_cap=1000.0)
    assert fig6 is not None

    fig7 = build_min_nights_vs_price_chart(sample_slice, price_cap=1000.0)
    assert fig7 is not None

    fig8 = build_price_tier_composition_chart(sample_slice)
    assert fig8 is not None

    fig9 = build_reviews_vs_price_chart(sample_slice, price_cap=1000.0)
    assert fig9 is not None

    fig10 = build_availability_by_borough_chart(sample_slice)
    assert fig10 is not None

    fig11 = build_host_portfolio_chart(sample_slice)
    assert fig11 is not None

    neigh_df = compute_neighborhood_aggregates(sample_slice, min_listings=1)
    fig12 = build_neighborhood_ranked_chart(neigh_df, ranking_type="Top 10")
    assert fig12 is not None


def test_map_modes_expose_consistent_neighborhood_metrics(real_data):
    """Price and review maps should expose the same complete neighborhood context."""
    sample_slice = real_data.sample(1000, random_state=7)
    for metric in ["Listing Density", "Median Price", "Review Activity"]:
        fig = build_market_map(sample_slice, metric=metric, price_cap=1000.0)
        hover_template = " ".join(
            str(trace.hovertemplate) for trace in fig.data if trace.hovertemplate
        )
        assert "Listings" in hover_template
        assert "Median price" in hover_template
        assert "Median reviews/mo" in hover_template


def test_capped_scatter_charts_explain_empty_state(real_data):
    """Price-cap charts should return a readable empty figure rather than a blank plot."""
    expensive_only = real_data[real_data["price"] > 1000].copy()
    for figure in [
        build_price_by_borough_room_chart(expensive_only, price_cap=1000),
        build_min_nights_vs_price_chart(expensive_only, price_cap=1000),
        build_reviews_vs_price_chart(expensive_only, price_cap=1000),
    ]:
        assert figure.layout.annotations
        assert "No listings" in figure.layout.annotations[0].text
