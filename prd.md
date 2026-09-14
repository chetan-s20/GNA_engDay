# PRD: NYC Airbnb Market Intelligence Dashboard

## 1. Product Summary

Build a polished, interactive Python dashboard that analyzes the New York City Airbnb market using the Kaggle dataset below.

- **Dataset:** `dgomonov/new-york-city-airbnb-open-data`
- **Primary input file:** `data/AB_NYC_2019.csv`
- **Submission type:** Interactive Python data-visualization project
- **Technology:** Python, Streamlit, Pandas, Plotly
- **Audience:** Hackathon judges and non-technical viewers

The dashboard must answer one clear question:

> Where are Airbnb listings concentrated in New York City, what drives price differences, and which areas appear premium or relatively good value?

The experience should be map-first, evidence-led, and visually distinctive. It must not resemble a generic business dashboard filled with unrelated charts.

## 2. Goals

### Primary Goals

1. Make geographic listing patterns immediately understandable.
2. Explain how nightly price varies by borough, neighborhood, and room type.
3. Explore review activity, availability, and host portfolios without overstating what the data proves.
4. Provide filters that let judges investigate the data themselves.
5. Create a reliable, reproducible application that runs locally from the raw CSV.
6. Create a compelling story in a five-minute demo.

### Success Criteria

A viewer should be able to answer the following in under two minutes:

1. Which boroughs contain the most Airbnb listings?
2. Where is supply geographically concentrated?
3. Which boroughs and room types command the highest nightly prices?
4. How do price, review activity, minimum stay, and availability vary together?
5. Which neighborhoods are premium markets and which offer relative value?

## 3. Non-Goals

Do not build the following:

- Authentication, accounts, or a database.
- Live Airbnb API integration.
- Booking, reservation, or payment functionality.
- Predictions represented as factual market results.
- Any paid map service or Mapbox access token requirement.
- Charts that cannot be traced back to a documented data transformation.

## 4. Dataset

The app uses the NYC Airbnb Open Data CSV. Expected source columns are listed below.

| Column | Meaning | Primary use |
| --- | --- | --- |
| `id` | Listing ID | Unique row identifier |
| `name` | Listing title | Optional map hover text |
| `host_id` | Host ID | Host portfolio analysis |
| `host_name` | Host name | Optional table detail |
| `neighbourhood_group` | Borough | Borough-level filtering and analysis |
| `neighbourhood` | Neighborhood | Neighborhood-level analysis |
| `latitude` | Latitude | Mapping |
| `longitude` | Longitude | Mapping |
| `room_type` | Entire home/apt, private room, shared room | Price and supply analysis |
| `price` | Listed nightly price in USD | Main numeric measure |
| `minimum_nights` | Minimum required stay | Booking-friction analysis |
| `number_of_reviews` | Total reviews | Demand proxy |
| `last_review` | Date of latest review | Optional recency indicator |
| `reviews_per_month` | Monthly review rate | Demand proxy |
| `calculated_host_listings_count` | Listings operated by host | Host portfolio analysis |
| `availability_365` | Days listed as available annually | Supply proxy |

### Dataset Caveats

- The data represents listings from 2019 and must be labeled as such.
- `availability_365` means calendar availability. It is not occupancy, bookings, revenue, or demand.
- Reviews are an imperfect demand proxy and do not measure quality or revenue.
- Listed price may not equal the final paid price.
- A neighborhood with many listings may be overrepresented by hosts with multiple listings.

## 5. Core User Stories

1. As a judge, I want a concise overview so that I understand the scale and composition of the NYC Airbnb market immediately.
2. As a judge, I want to explore listings on a map so that I can see where supply and premium prices cluster.
3. As a viewer, I want to filter the dashboard by borough, room type, price, reviews, and availability so that I can test findings myself.
4. As a viewer, I want clear explanations of the metrics so that I do not confuse availability with occupancy or correlation with causation.
5. As a presenter, I want dynamically generated findings so that the narrative remains accurate after filters change.

## 6. Technology and Dependencies

### Required Stack

- Python 3.11 or newer
- Streamlit
- Pandas
- NumPy
- Plotly

