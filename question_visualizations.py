"""Generate the three required question-answer images for the judging form.

Run:
    uv run python question_visualizations.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
import seaborn as sns

from submission_visualization import (
    ACCENT,
    BACKGROUND,
    BOROUGH_COLORS,
    DATA_PATH,
    GRID,
    INK,
    MUTED,
    ROOM_COLORS,
    SURFACE,
    load_data,
    style_axis,
)


OUTPUT_DIR = Path(__file__).resolve().parent / "submission"


def create_canvas(question_number: int, title: str, subtitle: str) -> plt.Figure:
    """Create a consistent 16:9 canvas for a form answer."""
    sns.set_theme(style="ticks")
    figure = plt.figure(figsize=(16, 9), dpi=150, facecolor=BACKGROUND)
    figure.text(
        0.045,
        0.955,
        f"QUESTION {question_number}",
        color=ACCENT,
        fontsize=10,
        fontweight="bold",
        ha="left",
        va="top",
    )
    figure.text(
        0.045,
        0.925,
        title,
        color=INK,
        fontsize=24,
        fontweight="bold",
        ha="left",
        va="top",
    )
    figure.text(
        0.045,
        0.878,
        subtitle,
        color=MUTED,
        fontsize=10.5,
        ha="left",
        va="top",
    )
    figure.text(
        0.955,
        0.952,
        "ANKUSH THAKUR  /  GU-2024-3416\nPYTHON TRACK  /  NYC AIRBNB 2019",
        color=MUTED,
        fontsize=8.5,
        fontweight="bold",
        ha="right",
        va="top",
        linespacing=1.6,
    )
    return figure


def add_footer(figure: plt.Figure, note: str) -> None:
    """Add shared source and methodological caveat copy."""
    figure.text(
        0.045,
        0.035,
        f"Source: NYC Airbnb Open Data (Kaggle)  |  {note}",
        color="#777B82",
        fontsize=7.5,
        ha="left",
    )


def save_figure(figure: plt.Figure, filename: str) -> Path:
    """Save a high-resolution image below the form's 10 MB limit."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / filename
    figure.savefig(output_path, dpi=150, facecolor=BACKGROUND)
    plt.close(figure)
    print(f"Saved {output_path}")
    return output_path


