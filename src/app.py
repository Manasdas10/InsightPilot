import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from datetime import datetime

# Import backend modules
from data_generator import generate_mock_datasets
from analytics_engine import AnalyticsEngine
from ai_engine import AIEngine
import database

# -------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# -------------------------------------------------------------
st.set_page_config(
    page_title="InsightPilot – Executive Decision Intelligence Platform",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Premium Custom CSS Styles
st.markdown("""
<style>
    /* Main Layout */
    .reportview-container {
        background: #0F172A;
    }
    
    /* Premium Cards */
    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #3B82F6;
    }
    .metric-title {
        font-size: 0.875rem;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 0.25rem;
    }
    .metric-delta {
        font-size: 0.875rem;
        font-weight: 600;
    }
    .delta-positive { color: #10B981; }
    .delta-negative { color: #EF4444; }
    
    /* Health Gauge Container */
    .health-container {
        background: radial-gradient(circle at top left, #1E3A8A, #0F172A);
        border: 1px solid #2563EB;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Ensure data folder and mock data are created
if not os.path.exists("data/revenue_trends.csv"):
    with st.spinner("Initializing system datasets..."):
        generate_mock_datasets()

# Initialize Engine
engine = AnalyticsEngine()

# -------------------------------------------------------------
# SIDEBAR CONTROL PANEL
# -------------------------------------------------------------
st.sidebar.title("✈️ InsightPilot")
st.sidebar.markdown("*Executive Decision Intelligence*")
st.sidebar.divider()

# API Key Config
st.sidebar.subheader("🔑 AI Configuration")
api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Enter your Gemini API key to enable dynamic AI analytics.")
ai = AIEngine(key=api_key)

if ai.active:
    st.sidebar.success("Gemini API Integrated")
else:
    st.sidebar.warning("Offline / Fallback Mode (No API Key)")

# File Ingestion
st.sidebar.subheader("📥 Data Ingestion")
uploaded_file = st.sidebar.file_uploader(
    "Upload custom CSV reports (Revenue, Customers, Feedback or Product)", 
    type=["csv"]
)

if uploaded_file is not None:
    # Save the file to data/ directory temporarily or overwrite default
    filename = uploaded_file.name
    data_type = "revenue"
    if "customer" in filename.lower():
        data_type = "customer"
    elif "feedback" in filename.lower():
        data_type = "feedback"
    elif "product" in filename.lower() or "usage" in filename.lower():
        data_type = "product"
        
    # Write file
    target_path = os.path.join("data", f"{data_type}_trends.csv" if data_type == "revenue" else f"{data_type}_metrics.csv" if data_type == "customer" else f"customer_feedback.csv" if data_type == "feedback" else f"product_usage.csv")
    
    # Read upload to count lines
    df_temp = pd.read_csv(uploaded_file)
    df_temp.to_csv(target_path, index=False)
    
    # Log upload in DB
    database.log_data_upload(filename, len(df_temp), data_type)
    
    st.sidebar.success(f"Successfully loaded {filename}!")
    # Reload engine data
    engine.load_data()

st.sidebar.divider()
st.sidebar.caption("InsightPilot Platform v1.0.0")

# -------------------------------------------------------------
# CORE ANALYTICS DATA RETRIEVAL
# -------------------------------------------------------------
kpis = engine.get_summary_kpis()

# -------------------------------------------------------------
# HEADER & SUMMARY KPI STRIPS
# -------------------------------------------------------------
st.title("Executive Decision Intelligence Platform")
st.caption(f"Platform Status: Operational | Data Sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Top Row KPI Summary
col_health, col_mrr, col_growth, col_churn, col_ltv = st.columns(5)

with col_health:
    health_color = "#10B981" if kpis["health_score"] >= 80 else ("#F59E0B" if kpis["health_score"] >= 60 else "#EF4444")
    st.markdown(f"""
    <div class="health-container">
        <div class="metric-title" style="color: #94A3B8;">Business Health Score</div>
        <div class="metric-value" style="color: {health_color}; font-size: 2.5rem;">{kpis['health_score']} <span style="font-size: 1.2rem; color: #94A3B8;">/100</span></div>
    </div>
    """, unsafe_allow_html=True)

with col_mrr:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Monthly Recurring Revenue</div>
        <div class="metric-value">${kpis['mrr']:,.0f}</div>
        <div class="metric-delta delta-positive">ARPU: ${kpis['arpu']:.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col_growth:
    delta_class = "delta-positive" if kpis["mrr_growth_pct"] >= 0 else "delta-negative"
    sign = "+" if kpis["mrr_growth_pct"] >= 0 else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">MoM Revenue Growth</div>
        <div class="metric-value {delta_class}">{sign}{kpis['mrr_growth_pct']}%</div>
        <div class="metric-delta">Target: +5.0%</div>
    </div>
    """, unsafe_allow_html=True)

with col_churn:
    churn_class = "delta-negative" if kpis["churn_rate_pct"] >= 5 else "delta-positive"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Customer Churn Rate</div>
        <div class="metric-value {churn_class}">{kpis['churn_rate_pct']:.1f}%</div>
        <div class="metric-delta">SaaS Benchmark: < 3%</div>
    </div>
    """, unsafe_allow_html=True)

with col_ltv:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Customer LTV (Est.)</div>
        <div class="metric-value">${kpis['ltv']:,.0f}</div>
        <div class="metric-delta">Active Accounts: {kpis['active_customers']}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# -------------------------------------------------------------
# MAIN NAVIGATION TABS
# -------------------------------------------------------------
tab_overview, tab_revenue, tab_customers, tab_product, tab_opportunities, tab_strategy = st.tabs([
    "📈 Executive Overview",
    "💰 Revenue Analytics",
    "👥 Customer Analytics",
    "📦 Product Analytics",
    "⚡ Growth Opportunities",
    "🤖 AI Strategy Engine"
])

# =============================================================
# TAB 1: EXECUTIVE OVERVIEW
# =============================================================
with tab_overview:
    st.subheader("Executive Analyst Briefing")
    
    # Generate/Retrieve Summary Report
    col_brief, col_actions = st.columns([2, 1])
    
    with col_brief:
        st.markdown("### AI Summary Dashboard")
        
        # Load AI Summary
        with st.spinner("Synthesizing metrics data..."):
            summary_content = ai.generate_executive_summary(kpis)
            st.markdown(summary_content)
            
    with col_actions:
        st.markdown("### Executive Actions Panel")
        
        st.markdown("Generate and archive strategic reports directly to the database:")
        report_type_select = st.selectbox("Report Type", ["weekly", "monthly", "board"])
        
        if st.button("Generate & Save Report", use_container_width=True):
            with st.spinner("Drafting full business report..."):
                report_title = f"{report_type_select.capitalize()} Business Review - {datetime.now().strftime('%B %Y')}"
                full_report = ai.generate_report(kpis, report_type=report_type_select)
                
                database.save_executive_report(
                    title=report_title,
                    report_type=report_type_select,
                    content=full_report,
                    metrics_summary=kpis
                )
                st.success(f"Saved report '{report_title}' successfully!")
                
        st.divider()
        st.markdown("### Saved Historical Reports")
        saved_reports = database.get_all_reports()
        if saved_reports:
            for rep in saved_reports[:5]:  # Display last 5 reports
                with st.expander(f"📄 {rep['title']} ({rep['created_at'][:10]})"):
                    st.markdown(rep["content"])
        else:
            st.info("No saved reports found. Click 'Generate & Save Report' to save your first review.")

# =============================================================
# TAB 2: REVENUE ANALYTICS
# =============================================================
with tab_revenue:
    st.subheader("Financial Performance & MRR Growth Trends")
    
    df_rev = engine.get_revenue_trends()
    if not df_rev.empty:
        # Chart 1: MRR Over Time
        fig_mrr = px.line(
            df_rev, x="Date", y="MRR",
            title="Monthly Recurring Revenue (MRR) Growth Trajectory",
            labels={"MRR": "Monthly Revenue ($)", "Date": "Month"},
            markers=True,
            color_discrete_sequence=["#3B82F6"]
        )
        fig_mrr.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#F8FAFC",
            grid={"rows": 1, "columns": 1}
        )
        fig_mrr.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#334155")
        fig_mrr.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#334155")
        
        st.plotly_chart(fig_mrr, use_container_width=True)
        
        # Chart 2: Revenue Decomposition (New, Expansion, Churn)
        st.markdown("### MRR Growth Decomposition")
        col_comp_1, col_comp_2 = st.columns([2, 1])
        
        with col_comp_1:
            fig_decomp = go.Figure()
            fig_decomp.add_trace(go.Bar(
                x=df_rev["Date"], y=df_rev["New_MRR"],
                name="New Customer MRR", marker_color="#10B981"
            ))
            fig_decomp.add_trace(go.Bar(
                x=df_rev["Date"], y=df_rev["Expansion_MRR"],
                name="Expansion MRR", marker_color="#3B82F6"
            ))
            fig_decomp.add_trace(go.Bar(
                x=df_rev["Date"], y=-df_rev["Churned_MRR"],
                name="Churned MRR", marker_color="#EF4444"
            ))
            
            fig_decomp.update_layout(
                barmode="relative",
                title="Net MRR Monthly Movements",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#F8FAFC"
            )
            st.plotly_chart(fig_decomp, use_container_width=True)
            
        with col_comp_2:
            st.markdown("#### Revenue Health Insights")
            # Calculate metrics
            total_new = df_rev["New_MRR"].sum()
            total_expansion = df_rev["Expansion_MRR"].sum()
            total_churn = df_rev["Churned_MRR"].sum()
            
            st.metric("Total New Revenue Added", f"${total_new:,.2f}")
            st.metric("Expansion Revenue Added", f"${total_expansion:,.2f}")
            st.metric("Total Churn Revenue Lost", f"${total_churn:,.2f}", delta="-MoM Churn", delta_color="inverse")
            
            st.markdown("""
            > [!TIP]
            > A healthy SaaS model targets expansion MRR to offset churn MRR, leading to a Net Revenue Retention (NRR) > 100%.
            """)
    else:
        st.info("No revenue trend data available. Please upload a revenue file or generate mock data.")

# =============================================================
# TAB 3: CUSTOMER ANALYTICS
# =============================================================
with tab_customers:
    st.subheader("Customer Segmentations & Retention Risk Diagnostics")
    
    col_cohort, col_churn_analysis = st.columns([1, 1])
    
    with col_cohort:
        st.markdown("### Plan-wise Status & Engagement Cohorts")
        df_cohort = engine.get_cohort_retention()
        if not df_cohort.empty:
            fig_cohort = px.bar(
                df_cohort, x="Plan", y="Count", color="Status",
                title="Customer Status Distribution by Subscription Tier",
                color_discrete_map={"Active": "#10B981", "Churned": "#EF4444"},
                barmode="group"
            )
            fig_cohort.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC")
            st.plotly_chart(fig_cohort, use_container_width=True)
            
            # Display detailed tabular view
            st.dataframe(df_cohort, use_container_width=True)
        else:
            st.info("No customer metrics found.")
            
    with col_churn_analysis:
        st.markdown("### Primary Drivers of Churn")
        churn_data = engine.get_churn_drivers()
        
        if churn_data:
            correlations = churn_data["correlations"]
            
            # Bar chart for correlations
            corr_df = pd.DataFrame({
                "Metric": list(correlations.keys()),
                "Correlation to Churn": list(correlations.values())
            }).sort_values("Correlation to Churn", ascending=True)
            
            fig_corr = px.bar(
                corr_df, x="Correlation to Churn", y="Metric",
                orientation='h',
                title="Metric Correlation to Churn Event",
                color="Correlation to Churn",
                color_continuous_scale="RdBu"
            )
            fig_corr.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC")
            st.plotly_chart(fig_corr, use_container_width=True)
            
            # Table comparison
            st.markdown("#### Active vs Churned Profile Breakdown")
            st.json(churn_data["grouped_metrics"])
        else:
            st.info("No customer records found to analyze churn drivers.")

# =============================================================
# TAB 4: PRODUCT ANALYTICS
# =============================================================
with tab_product:
    st.subheader("Feature Adoption & Core Product Engagement")
    
    df_prod = engine.get_product_metrics()
    if not df_prod.empty:
        col_prod_left, col_prod_right = st.columns([1, 1])
        
        with col_prod_left:
            st.markdown("### Monthly Feature Clicks")
            fig_clicks = px.pie(
                df_prod, values="TotalClicks", names="FeatureName",
                title="Share of Interaction Clicks by Feature",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_clicks.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC")
            st.plotly_chart(fig_clicks, use_container_width=True)
            
        with col_prod_right:
            st.markdown("### Average Daily Usage Duration")
            fig_duration = px.bar(
                df_prod, x="FeatureName", y="AvgDuration",
                title="Average Daily Duration spent per User Session (Minutes)",
                color="AvgActiveDays",
                color_continuous_scale="Viridis"
            )
            fig_duration.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC")
            st.plotly_chart(fig_duration, use_container_width=True)
            
        # Engagement Matrix DataFrame
        st.markdown("### Feature Engagement Details")
        st.dataframe(df_prod, use_container_width=True)
    else:
        st.info("Product usage metrics not uploaded.")

# =============================================================
# TAB 5: GROWTH OPPORTUNITIES
# =============================================================
with tab_opportunities:
    st.subheader("Opportunity Discovery Engine")
    st.markdown("The strategy engine automatically monitors indicators to isolate revenue leakage and growth opportunities:")
    
    opportunities = engine.get_growth_opportunities()
    
    if opportunities:
        for idx, opt in enumerate(opportunities):
            with st.container():
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom: 1rem; border-left: 4px solid #F59E0B;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #F8FAFC;">{opt['title']}</h4>
                        <span style="background-color: #3E2723; color: #FFB300; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 700;">
                            Impact: {opt['impact']}
                        </span>
                    </div>
                    <p style="color: #94A3B8; margin-top: 0.5rem; margin-bottom: 1rem;">{opt['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Interactive button to request AI to draft a detailed action plan
                if st.button(f"Draft Action Plan for: {opt['title']}", key=f"btn_opt_{idx}"):
                    st.write("")
                    with st.spinner("Synthesizing strategic action plan..."):
                        query_prompt = f"Develop a detailed project execution plan for this opportunity: {opt['title']}. Details: {opt['description']}. Target Impact: {opt['impact']}."
                        ai_response = ai.answer_query(query_prompt, kpis)
                        st.markdown("#### Strategy Brief Draft")
                        st.markdown(ai_response)
                        
                        # Log to DB
                        database.log_strategy_query(query_prompt, ai_response)
    else:
        st.info("No critical anomalies or opportunity items flagged with current data thresholds.")

# =============================================================
# TAB 6: AI STRATEGY ENGINE (Conversational Intelligence)
# =============================================================
with tab_strategy:
    st.subheader("AI Strategy Engine Workspace")
    st.markdown("Ask natural language business questions about your metrics, trends, or segments:")
    
    # Preset sample questions
    st.markdown("**Sample Analytical Queries:**")
    sample_queries = [
        "Why did churn spike in Month 18?",
        "What feature is under-utilized and how do we improve engagement?",
        "Which customer subscription plans yield the highest LTV and lowest churn?",
        "What are the top three business risks identified in current data?"
    ]
    
    col_sq1, col_sq2 = st.columns(2)
    with col_sq1:
        if st.button(sample_queries[0], use_container_width=True):
            st.session_state.query_input = sample_queries[0]
        if st.button(sample_queries[1], use_container_width=True):
            st.session_state.query_input = sample_queries[1]
    with col_sq2:
        if st.button(sample_queries[2], use_container_width=True):
            st.session_state.query_input = sample_queries[2]
        if st.button(sample_queries[3], use_container_width=True):
            st.session_state.query_input = sample_queries[3]
            
    # Input box
    user_query = st.text_input(
        "Ask a business question:",
        value=st.session_state.get("query_input", ""),
        key="query_textbox"
    )
    
    if st.button("Query Strategy Engine", type="primary"):
        if user_query.strip():
            with st.spinner("Analyzing parameters and drafting strategy..."):
                # Formulate a summary of raw data parameters for background context
                raw_context = f"""
                Current MRR is ${kpis['mrr']:,}. MoM growth rate is {kpis['mrr_growth_pct']}%. Churn rate is {kpis['churn_rate_pct']}%.
                Active Customer base count is {kpis['active_customers']} (total logs: {kpis['total_customers']}).
                ARPU is ${kpis['arpu']:.2f}. Est LTV is ${kpis['ltv']:.2f}.
                """
                
                # Fetch AI response
                answer = ai.answer_query(user_query, kpis, raw_context)
                
                # Log to DB
                database.log_strategy_query(user_query, answer)
                
                st.markdown("---")
                st.markdown(answer)
        else:
            st.warning("Please enter or select a query.")