### Required Dependencies

Create `requirements.txt` with at least:

```text
streamlit>=1.39
pandas>=2.2
numpy>=1.26
plotly>=5.24
```

### Map Requirement

Use Plotly with a token-free style such as `open-street-map` or `carto-positron`. The project must run without secrets, tokens, or external credentials.

## 7. Information Architecture

Implement one Streamlit app with a persistent sidebar and these main sections, presented as anchored sections or tabs:

1. Overview
2. Market Map
3. Price Analysis
4. Demand and Availability
5. Neighborhood Insights
6. Methodology

### Global Header

The top of the page must contain:

- Title: **NYC Airbnb Market Intelligence**
- Subtitle: **How location, room type, and listing behavior shaped New York City's short-term rental market in 2019**
- Source line with the Kaggle dataset name and URL
- A short statement explaining that insights are descriptive, not causal

## 8. Visual Design Direction

### Design Intent

Create an editorial urban-market report, not a default Streamlit app. The visual identity should resemble a refined New York city atlas or market intelligence brief.

### Style Requirements

- Background: deep charcoal or warm off-white; choose one coherent theme.
- Primary accent: a saturated taxi-yellow or transit-orange, used sparingly for highlights.
- Supporting colors: borough-specific muted colors with adequate contrast.
- Typography: use Streamlit-safe typography with a strong heading scale and compact data labels.
- Visual hierarchy: title and central map dominate; supporting charts are secondary.
- Use meaningful whitespace and clear section separation.
- Avoid excessive card borders, gradients, glassmorphism, and rainbow palettes.
- Do not use decorative icons unless they improve comprehension.

### Accessibility Requirements

- Minimum readable body text: 14px.
- Do not rely on color alone to distinguish room type or borough.
- Ensure chart tooltips carry exact values.
- Use high-contrast foreground/background combinations.
- Give every chart a descriptive heading and a one-line explanation.
- The app must remain usable at 375px wide without horizontal page scrolling.

## 9. Sidebar Filters

Create a sidebar titled **Explore the Market**. Filters apply to every chart, KPI, table, and generated insight.

| Filter | Default | Behavior |
| --- | --- | --- |
| Borough | All | Multi-select from `neighbourhood_group` |
| Room type | All | Multi-select from `room_type` |
| Price range | Full cleaned range | Slider limited by chart display cap |
| Minimum reviews | 0 | Numeric slider or input |
| Minimum availability | 0 | Numeric slider or input |
| Price display cap | $1,000 | Selectable cap for price charts |
| Map metric | Listing density | Switch between density, median price, and review activity |

### Filter Rules

- Display the filtered listing count in the sidebar and overview.
- Do not permanently delete price outliers from the source data.
- Apply the price display cap only to charts where extreme prices impair legibility.
- Explain the cap directly under each affected chart.
- If a filter selection returns no data, show an empty state with a **Reset filters** action.

## 10. Data Preparation

Implement data preparation in a reusable function named `prepare_data(df)`.

### Required Cleaning

1. Validate the CSV includes every required column. Show a clear error listing missing columns if it does not.
2. Drop records with missing `latitude`, `longitude`, `price`, `neighbourhood_group`, or `room_type`.
3. Convert `last_review` with `pd.to_datetime(..., errors="coerce")`.
4. Convert numeric fields safely with `pd.to_numeric(..., errors="coerce")`.
5. Exclude invalid prices where `price <= 0`.
6. Preserve price outliers in the cleaned dataset, but mark them as excluded from capped price charts.
7. Fill missing `reviews_per_month` with `0` only in a separate analysis field such as `reviews_per_month_filled`.
8. Normalize whitespace in borough, neighborhood, and room-type text values.

### Required Derived Fields

| Field | Definition |
| --- | --- |
| `log_price` | `np.log1p(price)` for optional skew-aware analysis |
| `price_tier` | Budget, Mid-range, Premium, Luxury based on filtered or whole-dataset quartiles; document the method |
| `host_category` | Single-listing host: 1; Small portfolio: 2-5; Professional host: 6+ |
| `has_reviews` | `number_of_reviews > 0` |
| `review_activity` | Low / Moderate / High based on quartiles of non-null `reviews_per_month` |
| `is_price_outlier` | `price > selected_price_cap` for display logic |

