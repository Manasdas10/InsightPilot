# Portfolio & Interview Preparation Guide - InsightPilot

This guide is structured to help you market **InsightPilot** in your resume, portfolio, and during technical interviews for Product Manager, Data Analyst, AI Engineer, or Full-Stack developer positions.

---

## 1. Resume Bullet Points (ATS-Friendly & Quantified)

* **Design & Architecture:** "Engineered and deployed **InsightPilot**, a production-grade Executive Decision Intelligence Platform using Python and Streamlit, automating the conversion of multi-dimensional raw business spreadsheets into board-ready tactical summaries."
* **Data Processing & Analytics:** "Developed a modular analytics processor using **Pandas** and **NumPy** to calculate complex SaaS metrics (MRR, Churn, LTV, ARPU) and generate customer cohort retention matrices, resulting in immediate diagnostic visibility for at-risk user accounts."
* **AI Integration & Engineering:** "Integrated Google Gemini API models using advanced prompt engineering, alongside building a deterministic rule-based fallback system that ensures 100% platform availability under offline or credential-limited environments."
* **Relational Storage & Auditing:** "Implemented a local transactional storage system with SQLite to archive generated executive reports, data ingestion logs, and strategy queries, reducing strategic review turnaround time."
* **Interactive Visualization:** "Designed dynamic corporate visualizations using **Plotly** and custom CSS stylesheet injections, improving dashboard usability for executive personas (Founders, PMs, Analysts)."

---

## 2. ATS-Friendly Project Description

**Project Title:** InsightPilot – Executive Decision Intelligence Platform  
**Role:** Lead Full-Stack & AI Engineer  
**Core Technologies:** Python, Streamlit, Pandas, NumPy, Plotly, SQLite, Gemini API / LLMs, Dotenv  

**Description:**  
InsightPilot is a decision-support platform that resolves the problem of fragmented business reports. It digests raw CSV files containing revenue logs, customer metadata, feedback sentiment, and feature clicks, programmatically transforming them into interactive visual intelligence and actionable boardroom strategy recommendations. Features include automated SaaS KPI calculators, cohort retention tables, correlation charts showing drivers of churn, a threshold-based growth opportunity engine, and a conversational AI strategy chat.

---

## 3. Core Interview Questions & Answers (Q&A)

### Q1: Why did you choose SQLite instead of a full PostgreSQL setup for this project?
**A:**  
"I selected SQLite because of the platform's deployment and runtime context. InsightPilot is designed as a self-contained decision intelligence tool that founders or analysts can run locally on confidential spreadsheets or deploy instantly to serverless platforms like Streamlit Community Cloud. SQLite requires zero configuration, stores data in a single file, and has no daemon overhead. It handles the relational structure (data upload logs, query histories, and report records) easily. However, because the database helper is structured behind clean abstractions in `src/database.py`, upgrading to PostgreSQL for enterprise deployments is a simple task of swapping the connection string and driver."

### Q2: How did you ensure the AI engine is resilient to network issues or missing API credentials?
**A:**  
"Production reliability is critical for executive dashboards. I built a robust offline/credential-missing fallback mode inside `src/ai_engine.py`. When the Gemini API key is missing or calls time out, the system routes queries to a rule-based heuristic engine. This engine parses the raw computed parameters (e.g., MRR, churn rate, plan details) and returns structured markdown briefs and strategy recommendations based on standard SaaS operational models (like alerting the user to high support ticket counts or drop in engagement). The user sees a fully populated, responsive interface with a warning banner, instead of a crashed application or blank screen."

### Q3: Explain how your cohort retention and churn driver calculations are implemented.
**A:**  
"For cohorts, we group active and churned customers by their subscription plan and tenure months using Pandas group aggregations (`groupby()`). For churn drivers, we first convert the categorical `Status` column to a binary integer value (`IsChurned` = 1 for Churned, 0 for Active). We then apply Pandas' `.corr()` function to calculate the Pearson correlation coefficient between the churn indicator and key numeric metrics like `EngagementScore`, `LastLoginDaysAgo`, `SupportTickets`, and `MonthlySpend`. This exposes which behaviors are most correlated with churn, which we render as an interactive Plotly horizontal bar chart to give executives clear diagnostic visibility."

### Q4: How is the 'Growth Opportunities' auto-discovery logic structured?
**A:**  
"Instead of relying on AI to crawl large raw tables (which is slow and expensive), the platform uses a hybrid heuristic approach. We use Pandas to filter the active customer base against specific business health thresholds:
1. **At-risk Accounts:** Active customers with low engagement (<60) and high support tickets (>2).
2. **Upsell Candidates:** Active 'Starter' plan users with high engagement (>=85) and tenure >= 6 months.
Once the system identifies these segments programmatically, it surfaces them on the dashboard. When an executive clicks 'Draft Action Plan', the system sends *only* the specific summary segment to the Gemini API. This reduces token usage, saves cost, and speeds up response times."

### Q5: What would you change to make this application scale to handle millions of customer records?
**A:**  
"To scale to millions of records, I would introduce three primary upgrades:
1. **Database Offloading:** Migrate the local SQLite database to an OLAP database like ClickHouse or Snowflake to execute aggregate queries (e.g., cohort retention calculations) rapidly on large datasets.
2. **Asynchronous Execution:** Shift calculations from the web server thread to a distributed task runner like Celery or Dramatiq, preventing Streamlit timeout lags.
3. **Data Chunking/Streaming:** Stream large CSV file ingestion using Pandas chunking or PyArrow rather than loading entire files into memory, keeping the server's memory footprint constant."
