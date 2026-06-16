-- Netflix Customer Intelligence - Database Schema

-- Customer Table
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    age INTEGER NOT NULL,
    gender VARCHAR(20) NOT NULL,
    subscription_type VARCHAR(20) NOT NULL,
    watch_hours DECIMAL(10,2),
    last_login_days INTEGER,
    region VARCHAR(50),
    device VARCHAR(50),
    monthly_fee DECIMAL(10,2),
    churned INTEGER DEFAULT 0,
    payment_method VARCHAR(50),
    number_of_profiles INTEGER DEFAULT 1,
    avg_watch_time_per_day DECIMAL(10,2),
    favorite_genre VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer Segments
CREATE TABLE customer_segments (
    segment_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES customers(customer_id),
    segment_name VARCHAR(50),
    health_score DECIMAL(5,2),
    risk_score DECIMAL(5,2),
    segment_date DATE DEFAULT CURRENT_DATE
);

-- Churn Predictions
CREATE TABLE churn_predictions (
    prediction_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES customers(customer_id),
    prediction_date DATE,
    churn_probability DECIMAL(5,4),
    risk_category VARCHAR(20),
    model_version VARCHAR(50)
);

-- Indexes
CREATE INDEX idx_customers_churned ON customers(churned);
CREATE INDEX idx_customers_subscription ON customers(subscription_type);
CREATE INDEX idx_customers_region ON customers(region);
CREATE INDEX idx_customers_device ON customers(device);
CREATE INDEX idx_customers_last_login ON customers(last_login_days);

-- Views
CREATE VIEW vw_customer_overview AS
SELECT 
    c.customer_id,
    c.age,
    c.gender,
    c.subscription_type,
    c.watch_hours,
    c.last_login_days,
    c.region,
    c.device,
    c.monthly_fee,
    c.churned,
    cs.segment_name,
    cs.health_score,
    cs.risk_score
FROM customers c
LEFT JOIN customer_segments cs ON c.customer_id = cs.customer_id;

CREATE VIEW vw_subscription_summary AS
SELECT 
    subscription_type,
    COUNT(*) as total_customers,
    SUM(CASE WHEN churned = 1 THEN 1 ELSE 0 END) as churned_count,
    ROUND(AVG(CASE WHEN churned = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate,
    ROUND(AVG(monthly_fee), 2) as avg_monthly_fee,
    ROUND(SUM(monthly_fee), 2) as total_revenue
FROM customers
GROUP BY subscription_type;
