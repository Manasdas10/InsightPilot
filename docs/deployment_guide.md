# Deployment Handbook - InsightPilot

InsightPilot can be deployed to local environments, Docker containers, or hosting platforms. This handbook covers the three most common production pipelines.

---

## 1. Streamlit Community Cloud (Recommended & Fastest)

Streamlit Community Cloud connects directly to your GitHub repository and handles deployment, SSL, and scaling automatically.

### Steps:
1. **Push your code to GitHub:**
   Make sure all files are committed and pushed to a public or private GitHub repository.
2. **Sign in to Streamlit Share:**
   Go to [share.streamlit.io](https://share.streamlit.io/) and log in using your GitHub account.
3. **Deploy New App:**
   - Click the "New app" button.
   - Select your repository (`InsightPilot`), branch (`main`), and main file path (`src/app.py`).
4. **Configure Secrets / Environment Variables:**
   - Click "Advanced settings" before deploying.
   - Under the "Secrets" text area, add your Gemini API Key in TOML format:
     ```toml
     GEMINI_API_KEY = "your_actual_gemini_api_key_here"
     ```
   - Click **Deploy**. Your app will be live at a custom URL in minutes.

---

## 2. Docker Containerization

For self-hosted virtual machines (AWS EC2, DigitalOcean Droplet) or Kubernetes clusters.

### Create a `Dockerfile`
Create a `Dockerfile` in the root of the project:
```dockerfile
# Use official lightweight Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose default Streamlit port
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run locally:
```bash
# Build the image
docker build -t insightpilot:latest .

# Run the container (injecting your API Key)
docker run -d -p 8501:8501 -e GEMINI_API_KEY="your_api_key" insightpilot:latest
```

---

## 3. Heroku Deployment

To deploy using Heroku Git:

### Steps:
1. **Add a `Procfile`:**
   Create a file named `Procfile` in the root directory:
   ```txt
   web: streamlit run src/app.py --server.port=$PORT --server.address=0.0.0.0
   ```
2. **Add `setup.sh` (optional, for configuring Streamlit server parameters):**
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [server]\n\
   headless = true\n\
   port = $PORT\n\
   enableCORS = false\n\
   \n\
   " > ~/.streamlit/config.toml
   ```
3. **Deploy:**
   ```bash
   # Login to Heroku CLI
   heroku login
   
   # Create a new app
   heroku create insightpilot-platform
   
   # Set API Key environment variable
   heroku config:set GEMINI_API_KEY="your_gemini_key_here"
   
   # Deploy code
   git add .
   git commit -m "Configure deployment"
   git push heroku main
   ```
