# NYC Airbnb Market Intelligence Dashboard

> **EngiViz - Engineering Day DataViz Hackathon Submission**  
> An editorial, evidence-led, and interactive data visualization application dissecting the New York City short-term rental market in 2019.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.24+-3F4F75?style=flat&logo=plotly&logoColor=white)](https://plotly.com)
[![Tests](https://img.shields.io/badge/Tests-pytest-10B981?style=flat)](tests/)

---

## 🎯 Central Research Question
> *Where are Airbnb listings concentrated in New York City, what drives price differences, and which areas appear premium or relatively good value?*

This dashboard delivers an editorial urban-market report combining high-contrast visual design, interactive token-free geospatial mapping, dynamic statistical insights, and micro-market analysis.

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
- Python 3.11 or newer
- Git

### 2. Clone and Setup Environment
```bash
# Clone the repository
git clone https://github.com/chetan-s20/GNA_engDay.git
cd GNA_engDay

# Create a Python 3.12 environment and install locked dependencies with uv
uv sync --python 3.12
```

### 3. Verify Dataset
The primary dataset is pre-configured at `data/AB_NYC_2019.csv`.
If you need to re-download it:
- Sourced from Kaggle: [`dgomonov/new-york-city-airbnb-open-data`](https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data)
- Ensure the CSV is placed at `data/AB_NYC_2019.csv`.

### 4. Run Application
```bash
uv run streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## Panel Submission Package

- Primary 2400x1350 visualization: [`submission/nyc_airbnb_market_intelligence.png`](submission/nyc_airbnb_market_intelligence.png)
- Three form-ready question images: [`submission/`](submission/)
- Reproducible Matplotlib + Seaborn generator: [`submission_visualization.py`](submission_visualization.py)
- Reproducible question-image generator: [`question_visualizations.py`](question_visualizations.py)
- Form-ready participant details, insights, methodology, and checklist: [`submission/SUBMISSION.md`](submission/SUBMISSION.md)

Regenerate the judging image with:

```bash
uv run python submission_visualization.py
```

---

## 🧪 Running Automated Tests

Run the complete test suite verifying data validation, cleaning rules, host segmentation, price tier derivation, empty filter safety, and end-to-end chart rendering:

```bash
uv run pytest -v
```

---

## 📊 Dashboard Architecture & Key Features

### 1. Overview & Market Scale
- **5 Global Responsive KPI Cards:** Real-time filtered listing count, median nightly rate, median monthly review velocity, median annual availability, and dominant supply borough.
- **Supply Distribution by Borough:** Horizontal bar chart comparing listing volume and market percentage shares.
- **Room-Type Mix:** Donut visual illustrating inventory distribution across Entire home/apt, Private room, and Shared room.
- **Price Dispersion:** Right-skew controlled box plots showcasing borough-level median pricing under configurable display caps.
- **Dynamic Observations:** Dynamically generated statistical narrative (recalculated upon filter changes without hardcoding).

### 2. Interactive Market Map
- **Offline Geographic Plot:** Longitude/latitude rendering works without map tiles, API keys, or Mapbox secrets.
- **3 Switchable Geospatial Layers:**
  1. *Listing Density Heatmap:* Spatial clustering of inventory.
  2. *Median Price Map:* Neighborhood-level aggregated nightly rates with listing count scaling.
  3. *Review Velocity Map:* Monthly review rate as an indicator of booking activity.
- **Supply vs. Price Bubble Chart:** Demonstrates how high supply volume (e.g. Brooklyn) diverges from high price premiums (Manhattan).

### 3. Price & Duration Analysis
- **Borough × Room Type Grouped Bars:** Reveals median pricing premiums of private apartments versus private rooms across each borough.
- **Price-Tier Composition (100% Stacked):** Stratifies market into Budget (Q1), Mid-range (Q2), Premium (Q3), and Luxury (Q4).
- **Stay-Duration Friction:** Scatterplot highlighting association between minimum night restrictions and rates, detailing the 30-day regulatory clustering.

### 4. Behavioral Demand & Host Portfolios
- **Demand Velocity vs. Price:** Reviews per month (demand proxy) mapped against nightly rates.
- **Calendar Availability:** Distribution of annual open calendar days across boroughs.
- **Commercial vs. Casual Host Portfolios:** Segmentation into Single-listing hosts (1), Small portfolios (2–5), and Professional/commercial operators (6+).

### 5. Micro-Market Neighborhood Benchmark
- **Listing Threshold Filter:** Configurable slider (default: $\ge 20$ listings) to eliminate small-sample noise.
- **Top 10 / Bottom 10 Comparison:** Ranked horizontal bars distinguishing premium from accessible neighborhoods.
- **Relative Value Signal (0–100):** An exploratory composite score:
  $$\text{Relative Value Score} = 50 \times (1 - \text{Price}_{\text{norm}}) + 50 \times \text{Reviews}_{\text{norm}}$$
  Highlights neighborhoods offering above-average review demand velocity at accessible price points.

### 6. Methodology & Limitations
- Complete lineage transparency.
- Full definitions of derived metrics.
- Explicit warnings: Calendar Availability $\neq$ Occupancy; Reviews $\neq$ Revenue; Advertised Rate $\neq$ Realized Revenue; Association $\neq$ Causation.

---

## 📂 Project Structure

```text
GNA_engDay/
├── app.py                      # Streamlit application entry point & layout
├── requirements.txt            # Python dependencies
├── README.md                   # Comprehensive documentation
├── prd.md                      # Product Requirements Document
├── data/
│   └── AB_NYC_2019.csv         # Kaggle NYC Airbnb Open Data source
├── src/
│   ├── __init__.py
│   ├── data.py                 # Cleaning, column validation, derived metrics, caching
│   ├── charts.py               # Plotly chart builders with editorial styling
│   ├── insights.py             # Dynamic statistical takeaway generation
│   └── styles.py               # Editorial theme, color palettes, Streamlit CSS
└── tests/
    ├── __init__.py
    ├── test_data.py            # Data validation, cleaning, and transformation tests
    ├── test_insights.py        # Edge-case & sparse data insight generation tests
    └── test_charts.py          # End-to-end chart rendering integration tests
```

---

## ⚖️ Hackathon Evaluation Alignment

| Dimension | Verifiable implementation |
| :--- | :--- |
| **Data Accuracy & Engineering** | Schema validation, safe type coercion, missing-value preservation, quartile price tiers, host segmentation, and tested neighborhood aggregation. |
| **Visual Design & Interactivity** | NYC editorial theme, token-free Carto maps, responsive KPIs, consistent chart styling, and global multi-faceted filters. |
| **Insights & Storytelling** | Filter-aware narrative takeaways, supply-versus-price comparison, neighborhood benchmarking, and explicit analytical caveats. |

---

Created for the GNA University Engineering Day Hackathon. The source dataset remains subject to its Kaggle listing terms.