### Caching

Use `@st.cache_data` for loading and cleaning the source CSV. The app should not reread the file for every interaction.

## 11. Dashboard Requirements

## 11.1 Overview

### Purpose

Give an immediate summary of market scale, supply composition, and price differences.

### Required KPI Cards

Show values after global filters:

1. **Filtered Listings**: number of included records.
2. **Median Nightly Price**: median `price` in USD.
3. **Median Reviews per Month**: median of `reviews_per_month_filled`.
4. **Median Availability**: median `availability_365` in days.
5. **Largest Borough by Supply**: borough with the most filtered listings.

### Required Visualizations

#### A. Listing Supply by Borough

- Chart: sorted horizontal bar chart.
- Dimension: `neighbourhood_group`.
- Metric: listing count and percentage of filtered listings.
- Requirement: labels must show exact counts.

#### B. Room-Type Mix

- Chart: 100% stacked horizontal bar or donut chart.
- Dimension: `room_type`.
- Metric: listing count and percentage.
- Requirement: include exact percentages in hover labels.

#### C. Price Distribution by Borough

- Chart: violin plot with embedded box plot, or a conventional box plot.
- X-axis: borough.
- Y-axis: nightly price.
- Use records under the selected price cap.
- Requirement: show median values clearly and note the price cap.

### Dynamic Insight Block

Generate two to three short findings using the currently filtered data. Do not hardcode claims.

Example patterns:

- "{borough} has the largest share of filtered listings, with {share:.1%} of supply."
- "Median nightly price is highest in {borough}, at ${median_price:,.0f}."
- "{room_type} represents {share:.1%} of filtered listings."

## 11.2 Market Map

### Purpose

Make geography the main visual story of the project.

### Required Map Modes

1. **Listing Density**: density map weighted by listing count.
2. **Median Price**: aggregate to neighborhood or coordinate bins, then map median nightly price.
3. **Review Activity**: aggregate median `reviews_per_month_filled` geographically.

### Map Requirements

- Use a token-free map style.
- Default initial view must frame New York City.
- Do not plot every record as an opaque marker when a density view is more readable.
- For price and review modes, aggregate where practical to avoid visual clutter.
- Tooltips must include borough, neighborhood, listing count, median price, and median review activity when the data is available.
- Include a visible color scale and meaningful legend title.

### Supporting Chart: Supply vs Price

- Chart: bubble scatterplot.
- Each bubble: borough.
- X-axis: listing count.
- Y-axis: median nightly price.
- Bubble size: median reviews per month or total reviews.
- Label boroughs directly or through hover.
- Purpose: show that high supply and high price are different market characteristics.

### Required Copy

Include this or equivalent text near the map:

> High listing density does not automatically mean high pricing. Compare supply concentration with median price to distinguish premium areas from high-volume areas.

## 11.3 Price Analysis

### Purpose

Explain how nightly price differs by accommodation type, borough, and booking restrictions.

### Required Visualizations

#### A. Median Price by Borough and Room Type

- Chart: grouped bar chart.
- X-axis: borough.
- Color: room type.
- Y-axis: median nightly price.
- Use the selected price cap.
- Requirement: use median rather than mean as the primary measure because price is right-skewed.

#### B. Minimum Nights vs Price

- Chart: scatterplot with low-opacity marks.
- X-axis: `minimum_nights`.
- Y-axis: `price`.
- Color: `room_type`.
- Display constraints: `price <= selected_price_cap` and `minimum_nights <= 60` by default.
- Include a note stating that the chart shows association, not causation.

#### C. Price-Tier Composition

- Chart: 100% stacked horizontal bar chart.
- Dimension: borough.
- Color: `price_tier`.
- Metric: share of listings.
- Purpose: reveal which boroughs contain more budget, mid-range, premium, or luxury listings.

### Valid Interpretation Rules

Allowed language:

- "is associated with"
- "shows a higher median"
- "is more concentrated in"
- "appears to cluster around"

Forbidden language:

