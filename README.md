# Netflix Customer Intelligence Platform

I built this project to learn how to tackle a real business problem from start to finish. It's a complete customer churn analysis for a streaming service - the kind of thing a data analyst or product analyst would actually do on the job.

## Why I Chose This Problem

I've always been curious about subscription businesses. They're interesting because losing a customer isn't just one lost sale - it's lost revenue every month until you win them back. Netflix seemed like a good case study because everyone knows the product, and churn is a genuine problem they face.

The dataset I used has 5,000 customers with information about their viewing habits, subscription details, and whether they churned. It's synthetic, but realistic enough to practice on.

## What I Actually Did

### Step 1: Understanding the Data

Before jumping into analysis, I wanted to understand what I was working with. Turns out the data was pretty clean - no missing values, no duplicates. The churn rate was around 25%, which is actually high for Netflix (their real rate is closer to 2-3%), but that makes for more interesting analysis.

One thing that surprised me: watch hours didn't correlate with churn as strongly as I expected. I would have thought heavy watchers would be loyal, but that's not always true.

### Step 2: Finding the Patterns

I spent a lot of time exploring correlations. The strongest predictor turned out to be `last_login_days` - how recently someone opened the app. Customers who haven't logged in for 30+ days have dramatically higher churn rates.

This seems obvious in hindsight - if you're not using the product, you're probably going to cancel. But it gives us a clear intervention window: do something BEFORE they hit 30 days of inactivity.

Other findings:
- Basic tier has the highest churn (price-sensitive customers)
- Mobile users churn slightly more than TV users
- Some "power users" still churn - engagement isn't everything

### Step 3: Building Customer Segments

I used K-Means clustering to group customers into 4 segments:
- **Power Users** - Heavy watchers, recent activity, low churn
- **Premium** - Higher tier, stable
- **Casual** - Moderate engagement, medium churn risk
- **At-Risk** - Low engagement, high login recency, high churn

I also built a health score (0-100) that predicts churn probability. The scoring logic is heuristic-based, but it validates well - customers with low scores do churn more often.

### Step 4: Machine Learning Models

I compared three models:
- Logistic Regression (AUC ~0.65)
- Random Forest (AUC ~0.72)
- XGBoost (AUC ~0.74)

XGBoost performed best, but honestly, the simple correlation analysis was more actionable. The model confirms what I found in EDA: login recency is the most important feature.

I saved the trained model so it could be used in production (or at least in the dashboard).

### Step 5: Making It Actionable

The final notebook translates findings into specific recommendations:
- Set up automated re-engagement at 14-day inactivity
- Win-back campaigns for at-risk customers
- Upsell opportunities for engaged Basic users
- Loyalty programs for power users

## The Dashboard

I built a Streamlit app that simulates what a real retention analytics tool might look like. It has 10 sections:

1. **Executive Overview** - High-level KPIs
2. **Customer Intelligence** - Deep behavior analysis
3. **Customer Search** - Look up individual customers
4. **Segment Explorer** - Compare segments
5. **Risk Monitoring** - Track high-risk customers
6. **Health Center** - Health score distribution
7. **Revenue at Risk** - Financial impact
8. **Retention Opportunities** - Upsell and win-back targets
9. **What-If Simulator** - Model scenarios
10. **Recommendations** - Action items

To run it:
```bash
cd streamlit_app
streamlit run app.py
```

## Project Structure

```
Netflix_Customer_Intelligence/
├── data/
│   └── netflix_customer_churn.csv      # Original dataset
├── notebooks/
│   ├── 01_Business_Understanding_and_Data_Preparation.ipynb
│   ├── 02_Customer_Behavior_and_Churn_Drivers.ipynb
│   ├── 03_Customer_Segmentation_and_Health_Scoring.ipynb
│   ├── 04_Churn_Prediction_and_Risk_Modeling.ipynb
│   └── 05_Retention_Strategy_and_Business_Recommendations.ipynb
├── streamlit_app/
│   └── app.py                          # Interactive dashboard
├── sql/
│   ├── schema.sql                      # Database schema
│   └── business_queries.sql            # 30+ analytical queries
├── src/
│   └── utils.py                        # Helper functions
├── models/                             # Saved ML model
├── reports/                            # Executive summary
├── requirements.txt
└── README.md
```

## What I Learned

1. **Simple insights often beat complex models.** The correlation analysis and health score are more immediately useful than the ML model. Sometimes a good heuristic is better than a black-box predictor.

2. **Business context matters.** Understanding *why* customers churn is more valuable than just predicting *if* they will. The model says someone is at risk, but it doesn't tell you what to do about it.

3. **Segmentation enables action.** You can't treat all customers the same. Different segments need different strategies.

4. **Dashboards should answer questions.** Every chart and metric should lead to a decision. If it doesn't, it's just decoration.

## Technical Stack

- **Analysis:** Python, pandas, numpy, matplotlib, seaborn
- **Machine Learning:** scikit-learn, XGBoost
- **Visualization:** plotly
- **Dashboard:** Streamlit
- **SQL:** Business intelligence queries included

## Setup

```bash
# Clone the repo
git clone <repo-url>
cd Netflix_Customer_Intelligence

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run notebooks
jupyter notebook

# Run dashboard
cd streamlit_app
streamlit run app.py
```

## What I'd Do Differently

If I had more time, I'd:
- Add time-series analysis to see how behavior changes over time
- Build cohort analysis to understand customer lifecycles
- Design A/B tests for the retention strategies
- Improve the ML model with hyperparameter tuning
- Connect to a real database instead of CSV files

---

This was my first end-to-end analytics project. I tried to approach it the way I would a real job assignment - starting with business questions, exploring the data thoroughly, and ending with actionable recommendations.

If you have feedback or suggestions, I'd love to hear them.
