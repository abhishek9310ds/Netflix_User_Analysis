-- Netflix Customer Intelligence - Business Analytics Queries
-- 25+ queries for customer analytics

-- ============ REVENUE ANALYSIS ============

-- Q1: Total revenue and ARPU
SELECT 
    COUNT(*) as total_customers,
    SUM(monthly_fee) as total_monthly_revenue,
    ROUND(AVG(monthly_fee), 2) as arpu,
    ROUND(SUM(monthly_fee) * 12, 2) as annual_revenue_projection
FROM customers;

-- Q2: Revenue by subscription type
SELECT 
    subscription_type,
    COUNT(*) as customers,
    ROUND(SUM(monthly_fee), 2) as total_revenue,
    ROUND(AVG(monthly_fee), 2) as avg_revenue,
    ROUND(SUM(monthly_fee) * 100.0 / (SELECT SUM(monthly_fee) FROM customers), 2) as revenue_share_pct
FROM customers
GROUP BY subscription_type
ORDER BY total_revenue DESC;

-- Q3: Revenue at risk from churned customers
SELECT 
    subscription_type,
    COUNT(*) as churned_customers,
    ROUND(SUM(monthly_fee), 2) as revenue_lost,
    ROUND(AVG(monthly_fee), 2) as avg_lost_per_customer
FROM customers
WHERE churned = 1
GROUP BY subscription_type
ORDER BY revenue_lost DESC;

-- Q4: Revenue by region
SELECT 
    region,
    COUNT(*) as customers,
    ROUND(SUM(monthly_fee), 2) as total_revenue,
    ROUND(AVG(monthly_fee), 2) as arpu,
    ROUND(SUM(CASE WHEN churned = 1 THEN monthly_fee ELSE 0 END), 2) as revenue_at_risk
FROM customers
GROUP BY region
ORDER BY total_revenue DESC;

-- Q5: Revenue by payment method
SELECT 
    payment_method,
    COUNT(*) as customers,
    ROUND(SUM(monthly_fee), 2) as total_revenue,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct
FROM customers
GROUP BY payment_method
ORDER BY total_revenue DESC;

-- ============ CHURN ANALYSIS ============

-- Q6: Overall churn metrics
SELECT 
    COUNT(*) as total_customers,
    SUM(CASE WHEN churned = 1 THEN 1 ELSE 0 END) as churned_customers,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct,
    ROUND(SUM(CASE WHEN churned = 1 THEN monthly_fee ELSE 0 END), 2) as revenue_impact
FROM customers;

-- Q7: Churn rate by subscription type
SELECT 
    subscription_type,
    COUNT(*) as total_customers,
    SUM(CASE WHEN churned = 1 THEN 1 ELSE 0 END) as churned_count,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct,
    ROUND(AVG(watch_hours), 2) as avg_watch_hours
FROM customers
GROUP BY subscription_type
ORDER BY churn_rate_pct DESC;

-- Q8: Churn rate by region
SELECT 
    region,
    COUNT(*) as total_customers,
    SUM(CASE WHEN churned = 1 THEN 1 ELSE 0 END) as churned_count,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct
FROM customers
GROUP BY region
ORDER BY churn_rate_pct DESC;

-- Q9: Churn rate by device
SELECT 
    device,
    COUNT(*) as total_customers,
    SUM(CASE WHEN churned = 1 THEN 1 ELSE 0 END) as churned_count,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct,
    ROUND(AVG(watch_hours), 2) as avg_watch_hours
FROM customers
GROUP BY device
ORDER BY churn_rate_pct DESC;

-- Q10: Churn by age group
SELECT 
    CASE 
        WHEN age BETWEEN 18 AND 25 THEN '18-25'
        WHEN age BETWEEN 26 AND 35 THEN '26-35'
        WHEN age BETWEEN 36 AND 45 THEN '36-45'
        WHEN age BETWEEN 46 AND 55 THEN '46-55'
        ELSE '56+'
    END as age_group,
    COUNT(*) as customers,
    SUM(CASE WHEN churned = 1 THEN 1 ELSE 0 END) as churned,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct
FROM customers
GROUP BY 
    CASE 
        WHEN age BETWEEN 18 AND 25 THEN '18-25'
        WHEN age BETWEEN 26 AND 35 THEN '26-35'
        WHEN age BETWEEN 36 AND 45 THEN '36-45'
        WHEN age BETWEEN 46 AND 55 THEN '46-55'
        ELSE '56+'
    END
ORDER BY churn_rate_pct DESC;

