import requests

FOOTBALL_API_KEY = "9e6ac22941b04001a3fbe82e9d49fcbf"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": FOOTBALL_API_KEY}

MAN_UTD_ID = 66
PL_CODE = "PL"

def get_standings():
    r = requests.get(f"{BASE_URL}/competitions/{PL_CODE}/standings", headers=HEADERS)
    r.raise_for_status()
    table = r.json()["standings"][0]["table"]
    rows = []
    for t in table:
        rows.append({
            "position": t["position"],
            "team": t["team"]["name"],
            "team_id": t["team"]["id"],
            "played": t["playedGames"],
            "won": t["won"],
            "draw": t["draw"],
            "lost": t["lost"],
            "gf": t["goalsFor"],
            "ga": t["goalsAgainst"],
            "gd": t["goalDifference"],
            "points": t["points"],
        })
    return rows

def get_recent_matches(team_id, limit=10):
    r = requests.get(
        f"{BASE_URL}/teams/{team_id}/matches",
        headers=HEADERS,
        params={"status": "FINISHED", "limit": limit}
    )
    r.raise_for_status()
    matches = r.json().get("matches", [])
    results = []
    for m in matches:
        is_home = m["homeTeam"]["id"] == team_id
        ms = m["score"]["fullTime"]["home"] if is_home else m["score"]["fullTime"]["away"]
        os_ = m["score"]["fullTime"]["away"] if is_home else m["score"]["fullTime"]["home"]
        opp = m["awayTeam"]["name"] if is_home else m["homeTeam"]["name"]
        if ms is None or os_ is None:
            continue
        res = "W" if ms > os_ else ("D" if ms == os_ else "L")
        results.append({
            "date": m["utcDate"][:10],
            "opponent": opp,
            "venue": "H" if is_home else "A",
            "score": f"{ms}-{os_}",
            "result": res,
            "competition": m.get("competition", {}).get("name", "Unknown"),
        })
    return results

def get_upcoming_matches(team_id, limit=6):
    r = requests.get(
        f"{BASE_URL}/teams/{team_id}/matches",
        headers=HEADERS,
        params={"status": "SCHEDULED", "limit": limit}
    )
    r.raise_for_status()
    matches = r.json().get("matches", [])
    upcoming = []
    for m in matches:
        is_home = m["homeTeam"]["id"] == team_id
        opp = m["awayTeam"]["name"] if is_home else m["homeTeam"]["name"]
        upcoming.append({
            "date": m["utcDate"][:10],
            "time": m["utcDate"][11:16],
            "opponent": opp,
            "venue": "H" if is_home else "A",
            "competition": m.get("competition", {}).get("name", "Unknown"),
        })
    return upcoming

def get_top_scorers():
    r = requests.get(f"{BASE_URL}/competitions/{PL_CODE}/scorers?limit=10", headers=HEADERS)
    r.raise_for_status()
    scorers = r.json().get("scorers", [])
    result = []
    for s in scorers:
        result.append({
            "player": s["player"]["name"],
            "team": s["team"]["name"],
            "goals": s["goals"],
            "assists": s.get("assists", 0),
            "played": s.get("playedMatches", 0),
        })
    return result

def get_team_info(team_id):
    r = requests.get(f"{BASE_URL}/teams/{team_id}", headers=HEADERS)
    r.raise_for_status()
    return r.json()

def standings_to_text(standings):
    lines = ["Premier League Standings:\n"]
    lines.append(f"{'Pos':<4} {'Team':<30} {'P':<4} {'W':<4} {'D':<4} {'L':<4} {'GF':<4} {'GA':<4} {'GD':<5} {'Pts'}")
    for t in standings:
        gd = f"+{t['gd']}" if t['gd'] >= 0 else str(t['gd'])
        lines.append(f"{t['position']:<4} {t['team']:<30} {t['played']:<4} {t['won']:<4} {t['draw']:<4} {t['lost']:<4} {t['gf']:<4} {t['ga']:<4} {gd:<5} {t['points']}")
    return "\n".join(lines)

def matches_to_text(matches, team_name="Team"):
    lines = [f"Recent matches for {team_name}:\n"]
    for m in matches:
        lines.append(f"  {m['date']} [{m['venue']}] vs {m['opponent']}: {m['score']} ({m['result']}) - {m['competition']}")
    return "\n".join(lines)

def scorers_to_text(scorers):
    lines = ["Top Premier League Scorers:\n"]
    for i, s in enumerate(scorers, 1):
        lines.append(f"  {i}. {s['player']} ({s['team']}): {s['goals']} goals, {s['assists']} assists in {s['played']} games")
    return "\n".join(lines)
