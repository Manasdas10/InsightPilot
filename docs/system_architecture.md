# System Architecture - InsightPilot

InsightPilot is designed with a modular, decoupling-first architecture to separate ingestion, analytical data processing, AI synthesis, and the interactive presentation layers.

---

## 1. System Ingestion & Data Flow

```
+------------------------------------------------------------+
|                       DATA INGESTION                       |
|   (Default csv files or user uploaded customized files)    |
+-----------------------------+------------------------------+
                              |
                              v
+------------------------------------------------------------+
|                    ANALYTICS ENGINE                        |
|  - Compiles SaaS metrics (MRR, Churn, LTV, ARPU)           |
|  - Computes customer cohort distributions                   |
|  - Formulates feature usage and session timelines          |
|  - Performs statistical correlations (Drivers of Churn)    |
+-----------------------------+------------------------------+
                              |
                              v
+------------------------------------------------------------+
|                        AI ENGINE                           |
|  - Prompt compilation using current analytics metrics       |
|  - Interfacing with Gemini SDK (MoE LLM)                   |
|  - Fallback logic for offline/keyless testing              |
+-----------------------------+------------------------------+
                              |
                              v
+------------------------------------------------------------+
|                    PRESENTATION LAYER                      |
|  - Injects custom CSS styling onto dashboard layout        |
|  - Renders multi-dimensional Plotly diagrams               |
|  - Chat workspace & Boardroom Report Archivist             |
+------------------------------------------------------------+
```

---

## 2. Relational Database Design (SQLite)

The system uses a local relational SQLite database (`insightpilot.db`) to record transactions, data ingestion logs, and generated board documents.

### Table Schema Definitions

```sql
-- Archive of AI-generated Executive Reports
CREATE TABLE executive_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,                -- e.g., 'Monthly Business Review - June 2026'
    report_type TEXT NOT NULL,          -- 'weekly', 'monthly', 'board'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content TEXT NOT NULL,              -- Markdown report contents
    metrics_summary TEXT                -- JSON string representation of KPIs at generation
);

-- Strategy Query Logs
CREATE TABLE strategy_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text TEXT NOT NULL,           -- The user prompt or preset question
    response_text TEXT NOT NULL,        -- Generated output response from AI
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data Uploads Ingestion Logs
CREATE TABLE data_uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,             -- Uploaded spreadsheet name
    row_count INTEGER NOT NULL,         -- Ingested row count
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_type TEXT NOT NULL             -- 'revenue', 'customer', 'feedback', 'product'
);
```

---

## 3. UI Dashboard Layout Design

```
+-----------------------------------------------------------------------------------+
| ✈️ InsightPilot  |                      EXECUTIVE inteligence PLATFORM             |
|                 |                                                                 |
| AI CONFIG       |  [Health Score: 85] [MRR: $80K] [Growth: +4%] [Churn: 2.1%] ... |
| [API Key Input] | --------------------------------------------------------------- |
|                 |  Tab 1: Overview | Tab 2: Revenue | Tab 3: Customers | ...      |
| DATA INGEST     | --------------------------------------------------------------- |
| [Upload CSV]    |                                                                 |
|                 |  +--------------------------------+ +------------------------+  |
|                 |  |                                | |                        |  |
|                 |  |       AI EXECUTIVE BRIEF       | |    REPORT GENERATOR    |  |
|                 |  |                                | |  [Monthly] [Save]      |  |
|                 |  | - MoM growth is stable.        | |                        |  |
|                 |  | - Low-tenure churn risk key.   | |  [Saved Reviews List]  |  |
|                 |  |                                | |   - June MBR (PDF)     |  |
|                 |  +--------------------------------+ +------------------------+  |
+-----------------------------------------------------------------------------------+
```

### Navigation Tabs
1. **Overview**: Display summary business intelligence and executive briefs.
2. **Revenue**: Financial trajectory, growth breakouts, and net MRR components.
3. **Customers**: Cohort tables, churn correlation indicators, and NPS feedback distributions.
4. **Product**: Feature usage frequencies, average session durations, and user active-days.
5. **Growth**: Rule-based opportunities detector prompting one-click actionable campaign strategies.
6. **Strategy Chat**: Conversational business intelligence query interface.
