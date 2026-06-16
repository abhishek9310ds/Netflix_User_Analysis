# Project Architecture

## Analytics Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    NETFLIX CUSTOMER INTELLIGENCE                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   RAW DATA  │───▶│   CLEAN &   │───▶│  ANALYZE &  │───▶│   BUILD &   │
│  (5K rows)  │    │   PREPARE   │    │   EXPLORE   │    │   MODEL     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │                  │
       ▼                  ▼                  ▼                  ▼
   customer_id        Feature Eng.       Correlation        ML Models
   demographics       - age_group        Analysis           - Logistic
   subscription       - engagement       - Churn drivers    - Random Forest
   behavior           - health_score     - Segments         - XGBoost
                      - risk_score       - CLV              

                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        OUTPUT LAYER                              │
├─────────────┬─────────────┬─────────────┬─────────────────────────┤
│  NOTEBOOKS  │  DASHBOARD  │    MODEL    │      REPORTS            │
│  (5 .ipynb) │ (Streamlit) │  (.pkl)     │      (PDF/SQL)          │
└─────────────┴─────────────┴─────────────┴─────────────────────────┘
```

## Data Pipeline

```
netflix_customer_churn.csv (5,000 customers, 14 features)
        │
        ▼
┌───────────────────────────────────┐
│     DATA PREPARATION (Notebook 1)  │
├───────────────────────────────────┤
│ • Data quality checks              │
│ • Missing value analysis           │
│ • Outlier detection                │
│ • Feature engineering:             │
│   - age_group                      │
│   - engagement_level               │
│   - login_recency                  │
│   - clv_estimate                   │
│   - high_risk_flag                 │
└───────────────────────────────────┘
        │
        ▼
prepared_data.csv (19 features)
        │
        ▼
┌───────────────────────────────────┐
│    SEGMENTATION (Notebook 3)       │
├───────────────────────────────────┤
│ • K-Means clustering (k=4)         │
│ • Segment naming:                  │
│   - Power Users                    │
│   - Premium                        │
│   - Casual                         │
│   - At-Risk                        │
│ • Health score (0-100)             │
│ • Health categories                │
└───────────────────────────────────┘
        │
        ▼
segmented_data.csv (25 features)
        │
        ▼
┌───────────────────────────────────┐
│   MODELING (Notebook 4)            │
├───────────────────────────────────┤
│ • Feature encoding                 │
│ • Train/test split (80/20)         │
│ • Model training:                  │
│   - Logistic Regression            │
│   - Random Forest                  │
│   - XGBoost                        │
│ • Risk scoring                     │
│ • Model artifacts saved            │
└───────────────────────────────────┘
        │
        ▼
model_predictions.csv + models/churn_model.pkl
```

## Dashboard Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              STREAMLIT APPLICATION (10 Pages)                    │
└─────────────────────────────────────────────────────────────────┘

Page 1: Executive Overview
├── KPI Cards (Customers, Churn Rate, Revenue, Health)
├── Health Distribution Pie Chart
├── Risk Category Bar Chart
└── Churn by Subscription Tier

Page 2: Customer Intelligence Hub
├── Engagement Analysis Tab
├── Subscription Insights Tab
├── Geographic View Tab
└── Device Patterns Tab

Page 3: Customer Search
├── Search by Customer ID / Risk / Health / Tier
├── Customer Profile Display
├── Risk Assessment Card
└── Recommended Actions

Page 4: Segment Explorer
├── Segment Selection Dropdown
├── Comparison Visualization
└── Segment Statistics Table

Page 5: Risk Monitoring
├── Risk Summary Cards (4 categories)
├── High-Risk Customer Table
└── Risk Factor Analysis

Page 6: Health Center
├── Health Score Distribution
├── Health Category Pie Chart
├── Health vs Churn Correlation
└── Key Health Metrics

Page 7: Revenue at Risk
├── Revenue Summary Cards
├── Revenue by Risk Category
└── Recovery Scenario Calculator

Page 8: Retention Opportunities
├── Win-Back Opportunities
├── Upsell Opportunities
└── Engagement Opportunities

Page 9: What-If Simulator
├── Churn Reduction Calculator
├── Campaign ROI Calculator
└── Scenario Modeling

Page 10: Recommendations
├── Priority Actions List
├── Key Insights
├── Implementation Timeline
└── Success Metrics
```

## File Structure

```
Netflix_Customer_Intelligence/
│
├── data/
│   ├── netflix_customer_churn.csv    # Original dataset
│   ├── prepared_data.csv             # After feature engineering
│   ├── segmented_data.csv            # After clustering
│   └── model_predictions.csv         # With ML predictions
│
├── notebooks/
│   ├── 01_Business_Understanding_and_Data_Preparation.ipynb
│   ├── 02_Customer_Behavior_and_Churn_Drivers.ipynb
│   ├── 03_Customer_Segmentation_and_Health_Scoring.ipynb
│   ├── 04_Churn_Prediction_and_Risk_Modeling.ipynb
│   └── 05_Retention_Strategy_and_Business_Recommendations.ipynb
│
├── streamlit_app/
│   └── app.py                        # 10-page dashboard
│
├── sql/
│   ├── schema.sql                    # Database schema
│   └── business_queries.sql          # 30+ analytical queries
│
├── models/
│   ├── churn_model.pkl               # Trained XGBoost model
│   ├── scaler.pkl                    # Feature scaler
│   ├── feature_columns.pkl           # Feature list
│   └── label_encoders.pkl            # Categorical encoders
│
├── src/
│   ├── __init__.py
│   └── utils.py                      # Helper functions
│
├── reports/
│   └── executive_summary.pdf         # Business report
│
├── docs/
│   └── overview.md                   # Project documentation
│
├── requirements.txt                  # Python dependencies
└── README.md                         # Project overview
```

## Key Metrics

| Metric | Value | Business Impact |
|--------|-------|-----------------|
| Total Customers | 5,000 | Dataset size |
| Churn Rate | ~25% | Primary problem |
| Model AUC | ~0.74 | Prediction accuracy |
| High-Risk Customers | ~15% | Target for intervention |
| Revenue at Risk | $X,XXX/month | Potential savings |

## Technologies Used

| Category | Tools |
|----------|-------|
| Data Analysis | pandas, numpy |
| Visualization | matplotlib, seaborn, plotly |
| Machine Learning | scikit-learn, XGBoost |
| Dashboard | Streamlit |
| Database | SQL (schema included) |
| Version Control | Git |
