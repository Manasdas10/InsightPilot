import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_mock_datasets(output_dir="data"):
    """
    Generates realistic, interconnected business datasets to serve as the default
    data sources for InsightPilot, reflecting structured trends and anomalies.
    """
    os.makedirs(output_dir, exist_ok=True)
    np.random.seed(42)  # For reproducible realistic data
    
    # -------------------------------------------------------------
    # 1. REVENUE TRENDS (Historical Monthly Data over 24 Months)
    # -------------------------------------------------------------
    start_date = datetime(2024, 6, 1)
    months = 24
    dates = [start_date + timedelta(days=30 * i) for i in range(months)]
    
    mrr = []
    new_mrr = []
    churned_mrr = []
    expansion_mrr = []
    active_customers = []
    
    current_mrr = 50000.0
    current_customers = 200
    
    for idx, date in enumerate(dates):
        # Normal growth: 5% new MRR, 1.5% expansion MRR
        growth_rate = 0.05
        expansion_rate = 0.015
        
        # Add realistic seasonal dip (e.g. July/August slowdown or specific crisis)
        # Let's create an anomaly in Month 18 (November 2025): Churn spikes, MRR drops
        is_anomaly_month = (idx == 17) # 18th month
        
        if is_anomaly_month:
            churn_rate = 0.14  # Unusually high churn (normal is 2-3%)
            growth_rate = 0.01
        else:
            # Random slight fluctuation in churn rate (1.8% to 3.2%)
            churn_rate = np.random.uniform(0.018, 0.032)
            
        n_mrr = current_mrr * growth_rate
        e_mrr = current_mrr * expansion_rate
        c_mrr = current_mrr * churn_rate
        
        current_mrr = current_mrr + n_mrr + e_mrr - c_mrr
        
        # Customer counts
        new_custs = int(n_mrr / 250)  # Assume $250 ARPU
        churn_custs = int(c_mrr / 250)
        current_customers = current_customers + new_custs - churn_custs
        
        mrr.append(round(current_mrr, 2))
        new_mrr.append(round(n_mrr, 2))
        churned_mrr.append(round(c_mrr, 2))
        expansion_mrr.append(round(e_mrr, 2))
        active_customers.append(current_customers)
        
    df_revenue = pd.DataFrame({
        "Date": [d.strftime("%Y-%m-%d") for d in dates],
        "MRR": mrr,
        "New_MRR": new_mrr,
        "Expansion_MRR": expansion_mrr,
        "Churned_MRR": churned_mrr,
        "Active_Customers": active_customers,
        "ARPU": [round(mrr[i] / active_customers[i], 2) for i in range(len(dates))]
    })
    df_revenue.to_csv(os.path.join(output_dir, "revenue_trends.csv"), index=False)
    
    # -------------------------------------------------------------
    # 2. CUSTOMER METRICS (Individual customer records)
    # -------------------------------------------------------------
    num_customers = 500
    customer_ids = [f"CUST-{1000 + i}" for i in range(num_customers)]
    plans = np.random.choice(["Starter", "Professional", "Enterprise"], size=num_customers, p=[0.5, 0.35, 0.15])
    
    # Associate properties with plans
    arpu_map = {"Starter": 100, "Professional": 300, "Enterprise": 1000}
    monthly_spends = [arpu_map[p] for p in plans]
    
    status_list = []
    tenure_list = []
    total_spend_list = []
    engagement_list = []
    support_tickets_list = []
    last_login_list = []
    
    for i in range(num_customers):
        # Enterprise users have lower churn, Professional is mid, Starter is higher
        plan = plans[i]
        churn_prob = 0.08 if plan == "Enterprise" else (0.15 if plan == "Professional" else 0.25)
        
        # Make some users churned
        status = "Churned" if np.random.random() < churn_prob else "Active"
        status_list.append(status)
        
        # Tenure
        if status == "Churned":
            # Churned customers tend to leave early
            tenure = np.random.randint(1, 12)
            # Low engagement
            engagement = np.random.randint(10, 50)
            # High support tickets or long inactivity
            support_tickets = np.random.randint(2, 9)
            last_login = np.random.randint(10, 90)
        else:
            tenure = np.random.randint(6, 36)
            engagement = np.random.randint(55, 100)
            support_tickets = np.random.randint(0, 3)
            last_login = np.random.randint(0, 7)
            
        tenure_list.append(tenure)
        total_spend_list.append(tenure * monthly_spends[i])
        engagement_list.append(engagement)
        support_tickets_list.append(support_tickets)
        last_login_list.append(last_login)
        
    df_customers = pd.DataFrame({
        "CustomerID": customer_ids,
        "Plan": plans,
        "Status": status_list,
        "TenureMonths": tenure_list,
        "MonthlySpend": monthly_spends,
        "TotalSpend": total_spend_list,
        "EngagementScore": engagement_list,
        "LastLoginDaysAgo": last_login_list,
        "SupportTickets": support_tickets_list
    })
    df_customers.to_csv(os.path.join(output_dir, "customer_metrics.csv"), index=False)
    
    # -------------------------------------------------------------
    # 3. PRODUCT USAGE (Engagement metrics for features)
    # -------------------------------------------------------------
    features = ["Dashboard", "Report_Builder", "Data_Export", "AI_Ask_Analyst", "Integrations_Settings"]
    usage_records = []
    
    for cust_id in customer_ids:
        # Determine engagement level based on customer metrics
        cust_row = df_customers[df_customers["CustomerID"] == cust_id].iloc[0]
        base_clicks = int(cust_row["EngagementScore"] * 1.5)
        
        for feat in features:
            # Preferences per feature
            if feat == "Dashboard":
                click_weight = 0.4
            elif feat == "AI_Ask_Analyst":
                click_weight = 0.25
            elif feat == "Report_Builder":
                click_weight = 0.2
            else:
                click_weight = 0.075
                
            clicks = int(np.random.poisson(base_clicks * click_weight))
            duration = round(clicks * np.random.uniform(0.8, 1.5), 1)
            active_days = min(30, max(1, int(cust_row["EngagementScore"] / 3.3) + np.random.randint(-2, 2)))
            
            usage_records.append({
                "CustomerID": cust_id,
                "FeatureName": feat,
                "Clicks_30D": clicks,
                "DurationMinutes_30D": duration,
                "ActiveDays_30D": active_days
            })
            
    df_usage = pd.DataFrame(usage_records)
    df_usage.to_csv(os.path.join(output_dir, "product_usage.csv"), index=False)
    
    # -------------------------------------------------------------
    # 4. CUSTOMER FEEDBACK
    # -------------------------------------------------------------
    categories = ["Pricing", "UX/UI Design", "Customer Support", "Product Features", "Reliability/Bugs"]
    
    feedback_pool = {
        "Pricing": [
            ("Great platform but a bit expensive for small startups.", 3, "Neutral"),
            ("Enterprise plan offers good value for large teams.", 5, "Positive"),
            ("Pricing structure is confusing and tiers scale too fast.", 2, "Negative"),
            ("Pricing is perfectly aligned with the value we get.", 5, "Positive"),
            ("A bit steep, but standard for the industry.", 4, "Positive")
        ],
        "UX/UI Design": [
            ("Extremely polished user interface, feels state-of-the-art.", 5, "Positive"),
            ("The dashboard layout is confusing and navigation is slow.", 2, "Negative"),
            ("Clean and interactive charts! Highly intuitive.", 5, "Positive"),
            ("Looks modern but mobile responsiveness could be improved.", 3, "Neutral"),
            ("Beautiful UI, but dark mode should be more customizable.", 4, "Positive")
        ],
        "Customer Support": [
            ("Support team resolved our configuration issue in 10 minutes.", 5, "Positive"),
            ("Hard to reach support, took 2 days for a reply.", 2, "Negative"),
            ("Support staff is helpful but lacks technical depth.", 3, "Neutral"),
            ("Amazing onboarding assistance. 10/10.", 5, "Positive")
        ],
        "Product Features": [
            ("The AI reporting feature saves us at least 5 hours a week.", 5, "Positive"),
            ("Needs more direct integrations with Salesforce and HubSpot.", 3, "Neutral"),
            ("AI recommendation engine is decent but needs custom prompts.", 4, "Positive"),
            ("Data export options are too limited, only raw CSV is supported.", 2, "Negative"),
            ("Love the cohort retention heatmaps! Very insightful.", 5, "Positive")
        ],
        "Reliability/Bugs": [
            ("Solid performance, never experienced downtime.", 5, "Positive"),
            ("Frequent timeouts when running heavy data analysis.", 2, "Negative"),
            ("Occasional bugs in file upload, but refreshing fixes it.", 3, "Neutral"),
            ("API connection drops occasionally during database sync.", 2, "Negative")
        ]
    }
    
    feedback_records = []
    # Sample about 120 feedbacks
    sampled_customers = np.random.choice(customer_ids, size=120, replace=False)
    
    for cust_id in sampled_customers:
        # Determine sentiment skew from customer metrics
        cust_row = df_customers[df_customers["CustomerID"] == cust_id].iloc[0]
        
        # If churned or low engagement, pick more negative/neutral responses
        if cust_row["Status"] == "Churned" or cust_row["EngagementScore"] < 50:
            category = np.random.choice(["Pricing", "Reliability/Bugs", "Customer Support"])
            # Filter pool options that are negative or neutral
            opts = [o for o in feedback_pool[category] if o[2] in ["Negative", "Neutral"]]
            if not opts:
                opts = feedback_pool[category]
        else:
            category = np.random.choice(categories)
            opts = [o for o in feedback_pool[category] if o[2] in ["Positive", "Neutral"]]
            if not opts:
                opts = feedback_pool[category]
                
        text, score, sentiment = opts[np.random.randint(len(opts))]
        
        feedback_records.append({
            "CustomerID": cust_id,
            "Timestamp": (datetime.now() - timedelta(days=np.random.randint(1, 90))).strftime("%Y-%m-%d %H:%M:%S"),
            "Category": category,
            "FeedbackText": text,
            "Score": score,
            "Sentiment": sentiment
        })
        
    df_feedback = pd.DataFrame(feedback_records)
    df_feedback.to_csv(os.path.join(output_dir, "customer_feedback.csv"), index=False)
    
    print(f"Realistic mock datasets successfully generated and stored in './{output_dir}'.")

if __name__ == "__main__":
    generate_mock_datasets()
