"""Plotly chart builders implementing the visual specifications from prd.md."""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.styles import (
    BOROUGH_COLORS,
    ROOM_TYPE_COLORS,
    PRICE_TIER_COLORS,
    HOST_CATEGORY_COLORS,
    apply_plotly_theme,
)


def empty_figure(message: str = "No data available for the current filter criteria.") -> go.Figure:
    """Return a styled blank figure with an explanatory text overlay."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=14, color="#94A3B8"),
    )
    apply_plotly_theme(fig)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


# ==========================================
# 1. OVERVIEW CHARTS
# ==========================================

def build_borough_supply_chart(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart showing listing counts and market shares per borough."""
    if df.empty:
        return empty_figure()

    counts = df["neighbourhood_group"].value_counts().reset_index()
    counts.columns = ["Borough", "Count"]
    total = counts["Count"].sum()
    counts["Percentage"] = (counts["Count"] / total) * 100
    counts = counts.sort_values(by="Count", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=counts["Borough"],
            x=counts["Count"],
            orientation="h",
            marker=dict(
                color=[BOROUGH_COLORS.get(b, "#6366F1") for b in counts["Borough"]],
                line=dict(width=1, color="rgba(255, 255, 255, 0.15)"),
            ),
            text=[f"{c:,} ({p:.1f}%)" for c, p in zip(counts["Count"], counts["Percentage"])],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Listings: %{x:,}<br>Share: %{customdata:.1f}%<extra></extra>",
            customdata=counts["Percentage"],
        )
    )

    fig.update_layout(
        title="Listing Supply by Borough (Volume & Share)",
        xaxis_title="Number of Listings",
        yaxis_title="",
        height=320,
    )
    return apply_plotly_theme(fig)


