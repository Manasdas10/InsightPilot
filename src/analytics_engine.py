import pandas as pd
import numpy as np
import os

class AnalyticsEngine:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.load_data()
        
    def load_data(self):
        """Loads default files or empty structures if not found."""
        try:
            self.df_revenue = pd.read_csv(os.path.join(self.data_dir, "revenue_trends.csv"))
        except Exception:
            self.df_revenue = pd.DataFrame()
            
        try:
            self.df_customers = pd.read_csv(os.path.join(self.data_dir, "customer_metrics.csv"))
        except Exception:
            self.df_customers = pd.DataFrame()
            
        try:
            self.df_feedback = pd.read_csv(os.path.join(self.data_dir, "customer_feedback.csv"))
        except Exception:
            self.df_feedback = pd.DataFrame()
            
        try:
            self.df_usage = pd.read_csv(os.path.join(self.data_dir, "product_usage.csv"))
        except Exception:
            self.df_usage = pd.DataFrame()

    def get_summary_kpis(self):
        """Computes executive-level KPIs and returns them as a dict."""
        kpis = {}
        if self.df_revenue.empty or self.df_customers.empty:
            return {
                "health_score": 0, "mrr": 0, "mrr_growth_pct": 0,
                "churn_rate_pct": 0, "ltv": 0, "arpu": 0, "active_customers": 0
            }
            
        # Get latest month metrics
        latest_rev_row = self.df_revenue.iloc[-1]
        prev_rev_row = self.df_revenue.iloc[-2] if len(self.df_revenue) > 1 else latest_rev_row
        
        mrr = float(latest_rev_row["MRR"])
        prev_mrr = float(prev_rev_row["MRR"])
        mrr_growth = ((mrr - prev_mrr) / prev_mrr * 100) if prev_mrr > 0 else 0
        
        active_customers = int(self.df_customers[self.df_customers["Status"] == "Active"].shape[0])
        total_customers = int(self.df_customers.shape[0])
        
        # Calculate active churn rate from customer database
        churned_customers = int(self.df_customers[self.df_customers["Status"] == "Churned"].shape[0])
        churn_rate = (churned_customers / total_customers * 100) if total_customers > 0 else 0
        
        # Average revenue per user (monthly spend for active ones)
        active_spends = self.df_customers[self.df_customers["Status"] == "Active"]["MonthlySpend"]
        arpu = float(active_spends.mean()) if not active_spends.empty else 0.0
        
        # Lifetime Value (LTV) = ARPU / Monthly Churn Rate
        # Standard SaaS calculation (let's assume monthly churn is approx churn_rate divided by average tenure)
        monthly_churn_est = (1 / self.df_customers["TenureMonths"].mean()) if not self.df_customers.empty else 0.05
        # Bound it reasonably
        monthly_churn_est = max(0.01, min(0.2, monthly_churn_est))
        ltv = arpu / monthly_churn_est if monthly_churn_est > 0 else 0.0
        
        # Business Health Score calculation (weighted index out of 100)
        # Factors: High engagement (+30), Low churn (+30), positive growth (+20), support ticket control (+20)
        avg_engagement = float(self.df_customers["EngagementScore"].mean()) if not self.df_customers.empty else 70
        avg_tickets = float(self.df_customers["SupportTickets"].mean()) if not self.df_customers.empty else 1.5
        
        engagement_factor = (avg_engagement / 100) * 30
        churn_factor = max(0, (30 - churn_rate))
        growth_factor = min(20, max(0, mrr_growth * 2))
        ticket_factor = max(0, 20 - (avg_tickets * 4))
        
        health_score = int(engagement_factor + churn_factor + growth_factor + ticket_factor)
        health_score = min(100, max(0, health_score))
        
        kpis = {
            "health_score": health_score,
            "mrr": round(mrr, 2),
            "mrr_growth_pct": round(mrr_growth, 2),
            "churn_rate_pct": round(churn_rate, 2),
            "ltv": round(ltv, 2),
            "arpu": round(arpu, 2),
            "active_customers": active_customers,
            "total_customers": total_customers
        }
        return kpis

    def get_revenue_trends(self):
        """Returns monthly revenue trend dataframe."""
        return self.df_revenue
        
    def get_cohort_retention(self):
        """Computes cohort-style retention based on tenure."""
        if self.df_customers.empty:
            return pd.DataFrame()
            
        # Group users by plan and status, calculating average metrics
        cohort_summary = self.df_customers.groupby(["Plan", "Status"]).agg(
            Count=("CustomerID", "count"),
            AvgTenure=("TenureMonths", "mean"),
            AvgEngagement=("EngagementScore", "mean")
        ).reset_index()
        return cohort_summary

    def get_churn_drivers(self):
        """Analyzes correlation and indicators of customer churn."""
        if self.df_customers.empty:
            return {}
            
        df = self.df_customers.copy()
        # Convert status to binary: 1 if Churned, 0 if Active
        df["IsChurned"] = (df["Status"] == "Churned").astype(int)
        
        # Calculate correlation of IsChurned with numerical metrics
        correlations = {}
        for col in ["TenureMonths", "EngagementScore", "LastLoginDaysAgo", "SupportTickets", "MonthlySpend"]:
            if col in df.columns:
                corr = df["IsChurned"].corr(df[col])
                correlations[col] = round(corr, 3) if not pd.isna(corr) else 0.0
                
        # Group metrics for visual contrast
        grouped = df.groupby("Status").agg(
            AvgEngagement=("EngagementScore", "mean"),
            AvgSupportTickets=("SupportTickets", "mean"),
            AvgLastLogin=("LastLoginDaysAgo", "mean"),
            AvgTenure=("TenureMonths", "mean")
        ).to_dict(orient="index")
        
        return {
            "correlations": correlations,
            "grouped_metrics": grouped
        }

    def get_customer_segments(self):
        """Segments customers into key strategic quadrants."""
        if self.df_customers.empty:
            return pd.DataFrame()
            
        # Simple segmentation rules:
        # - Champions: Active, high engagement (>= 80), tenure >= 12
        # - At-Risk: Active, low engagement (< 60), last login > 7 days ago
        # - Onboarding: Active, tenure < 3
        # - Steady: Active, not meeting other rules
        # - Churned: Churned status
        
        df = self.df_customers.copy()
        segments = []
        for idx, row in df.iterrows():
            if row["Status"] == "Churned":
                segments.append("Churned")
            elif row["EngagementScore"] >= 80 and row["TenureMonths"] >= 12:
                segments.append("Champions")
            elif row["EngagementScore"] < 60 and row["LastLoginDaysAgo"] > 7:
                segments.append("At-Risk")
            elif row["TenureMonths"] < 4:
                segments.append("Onboarding")
            else:
                segments.append("Stable Core")
                
        df["Segment"] = segments
        return df

    def get_product_metrics(self):
        """Aggregates engagement per feature."""
        if self.df_usage.empty:
            return pd.DataFrame()
            
        feat_stats = self.df_usage.groupby("FeatureName").agg(
            TotalClicks=("Clicks_30D", "sum"),
            AvgClicks=("Clicks_30D", "mean"),
            AvgDuration=("DurationMinutes_30D", "mean"),
            AvgActiveDays=("ActiveDays_30D", "mean")
        ).reset_index()
        
        return feat_stats

    def get_growth_opportunities(self):
        """Rule-based engine to discover specific business opportunities or leakage."""
        opportunities = []
        
        if self.df_customers.empty:
            return opportunities
            
        # 1. Check for Churn Leakage
        at_risk_count = self.df_customers[
            (self.df_customers["Status"] == "Active") & 
            (self.df_customers["EngagementScore"] < 60) & 
            (self.df_customers["SupportTickets"] > 2)
        ].shape[0]
        
        if at_risk_count > 0:
            potential_loss = at_risk_count * float(self.df_customers["MonthlySpend"].mean())
            opportunities.append({
                "title": f"At-Risk Retention Campaign",
                "impact": f"Save up to ${round(potential_loss * 12, 2):,} in annual recurring revenue (ARR)",
                "confidence": "High",
                "description": f"Identified {at_risk_count} active customers exhibiting low engagement scores (<60) and high support tickets. Targeted outreach can reduce churn probability by 25-30%."
            })
            
        # 2. Check for Account Expansion (Starter to Professional/Enterprise)
        expansion_candidates = self.df_customers[
            (self.df_customers["Status"] == "Active") & 
            (self.df_customers["Plan"] == "Starter") & 
            (self.df_customers["EngagementScore"] >= 85) &
            (self.df_customers["TenureMonths"] >= 6)
        ].shape[0]
        
        if expansion_candidates > 0:
            upsell_delta = (300 - 100) * expansion_candidates  # Starter to Professional delta
            opportunities.append({
                "title": f"Highly-Engaged Starter Upsell",
                "impact": f"Unlock up to ${round(upsell_delta * 12, 2):,} in incremental annual MRR",
                "confidence": "Medium",
                "description": f"Found {expansion_candidates} 'Starter' plan users with high engagement (>=85) and tenure >= 6 months. Offering a 14-day trial of 'Professional' features is highly likely to convert."
            })
            
        # 3. Product-led growth (AI feature adoption)
        if not self.df_usage.empty:
            ai_usage = self.df_usage[self.df_usage["FeatureName"] == "AI_Ask_Analyst"]
            unengaged_ai = ai_usage[ai_usage["Clicks_30D"] < 5].shape[0]
            if unengaged_ai > 0:
                opportunities.append({
                    "title": f"AI Strategy Feature Adoption Campaign",
                    "impact": f"Boost core customer retention by up to 8-10%",
                    "confidence": "High",
                    "description": f"Over {unengaged_ai} active customers make little to no use of the 'AI Ask Analyst' tool. Directing them via contextual tooltips or email guides increases engagement and retention."
                })
                
        # 4. Sentiment opportunities
        if not self.df_feedback.empty:
            bug_feedbacks = self.df_feedback[
                (self.df_feedback["Category"] == "Reliability/Bugs") & 
                (self.df_feedback["Sentiment"] == "Negative")
            ]
            if len(bug_feedbacks) > 15:
                opportunities.append({
                    "title": f"Critical Bug Resolution & Stability Sprint",
                    "impact": f"Reduce negative sentiment by 40% in Reliability metrics",
                    "confidence": "High",
                    "description": "Negative sentiment regarding reliability/bugs is trending up. Dedicating the next cycle to fixing core system performance drops can yield significant LTV gains."
                })
                
        return opportunities