def generate_question_one(frame: pd.DataFrame) -> Path:
    """Answer how prices vary across neighborhoods and room types."""
    figure = create_canvas(
        1,
        "How do prices vary across neighborhoods and room types?",
        "Median prices reveal a consistent entire-home premium, amplified in central Manhattan neighborhoods.",
    )

    eligible = frame.groupby("neighbourhood").size()
    top_neighborhoods = eligible[eligible >= 100].nlargest(15).index
    selected = frame[frame["neighbourhood"].isin(top_neighborhoods)].copy()
    neighborhood_order = (
        selected.groupby("neighbourhood")["price"].median().sort_values(ascending=False).index
    )
    heatmap_data = (
        selected.groupby(["neighbourhood", "room_type"])["price"]
        .median()
        .unstack()
        .reindex(index=neighborhood_order)
        .reindex(columns=["Entire home/apt", "Private room", "Shared room"])
    )
    annotations = heatmap_data.map(lambda value: f"${value:,.0f}" if pd.notna(value) else "-")

    heatmap_axis = figure.add_axes([0.115, 0.13, 0.56, 0.69])
    heatmap_axis.set_facecolor(SURFACE)
    heatmap_cmap = LinearSegmentedColormap.from_list(
        "airbnb_price", ["#25343A", "#5A93A8", "#F5B942", "#E47A50"]
    )
    sns.heatmap(
        heatmap_data,
        annot=annotations,
        fmt="",
        cmap=heatmap_cmap,
        linewidths=1,
        linecolor=BACKGROUND,
        cbar_kws={"label": "Median nightly price (USD)", "shrink": 0.72},
        annot_kws={"fontsize": 9, "fontweight": "bold"},
        ax=heatmap_axis,
    )
    heatmap_axis.set_title(
        "MEDIAN PRICE ACROSS THE 15 HIGHEST-SUPPLY NEIGHBORHOODS",
        loc="left",
        color=INK,
        fontsize=11,
        fontweight="bold",
        pad=14,
    )
    heatmap_axis.set_xlabel("")
    heatmap_axis.set_ylabel("")
    heatmap_axis.tick_params(axis="x", colors=MUTED, labelsize=9, rotation=0, length=0)
    heatmap_axis.tick_params(axis="y", colors=MUTED, labelsize=9, rotation=0, length=0)
    colorbar = heatmap_axis.collections[0].colorbar
    colorbar.ax.tick_params(colors=MUTED, labelsize=8)
    colorbar.set_label("Median nightly price (USD)", color=MUTED, fontsize=8)

    room_axis = figure.add_axes([0.735, 0.50, 0.22, 0.28])
    room_medians = (
        frame.groupby("room_type")["price"]
        .median()
        .reindex(["Entire home/apt", "Private room", "Shared room"])
        .sort_values()
    )
    bars = room_axis.barh(
        room_medians.index,
        room_medians.values,
        color=[ROOM_COLORS[name] for name in room_medians.index],
        height=0.58,
    )
    for bar, price in zip(bars, room_medians.values):
        room_axis.text(
            price + 4,
            bar.get_y() + bar.get_height() / 2,
            f"${price:,.0f}",
            color=INK,
            fontsize=10,
            fontweight="bold",
            va="center",
        )
    room_axis.set_xlim(0, 190)
    room_axis.set_title(
        "CITYWIDE ROOM-TYPE MEDIANS",
        loc="left",
        color=INK,
        fontsize=10.5,
        fontweight="bold",
        pad=12,
    )
    room_axis.set_xlabel("Nightly price (USD)", fontsize=8)
    room_axis.set_ylabel("")
    room_axis.xaxis.set_major_formatter(lambda value, _: f"${value:.0f}")
    style_axis(room_axis)

    premium = (room_medians["Entire home/apt"] / room_medians["Private room"] - 1) * 100
    figure.text(0.735, 0.385, f"+{premium:.0f}%", color=ACCENT, fontsize=30, fontweight="bold")
    figure.text(
        0.735,
        0.345,
        "entire-home median premium\nover private rooms",
        color=MUTED,
        fontsize=10,
        linespacing=1.5,
    )
    figure.text(
        0.735,
        0.245,
        "Midtown and Chelsea reach a \\$225\nentire-home median, while private rooms\nin the same areas remain lower at\n\\$150 and \\$105 respectively.",
        color=INK,
        fontsize=10,
        linespacing=1.55,
    )
    add_footer(
        figure,
        "48,884 positive-price listings; medians are used because nightly price is strongly right-skewed.",
    )
    return save_figure(figure, "question_1_price_by_neighborhood_room_type.png")


