"""
Netflix Retention Command Center
A business analytics application for customer retention intelligence.

This is not just a dashboard - it's operational software for retention teams.
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Netflix Retention Command Center",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Netflix-inspired styling
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #E50914;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #B3B3B3;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #333;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #B3B3B3;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-delta-positive {
        color: #46D369;
        font-size: 0.9rem;
    }
    .metric-delta-negative {
        color: #E50914;
        font-size: 0.9rem;
    }
    .risk-critical { color: #E50914; font-weight: 600; }
    .risk-high { color: #FF6B35; font-weight: 600; }
    .risk-medium { color: #FFC107; font-weight: 600; }
    .risk-low { color: #46D369; font-weight: 600; }
    
    div[data-testid="stSidebarNav"] { display: none; }
    .sidebar-section {
        padding: 0.5rem 0;
        border-bottom: 1px solid #333;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #1a1a2e;
        border-radius: 4px 4px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E50914;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Data loading with caching
@st.cache_data
def load_data():
    """Load customer data with engineered features."""
    df = pd.read_csv('data/netflix_customer_churn.csv')
    
    # Feature engineering
    df['health_score'] = 100 - (df['last_login_days'] * 1.5).clip(0, 60) - (20 - df['watch_hours'].clip(0, 20))
    df['health_score'] = df['health_score'].clip(0, 100)
    
    def health_cat(score):
        if score >= 80: return 'Healthy'
        elif score >= 60: return 'Monitor'
        elif score >= 40: return 'At-Risk'
        else: return 'Critical'
    
    df['health_category'] = df['health_score'].apply(health_cat)
    
    # Engagement level
    df['engagement_level'] = pd.cut(df['watch_hours'], 
                                     bins=[-1, 5, 15, 30, 100],
                                     labels=['Low', 'Medium', 'High', 'Power'])
    
    # Simple risk score
    df['risk_score'] = 0
    df.loc[df['last_login_days'] > 30, 'risk_score'] += 3
    df.loc[df['last_login_days'] > 45, 'risk_score'] += 2
    df.loc[df['watch_hours'] < 10, 'risk_score'] += 2
    df.loc[df['subscription_type'] == 'Basic', 'risk_score'] += 1
    df.loc[df['number_of_profiles'] == 1, 'risk_score'] += 1
    
    def risk_cat(score):
        if score <= 1: return 'Low'
        elif score <= 3: return 'Medium'
        elif score <= 5: return 'High'
        else: return 'Critical'
    
    df['risk_category'] = df['risk_score'].apply(risk_cat)
    
    # CLV estimate
    df['clv_estimate'] = df['monthly_fee'] * 12
    
    return df

@st.cache_resource
def load_model():
    """Load the trained ML model."""
    try:
        model = joblib.load('models/churn_model.pkl')
        scaler = joblib.load('models/scaler.pkl')
        feature_cols = joblib.load('models/feature_columns.pkl')
        return model, scaler, feature_cols
    except:
        return None, None, None

# Load data
try:
    df = load_data()
    model, scaler, feature_cols = load_model()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Sidebar navigation
st.sidebar.markdown("### 🎬 Netflix Retention Command Center")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Executive Overview",
     "👥 Customer Intelligence",
     "🔍 Customer Search",
     "📈 Segment Explorer",
     "⚠️ Risk Monitoring",
     "❤️ Health Center",
     "💰 Revenue at Risk",
     "🎯 Retention Opportunities",
     "🧪 What-If Simulator",
     "📋 Recommendations"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Total Customers:** {len(df):,}")
st.sidebar.markdown(f"**Active Churn Rate:** {df['churned'].mean()*100:.1f}%")

# Helper functions
def create_kpi_card(col, label, value, delta=None, delta_color='normal'):
    """Create a styled KPI card."""
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {f'<div class="metric-delta-{delta_color}">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)

def risk_color(risk):
    """Return color based on risk level."""
    colors = {'Low': '#46D369', 'Medium': '#FFC107', 'High': '#FF6B35', 'Critical': '#E50914'}
    return colors.get(risk, '#B3B3B3')

# ==================== PAGE 1: EXECUTIVE OVERVIEW ====================
if page == "📊 Executive Overview":
    st.markdown('<div class="main-header">Executive Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time retention intelligence at a glance</div>', unsafe_allow_html=True)
    
    # Top-level KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    total_customers = len(df)
    churned = df['churned'].sum()
    churn_rate = df['churned'].mean() * 100
    total_revenue = df['monthly_fee'].sum()
    revenue_lost = df[df['churned']==1]['monthly_fee'].sum()
    avg_health = df['health_score'].mean()
    high_risk_count = len(df[(df['risk_category'].isin(['High', 'Critical'])) & (df['churned']==0)])
    
    create_kpi_card(col1, "Total Customers", f"{total_customers:,}")
    create_kpi_card(col2, "Churn Rate", f"{churn_rate:.1f}%", f"↑ vs last month", "negative")
    create_kpi_card(col3, "Monthly Revenue", f"${total_revenue:,.0f}")
    create_kpi_card(col4, "Revenue Lost to Churn", f"${revenue_lost:,.0f}", "This month", "negative")
    
    col1, col2, col3, col4 = st.columns(4)
    create_kpi_card(col1, "Avg Health Score", f"{avg_health:.0f}", "Out of 100")
    create_kpi_card(col2, "High-Risk Customers", f"{high_risk_count:,}", "Active customers")
    create_kpi_card(col3, "Revenue at Risk", f"${df[(df['risk_category'].isin(['High', 'Critical'])) & (df['churned']==0)]['monthly_fee'].sum():,.0f}")
    create_kpi_card(col4, "Avg CLV", f"${df['clv_estimate'].mean():,.0f}")
    
    st.markdown("---")
    
    # Key charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Customer Health Distribution")
        health_counts = df['health_category'].value_counts()
        colors = ['#46D369', '#FFC107', '#FF6B35', '#E50914']
        fig = go.Figure(data=[go.Pie(
            labels=health_counts.index, 
            values=health_counts.values,
            marker_colors=colors,
            hole=0.4
        )])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Risk Category Distribution")
        risk_counts = df['risk_category'].value_counts()
        risk_order = ['Low', 'Medium', 'High', 'Critical']
        risk_counts = risk_counts.reindex(risk_order)
        
        fig = go.Figure(data=[go.Bar(
            x=risk_counts.index,
            y=risk_counts.values,
            marker_color=[risk_color(r) for r in risk_counts.index]
        )])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=350,
            xaxis_title="Risk Category",
            yaxis_title="Number of Customers"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Churn by segment
    st.subheader("Churn Rate by Subscription Tier")
    churn_by_sub = df.groupby('subscription_type')['churned'].mean() * 100
    
    fig = go.Figure(data=[go.Bar(
        x=churn_by_sub.index,
        y=churn_by_sub.values,
        marker_color=['#E50914', '#FFC107', '#46D369'],
        text=[f'{v:.1f}%' for v in churn_by_sub.values],
        textposition='outside'
    )])
    fig.add_hline(y=churn_rate, line_dash="dash", line_color="white", 
                  annotation_text=f"Average: {churn_rate:.1f}%")
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=350,
        yaxis_title="Churn Rate (%)"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE 2: CUSTOMER INTELLIGENCE ====================
elif page == "👥 Customer Intelligence":
    st.markdown('<div class="main-header">Customer Intelligence Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Deep dive into customer behavior patterns</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Engagement Analysis", "Subscription Insights", "Geographic View", "Device Patterns"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Watch Hours Distribution")
            fig = go.Figure(data=[go.Histogram(x=df['watch_hours'], nbinsx=40, 
                                               marker_color='#E50914', opacity=0.8)])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=350,
                xaxis_title="Watch Hours",
                yaxis_title="Number of Customers"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Login Recency vs Churn")
            login_churn = df.groupby(pd.cut(df['last_login_days'], bins=[0,7,14,30,60,100]))['churned'].mean() * 100
            fig = go.Figure(data=[go.Bar(
                x=['0-7', '8-14', '15-30', '31-60', '60+'],
                y=login_churn.values,
                marker_color=['#46D369', '#FFC107', '#FF6B35', '#E50914', '#B3B3B3']
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=350,
                xaxis_title="Days Since Last Login",
                yaxis_title="Churn Rate (%)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Engagement Level Distribution")
        eng_counts = df['engagement_level'].value_counts()
        fig = go.Figure(data=[go.Bar(
            x=eng_counts.index,
            y=eng_counts.values,
            marker_color=['#E50914', '#FFC107', '#46D369', '#1DB954']
        )])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Subscription Distribution")
            sub_counts = df['subscription_type'].value_counts()
            fig = go.Figure(data=[go.Pie(
                labels=sub_counts.index,
                values=sub_counts.values,
                marker_colors=['#E50914', '#FFC107', '#46D369'],
                hole=0.4
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Revenue by Tier")
            rev_by_sub = df.groupby('subscription_type')['monthly_fee'].sum()
            fig = go.Figure(data=[go.Bar(
                x=rev_by_sub.index,
                y=rev_by_sub.values,
                marker_color=['#E50914', '#FFC107', '#46D369']
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=350,
                yaxis_title="Monthly Revenue ($)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Churn Rate by Region")
        region_churn = df.groupby('region')['churned'].mean() * 100
        fig = go.Figure(data=[go.Bar(
            x=region_churn.index,
            y=region_churn.values,
            marker_color='#E50914'
        )])
        fig.add_hline(y=churn_rate, line_dash="dash", line_color="white")
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=400,
            yaxis_title="Churn Rate (%)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Device Usage")
            device_counts = df['device'].value_counts()
            fig = go.Figure(data=[go.Pie(
                labels=device_counts.index,
                values=device_counts.values,
                hole=0.4
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Churn by Device")
            device_churn = df.groupby('device')['churned'].mean() * 100
            fig = go.Figure(data=[go.Bar(
                x=device_churn.index,
                y=device_churn.values,
                marker_color='#E50914'
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=350,
                yaxis_title="Churn Rate (%)"
            )
            st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE 3: CUSTOMER SEARCH ====================
elif page == "🔍 Customer Search":
    st.markdown('<div class="main-header">Customer Search</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Look up individual customer profiles and risk assessments</div>', unsafe_allow_html=True)
    
    # Search inputs
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        search_type = st.selectbox("Search By", ["Customer ID", "Risk Category", "Health Category", "Subscription"])
    
    with col2:
        if search_type == "Customer ID":
            customer_ids = df['customer_id'].tolist()
            search_value = st.selectbox("Select Customer", customer_ids)
        elif search_type == "Risk Category":
            search_value = st.selectbox("Select Risk", ["Low", "Medium", "High", "Critical"])
        elif search_type == "Health Category":
            search_value = st.selectbox("Select Health", ["Healthy", "Monitor", "At-Risk", "Critical"])
        else:
            search_value = st.selectbox("Select Tier", ["Basic", "Standard", "Premium"])
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("Search", type="primary")
    
    # Display results
    if search_type == "Customer ID":
        customer = df[df['customer_id'] == search_value].iloc[0]
        
        st.markdown("---")
        st.subheader("Customer Profile")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            **Customer ID:** `{customer['customer_id']}`\n
            **Age:** {customer['age']}\n
            **Gender:** {customer['gender']}\n
            **Region:** {customer['region']}
            """)
        
        with col2:
            st.markdown(f"""
            **Subscription:** {customer['subscription_type']}\n
            **Monthly Fee:** ${customer['monthly_fee']:.2f}\n
            **Payment Method:** {customer['payment_method']}\n
            **Profiles:** {customer['number_of_profiles']}
            """)
        
        with col3:
            st.markdown(f"""
            **Watch Hours:** {customer['watch_hours']:.1f}\n
            **Last Login:** {customer['last_login_days']} days ago\n
            **Favorite Genre:** {customer['favorite_genre']}\n
            **Device:** {customer['device']}
            """)
        
        st.markdown("---")
        st.subheader("Risk Assessment")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            health_color = risk_color(customer['health_category'])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Health Score</div>
                <div class="metric-value" style="color: {health_color}">{customer['health_score']:.0f}</div>
                <div style="color: {health_color}">{customer['health_category']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            risk_col = risk_color(customer['risk_category'])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Risk Category</div>
                <div class="metric-value" style="color: {risk_col}">{customer['risk_category']}</div>
                <div style="color: {risk_col}">Risk Score: {customer['risk_score']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            churn_status = "CHURNED" if customer['churned'] == 1 else "ACTIVE"
            status_color = "#E50914" if customer['churned'] == 1 else "#46D369"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Account Status</div>
                <div class="metric-value" style="color: {status_color}">{churn_status}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Estimated CLV</div>
                <div class="metric-value">${customer['clv_estimate']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Recommendations based on profile
        st.markdown("---")
        st.subheader("Recommended Actions")
        
        if customer['health_category'] in ['At-Risk', 'Critical']:
            st.warning("⚠️ This customer is at high risk of churning. Consider immediate intervention.")
            st.markdown("""
            - Send personalized win-back email with discount offer
            - Reach out via customer success for feedback
            - Highlight new content in their preferred genres
            """)
        elif customer['health_category'] == 'Monitor':
            st.info("ℹ️ This customer shows early warning signs. Monitor closely.")
            st.markdown("""
            - Send re-engagement email with content recommendations
            - Offer upgrade incentive if on Basic tier
            """)
        else:
            st.success("✅ This customer is healthy and engaged.")
            st.markdown("""
            - Consider for referral program
            - Potential candidate for loyalty rewards
            """)
    
    else:
        # Filter by category
        if search_type == "Risk Category":
            filtered = df[df['risk_category'] == search_value]
        elif search_type == "Health Category":
            filtered = df[df['health_category'] == search_value]
        else:
            filtered = df[df['subscription_type'] == search_value]
        
        st.markdown(f"**Found {len(filtered):,} customers**")
        
        # Display top customers
        display_cols = ['customer_id', 'subscription_type', 'watch_hours', 'last_login_days', 
                       'health_score', 'risk_category', 'monthly_fee', 'churned']
        st.dataframe(filtered[display_cols].head(20), use_container_width=True)

# ==================== PAGE 4: SEGMENT EXPLORER ====================
elif page == "📈 Segment Explorer":
    st.markdown('<div class="main-header">Segment Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Compare and analyze customer segments</div>', unsafe_allow_html=True)
    
    # Segment selection
    col1, col2 = st.columns(2)
    
    with col1:
        seg1 = st.selectbox("Primary Segment", ["subscription_type", "region", "device", "engagement_level"], key='seg1')
    
    with col2:
        seg2 = st.selectbox("Compare By", ["churned", "health_category", "risk_category"], key='seg2')
    
    # Create comparison
    if seg2 == "churned":
        comparison = df.groupby(seg1)['churned'].agg(['mean', 'count'])
        comparison['mean'] = comparison['mean'] * 100
        comparison.columns = ['Churn Rate (%)', 'Customers']
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=comparison.index.astype(str),
            y=comparison['Churn Rate (%)'],
            name='Churn Rate',
            marker_color='#E50914',
            text=[f'{v:.1f}%' for v in comparison['Churn Rate (%)']],
            textposition='outside'
        ))
        fig.add_hline(y=df['churned'].mean()*100, line_dash="dash", line_color="white",
                     annotation_text=f"Average: {df['churned'].mean()*100:.1f}%")
        
    else:
        cross_tab = pd.crosstab(df[seg1], df[seg2], normalize='index') * 100
        fig = go.Figure()
        for col in cross_tab.columns:
            fig.add_trace(go.Bar(
                x=cross_tab.index.astype(str),
                y=cross_tab[col],
                name=str(col),
                marker_color=risk_color(str(col)) if seg2 in ['risk_category', 'health_category'] else None
            ))
        fig.update_layout(barmode='stack')
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Segment statistics
    st.subheader("Segment Statistics")
    seg_stats = df.groupby(seg1).agg({
        'customer_id': 'count',
        'churned': 'mean',
        'watch_hours': 'mean',
        'monthly_fee': ['mean', 'sum'],
        'health_score': 'mean'
    }).round(2)
    
    seg_stats.columns = ['Customers', 'Churn Rate', 'Avg Watch Hours', 'Avg Fee', 'Total Revenue', 'Avg Health']
    seg_stats['Churn Rate'] = (seg_stats['Churn Rate'] * 100).round(1)
    
    st.dataframe(seg_stats, use_container_width=True)

# ==================== PAGE 5: RISK MONITORING ====================
elif page == "⚠️ Risk Monitoring":
    st.markdown('<div class="main-header">Churn Risk Monitoring</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Identify and track high-risk customers</div>', unsafe_allow_html=True)
    
    # Risk summary
    col1, col2, col3, col4 = st.columns(4)
    
    for i, (cat, col) in enumerate(zip(['Low', 'Medium', 'High', 'Critical'], [col1, col2, col3, col4])):
        count = len(df[df['risk_category'] == cat])
        revenue = df[df['risk_category'] == cat]['monthly_fee'].sum()
        churn_rate = df[df['risk_category'] == cat]['churned'].mean() * 100
        
        col.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid {risk_color(cat)};">
            <div class="metric-label">{cat} Risk</div>
            <div class="metric-value">{count:,}</div>
            <div style="color: {risk_color(cat)}; font-size: 0.9rem;">
                ${revenue:,.0f}/mo • {churn_rate:.1f}% churn
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # High-risk customers table
    st.subheader("High-Risk Customers (Active)")
    
    high_risk = df[(df['risk_category'].isin(['High', 'Critical'])) & (df['churned'] == 0)].copy()
    high_risk = high_risk.sort_values('health_score')
    
    st.markdown(f"**{len(high_risk):,} customers** at high risk of churning")
    st.markdown(f"**${high_risk['monthly_fee'].sum():,.0f}** monthly revenue at risk")
    
    display_cols = ['customer_id', 'subscription_type', 'watch_hours', 'last_login_days', 
                   'health_score', 'risk_category', 'monthly_fee', 'clv_estimate']
    
    st.dataframe(
        high_risk[display_cols].head(50).style.applymap(
            lambda x: f'color: {risk_color(x)}' if isinstance(x, str) and x in ['High', 'Critical'] else '',
            subset=['risk_category']
        ),
        use_container_width=True
    )
    
    # Risk factors
    st.subheader("Common Risk Factors")
    
    col1, col2 = st.columns(2)
    
    with col1:
        inactive = len(df[df['last_login_days'] > 30])
        st.metric("Inactive > 30 days", f"{inactive:,}", f"{inactive/len(df)*100:.1f}%")
    
    with col2:
        low_engagement = len(df[df['watch_hours'] < 10])
        st.metric("Low Engagement (<10 hrs)", f"{low_engagement:,}", f"{low_engagement/len(df)*100:.1f}%")

# ==================== PAGE 6: HEALTH CENTER ====================
elif page == "❤️ Health Center":
    st.markdown('<div class="main-header">Customer Health Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Monitor overall customer health trends</div>', unsafe_allow_html=True)
    
    # Health distribution
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Health Score Distribution")
        fig = go.Figure(data=[go.Histogram(
            x=df['health_score'],
            nbinsx=20,
            marker_color='#46D369',
            opacity=0.8
        )])
        fig.add_vline(x=df['health_score'].mean(), line_dash="dash", line_color="white",
                     annotation_text=f"Mean: {df['health_score'].mean():.0f}")
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=400,
            xaxis_title="Health Score",
            yaxis_title="Number of Customers"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Health by Category")
        health_counts = df['health_category'].value_counts()
        health_order = ['Healthy', 'Monitor', 'At-Risk', 'Critical']
        health_counts = health_counts.reindex(health_order)
        
        fig = go.Figure(data=[go.Pie(
            labels=health_counts.index,
            values=health_counts.values,
            marker_colors=['#46D369', '#FFC107', '#FF6B35', '#E50914'],
            hole=0.4
        )])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Health vs Churn correlation
    st.subheader("Health Score vs Actual Churn")
    
    health_churn = df.groupby('health_category')['churned'].agg(['mean', 'count'])
    health_churn['mean'] = health_churn['mean'] * 100
    
    fig = go.Figure(data=[go.Bar(
        x=health_churn.index,
        y=health_churn['mean'],
        marker_color=['#46D369', '#FFC107', '#FF6B35', '#E50914'],
        text=[f'{v:.1f}%' for v in health_churn['mean']],
        textposition='outside'
    )])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=400,
        xaxis_title="Health Category",
        yaxis_title="Actual Churn Rate (%)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Health metrics
    st.subheader("Key Health Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    for i, (cat, col) in enumerate(zip(['Healthy', 'Monitor', 'At-Risk', 'Critical'], [col1, col2, col3, col4])):
        cat_df = df[df['health_category'] == cat]
        avg_watch = cat_df['watch_hours'].mean()
        avg_login = cat_df['last_login_days'].mean()
        
        col.metric(
            f"{cat}",
            f"{len(cat_df):,} customers",
            f"Watch: {avg_watch:.1f}h • Login: {avg_login:.0f}d"
        )

# ==================== PAGE 7: REVENUE AT RISK ====================
elif page == "💰 Revenue at Risk":
    st.markdown('<div class="main-header">Revenue at Risk Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Quantify revenue exposure and potential recovery</div>', unsafe_allow_html=True)
    
    # Revenue summary
    total_revenue = df['monthly_fee'].sum()
    churned_revenue = df[df['churned'] == 1]['monthly_fee'].sum()
    at_risk_revenue = df[(df['risk_category'].isin(['High', 'Critical'])) & (df['churned'] == 0)]['monthly_fee'].sum()
    
    col1, col2, col3 = st.columns(3)
    
    create_kpi_card(col1, "Total Monthly Revenue", f"${total_revenue:,.0f}")
    create_kpi_card(col2, "Lost to Churn", f"${churned_revenue:,.0f}", f"{churned_revenue/total_revenue*100:.1f}% of total", "negative")
    create_kpi_card(col3, "Revenue at Risk", f"${at_risk_revenue:,.0f}", "From active high-risk customers", "negative")
    
    st.markdown("---")
    
    # Revenue by risk category
    st.subheader("Revenue Distribution by Risk Category")
    
    rev_by_risk = df.groupby('risk_category')['monthly_fee'].sum()
    rev_by_risk = rev_by_risk.reindex(['Low', 'Medium', 'High', 'Critical'])
    
    fig = go.Figure(data=[go.Bar(
        x=rev_by_risk.index,
        y=rev_by_risk.values,
        marker_color=[risk_color(r) for r in rev_by_risk.index],
        text=[f'${v:,.0f}' for v in rev_by_risk.values],
        textposition='outside'
    )])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=400,
        yaxis_title="Monthly Revenue ($)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Recovery scenarios
    st.subheader("Revenue Recovery Scenarios")
    
    high_risk = df[(df['risk_category'].isin(['High', 'Critical'])) & (df['churned'] == 0)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        save_rate = st.slider("Expected Save Rate (%)", 0, 50, 20)
    
    with col2:
        potential_saves = int(len(high_risk) * save_rate / 100)
        potential_revenue = potential_saves * high_risk['monthly_fee'].mean()
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Potential Recovery</div>
            <div class="metric-value">${potential_revenue:,.0f}</div>
            <div class="metric-delta-positive">per month (${potential_revenue*12:,.0f}/year)</div>
            <div style="margin-top: 0.5rem; color: #B3B3B3;">
                {potential_saves:,} customers saved
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==================== PAGE 8: RETENTION OPPORTUNITIES ====================
elif page == "🎯 Retention Opportunities":
    st.markdown('<div class="main-header">Retention Opportunity Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Identify actionable retention and upsell opportunities</div>', unsafe_allow_html=True)
    
    # Opportunity 1: Win-back
    st.subheader("🔄 Win-Back Opportunities")
    
    at_risk = df[(df['risk_category'].isin(['High', 'Critical'])) & (df['churned'] == 0)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **{len(at_risk):,} customers** showing high-risk signals
        
        - Average health score: **{at_risk['health_score'].mean():.0f}**
        - Revenue at stake: **${at_risk['monthly_fee'].sum():,.0f}/month**
        
        **Recommended Actions:**
        - Immediate win-back email with 20% discount
        - Personal outreach for high-value customers
        - Content recommendations based on history
        """)
    
    with col2:
        # High-value at-risk
        high_value_at_risk = at_risk[at_risk['monthly_fee'] >= 15].sort_values('monthly_fee', ascending=False)
        st.markdown(f"**Top 10 High-Value At-Risk Customers:**")
        st.dataframe(high_value_at_risk[['customer_id', 'subscription_type', 'monthly_fee', 'health_score']].head(10), 
                    use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Opportunity 2: Upsell
    st.subheader("📈 Upsell Opportunities")
    
    upsell_candidates = df[
        (df['subscription_type'] == 'Basic') & 
        (df['watch_hours'] > 15) & 
        (df['churned'] == 0)
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **{len(upsell_candidates):,} Basic users** with high engagement
        
        - Currently paying: **$8.99/month**
        - Upsell to Standard: **$13.99/month** (+$5)
        - Potential revenue increase: **${len(upsell_candidates) * 5:,.0f}/month**
        
        **Recommended Actions:**
        - Highlight Standard benefits (HD, more profiles)
        - Limited-time upgrade discount
        - Show what they're missing
        """)
    
    with col2:
        st.markdown("**Top Upsell Candidates:**")
        st.dataframe(upsell_candidates[['customer_id', 'watch_hours', 'health_score', 'monthly_fee']].head(10),
                    use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Opportunity 3: Engagement
    st.subheader("🎯 Engagement Opportunities")
    
    low_engagement = df[
        (df['watch_hours'] < 10) & 
        (df['last_login_days'] <= 14) & 
        (df['churned'] == 0)
    ]
    
    st.markdown(f"""
    **{len(low_engagement):,} active customers** with low engagement
    
    These customers are logging in but not watching much. They need:
    - Personalized content recommendations
    - Highlight trending shows in their genres
    - Gamification to increase watch time
    """)

# ==================== PAGE 9: WHAT-IF SIMULATOR ====================
elif page == "🧪 What-If Simulator":
    st.markdown('<div class="main-header">What-If Simulation Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Model the impact of retention scenarios</div>', unsafe_allow_html=True)
    
    st.markdown("### Churn Reduction Impact Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_churn = df['churned'].mean() * 100
        target_churn = st.slider("Target Churn Rate (%)", 0.0, current_churn, current_churn - 5.0)
        
        arpu = df['monthly_fee'].mean()
        customers_saved = int(len(df) * (current_churn - target_churn) / 100)
        monthly_revenue = customers_saved * arpu
        annual_revenue = monthly_revenue * 12
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Current Churn Rate</div>
            <div class="metric-value">{current_churn:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Target Churn Rate</div>
            <div class="metric-value" style="color: #46D369;">{target_churn:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Customers Saved</div>
            <div class="metric-value">{customers_saved:,}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Monthly Revenue Recovered</div>
            <div class="metric-value" style="color: #46D369;">${monthly_revenue:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Annual Revenue Recovered</div>
            <div class="metric-value" style="color: #46D369;">${annual_revenue:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Retention campaign ROI
    st.markdown("---")
    st.subheader("Retention Campaign ROI Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        campaign_cost = st.number_input("Campaign Cost ($)", value=5000)
        discount_value = st.number_input("Discount per Customer ($)", value=10)
        response_rate = st.slider("Expected Response Rate (%)", 0, 50, 15)
        conversion_rate = st.slider("Conversion Rate of Responders (%)", 0, 50, 30)
    
    with col2:
        # Calculate ROI
        target_customers = len(df[(df['risk_category'].isin(['High', 'Critical'])) & (df['churned'] == 0)])
        responders = int(target_customers * response_rate / 100)
        conversions = int(responders * conversion_rate / 100)
        
        retention_revenue = conversions * df['monthly_fee'].mean() * 12  # Annual value
        discount_cost = conversions * discount_value
        total_cost = campaign_cost + discount_cost
        net_benefit = retention_revenue - total_cost
        roi = (net_benefit / total_cost) * 100 if total_cost > 0 else 0
        
        st.markdown(f"""
        **Campaign Target:** {target_customers:,} high-risk customers
        
        **Expected Responders:** {responders:,}
        
        **Expected Conversions:** {conversions:,}
        
        **Retention Value:** ${retention_revenue:,.0f} (annual)
        
        **Total Cost:** ${total_cost:,.0f}
        
        **Net Benefit:** <span style="color: {'#46D369' if net_benefit > 0 else '#E50914'}">${net_benefit:,.0f}</span>
        
        **ROI:** <span style="color: {'#46D369' if roi > 0 else '#E50914'}">{roi:.1f}%</span>
        """, unsafe_allow_html=True)

# ==================== PAGE 10: RECOMMENDATIONS ====================
elif page == "📋 Recommendations":
    st.markdown('<div class="main-header">Business Recommendation Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Data-driven retention strategies</div>', unsafe_allow_html=True)
    
    # Priority actions
    st.subheader("🎯 Priority Actions")
    
    actions = [
        {
            "Priority": 1,
            "Action": "Automated Re-engagement Campaign",
            "Trigger": "Customer inactive > 14 days",
            "Expected Impact": "High",
            "Effort": "Low",
            "Details": "Send personalized email with content recommendations and limited-time offer"
        },
        {
            "Priority": 2,
            "Action": "Win-Back Campaign for At-Risk",
            "Trigger": "Health score < 50, not churned",
            "Expected Impact": "High",
            "Effort": "Low",
            "Details": "20% discount for 3 months + personal outreach for high-value customers"
        },
        {
            "Priority": 3,
            "Action": "Upsell Engaged Basic Users",
            "Trigger": "Basic tier, watch hours > 15",
            "Expected Impact": "Medium-High",
            "Effort": "Medium",
            "Details": "Targeted upgrade offer highlighting HD and additional profiles"
        },
        {
            "Priority": 4,
            "Action": "Loyalty Program for Power Users",
            "Trigger": "Watch hours > 30, health > 80",
            "Expected Impact": "Medium",
            "Effort": "Medium",
            "Details": "Exclusive content access, referral bonuses, VIP support"
        },
        {
            "Priority": 5,
            "Action": "Mobile Experience Improvements",
            "Trigger": "Mobile users have higher churn",
            "Expected Impact": "Medium",
            "Effort": "High",
            "Details": "UX audit, performance optimization, offline viewing improvements"
        }
    ]
    
    for action in actions:
        with st.expander(f"**Priority {action['Priority']}:** {action['Action']}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**Trigger:** {action['Trigger']}")
                st.markdown(f"**Impact:** {action['Expected Impact']}")
            
            with col2:
                st.markdown(f"**Effort:** {action['Effort']}")
            
            with col3:
                st.markdown(f"**Details:** {action['Details']}")
    
    st.markdown("---")
    
    # Key insights
    st.subheader("📊 Key Insights from Analysis")
    
    insights = [
        "**Login recency is the #1 churn predictor** - Customers inactive for 30+ days have dramatically higher churn rates",
        "**Basic tier churns more** - Price-sensitive customers need more value demonstration",
        "**High engagement ≠ retention** - Some power users still churn; value perception matters",
        "**Mobile users are at slightly higher risk** - Device experience may need attention",
        "**The 14-30 day window is critical** - Intervention before 30 days of inactivity is key"
    ]
    
    for insight in insights:
        st.markdown(f"- {insight}")
    
    st.markdown("---")
    
    # Implementation timeline
    st.subheader("📅 Implementation Roadmap")
    
    timeline = """
    | Week | Action | Owner |
    |------|--------|-------|
    | 1-2 | Deploy automated re-engagement triggers | Marketing Ops |
    | 1-2 | Set up health score dashboards for CS team | Data Team |
    | 3-4 | Launch win-back email campaign | Marketing |
    | 3-4 | Begin upsell campaign for Basic users | Sales/Marketing |
    | 5-8 | Design loyalty program | Product |
    | 5-8 | A/B test retention offers | Marketing Ops |
    | 9+ | Mobile app improvements | Product/Engineering |
    """
    
    st.markdown(timeline)
    
    st.markdown("---")
    
    # Success metrics
    st.subheader("📈 Success Metrics to Track")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Primary Metrics:**
        - Monthly churn rate (current: {:.1f}%, target: {:.1f}%)
        - Revenue at risk (target: 20% reduction)
        - Average customer health score (target: +5 points)
        """.format(churn_rate, churn_rate - 5))
    
    with col2:
        st.markdown("""
        **Secondary Metrics:**
        - Win-back campaign conversion rate
        - Re-engagement email open rate
        - Upsell conversion rate
        - Customer satisfaction (NPS) by segment
        """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<small>
Netflix Retention Command Center v1.0<br>
Built for analytics portfolio demonstration
</small>
""", unsafe_allow_html=True)
