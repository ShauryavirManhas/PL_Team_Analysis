# ⚽ Premier League Multi-Agent AI Analysis System

A multi-agent AI system built with LangChain + Streamlit that analyses any Premier League team using 5 specialised AI agents.

## Agents

| Agent | Role |
|-------|------|
| 📊 Data Analyst | Extracts key stats from live PL data |
| 🔍 Scout | Assesses form, strengths and weaknesses |
| 🎯 Tactician | Tactical analysis + match predictions |
| 📰 Journalist | Writes a compelling narrative report |
| 🧠 Orchestrator | Synthesises all agents into a final verdict |

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. In the app
- Enter your **Gemini API key** (needs Gemini Flash access)
- Select a Premier League team
- Click **Run Analysis**

## Data Source
Live data from [football-data.org](https://football-data.org) — free tier API.
