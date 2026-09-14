"""Visual design system and custom styling for the NYC Airbnb Market Intelligence Dashboard."""

# Borough color palette - muted yet distinguishable with high contrast
BOROUGH_COLORS = {
    "Manhattan": "#F5B942",
    "Brooklyn": "#CF6A4C",
    "Queens": "#4D9B8F",
    "Bronx": "#7986B7",
    "Staten Island": "#A77B9E",
}

# Room type colors
ROOM_TYPE_COLORS = {
    "Entire home/apt": "#F5B942",
    "Private room": "#5A93A8",
    "Shared room": "#B77A6A",
}

# Price tier colors
PRICE_TIER_COLORS = {
    "Budget": "#10B981",
    "Mid-range": "#3B82F6",
    "Premium": "#F59E0B",
    "Luxury": "#EF4444",
}

# Host category colors
HOST_CATEGORY_COLORS = {
    "Single-listing host": "#10B981",
    "Small portfolio": "#6366F1",
    "Professional host": "#F59E0B",
    "Unknown": "#64748B",
}

# Custom Streamlit CSS injection
CUSTOM_CSS = """
<style>
    :root {
        --ink: #F3F0E8;
        --muted: #AAA79F;
        --surface: #171A1F;
        --surface-raised: #1E2228;
        --line: #34383F;
        --yellow: #F5B942;
        --blue: #74A8BA;
    }

    [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: #101216;
        color: var(--ink);
    }
    [data-testid="stSidebar"] {
        background: #15181D;
        border-right: 1px solid var(--line);
    }
    .block-container {
        max-width: 1480px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    ::selection { background: #F5B942; color: #101216; }
    a { color: #8DBAC9 !important; text-underline-offset: 3px; }
    :focus-visible { outline: 2px solid var(--yellow) !important; outline-offset: 2px; }

    h1, h2, h3, h4, h5, h6 {
        color: var(--ink) !important;
        font-family: "Avenir Next", "Segoe UI", sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    p, label, [data-testid="stMarkdownContainer"] { font-size: 0.94rem; }

    .editorial-header {
        border-top: 1px solid var(--line);
        border-bottom: 1px solid var(--line);
        padding: 28px 0 24px;
        margin-bottom: 22px;
    }
    .editorial-header h1 {
        margin: 0 0 8px 0;
        max-width: 900px;
        color: var(--ink) !important;
        font-size: clamp(2rem, 5vw, 4.35rem);
        line-height: 0.98;
        letter-spacing: -0.04em;
    }
    .editorial-header p {
        margin: 0;
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.6;
        max-width: 72ch;
    }
    .badge-bar {
        margin-top: 14px;
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
    }
    .editorial-badge {
        display: inline-flex;
        align-items: center;
        padding: 5px 10px;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        background: rgba(245, 185, 66, 0.08);
        color: #F5C969;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .editorial-badge-blue {
        display: inline-flex;
        align-items: center;
        padding: 5px 10px;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        background: rgba(116, 168, 186, 0.1);
        color: #9BC8D7;
        border: 1px solid rgba(116, 168, 186, 0.35);
    }

    /* KPI metric cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 10px;
        margin-bottom: 28px;
    }
    .kpi-card {
        background: var(--surface);
        border-top: 2px solid var(--line);
        border-radius: 12px;
        padding: 18px 18px 16px;
        transition: border-color 0.15s ease;
    }
    .kpi-card:hover {
        border-color: var(--yellow);
    }
    .kpi-title {
        color: #B6B3AA;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: var(--ink);
        font-size: 1.75rem;
        font-weight: 800;
        line-height: 1.2;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    .kpi-caption {
        color: #AAA79F;
        font-size: 0.875rem;
        margin-top: 4px;
    }

    /* Dynamic Insight Callout Box */
    .insight-callout {
        background: #191C21;
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 16px 18px;
        margin: 18px 0;
    }
    .insight-callout h4 {
        margin: 0 0 6px 0;
        font-size: 0.9rem;
        color: #F5C969 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .insight-callout ul {
        margin: 0;
        padding-left: 18px;
        color: #D8D5CD;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    /* Caution & Caveats Notice */
    .caveat-notice {
        background: rgba(245, 158, 11, 0.06);
        border: 1px solid rgba(245, 185, 66, 0.35);
        border-radius: 10px;
        padding: 12px 16px;
        margin: 12px 0 20px 0;
        font-size: 0.9rem;
        color: #F3D98D;
        line-height: 1.5;
    }

    /* Clean Streamlit tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid var(--line);
        padding-bottom: 4px;
        overflow-x: auto;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 8px;
        padding: 0 16px;
        font-size: 0.9rem;
        font-weight: 600;
        background-color: transparent;
        color: #94A3B8;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #272B31 !important;
        color: var(--ink) !important;
    }

    /* Plotly chart container styling */
    .chart-container {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }
    .chart-caption {
        font-size: 0.88rem;
        color: #AAA79F;
        margin-top: 6px;
        line-height: 1.55;
    }
    .chart-deck {
        color: #B8B5AD;
        font-size: 0.9rem;
        margin: -0.35rem 0 0.8rem;
        max-width: 76ch;
    }
    [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 12px; }
    [data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }

    @media (max-width: 700px) {
        .block-container { padding: 1rem 0.8rem 3rem; }
        .editorial-header { padding: 20px 0; }
        .editorial-header h1 { font-size: 2.35rem; line-height: 1.02; }
        .badge-bar { gap: 7px; }
        .kpi-container { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .kpi-card { padding: 14px; }
        .kpi-value { font-size: 1.45rem; }
        .stTabs [data-baseweb="tab"] { min-width: max-content; padding: 0 12px; }
    }
    @media (max-width: 420px) {
        .kpi-container { grid-template-columns: 1fr; }
    }
</style>
"""

def apply_plotly_theme(fig):
    """Apply consistent editorial styling to any Plotly figure."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#101216",
        plot_bgcolor="#171A1F",
        font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            color="#E8E5DD",
            size=14
        ),
        margin=dict(l=40, r=30, t=50, b=40),
        legend=dict(
            bgcolor="rgba(23, 26, 31, 0.92)",
            bordercolor="rgba(255, 255, 255, 0.1)",
            borderwidth=1,
            font=dict(size=13, color="#D8D5CD")
        ),
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=14,
            font_family="monospace",
            font_color="#F8FAFC"
        )
    )
    # Style axes
    fig.update_xaxes(
        gridcolor="#2C3036",
        zerolinecolor="#3B4048",
        showline=True,
        linecolor="#3B4048"
    )
    fig.update_yaxes(
        gridcolor="#2C3036",
        zerolinecolor="#3B4048",
        showline=True,
        linecolor="#3B4048"
    )
    return fig