- "causes"
- "proves"
- "guarantees"
- "best investment"

## 11.4 Demand and Availability

### Purpose

Explore behavioral signals while making the limits of the data explicit.

### Required Visualizations

#### A. Reviews per Month vs Price

- Chart: scatterplot or density scatter.
- X-axis: `reviews_per_month_filled`.
- Y-axis: `price`.
- Color: borough or room type.
- Apply the selected price cap.
- Add a caption: reviews are a demand proxy, not a revenue or quality metric.

#### B. Availability by Borough

- Chart: box plot or violin plot.
- X-axis: borough.
- Y-axis: `availability_365`.
- Caption: availability reflects days open on a calendar, not confirmed occupancy.

#### C. Host Portfolio Composition

- Chart: bar chart.
- Dimension: `host_category`.
- Metric: listing count and share.
- Optional second chart: compare median price by host category.

## 11.5 Neighborhood Insights

### Purpose

Provide a concise decision-oriented comparison of neighborhoods.

### Required Neighborhood Ranking Table

Create a sortable table using neighborhoods with at least 20 filtered listings by default. Let users change the minimum threshold.

| Column | Calculation |
| --- | --- |
| Neighborhood | `neighbourhood` |
| Borough | `neighbourhood_group` |
| Listings | Record count |
| Median price | Median `price` |
| Median reviews/month | Median `reviews_per_month_filled` |
| Median availability | Median `availability_365` |
| Dominant room type | Most frequent `room_type` |
| Relative value signal | Optional, clearly defined metric |

### Optional Relative Value Signal

If implemented, label this as **Relative Value Signal**, never "best investment" or "best neighborhood."

Suggested approach:

1. Standardize median price and median review activity within the selected filtered data.
2. Higher review activity increases the score.
3. Lower price increases the score.
4. Display the score only as an exploratory ranking.
5. Show the formula and caveats in Methodology.

### Required Comparison Chart

- Chart: ranked horizontal bar chart of median neighborhood price.
- Filter to neighborhoods meeting the listing threshold.
- Let the user choose Top 10 or Bottom 10.
- Include borough color or grouping.

## 11.6 Methodology

Include an expandable section containing:

1. Dataset source and 2019 coverage.
2. Cleaning rules.
3. Price outlier handling and selected display cap.
4. Definitions of each derived field.
5. Difference between availability and occupancy.
6. Difference between association and causation.
7. Limitations of reviews as a demand proxy.
8. The optional relative value score formula, if implemented.

## 12. File Structure

Use this structure unless the existing project structure requires an equivalent alternative:

```text
.
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── AB_NYC_2019.csv
├── src/
│   ├── __init__.py
│   ├── data.py
│   ├── charts.py
│   ├── insights.py
│   └── styles.py
└── tests/
    ├── test_data.py
    └── test_insights.py
```

### Module Responsibilities

| File | Responsibility |
| --- | --- |
| `app.py` | Streamlit page layout, filters, section composition |
| `src/data.py` | Loading, validation, cleaning, field derivation, filtering |
| `src/charts.py` | Plotly chart builders with consistent styling |
| `src/insights.py` | Safe dynamic text insight generation |
| `src/styles.py` | Shared palette, layout constants, Streamlit CSS |
| `tests/test_data.py` | Cleaning, validation, and transformation tests |
| `tests/test_insights.py` | Insight behavior for normal and sparse data |

## 13. Functional Requirements

1. The application must run with `streamlit run app.py`.
2. The app must load `data/AB_NYC_2019.csv` by default.
3. If the file is absent, show instructions explaining where to place it and link to the Kaggle source.
4. All sidebar filters must update all KPIs, charts, maps, insight text, and ranking tables.
5. Charts must use hover labels with readable formatted values.
6. All price charts must disclose when a display cap is applied.
7. The app must never require a private API key.
8. The dashboard must handle a no-data filter state without throwing an exception.
9. All calculated metrics must be calculated from filtered data unless explicitly labeled as overall-dataset benchmarks.
10. The map must be usable without custom map credentials.

## 14. Performance Requirements

