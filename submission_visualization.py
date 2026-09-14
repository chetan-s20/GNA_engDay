"""Generate the high-resolution static visualization used for panel judging.

Run:
    python submission_visualization.py

Output:
    submission/nyc_airbnb_market_intelligence.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "AB_NYC_2019.csv"
OUTPUT_PATH = ROOT / "submission" / "nyc_airbnb_market_intelligence.png"

BACKGROUND = "#101216"
SURFACE = "#171A1F"
INK = "#F3F0E8"
MUTED = "#AAA79F"
GRID = "#30343A"
ACCENT = "#F5B942"

BOROUGH_COLORS = {
    "Manhattan": "#F5B942",
    "Brooklyn": "#CF6A4C",
    "Queens": "#4D9B8F",
    "Bronx": "#7986B7",
    "Staten Island": "#A77B9E",
}

ROOM_COLORS = {
    "Entire home/apt": "#F5B942",
    "Private room": "#5A93A8",
    "Shared room": "#B77A6A",
}


def style_axis(ax: plt.Axes) -> None:
    """Apply the shared dark editorial chart treatment."""
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=MUTED, labelsize=9, length=0)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    ax.title.set_color(INK)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=0.7, alpha=0.65)
    ax.set_axisbelow(True)


def load_data() -> pd.DataFrame:
    """Load and minimally clean the source data for the static submission."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    frame = pd.read_csv(DATA_PATH)
    numeric = [
        "latitude",
        "longitude",
        "price",
        "minimum_nights",
        "number_of_reviews",
        "reviews_per_month",
        "availability_365",
    ]
    for column in numeric:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    frame = frame.dropna(
        subset=["latitude", "longitude", "price", "neighbourhood_group", "room_type"]
    ).copy()
    frame = frame[frame["price"] > 0].copy()
    frame["reviews_per_month_filled"] = frame["reviews_per_month"].fillna(0)
    return frame


def add_heading(fig: plt.Figure, listing_count: int) -> None:
    """Add title, participant attribution, and dataset context."""
    fig.text(
        0.045,
        0.955,
        "NYC AIRBNB MARKET INTELLIGENCE",
        color=INK,
        fontsize=27,
        fontweight="bold",
        ha="left",
        va="top",
    )
    fig.text(
        0.045,
        0.915,
        "The price of place across 48,884 New York City listings",
        color=MUTED,
        fontsize=13,
        ha="left",
        va="top",
    )
    fig.text(
        0.955,
        0.952,
        "ANKUSH THAKUR  /  GU-2024-3416\nPYTHON TRACK  /  2019 DATA",
        color=MUTED,
        fontsize=8.5,
        fontweight="bold",
        ha="right",
        va="top",
        linespacing=1.6,
    )
    fig.text(
        0.045,
        0.035,
        f"Source: NYC Airbnb Open Data (Kaggle)  |  {listing_count:,} positive-price listings  |  "
        "Listed price is descriptive and does not represent realized revenue.",
        color="#777B82",
        fontsize=7.5,
        ha="left",
    )


def add_map(ax: plt.Axes, frame: pd.DataFrame) -> None:
    """Draw the recognizable geographic footprint of the five boroughs."""
    sns.scatterplot(
        data=frame,
        x="longitude",
        y="latitude",
        hue="neighbourhood_group",
        palette=BOROUGH_COLORS,
        s=7,
        alpha=0.34,
        linewidth=0,
        legend=False,
        rasterized=True,
        ax=ax,
    )
    centers = frame.groupby("neighbourhood_group")[["longitude", "latitude"]].median()
    offsets = {
        "Manhattan": (-0.005, 0.008),
        "Brooklyn": (0.004, -0.012),
        "Queens": (0.020, 0.008),
        "Bronx": (0.004, 0.010),
        "Staten Island": (-0.002, -0.004),
    }
    for borough, row in centers.iterrows():
        dx, dy = offsets.get(borough, (0, 0))
        ax.text(
            row["longitude"] + dx,
            row["latitude"] + dy,
            borough.upper(),
            color=INK,
            fontsize=7.5,
            fontweight="bold",
            ha="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=BACKGROUND, edgecolor="none", alpha=0.82),
        )

    ax.set_title(
        "SUPPLY FORMS A DISTINCT GEOGRAPHIC MARKET",
        loc="left",
        fontsize=11,
        fontweight="bold",
        color=INK,
        pad=13,
    )
    ax.text(
        0,
        1.01,
        "Each mark is one listing; color identifies borough.",
        transform=ax.transAxes,
        color=MUTED,
        fontsize=8.5,
        va="bottom",
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)

    handles = [
        Line2D([0], [0], marker="o", color="none", label=name, markerfacecolor=color, markersize=7)
        for name, color in BOROUGH_COLORS.items()
    ]
    legend = ax.legend(
        handles=handles,
        loc="lower left",
        ncol=2,
        frameon=False,
        fontsize=8,
        labelcolor=MUTED,
        handletextpad=0.3,
        columnspacing=0.8,
    )
    legend.set_zorder(10)


