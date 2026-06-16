# Project Documentation

## Overview

This project analyzes Netflix customer churn data to identify at-risk customers and develop retention strategies.

## Notebooks

1. **01_Business_Understanding_and_Data_Preparation.ipynb**
   - Data quality assessment
   - Feature engineering
   - Initial hypothesis formation

2. **02_Customer_Behavior_and_Churn_Drivers.ipynb**
   - Churn analysis by subscription, region, device
   - Correlation analysis
   - Key driver identification

3. **03_Customer_Segmentation_and_Health_Scoring.ipynb**
   - K-Means clustering
   - Health score development
   - Segment profiling

4. **04_Churn_Prediction_and_Risk_Modeling.ipynb**
   - Model comparison (Logistic Regression, Random Forest, XGBoost)
   - Feature importance
   - Risk scoring

5. **05_Retention_Strategy_and_Business_Recommendations.ipynb**
   - Segment-specific strategies
   - Revenue impact simulation
   - Action prioritization

## Streamlit Application

The dashboard provides 10 sections for customer intelligence:

1. Executive Command Center
2. Customer Intelligence Hub
3. Customer Search
4. Risk Monitoring Center
5. Segment Explorer
6. Revenue At Risk Analyzer
7. Retention Strategy Simulator
8. Churn Prediction Center
9. Customer Health Dashboard
10. Business Recommendations Engine

## SQL Queries

30+ business analytics queries covering:
- Revenue analysis
- Churn analysis
- Subscription analysis
- Regional analysis
- Device analysis
- Segment analysis

## Model Artifacts

- `churn_model.pkl` - Trained XGBoost model
- `scaler.pkl` - StandardScaler for feature normalization
- `feature_columns.pkl` - Feature column names
- `label_encoders.pkl` - Categorical encoders
