import google.generativeai as genai
from football_data import (
    get_standings, get_recent_matches, get_upcoming_matches,
    get_top_scorers, standings_to_text, matches_to_text, scorers_to_text
)

TEAMS = {
    "Manchester United": 66,
    "Arsenal": 57,
    "Manchester City": 65,
    "Liverpool": 64,
    "Chelsea": 61,
    "Aston Villa": 58,
    "Tottenham Hotspur": 73,
    "Newcastle United": 67,
    "Brighton": 397,
    "Brentford": 402,
}

AGENTS = {
    "📊 Data Analyst": {
        "color": "#00d4ff",
        "role": "data_analyst",
        "description": "Fetches and interprets raw stats from the Premier League",
    },
    "🔍 Scout": {
        "color": "#ffd700",
        "role": "scout",
        "description": "Analyses team form, strengths and weaknesses",
    },
    "📰 Journalist": {
        "color": "#ff6b6b",
        "role": "journalist",
        "description": "Writes a compelling narrative summary of findings",
    },
    "🎯 Tactician": {
        "color": "#c8ff00",
        "role": "tactician",
        "description": "Provides tactical insights and match predictions",
    },
    "🧠 Orchestrator": {
        "color": "#bf5fff",
        "role": "orchestrator",
        "description": "Coordinates all agents and produces the final report",
    },
}

def call_gemini(api_key, system, user):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest",
        system_instruction=system
    )
    response = model.generate_content(user)
    return response.text

def run_data_analyst(api_key, standings, matches, scorers, team_name):
    system = """You are a Premier League Data Analyst agent. Analyse raw football statistics
and extract the most important numerical insights. Be precise and data-driven.
Focus on: league position, points, win rate, goal difference, recent form, and comparison
to the top 4 and leader. Output 4-6 bullet points."""
    user = f"""Analyse the following data for {team_name}:

{standings_to_text(standings)}

{matches_to_text(matches, team_name)}

{scorers_to_text(scorers)}

Provide your data analysis."""
    return call_gemini(api_key, system, user)

def run_scout(api_key, standings, matches, team_name):
    system = """You are a Premier League Scout agent. Assess team form, momentum,
strengths and weaknesses based on results. Look at win streaks, home vs away performance,
goals scored vs conceded, and patterns. Output 4-6 bullet points."""
    user = f"""Scout report for {team_name}:

{standings_to_text(standings)}

{matches_to_text(matches, team_name)}

Provide your scouting assessment."""
    return call_gemini(api_key, system, user)

def run_tactician(api_key, standings, matches, upcoming, team_name):
    system = """You are a Premier League Tactics Expert agent. Provide tactical analysis:
formations likely being used, attacking/defensive patterns, key players to watch,
and predictions for upcoming fixtures. Be bold. Output 4-6 bullet points plus
a prediction for their next match."""
    upcoming_text = "\n".join([
        f"  {u['date']} [{u['venue']}] vs {u['opponent']} - {u['competition']}"
        for u in upcoming[:4]
    ]) if upcoming else "No upcoming fixtures found."
    user = f"""Tactical analysis for {team_name}:

{standings_to_text(standings)}

{matches_to_text(matches, team_name)}

Upcoming fixtures:
{upcoming_text}

Provide your tactical analysis and predictions."""
    return call_gemini(api_key, system, user)

def run_journalist(api_key, analyst_output, scout_output, tactician_output, team_name):
    system = """You are a Premier League Journalist agent. Write a compelling, engaging
narrative summary like a match day programme article. Confident, authoritative tone.
Include a punchy headline. Write 3-4 paragraphs like a top football publication."""
    user = f"""Write a journalist's report on {team_name}'s current Premier League season.

Data Analyst says:
{analyst_output}

Scout says:
{scout_output}

Tactician says:
{tactician_output}

Write your article."""
    return call_gemini(api_key, system, user)

def run_orchestrator(api_key, analyst_output, scout_output, tactician_output, journalist_output, team_name):
    system = """You are the Orchestrator agent — head of a multi-agent Premier League analysis system.
Produce a final executive summary including:
1. A one-line verdict on the team's season
2. Top 3 strengths
3. Top 3 concerns
4. Season prediction (final league position)
5. Star player to watch
Be decisive and authoritative."""
    user = f"""Final orchestration for {team_name}.

From Data Analyst:
{analyst_output}

From Scout:
{scout_output}

From Tactician:
{tactician_output}

From Journalist:
{journalist_output}

Produce your final executive summary."""
    return call_gemini(api_key, system, user)

def run_analysis(gemini_api_key, team_name, yield_step):
    team_id = TEAMS.get(team_name, 66)

    yield_step("📊 Data Analyst", "Fetching live Premier League data…", "fetching")
    standings = get_standings()
    matches   = get_recent_matches(team_id, limit=10)
    upcoming  = get_upcoming_matches(team_id, limit=6)
    scorers   = get_top_scorers()

    yield_step("📊 Data Analyst", "Analysing statistics and league data…", "thinking")
    analyst_out = run_data_analyst(gemini_api_key, standings, matches, scorers, team_name)
    yield_step("📊 Data Analyst", analyst_out, "done")

    yield_step("🔍 Scout", "Reviewing form, results and patterns…", "thinking")
    scout_out = run_scout(gemini_api_key, standings, matches, team_name)
    yield_step("🔍 Scout", scout_out, "done")

    yield_step("🎯 Tactician", "Analysing tactics and upcoming fixtures…", "thinking")
    tactician_out = run_tactician(gemini_api_key, standings, matches, upcoming, team_name)
    yield_step("🎯 Tactician", tactician_out, "done")

    yield_step("📰 Journalist", "Writing narrative report…", "thinking")
    journalist_out = run_journalist(gemini_api_key, analyst_out, scout_out, tactician_out, team_name)
    yield_step("📰 Journalist", journalist_out, "done")

    yield_step("🧠 Orchestrator", "Synthesising all agent reports into final verdict…", "thinking")
    orchestrator_out = run_orchestrator(gemini_api_key, analyst_out, scout_out, tactician_out, journalist_out, team_name)
    yield_step("🧠 Orchestrator", orchestrator_out, "done")

    return {
        "analyst": analyst_out,
        "scout": scout_out,
        "tactician": tactician_out,
        "journalist": journalist_out,
        "orchestrator": orchestrator_out,
        "standings": standings,
        "matches": matches,
        "upcoming": upcoming,
        "scorers": scorers,
    }