def generate_question_two(frame: pd.DataFrame) -> Path:
    """Answer whether highly reviewed listings form geographic clusters."""
    positive_reviews = frame[frame["number_of_reviews"] > 0]
    high_review_threshold = positive_reviews["number_of_reviews"].quantile(0.75)
    highlighted = frame[frame["number_of_reviews"] >= high_review_threshold].copy()

    figure = create_canvas(
        2,
        "Are there geospatial clusters of highly reviewed listings?",
        f"Yes. Top-quartile reviewed listings ({high_review_threshold:.0f}+ reviews) cluster in Manhattan, Brooklyn, and western Queens corridors.",
    )

    map_axis = figure.add_axes([0.045, 0.13, 0.61, 0.69])
    map_axis.set_facecolor(SURFACE)
    map_axis.scatter(
        frame["longitude"],
        frame["latitude"],
        s=2,
        color="#34383F",
        alpha=0.25,
        linewidth=0,
        rasterized=True,
    )
    sns.scatterplot(
        data=highlighted,
        x="longitude",
        y="latitude",
        hue="neighbourhood_group",
        palette=BOROUGH_COLORS,
        size="number_of_reviews",
        sizes=(7, 42),
        size_norm=(high_review_threshold, highlighted["number_of_reviews"].quantile(0.99)),
        alpha=0.64,
        linewidth=0,
        legend=False,
        rasterized=True,
        ax=map_axis,
    )
    map_axis.set_xlim(-74.28, -73.68)
    map_axis.set_ylim(40.48, 40.93)
    map_axis.set_aspect(1.18)
    map_axis.set_xticks([])
    map_axis.set_yticks([])
    map_axis.set_xlabel("")
    map_axis.set_ylabel("")
    for spine in map_axis.spines.values():
        spine.set_visible(False)
    map_axis.set_title(
        "TOP-QUARTILE REVIEWED LISTINGS FORM VISIBLE CORRIDORS",
        loc="left",
        color=INK,
        fontsize=11,
        fontweight="bold",
        pad=14,
    )
    map_axis.text(
        0,
        1.01,
        "Faint marks show all listings; colored marks have 33 or more reviews.",
        transform=map_axis.transAxes,
        color=MUTED,
        fontsize=8.5,
        va="bottom",
    )

    handles = [
        Line2D([0], [0], marker="o", color="none", label=name, markerfacecolor=color, markersize=7)
        for name, color in BOROUGH_COLORS.items()
    ]
    map_axis.legend(
        handles=handles,
        loc="lower left",
        ncol=2,
        frameon=False,
        fontsize=8,
        labelcolor=MUTED,
        handletextpad=0.3,
        columnspacing=0.8,
    )

    neighborhood_summary = (
        frame.groupby(["neighbourhood_group", "neighbourhood"])
        .agg(
            listings=("id", "size"),
            high_review_share=("number_of_reviews", lambda values: (values >= high_review_threshold).mean() * 100),
        )
        .reset_index()
    )
    ranked = (
        neighborhood_summary[neighborhood_summary["listings"] >= 100]
        .nlargest(10, "high_review_share")
        .sort_values("high_review_share")
    )
    rank_axis = figure.add_axes([0.72, 0.22, 0.235, 0.60])
    bars = rank_axis.barh(
        ranked["neighbourhood"],
        ranked["high_review_share"],
        color=[BOROUGH_COLORS[name] for name in ranked["neighbourhood_group"]],
        height=0.62,
    )
    for bar, share in zip(bars, ranked["high_review_share"]):
        rank_axis.text(
            share + 0.8,
            bar.get_y() + bar.get_height() / 2,
            f"{share:.1f}%",
            color=INK,
            fontsize=8.5,
            fontweight="bold",
            va="center",
        )
    rank_axis.set_xlim(0, 52)
    rank_axis.set_title(
        "SHARE OF LISTINGS WITH 33+ REVIEWS",
        loc="left",
        color=INK,
        fontsize=10.5,
        fontweight="bold",
        pad=12,
    )
    rank_axis.set_xlabel("Percent of neighborhood listings", fontsize=8)
    rank_axis.set_ylabel("")
    rank_axis.xaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")
    style_axis(rank_axis)

    figure.text(0.72, 0.135, "45.4%", color=ACCENT, fontsize=24, fontweight="bold")
    figure.text(
        0.79,
        0.143,
        "of East Elmhurst listings are\nin the high-review group.",
        color=MUTED,
        fontsize=9,
        linespacing=1.4,
    )
    add_footer(
        figure,
        "High-review means the top quartile among listings with reviews (33+); review count is an activity proxy, not quality or revenue.",
    )
    return save_figure(figure, "question_2_geospatial_review_clusters.png")


