"""Dynamic statistical narrative generation engine.

Adheres strictly to PRD guidelines:
- Non-hardcoded findings calculated from the current filtered state.
- Descriptive and associative language only ('is associated with', 'shows a higher median', 'is more concentrated in').
- Strict avoidance of causal claims ('causes', 'proves', 'guarantees', 'best investment').
- Robust handling of single-category, sparse, and empty filter slices.
"""

import pandas as pd


def generate_overview_insights(df: pd.DataFrame) -> list[str]:
    """Generate 2-3 dynamic takeaway bullets for the Overview section."""
    if df.empty:
        return ["No listings match the current filter criteria to generate insights."]

    insights = []
    total_count = len(df)

    # 1. Borough supply share
    borough_counts = df["neighbourhood_group"].value_counts()
    if not borough_counts.empty:
        top_borough = borough_counts.index[0]
        top_count = borough_counts.iloc[0]
        top_share = (top_count / total_count) * 100
        insights.append(
            f"**{top_borough}** has the largest share of filtered listings, "
            f"accounting for **{top_share:.1f}%** of market supply ({top_count:,} listings)."
        )

    # 2. Median price leader
    borough_medians = df.groupby("neighbourhood_group")["price"].median()
    if not borough_medians.empty:
        highest_borough = borough_medians.idxmax()
        highest_median = borough_medians.max()
        insights.append(
            f"Median nightly price is highest in **{highest_borough}** at **${highest_median:,.0f}**, "
            f"compared to an overall filtered median of **${df['price'].median():,.0f}**."
        )

    # 3. Room type composition
    room_counts = df["room_type"].value_counts()
    if not room_counts.empty:
        top_room = room_counts.index[0]
        room_share = (room_counts.iloc[0] / total_count) * 100
        insights.append(
            f"**{top_room}** represents **{room_share:.1f}%** of active accommodations in this selection."
        )

    return insights


def generate_price_insights(df: pd.DataFrame, price_cap: float = 1000.0) -> list[str]:
    """Generate dynamic insights for price analysis."""
    if df.empty:
        return ["No listings available for price insight analysis."]

    insights = []
    capped_df = df[df["price"] <= price_cap]
    if capped_df.empty:
        return [
            f"No listings fall within the current ${price_cap:,.0f} chart display cap."
        ]

    # Check room type price differences
    room_medians = capped_df.groupby("room_type")["price"].median()
    if "Entire home/apt" in room_medians and "Private room" in room_medians:
        home_med = room_medians["Entire home/apt"]
        priv_med = room_medians["Private room"]
        diff_pct = ((home_med - priv_med) / priv_med) * 100 if priv_med > 0 else 0
        insights.append(
            f"Entire home/apt listings show a **{diff_pct:.0f}% median premium** "
            f"(${home_med:,.0f} vs. ${priv_med:,.0f}) over private rooms."
        )

    # Check minimum nights correlation / median
    short_stay = capped_df[capped_df["minimum_nights"] <= 3]["price"].median()
    long_stay = capped_df[capped_df["minimum_nights"] >= 30]["price"].median()
    if not pd.isna(short_stay) and not pd.isna(long_stay) and len(capped_df[capped_df["minimum_nights"] >= 30]) >= 10:
        insights.append(
            f"Short-stay listings (<= 3 nights) show a median of **${short_stay:,.0f}**, "
            f"while extended-stay listings (>= 30 nights) show a median of **${long_stay:,.0f}**."
        )

    # Price tier breakdown
    if "price_tier" in capped_df.columns:
        tier_counts = capped_df["price_tier"].value_counts(normalize=True) * 100
        lux_share = tier_counts.get("Luxury", 0.0)
        bud_share = tier_counts.get("Budget", 0.0)
        insights.append(
            f"The filtered segment comprises **{bud_share:.1f}% Budget** listings and "
            f"**{lux_share:.1f}% Luxury** tier units."
        )

    return insights


def generate_demand_insights(df: pd.DataFrame) -> list[str]:
    """Generate dynamic insights for demand and availability."""
    if df.empty:
        return ["No listings available for demand insight analysis."]

    insights = []
    # Host portfolio breakdown
    if "host_category" in df.columns:
        host_counts = df["host_category"].value_counts(normalize=True) * 100
        single_share = host_counts.get("Single-listing host", 0.0)
        pro_share = host_counts.get("Professional host", 0.0)
        insights.append(
            f"Single-property hosts operate **{single_share:.1f}%** of listings, "
            f"whereas professional hosts (6+ listings) manage **{pro_share:.1f}%**."
        )

    # Availability vs Reviews
    zero_avail = (df["availability_365"] == 0).mean() * 100
    insights.append(
        f"**{zero_avail:.1f}%** of listings show 0 calendar availability for the year, "
        "which can reflect inactive, booked, or withheld dates; this dataset cannot distinguish them."
    )

    return insights
