"""NYC Airbnb Market Intelligence Dashboard

Production-grade Streamlit application fulfilling all specifications in prd.md.
"""

from pathlib import Path
import html
import re

import streamlit as st

# Page configuration - must be very first Streamlit call
st.set_page_config(
    page_title="NYC Airbnb Market Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.styles import CUSTOM_CSS
from src.data import (
    load_source_data,
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


def insight_list_html(items: list[str]) -> str:
    """Render trusted computed insights while preserving their emphasis markers."""
    rendered = []
    for item in items:
        safe_item = html.escape(item)
        safe_item = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe_item)
        rendered.append(f"<li>{safe_item}</li>")
    return "".join(rendered)

# Inject custom editorial CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -------------------------------------------------------------
# 1. FILE EXISTENCE & LOADING PIPELINE
# -------------------------------------------------------------
DATA_PATH = Path(__file__).resolve().parent / "data" / "AB_NYC_2019.csv"

if not DATA_PATH.exists():
    st.error("Dataset file missing: `data/AB_NYC_2019.csv` was not found.")
    st.markdown(
        """
        ### How to set up the data:
        1. Download the New York City Airbnb Open Data from Kaggle:
           [Kaggle Dataset: dgomonov/new-york-city-airbnb-open-data](https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data)
        2. Place the unzipped `AB_NYC_2019.csv` file into the `data/` folder:
           ```text
           data/AB_NYC_2019.csv
           ```
        3. Refresh this page.
        """
    )
    st.stop()

try:
    raw_df = load_source_data(str(DATA_PATH))
    df_clean = load_and_prepare_data(str(DATA_PATH))
except Exception as e:
    st.error(f"Error loading and processing dataset: {e}")
    st.stop()

TOTAL_LISTINGS = len(df_clean)

# -------------------------------------------------------------
# 2. SIDEBAR CONTROLS & FILTERS
# -------------------------------------------------------------
st.sidebar.markdown("## Explore the Market")
st.sidebar.markdown(
    "<p style='font-size:0.88rem; color:#AAA79F; margin-top:-10px;'>"
    "Interactive filters dynamically update all metrics, charts, maps, and insights."
    "</p>",
    unsafe_allow_html=True,
)

# Reset filters mechanism
if st.sidebar.button("Reset all filters", width="stretch"):
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
max_p = float(df_clean["price"].max())
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
    max_value=int(df_clean["number_of_reviews"].max()),
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
st.sidebar.markdown("### Visualization Options")

# Price display cap (for skew control)
price_cap_options = sorted({500.0, 1000.0, 2000.0, 5000.0, max_p})
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
    <div style='background:#1E2228; border-top:2px solid #F5B942; border-radius:12px; padding:14px; text-align:center;'>
        <div style='font-size:0.875rem; color:#B6B3AA; text-transform:uppercase; letter-spacing:.05em;'>Listings in view</div>
        <div style='font-size:1.4rem; font-weight:800; color:#F3F0E8; font-variant-numeric:tabular-nums;'>{FILTERED_COUNT:,} <span style='font-size:0.875rem; color:#AAA79F;'>/ {TOTAL_LISTINGS:,}</span></div>
        <div style='font-size:0.875rem; color:#AAA79F; margin-top:2px;'>{pct_active:.1f}% of cleaned listings</div>
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
        <p>How location, room type, and listing behavior shaped New York City's short-term rental market in 2019.</p>
        <div class="badge-bar">
            <span class="editorial-badge">Ankush Thakur · GU-2024-3416</span>
            <span class="editorial-badge">48K+ listings · 5 boroughs</span>
            <a class="editorial-badge-blue" href="https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data" target="_blank">Kaggle source</a>
            <span class="editorial-badge">Descriptive, not causal</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Empty filter state check
if filtered_df.empty:
    st.warning("No listings match the chosen filter combination.")
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
            <div class="kpi-caption">Review activity proxy</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Median Availability</div>
            <div class="kpi-value">{median_avail:.0f}d</div>
            <div class="kpi-caption">Days open per year</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Largest Supply Borough</div>
            <div class="kpi-value" style="font-size:1.25rem; font-family:inherit;">{top_borough}</div>
            <div class="kpi-caption">{top_borough_share:.1f}% of filtered market</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# 6. MAIN NAVIGATION TABS
# -------------------------------------------------------------
tab_map, tab_overview, tab_price, tab_demand, tab_neighborhoods, tab_methodology = st.tabs(
    [
        "Market Map",
        "Overview",
        "Price Analysis",
        "Demand & Availability",
        "Neighborhoods",
        "Methodology",
    ]
)

# =============================================================
# TAB 1: OVERVIEW
# =============================================================
with tab_overview:
    # Dynamic Takeaways Callout
    overview_insights = generate_overview_insights(filtered_df)
    insights_html = insight_list_html(overview_insights)
    st.markdown(
        f"""
        <div class="insight-callout">
             <h4>Market observations</h4>
            <ul>{insights_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("<p class='chart-deck'>Compare each borough's volume and share of the currently filtered market.</p>", unsafe_allow_html=True)
        st.plotly_chart(build_borough_supply_chart(filtered_df), width="stretch")
    with col2:
        st.markdown("<p class='chart-deck'>See how entire homes, private rooms, and shared rooms divide available supply.</p>", unsafe_allow_html=True)
        st.plotly_chart(build_room_type_mix_chart(filtered_df), width="stretch")

    st.markdown("<p class='chart-deck'>Compare medians and dispersion rather than relying on averages in this right-skewed market.</p>", unsafe_allow_html=True)
    st.plotly_chart(
        build_price_distribution_chart(filtered_df, price_cap=selected_price_cap),
        width="stretch",
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
            <strong>Read the map in layers:</strong> high listing density does not automatically indicate high pricing.
            Switch between supply, median price, and review activity to distinguish high-volume areas from premium areas.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<p class='chart-deck'>Neighborhood centroids summarize every filtered listing and expose the same core metrics in each hover state.</p>", unsafe_allow_html=True)
    st.plotly_chart(
        build_market_map(filtered_df, metric=selected_map_metric, price_cap=selected_price_cap),
        width="stretch",
    )

    st.markdown(
        f"<p class='chart-caption'>Locally rendered longitude/latitude view with no external tile dependency. Current layer: <strong>{selected_map_metric}</strong>. Price mode applies the ${selected_price_cap:,.0f} display cap.</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<p class='chart-deck'>Bubble position separates supply scale from price level; bubble area represents cumulative review activity.</p>", unsafe_allow_html=True)
    st.plotly_chart(build_supply_vs_price_chart(filtered_df), width="stretch")
    st.markdown(
        "<p class='chart-caption'>Bubble size represents total reviews, an imperfect activity proxy. Interpret the current filtered selection rather than assuming a fixed borough ranking.</p>",
        unsafe_allow_html=True,
    )

# =============================================================
# TAB 3: PRICE ANALYSIS
# =============================================================
with tab_price:
    price_insights = generate_price_insights(filtered_df, price_cap=selected_price_cap)
    p_insights_html = insight_list_html(price_insights)
    st.markdown(
        f"""
        <div class="insight-callout">
             <h4>Pricing observations</h4>
            <ul>{p_insights_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("<p class='chart-deck'>Median prices reveal the room-type premium within each borough.</p>", unsafe_allow_html=True)
        st.plotly_chart(
            build_price_by_borough_room_chart(filtered_df, price_cap=selected_price_cap),
            width="stretch",
        )
    with col_p2:
        st.markdown("<p class='chart-deck'>Price quartiles show how each borough's inventory is distributed across market tiers.</p>", unsafe_allow_html=True)
        st.plotly_chart(build_price_tier_composition_chart(filtered_df), width="stretch")

    st.markdown("<p class='chart-deck'>Explore the association between stay requirements and advertised nightly price.</p>", unsafe_allow_html=True)
    st.plotly_chart(
        build_min_nights_vs_price_chart(filtered_df, price_cap=selected_price_cap),
        width="stretch",
    )
    st.markdown(
        f"<p class='chart-caption'>Shows association, not causation. Prices above ${selected_price_cap:,.0f} and minimum stays above 60 nights are omitted from this view for legibility.</p>",
        unsafe_allow_html=True,
    )

# =============================================================
# TAB 4: DEMAND & AVAILABILITY
# =============================================================
with tab_demand:
    demand_insights = generate_demand_insights(filtered_df)
    d_insights_html = insight_list_html(demand_insights)
    st.markdown(
        f"""
        <div class="insight-callout">
             <h4>Activity and portfolio observations</h4>
            <ul>{d_insights_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("<p class='chart-deck'>Test whether review activity and advertised price move together in the filtered market.</p>", unsafe_allow_html=True)
        st.plotly_chart(
            build_reviews_vs_price_chart(filtered_df, price_cap=selected_price_cap),
            width="stretch",
        )
        st.markdown(
            f"<p class='chart-caption'>Reviews are an imperfect activity proxy, not verified demand, revenue, or quality. Prices above ${selected_price_cap:,.0f} are omitted.</p>",
            unsafe_allow_html=True,
        )
    with col_d2:
        st.markdown("<p class='chart-deck'>Compare the spread of calendar availability across boroughs.</p>", unsafe_allow_html=True)
        st.plotly_chart(build_availability_by_borough_chart(filtered_df), width="stretch")
        st.markdown(
            "<p class='chart-caption'>Availability reflects days marked open on the calendar, not confirmed occupancy, vacancy, or bookings.</p>",
            unsafe_allow_html=True,
        )

    st.markdown("<p class='chart-deck'>See how much listing supply is associated with individual hosts versus larger portfolios.</p>", unsafe_allow_html=True)
    st.plotly_chart(build_host_portfolio_chart(filtered_df), width="stretch")
    st.markdown(
        "<p class='chart-caption'>Single-listing hosts (1 property) vs Small portfolios (2-5) vs Professional / commercial operators (6+).</p>",
        unsafe_allow_html=True,
    )

# =============================================================
# TAB 5: NEIGHBORHOOD INSIGHTS
# =============================================================
with tab_neighborhoods:
    st.markdown("### Micro-Market Neighborhood Analysis")

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
        st.markdown("<p class='chart-deck'>Rank neighborhoods only after applying a minimum sample-size threshold to reduce small-market noise.</p>", unsafe_allow_html=True)
        st.plotly_chart(
            build_neighborhood_ranked_chart(df_neigh, ranking_type=rank_view),
            width="stretch",
        )

        st.markdown("#### Neighborhood Benchmark Table")
        st.markdown(
            "<p style='font-size:0.9rem; color:#AAA79F;'>"
            "<strong>Relative Value Signal:</strong> An exploratory composite score (0-100) that balances accessible median pricing with higher monthly review activity. "
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
            width="stretch",
            height=400,
        )

# =============================================================
# TAB 6: METHODOLOGY & LIMITATIONS
# =============================================================
with tab_methodology:
    st.markdown("### Methodology, Data Lineage & Limitations")
    excluded_rows = len(raw_df) - len(df_clean)
    cap_excluded = int((filtered_df["price"] > selected_price_cap).sum())
    missing_reviews = int(raw_df["reviews_per_month"].isna().sum())
    with st.expander("Data quality snapshot", expanded=True):
        q1, q2, q3, q4 = st.columns(4)
        q1.metric("Raw rows", f"{len(raw_df):,}")
        q2.metric("Clean rows", f"{len(df_clean):,}")
        q3.metric("Rows removed", f"{excluded_rows:,}")
        q4.metric("Above chart cap", f"{cap_excluded:,}")
        st.caption(
            f"The source contains {missing_reviews:,} missing monthly-review values. "
            "They remain missing in the raw field and are represented as zero only in the analysis field."
        )
    with st.expander("Methods and limitations", expanded=True):
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
        - **`review_activity`:** Segmented into Low, Moderate, and High using the first and third quartiles of positive monthly review activity.
        - **`is_price_outlier`:** Flags listings above the default $1,000 chart display cap; interactive charts recalculate against the selected cap.
        - **`relative_value_score`:** Composite metric normalized between 0 and 100:
          $$Score = 50 \\times (1 - \\text{Price}_{\\text{norm}}) + 50 \\times \\text{Reviews}_{\\text{norm}}$$
          This highlights micro-markets with above-average review activity and below-average median pricing.

        #### 4. Critical Analytical Limitations & Cautions
        - **Calendar Availability $\\neq$ Occupancy:** `availability_365` measures the number of days a host opened their calendar. A zero-availability listing could mean it was fully booked 365 days, or that the host deactivated the listing. It must never be confused with confirmed occupancy or revenue.
        - **Reviews as an Imperfect Activity Proxy:** Not all guests leave reviews. Review counts indicate observed review activity rather than total guest volume, demand, or host profitability.
        - **Advertised Rate $\\neq$ Realized Revenue:** Listed prices do not include cleaning fees, taxes, or seasonal discounts.
        - **Association vs. Causation:** All relationships identified (e.g., between minimum nights and prices, or borough and review rates) are purely correlative and observational.
        """
        )