1. Use `st.cache_data` for the load and preparation step.
2. Aggregate map data where possible rather than rendering expensive raw point layers for every mode.
3. Use at most 10,000 random points for scatterplots when filters still return more records than that; retain aggregates for statistics.
4. The app should become interactive within approximately five seconds on a typical local machine after the initial dataset load.
5. Avoid unnecessary reruns and duplicate groupby operations.

## 15. Testing Requirements

### Unit Tests

Write tests for:

1. Missing required columns produces a clear validation error.
2. Invalid and zero prices are removed.
3. Missing reviews per month are handled without overwriting the raw column.
4. Host categories are correctly assigned at boundaries 1, 2, 5, and 6.
5. Price tiers are assigned for valid input.
6. A no-data filter result returns an empty data frame safely.
7. Generated insights do not fail when only one borough or room type remains.

### Manual Test Cases

1. Load the complete dataset with default filters.
2. Select only Manhattan.
3. Select only Private room.
4. Narrow price to a small range.
5. Set filters that return no listings.
6. Switch every map metric.
7. Resize to mobile-width viewport.
8. Confirm the app works without an internet-hosted token or environment variable.

## 16. Acceptance Criteria

The project is complete only when all of these conditions are met:

- [ ] A judge can run `pip install -r requirements.txt` followed by `streamlit run app.py`.
- [ ] The dashboard clearly identifies the dataset as NYC Airbnb Open Data from 2019.
- [ ] Sidebar filters affect every displayed metric and chart.
- [ ] The main map provides density, price, and review-activity views.
- [ ] Overview includes five responsive KPI cards and three summary visuals.
- [ ] Price analysis includes borough/room-type comparison, minimum-nights scatter, and price-tier composition.
- [ ] Demand and availability includes review-price, availability, and host-portfolio views.
- [ ] Neighborhood section includes a minimum-listing threshold and sortable summary table.
- [ ] Outlier treatment and data limitations are visible to viewers.
- [ ] The app has an informative missing-file state and no-data state.
- [ ] The map works without a Mapbox token.
- [ ] Unit tests pass.
- [ ] Desktop and mobile layouts are readable and do not overflow horizontally.

## 17. Recommended Build Order

1. Create the project structure and dependency file.
2. Download the Kaggle CSV and place it in `data/AB_NYC_2019.csv`.
3. Implement loading, validation, cleaning, derived fields, and unit tests.
4. Build the sidebar and global filtering function.
5. Build the overview KPIs and summary charts.
6. Build and verify the three map modes.
7. Build price, demand, availability, and host portfolio charts.
8. Build neighborhood aggregation, ranking table, and comparison chart.
9. Add generated insights and methodology content.
10. Apply the final visual design system and test desktop/mobile layouts.
11. Run unit tests and manually test every filter state.

## 18. Suggested Demo Narrative

Use this sequence in the presentation:

1. Start on Overview: establish the scale of NYC's listing market and explain the supply split by borough and room type.
2. Open Market Map: show that geographic concentration and premium pricing are separate patterns.
3. Move to Price Analysis: compare entire homes and private rooms within each borough.
4. Open Demand and Availability: responsibly interpret reviews and availability as indicators, not direct measures of revenue or occupancy.
5. Finish on Neighborhood Insights: compare premium neighborhoods with areas showing a stronger relative value signal.
6. Close with the limitation statement: Airbnb listing data describes advertised market supply, not final transaction outcomes.

## 19. Agent Implementation Prompt

Use the following prompt with an implementation agent:

```text
Implement the NYC Airbnb Market Intelligence Dashboard described in prd.md.

Build a production-quality Streamlit application in this repository using Python, Pandas, NumPy, and Plotly. Follow every functional requirement, data-cleaning rule, chart specification, performance constraint, and acceptance criterion in prd.md.

Use data/AB_NYC_2019.csv as the expected source data. Do not require a Mapbox token or any secret. Build a polished map-first dashboard with responsive desktop and mobile layouts, global filters, safe empty states, and all required narrative sections.

Create the required file structure, requirements.txt, a useful README with setup instructions, and unit tests. Do not fabricate results or use causal language. Run the test suite and verify `streamlit run app.py` starts successfully before finishing.
```