def generate_question_three(frame: pd.DataFrame) -> Path:
    """Answer the minimum-nights and availability correlation question."""
    spearman = frame["minimum_nights"].rank().corr(frame["availability_365"].rank())
    display_frame = frame[frame["minimum_nights"] <= 90].copy()
    sample = display_frame.sample(min(12000, len(display_frame)), random_state=42)

    stay_bins = [0, 1, 3, 7, 29, 90, np.inf]
    stay_labels = ["1 night", "2-3", "4-7", "8-29", "30-90", "91+"]
    frame = frame.copy()
    frame["stay_bucket"] = pd.cut(
        frame["minimum_nights"], bins=stay_bins, labels=stay_labels, include_lowest=True
    )
    bucket_summary = (
        frame.groupby("stay_bucket", observed=True)
        .agg(
            listings=("id", "size"),
            median_availability=("availability_365", "median"),
        )
        .reset_index()
    )

    figure = create_canvas(
        3,
        "What is the correlation between minimum nights and availability?",
        f"The overall monotonic relationship is weak (Spearman rho = {spearman:+.3f}), but 30+ night listings form a distinct high-availability segment.",
    )

    scatter_axis = figure.add_axes([0.045, 0.15, 0.59, 0.66])
    sns.scatterplot(
        data=sample,
        x="minimum_nights",
        y="availability_365",
        hue="room_type",
        palette=ROOM_COLORS,
        s=11,
        alpha=0.20,
        linewidth=0,
        rasterized=True,
        ax=scatter_axis,
    )
    scatter_axis.axvline(30, color=ACCENT, linestyle="--", linewidth=1.5, alpha=0.9)
    scatter_axis.text(
        31,
        350,
        "30-night threshold",
        color=ACCENT,
        fontsize=8.5,
        fontweight="bold",
        va="top",
    )
    scatter_axis.set_xlim(0, 90)
    scatter_axis.set_ylim(0, 365)
    scatter_axis.set_title(
        "MINIMUM STAY AND CALENDAR AVAILABILITY",
        loc="left",
        color=INK,
        fontsize=11,
        fontweight="bold",
        pad=14,
    )
    scatter_axis.set_xlabel("Minimum nights required (view capped at 90)", fontsize=9)
    scatter_axis.set_ylabel("Calendar availability (days per year)", fontsize=9)
    legend = scatter_axis.legend(
        title=None,
        frameon=False,
        fontsize=8,
        labelcolor=MUTED,
        loc="upper left",
        ncol=3,
    )
    for text in legend.get_texts():
        text.set_color(MUTED)
    style_axis(scatter_axis)

    bucket_axis = figure.add_axes([0.70, 0.36, 0.255, 0.45])
    bars = bucket_axis.barh(
        bucket_summary["stay_bucket"].astype(str),
        bucket_summary["median_availability"],
        color=["#5A93A8", "#5A93A8", "#5A93A8", "#7986B7", ACCENT, ACCENT],
        height=0.6,
    )
    for bar, days, count in zip(
        bars, bucket_summary["median_availability"], bucket_summary["listings"]
    ):
        bucket_axis.text(
            days + 5,
            bar.get_y() + bar.get_height() / 2,
            f"{days:.0f} days  |  n={count:,}",
            color=INK,
            fontsize=8.2,
            fontweight="bold",
            va="center",
        )
    bucket_axis.set_xlim(0, 350)
    bucket_axis.set_title(
        "MEDIAN AVAILABILITY BY STAY POLICY",
        loc="left",
        color=INK,
        fontsize=10.5,
        fontweight="bold",
        pad=12,
    )
    bucket_axis.set_xlabel("Median available days per year", fontsize=8)
    bucket_axis.set_ylabel("Minimum-stay group", fontsize=8)
    style_axis(bucket_axis)

    figure.text(0.70, 0.255, f"rho = {spearman:+.3f}", color=ACCENT, fontsize=27, fontweight="bold")
    figure.text(
        0.70,
        0.213,
        "Weak overall rank correlation",
        color=MUTED,
        fontsize=9.5,
    )
    figure.text(
        0.70,
        0.145,
        "30-90 night listings show a 268-day median\navailability versus 9 days for 4-7 night listings.",
        color=INK,
        fontsize=9.5,
        linespacing=1.5,
    )
    add_footer(
        figure,
        "Correlation is descriptive, not causal; availability means calendar-open days and does not equal vacancy or occupancy.",
    )
    return save_figure(figure, "question_3_minimum_nights_vs_availability.png")


def main() -> None:
    """Generate all three required answer images."""
    frame = load_data()
    generate_question_one(frame)
    generate_question_two(frame)
    generate_question_three(frame)


if __name__ == "__main__":
    main()
