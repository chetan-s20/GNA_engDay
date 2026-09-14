# Panel Submission Details

## 1. Participant and Project

- **Project / Visualization Title:** NYC Airbnb Market Intelligence: The Price of Place
- **Lead Student Name:** Ankush Thakur
- **College Roll No. / Student ID:** GU-2024-3416
- **Department / Branch:** Computer Science & Engineering
- **Year of Study:** 3rd Year (Junior)
- **Team Members:** Ankush Thakur

## 2. Dataset and Methodology Track

- **Chosen Kaggle Dataset:** Airbnb Listings & Reviews (Geospatial & Hospitality)
- **Kaggle dataset:** `dgomonov/new-york-city-airbnb-open-data`
- **Submission Track:** Python Track
- **Python libraries to select:** Matplotlib, Seaborn, Plotly

Do not select Superstore. This repository analyzes the NYC Airbnb dataset.

## 3. Files to Submit

- **Primary Visualization Image:** `submission/nyc_airbnb_market_intelligence.png`
- **Answer to Question 1:** `submission/question_1_price_by_neighborhood_room_type.png`
- **Answer to Question 2:** `submission/question_2_geospatial_review_clusters.png`
- **Answer to Question 3:** `submission/question_3_minimum_nights_vs_availability.png`
- **Python Visualization Script:** `submission_visualization.py`
- **Question Visualization Script:** `question_visualizations.py`
- **Interactive Dashboard Script:** `app.py`
- **Full project archive:** upload a ZIP of the repository if the portal permits it
- **GitHub / Live Link:** add the deployed Streamlit URL or public GitHub repository URL before submission

The primary image is a 16:9, high-resolution artifact created with both Matplotlib and Seaborn. The interactive dashboard uses Plotly.

### Required Question Uploads

Upload the three files in this exact order:

1. **Upload Answer to Question 1:** `question_1_price_by_neighborhood_room_type.png`
2. **Upload Answer to Question 2:** `question_2_geospatial_review_clusters.png`
3. **Upload Answer to Question 3:** `question_3_minimum_nights_vs_availability.png`

## 4. Key Data Insights Discovered

Add these as separate bullets in the form:

1. **Manhattan and Brooklyn contain 85.4% of all cleaned listings**, showing that Airbnb supply was highly concentrated in the city's two largest short-term-rental markets.
2. **Manhattan's median advertised nightly price was $150, compared with a $106 citywide median**, while the Bronx had the lowest borough median at $65.
3. **Entire homes had a $160 median nightly price versus $70 for private rooms**, a 129% median premium that shows room type is strongly associated with advertised price.
4. **Among neighborhoods with at least 100 listings, Tribeca had the highest median price at $295, while Borough Park had the lowest at $53.50**, revealing a large location premium even among established listing markets.
5. **35.9% of listings showed zero calendar availability**, but this cannot be interpreted as occupancy because hosts may close, deactivate, or withhold their calendars.

If the form permits only two bullets, use bullets 1 and 3. If it permits three, add bullet 4.

## 5. Design and Analytical Methodology

Paste this into the 1-2 sentence methodology field:

> I combined a geospatial listing map with robust median-based comparisons because Airbnb prices are strongly right-skewed. Matplotlib and Seaborn produce the high-resolution judging snapshot, while Plotly powers a filter-aware interactive dashboard; all findings are descriptive associations rather than causal or revenue claims.

## 6. Short Project Description

Use this if the form provides an additional description field:

> NYC Airbnb Market Intelligence examines 48,884 positive-price listings across all five boroughs. It separates supply concentration from price premiums, compares room types, explores review and availability signals, and benchmarks neighborhoods while clearly documenting the limitations of observational listing data.

## 7. Demo Sequence

1. Open the Market Map and switch between Listing Density, Median Price, and Review Activity.
2. Point out that Manhattan and Brooklyn dominate supply, but supply volume and median price are different dimensions.
3. Open Price Analysis and compare the entire-home premium with private rooms across boroughs.
4. Open Neighborhoods and demonstrate the minimum-listing threshold before showing premium and accessible markets.
5. Close on Methodology and state that availability is not occupancy and reviews are not verified demand or revenue.

## 8. Final Submission Checklist

- [ ] Select **Airbnb Listings & Reviews (Geospatial & Hospitality)**.
- [ ] Select **Python Track**.
- [ ] Select **Matplotlib**, **Seaborn**, and **Plotly**.
- [ ] Upload `submission/nyc_airbnb_market_intelligence.png` as the primary image.
- [ ] Upload `submission_visualization.py` or the full repository archive.
- [ ] Add the deployed dashboard or GitHub URL.
- [ ] Paste the key insights from this document.
- [ ] Paste the two-sentence methodology.
- [ ] Open the uploaded image once to verify text remains readable.
