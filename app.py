"""NYC Airbnb Market Intelligence Dashboard

Production-grade Streamlit application fulfilling all specifications in prd.md.
"""

import os
import streamlit as st
import pandas as pd
import numpy as np

# Page configuration - must be very first Streamlit call
st.set_page_config(
    page_title="NYC Airbnb Market Intelligence",
    page_icon="🗽",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.styles import CUSTOM_CSS, BOROUGH_COLORS
from src.data import (
    load_and_prepare_data,
    filter_data,
    compute_neighborhood_aggregates,
)
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
from src.insights import (
    generate_overview_insights,
    generate_price_insights,
    generate_demand_insights,
)

# Inject custom editorial CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -------------------------------------------------------------
# 1. FILE EXISTENCE & LOADING PIPELINE
# -------------------------------------------------------------
DATA_PATH = os.path.join("data", "AB_NYC_2019.csv")

if not os.path.exists(DATA_PATH):
    st.error("⚠️ Dataset File Missing: `data/AB_NYC_2019.csv` was not found.")
    st.markdown(
        """
        ### How to set up the data:
        1. Download the New York City Airbnb Open Data from Kaggle:
           [Kaggle Dataset: dgomonov/new-york-city-airbnb-open-data](https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data)
        2. Place the unzipped `AB_NYC_2019.csv` file into the `data/` folder:
           ```text
           e:/GNA_engDay/data/AB_NYC_2019.csv
           ```
        3. Refresh this page.
        """
    )
    st.stop()

try:
    df_clean = load_and_prepare_data(DATA_PATH)
except Exception as e:
    st.error(f"Error loading and processing dataset: {e}")
    st.stop()

TOTAL_LISTINGS = len(df_clean)

# -------------------------------------------------------------
# 2. SIDEBAR CONTROLS & FILTERS
# -------------------------------------------------------------
st.sidebar.markdown("## 🗽 Explore the Market")
st.sidebar.markdown(
    "<p style='font-size:0.8rem; color:#94A3B8; margin-top:-10px;'>"
    "Interactive filters dynamically update all metrics, charts, maps, and insights."
    "</p>",
    unsafe_allow_html=True,
)

# Reset filters mechanism
if st.sidebar.button("↺ Reset All Filters", use_container_width=True):
    for key in ["filter_boroughs", "filter_rooms", "filter_price", "filter_reviews", "filter_avail", "filter_cap", "filter_map_metric"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Borough filter
all_boroughs = sorted(df_clean["neighbourhood_group"].unique())
selected_boroughs = st.sidebar.multiselect(
    "Boroughs",
    options=all_boroughs,
    default=all_boroughs,
    key="filter_boroughs",
)

# Room type filter
all_rooms = sorted(df_clean["room_type"].unique())
selected_rooms = st.sidebar.multiselect(
    "Room Types",
    options=all_rooms,
    default=all_rooms,
    key="filter_rooms",
)

# Price range filter
min_p = float(df_clean["price"].min())
max_p = float(min(df_clean["price"].max(), 5000.0))
selected_price_range = st.sidebar.slider(
    "Nightly Price Range ($ USD)",
    min_value=float(min_p),
    max_value=float(max_p),
    value=(float(min_p), float(max_p)),
    step=10.0,
    key="filter_price",
)

# Minimum reviews filter
selected_min_reviews = st.sidebar.slider(
    "Minimum Total Reviews",
    min_value=0,
    max_value=100,
    value=0,
    step=5,
    key="filter_reviews",
)

# Minimum availability filter
selected_min_avail = st.sidebar.slider(
    "Minimum Annual Availability (Days)",
    min_value=0,
    max_value=365,
    value=0,
    step=15,
    key="filter_avail",
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Visualization Options")

# Price display cap (for skew control)
price_cap_options = [500.0, 1000.0, 2000.0, 5000.0, 10000.0]
selected_price_cap = st.sidebar.selectbox(
    "Price Display Cap ($ USD)",
    options=price_cap_options,
    index=1,  # Default $1,000
    help="Caps extreme price outliers in distribution and scatter visuals to preserve visual resolution.",
    key="filter_cap",
)

# Map metric mode
map_metric_modes = ["Listing Density", "Median Price", "Review Activity"]
selected_map_metric = st.sidebar.selectbox(
    "Primary Map Layer",
    options=map_metric_modes,
    index=0,
    key="filter_map_metric",
)

# -------------------------------------------------------------
# 3. APPLY FILTERING
# -------------------------------------------------------------
filtered_df = filter_data(
    df_clean,
    selected_boroughs=selected_boroughs,
    selected_room_types=selected_rooms,
    price_min=selected_price_range[0],
    price_max=selected_price_range[1],
    min_reviews=selected_min_reviews,
    min_availability=selected_min_avail,
)

FILTERED_COUNT = len(filtered_df)
pct_active = (FILTERED_COUNT / TOTAL_LISTINGS * 100) if TOTAL_LISTINGS > 0 else 0

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""
    <div style='background:#111827; border:1px solid #1F2937; border-radius:8px; padding:12px; text-align:center;'>
        <div style='font-size:0.75rem; color:#9CA3AF; text-transform:uppercase;'>Active Filtered Corpus</div>
        <div style='font-size:1.4rem; font-weight:800; color:#10B981; font-family:monospace;'>{FILTERED_COUNT:,} <span style='font-size:0.8rem; color:#6B7280;'>/ {TOTAL_LISTINGS:,}</span></div>
        <div style='font-size:0.75rem; color:#6B7280; margin-top:2px;'>{pct_active:.1f}% of city listings</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# 4. GLOBAL HEADER & EDITORIAL BANNER
# -------------------------------------------------------------
st.markdown(
    """
    <div class="editorial-header">
        <h1>NYC Airbnb Market Intelligence</h1>
        <p>How location, room type, and host behavior shaped New York City's short-term rental market in 2019.</p>
        <div class="badge-bar">
            <span class="editorial-badge">Data: NYC Open Data 2019</span>
            <span class="editorial-badge-blue">Kaggle: dgomonov/new-york-city-airbnb-open-data</span>
            <span class="editorial-badge">Methodology: Observational & Descriptive</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Empty filter state check
if filtered_df.empty:
    st.warning("⚠️ No listings match the chosen filter combinations.")
    st.info("Try broadening your price range, reducing minimum review/availability thresholds, or resetting filters.")
    if st.button("Reset Filters Now"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# -------------------------------------------------------------
# 5. FIVE RESPONSIVE KPI CARDS
# -------------------------------------------------------------
median_price = filtered_df["price"].median()
median_rpm = filtered_df["reviews_per_month_filled"].median()
median_avail = filtered_df["availability_365"].median()

borough_counts = filtered_df["neighbourhood_group"].value_counts()
top_borough = borough_counts.index[0] if not borough_counts.empty else "N/A"
top_borough_share = (borough_counts.iloc[0] / FILTERED_COUNT * 100) if not borough_counts.empty else 0

st.markdown(
    f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-title">Filtered Listings</div>
            <div class="kpi-value">{FILTERED_COUNT:,}</div>
            <div class="kpi-caption">{pct_active:.1f}% of total supply</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Median Nightly Price</div>
            <div class="kpi-value">${median_price:,.0f}</div>
            <div class="kpi-caption">USD per night</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Median Reviews / Mo</div>
            <div class="kpi-value">{median_rpm:.2f}</div>
            <div class="kpi-caption">Demand velocity proxy</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Median Availability</div>
            <div class="kpi-value">{median_avail:.0f}d</div>
            <div class="kpi-caption">Days open per year</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Largest Supply Borough</div>
            <div class="kpi-value" style="font-size:1.25rem; font-family:inherit;">{top_borough}</div>
            <div class="kpi-caption">{top_borough_share:.1f}% of active market</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# 6. MAIN NAVIGATION TABS
# -------------------------------------------------------------
tab_overview, tab_map, tab_price, tab_demand, tab_neighborhoods, tab_methodology = st.tabs(
    [
        "📊 1. Overview",
        "🗺️ 2. Market Map",
        "💲 3. Price Analysis",
        "📈 4. Demand & Availability",
        "🏘️ 5. Neighborhood Insights",
        "📖 6. Methodology & Caveats",
    ]
)

# =============================================================
# TAB 1: OVERVIEW
# =============================================================
with tab_overview:
    # Dynamic Takeaways Callout
    overview_insights = generate_overview_insights(filtered_df)
    insights_html = "".join([f"<li>{item}</li>" for item in overview_insights])
    st.markdown(
        f"""
        <div class="insight-callout">
            <h4>💡 Dynamic Market Observations</h4>
            <ul>{insights_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([3, 2])
    with col1:
        st.plotly_chart(build_borough_supply_chart(filtered_df), use_container_width=True)
    with col2:
        st.plotly_chart(build_room_type_mix_chart(filtered_df), use_container_width=True)

    st.plotly_chart(
        build_price_distribution_chart(filtered_df, price_cap=selected_price_cap),
        use_container_width=True,
    )
    st.markdown(
        f"<p class='chart-caption'>* Note: Nightly price distributions are right-skewed; display is capped at ${selected_price_cap:,.0f} "
        "to ensure visual legibility of medians and quartiles. Adjust display cap in the sidebar.</p>",
        unsafe_allow_html=True,
    )

# =============================================================
# TAB 2: MARKET MAP
# =============================================================
with tab_map:
    st.markdown(
        """
        <div class="caveat-notice">
            <strong>Geospatial Principle:</strong> High listing density does not automatically indicate high pricing. 
            Compare supply concentration against median price to differentiate volume markets (e.g., Bedford-Stuyvesant) 
            from high-yield luxury clusters (e.g., Midtown / Tribeca).
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Primary Map
    st.plotly_chart(
        build_market_map(filtered_df, metric=selected_map_metric, price_cap=selected_price_cap),
        use_container_width=True,
    )

    st.markdown(
        f"<p class='chart-caption'>Token-free map rendered via Carto-Positron tiles. Current Mode: <strong>{selected_map_metric}</strong>.</p>",
        unsafe_allow_html=True,
    )

    # Supporting Visual: Supply vs Price Bubble Chart
    st.plotly_chart(build_supply_vs_price_chart(filtered_df), use_container_width=True)
    st.markdown(
        "<p class='chart-caption'>Bubble size denotes total reviews (cumulative activity proxy). "
        "Notice how Manhattan and Brooklyn dominate supply, but Manhattan pulls away significantly in median price.</p>",
        unsafe_allow_html=True,
    )

# =============================================================
# TAB 3: PRICE ANALYSIS
# =============================================================
with tab_price:
    price_insights = generate_price_insights(filtered_df, price_cap=selected_price_cap)
    p_insights_html = "".join([f"<li>{item}</li>" for item in price_insights])
    st.markdown(
        f"""
        <div class="insight-callout">
            <h4>💡 Pricing Structure & Dispersion Insights</h4>
            <ul>{p_insights_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.plotly_chart(
            build_price_by_borough_room_chart(filtered_df, price_cap=selected_price_cap),
            use_container_width=True,
        )
    with col_p2:
        st.plotly_chart(build_price_tier_composition_chart(filtered_df), use_container_width=True)

    st.plotly_chart(
        build_min_nights_vs_price_chart(filtered_df, price_cap=selected_price_cap),
        use_container_width=True,
    )
    st.markdown(
        "<p class='chart-caption'>* Shows association between minimum stay requirements and advertised nightly rate. "
        "NYC's 30-day minimum stay rule (for unhosted rentals) creates visible clustering at 30 nights.</p>",
        unsafe_allow_html=True,
    )

# =============================================================
# TAB 4: DEMAND & AVAILABILITY
# =============================================================
with tab_demand:
    demand_insights = generate_demand_insights(filtered_df)
    d_insights_html = "".join([f"<li>{item}</li>" for item in demand_insights])
    st.markdown(
        f"""
        <div class="insight-callout">
            <h4>💡 Behavioral & Portfolio Insights</h4>
            <ul>{d_insights_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.plotly_chart(
            build_reviews_vs_price_chart(filtered_df, price_cap=selected_price_cap),
            use_container_width=True,
        )
        st.markdown(
            "<p class='chart-caption'>* Caution: Reviews represent an imperfect demand and booking proxy, "
            "not verified revenue or occupancy rates.</p>",
            unsafe_allow_html=True,
        )
    with col_d2:
        st.plotly_chart(build_availability_by_borough_chart(filtered_df), use_container_width=True)
        st.markdown(
            "<p class='chart-caption'>* Caution: Availability reflects calendar days unbooked or open, "
            "which may reflect unlisted calendars rather than true vacancy.</p>",
            unsafe_allow_html=True,
        )

    st.plotly_chart(build_host_portfolio_chart(filtered_df), use_container_width=True)
    st.markdown(
        "<p class='chart-caption'>Single-listing hosts (1 property) vs Small portfolios (2-5) vs Professional / commercial operators (6+).</p>",
        unsafe_allow_html=True,
    )

# =============================================================
# TAB 5: NEIGHBORHOOD INSIGHTS
# =============================================================
with tab_neighborhoods:
    st.markdown("### 🏘️ Micro-Market Neighborhood Analysis")

    col_n1, col_n2 = st.columns([2, 2])
    with col_n1:
        min_thresh = st.slider(
            "Minimum Listings Threshold",
            min_value=5,
            max_value=100,
            value=20,
            step=5,
            help="Filters out micro-neighborhoods with low sample sizes to prevent skewing median values.",
        )
    with col_n2:
        rank_view = st.radio(
            "Ranking View",
            options=["Top 10 (Highest Price)", "Bottom 10 (Budget / Accessible)"],
            horizontal=True,
        )

    df_neigh = compute_neighborhood_aggregates(filtered_df, min_listings=min_thresh)

    if df_neigh.empty:
        st.info("No neighborhoods satisfy the minimum listing threshold under current filter conditions.")
    else:
        # Comparison Chart
        st.plotly_chart(
            build_neighborhood_ranked_chart(df_neigh, ranking_type=rank_view),
            use_container_width=True,
        )

        st.markdown("#### Neighborhood Benchmark Table")
        st.markdown(
            "<p style='font-size:0.85rem; color:#94A3B8;'>"
            "<strong>Relative Value Signal:</strong> An exploratory composite score (0-100) that balances accessible median pricing with higher monthly review velocity. "
            "Higher scores highlight active, affordable micro-markets without making causal investment claims."
            "</p>",
            unsafe_allow_html=True,
        )

        # Formatting table for display
        display_table = df_neigh.rename(
            columns={
                "neighbourhood": "Neighborhood",
                "neighbourhood_group": "Borough",
                "listings": "Listings",
                "median_price": "Median Nightly Price ($)",
                "median_reviews_per_month": "Median Reviews/Mo",
                "median_availability": "Median Avail (Days)",
                "dominant_room_type": "Dominant Room Type",
                "relative_value_score": "Relative Value Signal (0-100)",
            }
        )[
            [
                "Neighborhood",
                "Borough",
                "Listings",
                "Median Nightly Price ($)",
                "Median Reviews/Mo",
                "Median Avail (Days)",
                "Dominant Room Type",
                "Relative Value Signal (0-100)",
            ]
        ]

        st.dataframe(
            display_table.style.format(
                {
                    "Listings": "{:,}",
                    "Median Nightly Price ($)": "${:,.0f}",
                    "Median Reviews/Mo": "{:.2f}",
                    "Median Avail (Days)": "{:.0f}",
                    "Relative Value Signal (0-100)": "{:.1f}",
                }
            ),
            use_container_width=True,
            height=400,
        )

# =============================================================
# TAB 6: METHODOLOGY & LIMITATIONS
# =============================================================
with tab_methodology:
    st.markdown("### 📖 Methodology, Data Lineage & Limitations")
    st.markdown(
        """
        #### 1. Data Source & Coverage
        This project analyzes the public **New York City Airbnb Open Data** dataset (2019) published on Kaggle 
        by user *dgomonov* (`dgomonov/new-york-city-airbnb-open-data`). The data comprises **48,895 original records** 
        representing advertised listings across all five NYC boroughs up to mid-2019.

        #### 2. Cleaning & Transformation Rules
        - **Record Validation:** Verified all 16 canonical schema columns exist.
        - **Spatial Integrity:** Excluded records missing geographic coordinates (`latitude`, `longitude`), `price`, or borough classification.
        - **Price Sanitization:** Removed non-positive prices (`price <= 0`).
        - **Missing Review Imputation:** Missing values in `reviews_per_month` are preserved in the raw column and filled with `0.0` exclusively in an explicit analytical column (`reviews_per_month_filled`) to avoid skewing zero-review properties.
        - **String Normalization:** Whitespace trimmed across all categorical text fields.

        #### 3. Derived Analytical Metrics
        - **`log_price`:** `log(1 + price)` computed to stabilize heavy right-tailed price distributions during regression/correlation analysis.
        - **`price_tier`:** Stratified using overall dataset quartiles:
          - *Budget:* $\\le Q1$ (Bottom 25%)
          - *Mid-range:* $Q1 < x \\le Q2$
          - *Premium:* $Q2 < x \\le Q3$
          - *Luxury:* $> Q3$ (Top 25%)
        - **`host_category`:** Host segmentation into:
          - *Single-listing host:* 1 listing
          - *Small portfolio:* 2–5 listings
          - *Professional host:* 6+ listings
        - **`review_activity`:** Segmented into Low, Moderate, and High based on non-zero monthly review tertiles.
        - **`relative_value_score`:** Composite metric normalized between 0 and 100:
          $$Score = 50 \\times (1 - \\text{Price}_{\\text{norm}}) + 50 \\times \\text{Reviews}_{\\text{norm}}$$
          This highlights micro-markets that provide above-average review demand velocity at below-average median pricing.

        #### 4. Critical Analytical Limitations & Cautions
        - **Calendar Availability $\\neq$ Occupancy:** `availability_365` measures the number of days a host opened their calendar. A zero-availability listing could mean it was fully booked 365 days, or that the host deactivated the listing. It must never be confused with confirmed occupancy or revenue.
        - **Reviews as an Imperfect Demand Proxy:** Not all guests leave reviews (typical Airbnb review rates range between 50%–70%). Review counts indicate booking velocity rather than total guest volume or host profitability.
        - **Advertised Rate $\\neq$ Realized Revenue:** Listed prices do not include cleaning fees, taxes, or seasonal discounts.
        - **Association vs. Causation:** All relationships identified (e.g., between minimum nights and prices, or borough and review rates) are purely correlative and observational.
        """
    )