-- Q11: High-risk customers (inactive > 30 days)
SELECT 
    COUNT(*) as high_risk_customers,
    ROUND(AVG(last_login_days), 1) as avg_days_inactive,
    ROUND(AVG(watch_hours), 2) as avg_watch_hours,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as actual_churn_rate
FROM customers
WHERE last_login_days > 30;

-- Q12: Churn by engagement level
SELECT 
    CASE 
        WHEN watch_hours < 10 THEN 'Low Engagement'
        WHEN watch_hours BETWEEN 10 AND 25 THEN 'Medium Engagement'
        WHEN watch_hours BETWEEN 25 AND 40 THEN 'High Engagement'
        ELSE 'Power Users'
    END as engagement_level,
    COUNT(*) as customers,
    SUM(CASE WHEN churned = 1 THEN 1 ELSE 0 END) as churned,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct
FROM customers
GROUP BY 
    CASE 
        WHEN watch_hours < 10 THEN 'Low Engagement'
        WHEN watch_hours BETWEEN 10 AND 25 THEN 'Medium Engagement'
        WHEN watch_hours BETWEEN 25 AND 40 THEN 'High Engagement'
        ELSE 'Power Users'
    END
ORDER BY churn_rate_pct DESC;

-- ============ SUBSCRIPTION ANALYSIS ============

-- Q13: Subscription distribution
SELECT 
    subscription_type,
    COUNT(*) as customers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers), 2) as pct_of_total,
    ROUND(AVG(watch_hours), 2) as avg_watch_hours,
    ROUND(AVG(number_of_profiles), 2) as avg_profiles
FROM customers
GROUP BY subscription_type;

-- Q14: Upsell candidates (Basic with high engagement)
SELECT 
    COUNT(*) as upsell_candidates,
    ROUND(AVG(watch_hours), 2) as avg_watch_hours,
    ROUND(AVG(monthly_fee), 2) as current_fee,
    ROUND((13.99 - AVG(monthly_fee)) * COUNT(*), 2) as potential_revenue_increase
FROM customers
WHERE subscription_type = 'Basic' AND watch_hours > 15;

-- Q15: Subscription by region
SELECT 
    region,
    subscription_type,
    COUNT(*) as customers,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY region), 2) as pct_in_region
FROM customers
GROUP BY region, subscription_type
ORDER BY region, customers DESC;

-- Q16: Profile count analysis
SELECT 
    number_of_profiles,
    COUNT(*) as customers,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct,
    ROUND(AVG(monthly_fee), 2) as avg_fee
FROM customers
GROUP BY number_of_profiles
ORDER BY number_of_profiles;

-- ============ REGION ANALYSIS ============

-- Q17: Region performance summary
SELECT 
    region,
    COUNT(*) as customers,
    ROUND(AVG(monthly_fee), 2) as arpu,
    ROUND(SUM(monthly_fee), 2) as total_revenue,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct,
    ROUND(AVG(watch_hours), 2) as avg_watch_hours
FROM customers
GROUP BY region
ORDER BY total_revenue DESC;

-- Q18: Top regions by customer count
SELECT 
    region,
    COUNT(*) as customers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers), 2) as pct_of_total,
    ROUND(AVG(watch_hours), 2) as avg_engagement
FROM customers
GROUP BY region
ORDER BY customers DESC
LIMIT 5;

-- Q19: Regions with highest churn risk
SELECT 
    region,
    COUNT(*) as customers,
    SUM(CASE WHEN churned = 1 THEN 1 ELSE 0 END) as churned,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct,
    ROUND(AVG(last_login_days), 1) as avg_login_days
FROM customers
GROUP BY region
HAVING AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) > 0.25
ORDER BY churn_rate_pct DESC;

-- ============ DEVICE ANALYSIS ============

-- Q20: Device usage statistics
SELECT 
    device,
    COUNT(*) as customers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers), 2) as pct_of_total,
    ROUND(AVG(watch_hours), 2) as avg_watch_hours,
    ROUND(AVG(avg_watch_time_per_day), 2) as avg_daily_watch,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct
FROM customers
GROUP BY device
ORDER BY customers DESC;

-- Q21: Device by subscription type
SELECT 
    device,
    subscription_type,
    COUNT(*) as customers,
    ROUND(AVG(monthly_fee), 2) as avg_fee
FROM customers
GROUP BY device, subscription_type
ORDER BY device, subscription_type;

-- ============ SEGMENT ANALYSIS ============

