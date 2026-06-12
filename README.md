# InsightPilot – Executive Decision Intelligence Platform

InsightPilot is a production-grade, AI-powered Executive Decision Intelligence platform. It acts as an automated Chief Strategy Officer and Senior Business Analyst—digesting multi-dimensional raw business records (revenue growth tracks, customer retention parameters, product feature metrics, and customer feedback sentiments) to generate interactive visual insights, anomaly explanations, opportunity alerts, and formal boardroom reviews.

Built using **Streamlit**, **Pandas**, **Plotly**, **SQLite**, and **Google Gemini API**, it provides a self-contained, offline-fallback enabled decision-support environment for Founders, PMs, and Business Analysts.

---

## Key Features

1. **📈 Executive Overview Dashboard**
   - Live health index metric tracking business stability on a scale of 0-100.
   - Core SaaS metrics card strip (MRR, MoM Growth, Customer Churn, LTV, ARPU).
   - Generative executive brief synthesizing current performance with operational risks.
   - Archive utility to compile, output, and store formal Monthly/Weekly Board Reviews.

2. **💰 Revenue Analytics**
   - Month-over-month MRR trends.
   - Net MRR Movement decompositions (isolating New Customer MRR vs. Expansion MRR vs. Churn leakage).

3. **👥 Customer Analytics**
   - Customer status distributions and cohort-style groupings.
   - Statistical correlation metrics highlighting primary drivers of customer churn (e.g. support ticket peaks vs. login inactivity).

4. **📦 Feature Adoption & Engagement**
   - Aggregated feature click frequencies.
   - Feature utilization analysis (identifying active-day trends and session durations).

5. **⚡ Opportunity Discovery Engine**
   - Automatically monitors thresholds to flag revenue leakages or upsell potentials.
   - **One-click Strategy Draft**: Synthesizes custom tactical playbooks/campaigns targeting identified opportunities.

6. **🤖 AI Strategy Chat Workspace**
   - Conversational AI workspace designed to answer complex business questions (e.g. *"Why did churn spike in Month 18?"*).

---

## Technical Architecture

```
InsightPilot/
│
├── .env.example                # Template for GEMINI_API_KEY configuration
├── README.md                   # Project documentation
├── requirements.txt            # System dependencies
│
├── data/                       # Default generated mock business files
│   ├── revenue_trends.csv      
│   ├── customer_metrics.csv    
│   ├── customer_feedback.csv   
│   └── product_usage.csv       
│
├── src/
│   ├── __init__.py
│   ├── database.py             # SQLite interface & schema initialization
│   ├── data_generator.py       # Programmatic generator for realistic relational data
│   ├── analytics_engine.py     # Pandas metrics engine (cohorts, correlations)
│   ├── ai_engine.py            # LLM prompts & offline fallback business logic
│   └── app.py                  # Streamlit Multi-Page interactive dashboard
│
└── docs/
    ├── system_architecture.md   # Component-level architectural design
    ├── interview_questions.md  # Portfolio-ready resume bullets & interview Q&As
    └── deployment_guide.md     # Multi-platform deployment handbook
```

---

## Setup & Local Installation

### Prerequisites
- Python 3.9 or higher
- Git

### Installation Steps

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/InsightPilot.git
   cd InsightPilot
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```
   Open the `.env` file and insert your Google Gemini API Key:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key
   ```
   *(Note: The platform features a fully-functional, deterministic fallback engine that simulates AI analysis if an API Key is not configured).*

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Default Datasets:**
   Generate the default mock business metrics:
   ```bash
   python src/data_generator.py
   ```

5. **Run the Dashboard:**
   ```bash
   streamlit run src/app.py
   ```
   The application will open automatically in your browser at `http://localhost:8501`.

---

## License
This project is open-source and licensed under the MIT License.