def build_room_type_mix_chart(df: pd.DataFrame) -> go.Figure:
    """Donut chart illustrating accommodation mix and percentage shares."""
    if df.empty:
        return empty_figure()

    counts = df["room_type"].value_counts().reset_index()
    counts.columns = ["Room Type", "Count"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=counts["Room Type"],
                values=counts["Count"],
                hole=0.55,
                marker=dict(
                    colors=[ROOM_TYPE_COLORS.get(rt, "#94A3B8") for rt in counts["Room Type"]],
                    line=dict(color="#0B0F19", width=2),
                ),
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Listings: %{value:,}<br>Share: %{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title="Room-Type Mix",
        height=320,
        showlegend=True,
    )
    return apply_plotly_theme(fig)


def build_price_distribution_chart(df: pd.DataFrame, price_cap: float = 1000.0) -> go.Figure:
    """Box plot of nightly prices across boroughs for records under display cap."""
    if df.empty:
        return empty_figure()

    capped_df = df[df["price"] <= price_cap]
    if capped_df.empty:
        return empty_figure("No listings within the current price display cap.")

    fig = px.box(
        capped_df,
        x="neighbourhood_group",
        y="price",
        color="neighbourhood_group",
        color_discrete_map=BOROUGH_COLORS,
        points=False,
    )

    fig.update_layout(
        title=f"Nightly Price Distribution by Borough (Capped at ${price_cap:,.0f})",
        xaxis_title="Borough",
        yaxis_title="Nightly Price ($ USD)",
        showlegend=False,
        height=350,
    )
    return apply_plotly_theme(fig)


# ==========================================
# 2. MARKET MAP & SUPPORTING VISUALS
# ==========================================

def build_market_map(
    df: pd.DataFrame,
    metric: str = "Listing Density",
    price_cap: float = 1000.0,
) -> go.Figure:
    """Interactive map using token-free Carto-Positron / OpenStreetMap tiles.

    Supported modes:
    - 'Listing Density': Density heatmap of listings
    - 'Median Price': Aggregated neighborhood median prices
    - 'Review Activity': Aggregated neighborhood median monthly reviews
    """
    if df.empty:
        return empty_figure("No geographic coordinates match the current filters.")

    center_lat, center_lon = 40.728, -73.945

    if metric == "Listing Density":
        # Sample for ultra-smooth rendering if over 12,000 points
        sample_df = df.sample(n=min(12000, len(df)), random_state=42) if len(df) > 12000 else df
        if hasattr(px, "density_map"):
            fig = px.density_map(
                sample_df,
                lat="latitude",
                lon="longitude",
                radius=9,
                zoom=9.7,
                center=dict(lat=center_lat, lon=center_lon),
                map_style="carto-positron",
                color_continuous_scale="Viridis",
            )
        else:
            fig = px.density_mapbox(
                sample_df,
                lat="latitude",
                lon="longitude",
                radius=9,
                zoom=9.7,
                center=dict(lat=center_lat, lon=center_lon),
                mapbox_style="carto-positron",
                color_continuous_scale="Viridis",
            )
        fig.update_layout(
            title="NYC Listing Density Heatmap (Geographic Supply Concentration)",
            coloraxis_colorbar=dict(title="Density Index"),
            height=540,
        )
    elif metric == "Median Price":
        # Aggregate by neighborhood for clean, informative, non-cluttered map
        neigh_agg = (
            df[df["price"] <= price_cap]
            .groupby(["neighbourhood_group", "neighbourhood"])
            .agg(
                median_price=("price", "median"),
                listings=("id", "count"),
                reviews=("number_of_reviews", "sum"),
                lat=("latitude", "mean"),
                lon=("longitude", "mean"),
            )
            .reset_index()
        )
        if neigh_agg.empty:
            return empty_figure("No data under current price cap for mapping.")

        map_kwargs = dict(
            lat="lat",
            lon="lon",
            size="listings",
            color="median_price",
            color_continuous_scale="Plasma",
            size_max=22,
            zoom=9.7,
            center=dict(lat=center_lat, lon=center_lon),
            hover_name="neighbourhood",
            hover_data={
                "lat": False,
                "lon": False,
                "neighbourhood_group": True,
                "median_price": ":$.0f",
                "listings": ":,",
                "reviews": ":,",
            },
            labels={
                "neighbourhood_group": "Borough",
                "median_price": "Median Price ($)",
                "listings": "Listings",
                "reviews": "Total Reviews",
            },
        )
        if hasattr(px, "scatter_map"):
            fig = px.scatter_map(neigh_agg, map_style="carto-positron", **map_kwargs)
        else:
            fig = px.scatter_mapbox(neigh_agg, mapbox_style="carto-positron", **map_kwargs)

        fig.update_layout(
            title=f"Neighborhood Median Nightly Price (Capped at ${price_cap:,.0f})",
            coloraxis_colorbar=dict(title="Median Price ($)"),
            height=540,
        )
    else:  # Review Activity
        neigh_agg = (
            df.groupby(["neighbourhood_group", "neighbourhood"])
            .agg(
                median_reviews=("reviews_per_month_filled", "median"),
                listings=("id", "count"),
                lat=("latitude", "mean"),
                lon=("longitude", "mean"),
            )
            .reset_index()
        )
        map_kwargs = dict(
            lat="lat",
            lon="lon",
            size="listings",
            color="median_reviews",
            color_continuous_scale="Turbo",
            size_max=22,
            zoom=9.7,
            center=dict(lat=center_lat, lon=center_lon),
            hover_name="neighbourhood",
            hover_data={
                "lat": False,
                "lon": False,
                "neighbourhood_group": True,
                "median_reviews": ":.2f",
                "listings": ":,",
            },
            labels={
                "neighbourhood_group": "Borough",
                "median_reviews": "Median Reviews/Mo",
                "listings": "Listings",
            },
        )
        if hasattr(px, "scatter_map"):
            fig = px.scatter_map(neigh_agg, map_style="carto-positron", **map_kwargs)
        else:
            fig = px.scatter_mapbox(neigh_agg, mapbox_style="carto-positron", **map_kwargs)

        fig.update_layout(
            title="Geographic Review Activity (Proxy for Monthly Demand Velocity)",
            coloraxis_colorbar=dict(title="Reviews/Mo"),
            height=540,
        )

    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    return apply_plotly_theme(fig)


def build_supply_vs_price_chart(df: pd.DataFrame) -> go.Figure:
    """Bubble chart contrasting supply volume against median price across boroughs."""
    if df.empty:
        return empty_figure()

    borough_summary = (
        df.groupby("neighbourhood_group")
        .agg(
            listings=("id", "count"),
            median_price=("price", "median"),
            total_reviews=("number_of_reviews", "sum"),
            median_rpm=("reviews_per_month_filled", "median"),
        )
        .reset_index()
    )

    fig = px.scatter(
        borough_summary,
        x="listings",
        y="median_price",
        size="total_reviews",
        color="neighbourhood_group",
        color_discrete_map=BOROUGH_COLORS,
        text="neighbourhood_group",
        size_max=35,
        hover_data={
            "listings": ":,",
            "median_price": ":$.0f",
            "total_reviews": ":,",
            "median_rpm": ":.2f",
        },
        labels={
            "listings": "Listing Supply (Volume)",
            "median_price": "Median Nightly Price ($ USD)",
            "total_reviews": "Total Reviews",
            "neighbourhood_group": "Borough",
        },
    )

    fig.update_traces(textposition="top center")
    fig.update_layout(
        title="Supply Concentration vs. Median Price by Borough",
        height=380,
    )
    return apply_plotly_theme(fig)


# ==========================================
# 3. PRICE ANALYSIS CHARTS
# ==========================================

def build_price_by_borough_room_chart(df: pd.DataFrame, price_cap: float = 1000.0) -> go.Figure:
    """Grouped bar chart showing median price by borough and room type."""
    if df.empty:
        return empty_figure()

    capped_df = df[df["price"] <= price_cap]
    grouped = (
        capped_df.groupby(["neighbourhood_group", "room_type"])["price"]
        .median()
        .reset_index()
    )

    fig = px.bar(
        grouped,
        x="neighbourhood_group",
        y="price",
        color="room_type",
        barmode="group",
        color_discrete_map=ROOM_TYPE_COLORS,
        text_auto="$.0f",
        labels={
            "neighbourhood_group": "Borough",
            "price": "Median Price ($ USD)",
            "room_type": "Room Type",
        },
    )

    fig.update_layout(
        title=f"Median Nightly Price by Borough & Room Type (Capped at ${price_cap:,.0f})",
        height=380,
    )
    return apply_plotly_theme(fig)


def build_min_nights_vs_price_chart(df: pd.DataFrame, price_cap: float = 1000.0) -> go.Figure:
    """Scatterplot examining relationship between stay requirements and price."""
    if df.empty:
        return empty_figure()

    filtered = df[(df["price"] <= price_cap) & (df["minimum_nights"] <= 60)]
    if len(filtered) > 5000:
        filtered = filtered.sample(5000, random_state=42)

    fig = px.scatter(
        filtered,
        x="minimum_nights",
        y="price",
        color="room_type",
        color_discrete_map=ROOM_TYPE_COLORS,
        opacity=0.35,
        trendline=None,
        labels={
            "minimum_nights": "Minimum Nights Required",
            "price": "Nightly Price ($ USD)",
            "room_type": "Room Type",
        },
        hover_data=["neighbourhood_group", "neighbourhood"],
    )

    fig.update_layout(
        title="Minimum Nights vs. Nightly Price (Stay Duration Friction)",
        height=380,
    )
    return apply_plotly_theme(fig)


def build_price_tier_composition_chart(df: pd.DataFrame) -> go.Figure:
    """100% stacked horizontal bar chart of price tiers across boroughs."""
    if df.empty or "price_tier" not in df.columns:
        return empty_figure()

    cross_tab = (
        pd.crosstab(df["neighbourhood_group"], df["price_tier"], normalize="index")
        * 100
    ).reset_index()

    # Ensure consistent tier order
    tier_order = ["Budget", "Mid-range", "Premium", "Luxury"]
    existing_tiers = [t for t in tier_order if t in cross_tab.columns]

    fig = go.Figure()
    for tier in existing_tiers:
        fig.add_trace(
            go.Bar(
                name=tier,
                y=cross_tab["neighbourhood_group"],
                x=cross_tab[tier],
                orientation="h",
                marker_color=PRICE_TIER_COLORS.get(tier, "#94A3B8"),
                text=[f"{v:.1f}%" if v >= 5 else "" for v in cross_tab[tier]],
                textposition="inside",
                hovertemplate=f"<b>%{{y}}</b><br>{tier}: %{{x:.1f}}%<extra></extra>",
            )
        )

    fig.update_layout(
        title="Price-Tier Composition by Borough (100% Stacked)",
        barmode="stack",
        xaxis_title="Percentage Share (%)",
        yaxis_title="",
        height=350,
    )
    return apply_plotly_theme(fig)


# ==========================================
# 4. DEMAND & AVAILABILITY CHARTS
# ==========================================

def build_reviews_vs_price_chart(df: pd.DataFrame, price_cap: float = 1000.0) -> go.Figure:
    """Scatterplot comparing review velocity (demand proxy) and nightly price."""
    if df.empty:
        return empty_figure()

    filtered = df[df["price"] <= price_cap]
    if len(filtered) > 5000:
        filtered = filtered.sample(5000, random_state=42)

    fig = px.scatter(
        filtered,
        x="reviews_per_month_filled",
        y="price",
        color="neighbourhood_group",
        color_discrete_map=BOROUGH_COLORS,
        opacity=0.4,
        labels={
            "reviews_per_month_filled": "Reviews Per Month (Filled)",
            "price": "Nightly Price ($ USD)",
            "neighbourhood_group": "Borough",
        },
        hover_data=["neighbourhood", "room_type"],
    )

    fig.update_layout(
        title="Reviews per Month vs. Nightly Price",
        height=380,
    )
    return apply_plotly_theme(fig)


def build_availability_by_borough_chart(df: pd.DataFrame) -> go.Figure:
    """Box plot tracking annual calendar availability across boroughs."""
    if df.empty:
        return empty_figure()

    fig = px.box(
        df,
        x="neighbourhood_group",
        y="availability_365",
        color="neighbourhood_group",
        color_discrete_map=BOROUGH_COLORS,
        points=False,
        labels={
            "neighbourhood_group": "Borough",
            "availability_365": "Annual Available Days (out of 365)",
        },
    )

    fig.update_layout(
        title="Calendar Availability by Borough (Supply Liquidity)",
        height=350,
        showlegend=False,
    )
    return apply_plotly_theme(fig)


def build_host_portfolio_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart mapping listings and shares by host portfolio category."""
    if df.empty or "host_category" not in df.columns:
        return empty_figure()

    order = ["Single-listing host", "Small portfolio", "Professional host"]
    counts = df["host_category"].value_counts().reindex(order).fillna(0).reset_index()
    counts.columns = ["Category", "Listings"]
    total = counts["Listings"].sum()
    counts["Share"] = (counts["Listings"] / total) * 100 if total > 0 else 0

    # Also calculate median price per category
    medians = df.groupby("host_category")["price"].median().reindex(order).fillna(0).values
    counts["Median Price"] = medians

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=counts["Category"],
            y=counts["Listings"],
            marker=dict(
                color=[HOST_CATEGORY_COLORS.get(c, "#6366F1") for c in counts["Category"]],
                line=dict(color="rgba(255, 255, 255, 0.15)", width=1),
            ),
            text=[f"{c:,.0f} ({s:.1f}%)" for c, s in zip(counts["Listings"], counts["Share"])],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Listings: %{y:,}<br>Median Price: $%{customdata:,.0f}<extra></extra>",
            customdata=counts["Median Price"],
        )
    )

    fig.update_layout(
        title="Host Portfolio Scale (Individual vs. Commercial Operators)",
        xaxis_title="",
        yaxis_title="Total Listings",
        height=350,
    )
    return apply_plotly_theme(fig)


# ==========================================
# 5. NEIGHBORHOOD INSIGHT CHARTS
# ==========================================

def build_neighborhood_ranked_chart(
    df_neighborhoods: pd.DataFrame, ranking_type: str = "Top 10 (Highest Price)"
) -> go.Figure:
    """Ranked horizontal bar chart of neighborhood median prices."""
    if df_neighborhoods.empty:
        return empty_figure("No neighborhoods meet the current listing volume threshold.")

    if "Top" in ranking_type:
        plot_df = df_neighborhoods.nlargest(10, "median_price").sort_values("median_price", ascending=True)
        title = "Top 10 Most Expensive Neighborhoods by Median Price"
    else:
        plot_df = df_neighborhoods.nsmallest(10, "median_price").sort_values("median_price", ascending=False)
        title = "Top 10 Most Accessible (Budget) Neighborhoods by Median Price"

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=plot_df["neighbourhood"],
            x=plot_df["median_price"],
            orientation="h",
            marker=dict(
                color=[BOROUGH_COLORS.get(b, "#6366F1") for b in plot_df["neighbourhood_group"]],
            ),
            text=[f"${p:,.0f} ({b})" for p, b in zip(plot_df["median_price"], plot_df["neighbourhood_group"])],
            textposition="outside",
            hovertemplate="<b>%{y}</b> (%{customdata[0]})<br>Median Price: $%{x:,.0f}<br>Listings: %{customdata[1]:,}<extra></extra>",
            customdata=plot_df[["neighbourhood_group", "listings"]].values,
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Median Nightly Price ($ USD)",
        yaxis_title="",
        height=380,
    )
    return apply_plotly_theme(fig)
