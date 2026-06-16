"""
Utility functions for Netflix Customer Intelligence Platform.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def calculate_health_score(df):
    """
    Calculate customer health score (0-100).
    
    Higher score = healthier customer.
    """
    score = 100
    
    # Deduct for login recency (most important factor)
    score -= df['last_login_days'].clip(0, 40) * 1.0
    
    # Deduct for low engagement
    score -= (20 - df['watch_hours'].clip(0, 20)) * 0.5
    
    # Bonus for premium subscription
    score += np.where(df['subscription_type'] == 'Premium', 5, 0)
    score += np.where(df['subscription_type'] == 'Standard', 2, 0)
    
    # Bonus for multiple profiles
    score += (df['number_of_profiles'] - 1) * 2
    
    return score.clip(0, 100)


def calculate_risk_score(df):
    """
    Calculate churn risk score (0-100).
    
    Higher score = higher risk.
    """
    risk = 0
    
    # Login recency contribution (40 points max)
    risk += (df['last_login_days'] / 60 * 40).clip(0, 40)
    
    # Low engagement contribution (30 points max)
    risk += ((20 - df['watch_hours'].clip(0, 20)) / 20 * 30).clip(0, 30)
    
    # Subscription tier contribution (15 points max)
    risk += np.where(df['subscription_type'] == 'Basic', 15, 0)
    risk += np.where(df['subscription_type'] == 'Standard', 5, 0)
    
    # Single profile contribution (15 points max)
    risk += np.where(df['number_of_profiles'] == 1, 15, 0)
    
    return risk.clip(0, 100)


def assign_segment(row):
    """
    Assign customer segment based on behavior.
    """
    if row['watch_hours'] > 25 and row['last_login_days'] < 15:
        return 'Power Users'
    elif row['last_login_days'] > 35 or row['watch_hours'] < 5:
        return 'At-Risk'
    elif row['monthly_fee'] >= 15:
        return 'Premium'
    else:
        return 'Casual'


def calculate_clv(row, churn_rate_by_segment):
    """
    Estimate customer lifetime value.
    """
    segment = row.get('segment', 'Casual')
    retention = 1 - churn_rate_by_segment.get(segment, 0.25)
    
    if retention >= 0.99:
        retention = 0.98  # Cap for stability
    
    lifetime_months = min(1 / (1 - retention), 36)  # Cap at 3 years
    clv = row['monthly_fee'] * lifetime_months
    
    return clv


def get_risk_category(risk_score):
    """
    Categorize risk score into category.
    """
    if risk_score < 30:
        return 'Low'
    elif risk_score < 50:
        return 'Medium'
    elif risk_score < 70:
        return 'High'
    else:
        return 'Critical'


def get_health_category(health_score):
    """
    Categorize health score into category.
    """
    if health_score >= 80:
        return 'Healthy'
    elif health_score >= 60:
        return 'Monitor'
    elif health_score >= 40:
        return 'At-Risk'
    else:
        return 'Critical'


def simulate_retention_impact(current_churn, target_churn, customers, arpu):
    """
    Simulate revenue impact of retention improvement.
    """
    customers_saved = int(customers * (current_churn - target_churn))
    monthly_impact = customers_saved * arpu
    annual_impact = monthly_impact * 12
    
    return {
        'customers_saved': customers_saved,
        'monthly_impact': monthly_impact,
        'annual_impact': annual_impact
    }


def load_and_prepare_data(filepath):
    """
    Load and prepare the Netflix customer data.
    """
    df = pd.read_csv(filepath)
    
    # Add calculated fields
    df['health_score'] = calculate_health_score(df)
    df['risk_score'] = calculate_risk_score(df)
    df['segment'] = df.apply(assign_segment, axis=1)
    df['risk_category'] = df['risk_score'].apply(get_risk_category)
    df['health_category'] = df['health_score'].apply(get_health_category)
    df['clv'] = df['monthly_fee'] * 12
    
    return df