def add_supply_chart(ax: plt.Axes, frame: pd.DataFrame) -> None:
    """Show borough listing volume and share."""
    supply = frame["neighbourhood_group"].value_counts().sort_values()
    bars = ax.barh(
        supply.index,
        supply.values,
        color=[BOROUGH_COLORS[name] for name in supply.index],
        height=0.58,
    )
    for bar, count in zip(bars, supply.values):
        share = count / len(frame) * 100
        ax.text(
            count + 320,
            bar.get_y() + bar.get_height() / 2,
            f"{count:,}  {share:.1f}%",
            va="center",
            color=INK,
            fontsize=8.5,
            fontweight="bold",
        )
    ax.set_xlim(0, supply.max() * 1.28)
    ax.set_title(
        "MANHATTAN + BROOKLYN HOLD 85% OF SUPPLY",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        color=INK,
        pad=12,
    )
    ax.set_xlabel("Listings", fontsize=8)
    ax.set_ylabel("")
    style_axis(ax)


def add_price_chart(ax: plt.Axes, frame: pd.DataFrame) -> None:
    """Compare robust median price by borough and room type."""
    price_summary = (
        frame.groupby(["neighbourhood_group", "room_type"], as_index=False)["price"]
        .median()
        .rename(columns={"price": "median_price"})
    )
    borough_order = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
    sns.barplot(
        data=price_summary,
        x="median_price",
        y="neighbourhood_group",
        hue="room_type",
        order=borough_order,
        hue_order=["Entire home/apt", "Private room", "Shared room"],
        palette=ROOM_COLORS,
        ax=ax,
    )
    ax.set_title(
        "ROOM TYPE AMPLIFIES THE LOCATION PREMIUM",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        color=INK,
        pad=12,
    )
    ax.set_xlabel("Median nightly price (USD)", fontsize=8)
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(lambda value, _: f"${value:.0f}")
    legend = ax.legend(
        title=None,
        frameon=False,
        fontsize=7.5,
        labelcolor=MUTED,
        loc="lower right",
    )
    for text in legend.get_texts():
        text.set_color(MUTED)
    style_axis(ax)


def add_neighborhood_chart(ax: plt.Axes, frame: pd.DataFrame) -> None:
    """Contrast established premium and accessible neighborhoods."""
    neighborhoods = (
        frame.groupby(["neighbourhood_group", "neighbourhood"], as_index=False)
        .agg(listings=("id", "size"), median_price=("price", "median"))
    )
    eligible = neighborhoods[neighborhoods["listings"] >= 100]
    selected = pd.concat(
        [eligible.nlargest(3, "median_price"), eligible.nsmallest(3, "median_price")]
    ).sort_values("median_price")
    colors = [BOROUGH_COLORS[name] for name in selected["neighbourhood_group"]]
    bars = ax.barh(selected["neighbourhood"], selected["median_price"], color=colors, height=0.58)
    for bar, price in zip(bars, selected["median_price"]):
        ax.text(
            price + 5,
            bar.get_y() + bar.get_height() / 2,
            f"${price:,.0f}",
            va="center",
            color=INK,
            fontsize=8.5,
            fontweight="bold",
        )
    ax.set_xlim(0, selected["median_price"].max() * 1.22)
    ax.set_title(
        "PRICE GAP PERSISTS IN ESTABLISHED MARKETS",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        color=INK,
        pad=12,
    )
    ax.set_xlabel("Median nightly price; neighborhoods with 100+ listings", fontsize=8)
    ax.set_ylabel("")
    style_axis(ax)


def add_insight_strip(fig: plt.Figure, frame: pd.DataFrame) -> None:
    """Add three computed findings as a compact evidence strip."""
    manhattan_share = (frame["neighbourhood_group"] == "Manhattan").mean() * 100
    overall_median = frame["price"].median()
    room_medians = frame.groupby("room_type")["price"].median()
    premium = (room_medians["Entire home/apt"] / room_medians["Private room"] - 1) * 100
    findings = [
        (f"{manhattan_share:.1f}%", "of all listings are in Manhattan"),
        (f"${overall_median:,.0f}", "citywide median nightly price"),
        (f"+{premium:.0f}%", "entire-home median vs private room"),
    ]
    x_positions = [0.05, 0.26, 0.47]
    for x, (value, label) in zip(x_positions, findings):
        fig.text(x, 0.118, value, color=ACCENT, fontsize=19, fontweight="bold", ha="left")
        fig.text(x, 0.091, label, color=MUTED, fontsize=8.2, ha="left")


def build_visualization(frame: pd.DataFrame) -> plt.Figure:
    """Compose the final 16:9 judging artifact."""
    sns.set_theme(style="ticks")
    figure = plt.figure(figsize=(16, 9), dpi=150, facecolor=BACKGROUND)
    grid = figure.add_gridspec(
        15,
        16,
        left=0.045,
        right=0.955,
        top=0.84,
        bottom=0.16,
        wspace=1.35,
        hspace=2.4,
    )

    map_axis = figure.add_subplot(grid[:, :9])
    supply_axis = figure.add_subplot(grid[:4, 10:])
    price_axis = figure.add_subplot(grid[5:9, 10:])
    neighborhood_axis = figure.add_subplot(grid[10:, 10:])

    for axis in [map_axis, supply_axis, price_axis, neighborhood_axis]:
        style_axis(axis)

    add_heading(figure, len(frame))
    add_map(map_axis, frame)
    add_supply_chart(supply_axis, frame)
    add_price_chart(price_axis, frame)
    add_neighborhood_chart(neighborhood_axis, frame)
    add_insight_strip(figure, frame)
    return figure


def main() -> None:
    """Generate and save the panel-ready PNG."""
    frame = load_data()
    figure = build_visualization(frame)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT_PATH, dpi=150, facecolor=BACKGROUND)
    plt.close(figure)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
