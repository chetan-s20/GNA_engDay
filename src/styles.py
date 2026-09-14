"""Visual design system and custom styling for the NYC Airbnb Market Intelligence Dashboard."""

# Borough color palette - muted yet distinguishable with high contrast
BOROUGH_COLORS = {
    "Manhattan": "#6366F1",      # Indigo
    "Brooklyn": "#EC4899",       # Rose / Pink
    "Queens": "#10B981",         # Emerald
    "Bronx": "#F59E0B",          # Amber / Taxi Yellow
    "Staten Island": "#06B6D4",   # Cyan
}

# Room type colors
ROOM_TYPE_COLORS = {
    "Entire home/apt": "#6366F1",
    "Private room": "#8B5CF6",
    "Shared room": "#14B8A6",
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
}

# Custom Streamlit CSS injection
CUSTOM_CSS = """
<style>
    /* Dark editorial styling */
    .main {
        background-color: #0B0F19;
        color: #E2E8F0;
    }
    
    /* Header typography */
    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Header banner styling */
    .editorial-header {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 24px;
    }
    .editorial-header h1 {
        margin: 0 0 8px 0;
        font-size: 2.2rem;
        background: linear-gradient(90deg, #FFFFFF 0%, #E2E8F0 60%, #F59E0B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .editorial-header p {
        margin: 0;
        color: #94A3B8;
        font-size: 0.95rem;
        line-height: 1.5;
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
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        background: rgba(245, 158, 11, 0.12);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .editorial-badge-blue {
        background: rgba(99, 102, 241, 0.12);
        color: #818CF8;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }

    /* KPI metric cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 12px;
        padding: 16px 20px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .kpi-card:hover {
        border-color: #374151;
        transform: translateY(-2px);
    }
    .kpi-title {
        color: #9CA3AF;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #F9FAFB;
        font-size: 1.75rem;
        font-weight: 800;
        line-height: 1.2;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    .kpi-caption {
        color: #6B7280;
        font-size: 0.75rem;
        margin-top: 4px;
    }

    /* Dynamic Insight Callout Box */
    .insight-callout {
        background: rgba(99, 102, 241, 0.08);
        border-left: 4px solid #6366F1;
        border-radius: 0 10px 10px 0;
        padding: 14px 18px;
        margin: 18px 0;
    }
    .insight-callout h4 {
        margin: 0 0 6px 0;
        font-size: 0.85rem;
        color: #A5B4FC !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .insight-callout ul {
        margin: 0;
        padding-left: 18px;
        color: #CBD5E1;
        font-size: 0.88rem;
        line-height: 1.6;
    }

    /* Caution & Caveats Notice */
    .caveat-notice {
        background: rgba(245, 158, 11, 0.06);
        border: 1px dashed rgba(245, 158, 11, 0.3);
        border-radius: 10px;
        padding: 12px 16px;
        margin: 12px 0 20px 0;
        font-size: 0.82rem;
        color: #FCD34D;
        line-height: 1.5;
    }

    /* Clean Streamlit tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #1F2937;
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 8px;
        padding: 0 16px;
        font-size: 0.85rem;
        font-weight: 600;
        background-color: transparent;
        color: #94A3B8;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
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
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 6px;
        font-style: italic;
    }
</style>
"""

def apply_plotly_theme(fig):
    """Apply consistent editorial styling to any Plotly figure."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B0F19",
        plot_bgcolor="#0F172A",
        font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            color="#E2E8F0",
            size=12
        ),
        margin=dict(l=40, r=30, t=50, b=40),
        legend=dict(
            bgcolor="rgba(15, 23, 42, 0.7)",
            bordercolor="rgba(255, 255, 255, 0.1)",
            borderwidth=1,
            font=dict(size=11, color="#CBD5E1")
        ),
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=12,
            font_family="monospace",
            font_color="#F8FAFC"
        )
    )
    # Style axes
    fig.update_xaxes(
        gridcolor="#1E293B",
        zerolinecolor="#334155",
        showline=True,
        linecolor="#334155"
    )
    fig.update_yaxes(
        gridcolor="#1E293B",
        zerolinecolor="#334155",
        showline=True,
        linecolor="#334155"
    )
    return fig