-- Q22: Customer value segments
SELECT 
    CASE 
        WHEN monthly_fee >= 17 THEN 'High Value'
        WHEN monthly_fee >= 12 THEN 'Medium Value'
        ELSE 'Standard Value'
    END as value_segment,
    COUNT(*) as customers,
    ROUND(SUM(monthly_fee), 2) as total_revenue,
    ROUND(AVG(watch_hours), 2) as avg_engagement,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct
FROM customers
GROUP BY 
    CASE 
        WHEN monthly_fee >= 17 THEN 'High Value'
        WHEN monthly_fee >= 12 THEN 'Medium Value'
        ELSE 'Standard Value'
    END
ORDER BY total_revenue DESC;

-- Q23: At-risk customer profile
SELECT 
    region,
    subscription_type,
    device,
    COUNT(*) as at_risk_count,
    ROUND(AVG(watch_hours), 2) as avg_watch,
    ROUND(AVG(last_login_days), 1) as avg_inactive_days
FROM customers
WHERE churned = 1
GROUP BY region, subscription_type, device
ORDER BY at_risk_count DESC
LIMIT 10;

-- Q24: Retention opportunity analysis
SELECT 
    region,
    subscription_type,
    COUNT(*) as customers_to_target,
    ROUND(SUM(monthly_fee), 2) as revenue_opportunity,
    ROUND(AVG(last_login_days), 1) as avg_inactive_days
FROM customers
WHERE last_login_days BETWEEN 15 AND 45 
    AND churned = 0
    AND watch_hours < 15
GROUP BY region, subscription_type
ORDER BY revenue_opportunity DESC;

-- Q25: Genre preference by churn
SELECT 
    favorite_genre,
    COUNT(*) as total_customers,
    SUM(CASE WHEN churned = 1 THEN 1 ELSE 0 END) as churned,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct,
    ROUND(AVG(watch_hours), 2) as avg_watch_hours
FROM customers
GROUP BY favorite_genre
ORDER BY churn_rate_pct DESC;

-- Q26: Gender analysis
SELECT 
    gender,
    COUNT(*) as customers,
    ROUND(AVG(monthly_fee), 2) as avg_fee,
    ROUND(AVG(watch_hours), 2) as avg_watch,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct
FROM customers
GROUP BY gender
ORDER BY customers DESC;

-- Q27: Monthly fee distribution
SELECT 
    CASE 
        WHEN monthly_fee < 10 THEN 'Basic ($8.99)'
        WHEN monthly_fee < 15 THEN 'Standard ($13.99)'
        ELSE 'Premium ($17.99)'
    END as fee_tier,
    COUNT(*) as customers,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct,
    ROUND(AVG(watch_hours), 2) as avg_watch
FROM customers
GROUP BY 
    CASE 
        WHEN monthly_fee < 10 THEN 'Basic ($8.99)'
        WHEN monthly_fee < 15 THEN 'Standard ($13.99)'
        ELSE 'Premium ($17.99)'
    END;

-- Q28: Customer lifetime value estimation
SELECT 
    customer_id,
    monthly_fee,
    number_of_profiles,
    watch_hours,
    ROUND(monthly_fee * 12, 2) as estimated_annual_value,
    ROUND(monthly_fee * 36, 2) as estimated_3yr_value
FROM customers
WHERE churned = 0
ORDER BY estimated_3yr_value DESC
LIMIT 100;

-- Q29: Engagement quartile analysis
SELECT 
    NTILE(4) OVER (ORDER BY watch_hours) as engagement_quartile,
    COUNT(*) as customers,
    ROUND(MIN(watch_hours), 2) as min_hours,
    ROUND(MAX(watch_hours), 2) as max_hours,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate_pct
FROM customers
GROUP BY NTILE(4) OVER (ORDER BY watch_hours)
ORDER BY engagement_quartile;

-- Q30: Comprehensive dashboard query
SELECT 
    (SELECT COUNT(*) FROM customers) as total_customers,
    (SELECT ROUND(SUM(monthly_fee), 2) FROM customers) as total_revenue,
    (SELECT ROUND(AVG(monthly_fee), 2) FROM customers) as arpu,
    (SELECT ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) FROM customers) as churn_rate_pct,
    (SELECT ROUND(AVG(watch_hours), 2) FROM customers) as avg_watch_hours,
    (SELECT COUNT(*) FROM customers WHERE last_login_days <= 7) as active_users_7d,
    (SELECT COUNT(*) FROM customers WHERE last_login_days > 30) as inactive_users_30d;
