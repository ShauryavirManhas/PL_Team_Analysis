import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
from agents import run_analysis, AGENTS, TEAMS

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PL MultiAgent — Premier League AI Analysis",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #0d0d0d;
}

/* Main background */
.main { background: #0d0d0d; }
[data-testid="stAppViewContainer"] { background: #0d0d0d; }
[data-testid="stSidebar"] {
    background: #111 !important;
    border-right: 1px solid #222;
}

/* Headers */
h1, h2, h3 {
    font-family: 'Bebas Neue', sans-serif !important;
    letter-spacing: 0.04em !important;
    color: #f0f0f0 !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #191919;
    border: 1px solid #2a2a2a;
    border-radius: 0;
    padding: 16px !important;
}

/* Agent cards */
.agent-card {
    background: #131313;
    border: 1px solid #2a2a2a;
    padding: 20px 24px;
    margin: 10px 0;
    border-radius: 2px;
    position: relative;
}
.agent-card-thinking {
    border-left: 3px solid #ffd700;
    animation: pulse-border 1.5s infinite;
}
.agent-card-done { border-left: 3px solid #4ade80; }
.agent-card-fetching { border-left: 3px solid #60a5fa; }

@keyframes pulse-border {
    0%, 100% { border-left-color: #ffd700; }
    50% { border-left-color: #ff9900; }
}

.agent-name {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.agent-status {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #666;
    margin-bottom: 8px;
}
.agent-output {
    font-size: 14px;
    color: #bbb;
    line-height: 1.7;
    white-space: pre-wrap;
}

/* Verdict box */
.verdict-box {
    background: linear-gradient(135deg, #1a0a0a, #0d0d0d);
    border: 1px solid #3a1a1a;
    border-top: 3px solid #da291c;
    padding: 28px 32px;
    margin: 20px 0;
}
.verdict-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 32px;
    color: #da291c;
    letter-spacing: 0.04em;
    margin-bottom: 16px;
}
.verdict-text {
    font-size: 15px;
    color: #ccc;
    line-height: 1.8;
    white-space: pre-wrap;
}

/* Form badges */
.form-badge {
    display: inline-block;
    width: 28px; height: 28px;
    border-radius: 50%;
    text-align: center;
    line-height: 28px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    margin: 2px;
}
.form-W { background: rgba(74,222,128,0.15); color: #4ade80; border: 1px solid #4ade80; }
.form-D { background: rgba(251,191,36,0.15);  color: #fbbf24; border: 1px solid #fbbf24; }
.form-L { background: rgba(248,113,113,0.15); color: #f87171; border: 1px solid #f87171; }

/* Sidebar styles */
.sidebar-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #666;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 6px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: #111; border-bottom: 1px solid #2a2a2a; }
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.1em !important;
    color: #666 !important;
}
.stTabs [aria-selected="true"] { color: #da291c !important; border-bottom: 2px solid #da291c !important; }

/* Buttons */
.stButton > button {
    background: #da291c !important;
    color: white !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 12px 28px !important;
    width: 100% !important;
}
.stButton > button:hover { background: #ff3326 !important; }

/* Selectbox */
.stSelectbox > div > div {
    background: #191919 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 0 !important;
    color: #f0f0f0 !important;
    font-family: 'DM Mono', monospace !important;
}

/* Text input */
.stTextInput > div > div > input {
    background: #191919 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 0 !important;
    color: #f0f0f0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 13px !important;
}

/* Table */
.dataframe { background: #111 !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "results"       not in st.session_state: st.session_state.results       = None
if "agent_logs"    not in st.session_state: st.session_state.agent_logs    = []
if "running"       not in st.session_state: st.session_state.running       = False
if "selected_team" not in st.session_state: st.session_state.selected_team = "Manchester United"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h1 style='font-size:28px;color:#da291c;margin-bottom:4px'>⚽ PL MultiAgent</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-family:DM Mono,monospace;font-size:10px;color:#555;letter-spacing:0.12em;margin-bottom:24px'>PREMIER LEAGUE AI ANALYSIS</p>", unsafe_allow_html=True)

    st.markdown("---")

    # st.markdown("<div class='sidebar-label'>Gemini API Key</div>", unsafe_allow_html=True)
    # gemini_key = st.text_input("", placeholder="AIza...", type="password", label_visibility="collapsed")

    gemini_key=st.secrets["gemini_key"]

    st.markdown("<div class='sidebar-label' style='margin-top:16px'>Select Team</div>", unsafe_allow_html=True)
    selected_team = st.selectbox("", list(TEAMS.keys()), label_visibility="collapsed",
                                  index=list(TEAMS.keys()).index(st.session_state.selected_team))
    st.session_state.selected_team = selected_team

    st.markdown("<br>", unsafe_allow_html=True)
    run_button = st.button("⚡ Run Analysis")

    st.markdown("---")
    st.markdown("<div class='sidebar-label'>Agents</div>", unsafe_allow_html=True)
    for name, info in AGENTS.items():
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:8px;margin:6px 0'>
            <div style='width:8px;height:8px;border-radius:50%;background:{info["color"]};flex-shrink:0'></div>
            <span style='font-family:DM Mono,monospace;font-size:10px;color:#888'>{name}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div class='sidebar-label'>How it works</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family:DM Mono,monospace;font-size:10px;color:#555;line-height:1.8'>
    1. Fetches live PL data<br>
    2. Data Analyst extracts stats<br>
    3. Scout assesses form<br>
    4. Tactician predicts matches<br>
    5. Journalist writes narrative<br>
    6. Orchestrator synthesises all
    </div>""", unsafe_allow_html=True)

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown(f"<h1 style='font-size:52px;margin-bottom:4px'>{selected_team.upper()}</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-family:DM Mono,monospace;font-size:11px;color:#555;letter-spacing:0.15em;margin-bottom:32px'>PREMIER LEAGUE · MULTI-AGENT AI ANALYSIS SYSTEM</p>", unsafe_allow_html=True)

# ── Run analysis ──────────────────────────────────────────────────────────────
if run_button:
    # if not gemini_key:
    #     st.error("Please enter your Gemini API key in the sidebar.")
    # else:
    st.session_state.running   = True
    st.session_state.agent_logs = []
    st.session_state.results   = None

    agent_placeholder = st.empty()

    def yield_step(agent_name, message, status):
        st.session_state.agent_logs.append({
            "agent": agent_name,
            "message": message,
            "status": status,
        })
        # Render current logs
        with agent_placeholder.container():
            st.markdown("<h2 style='font-size:28px;margin-bottom:20px'>🤖 Agent Pipeline Running…</h2>", unsafe_allow_html=True)
            for log in st.session_state.agent_logs:
                color = AGENTS.get(log["agent"], {}).get("color", "#888")
                status_icon = {"thinking": "⏳", "fetching": "📡", "done": "✅"}.get(log["status"], "•")
                card_class  = f"agent-card agent-card-{log['status']}"
                st.markdown(f"""
                <div class="{card_class}">
                    <div class="agent-name" style="color:{color}">{log['agent']}</div>
                    <div class="agent-status">{status_icon} {log['status'].upper()}</div>
                    <div class="agent-output">{log['message']}</div>
                </div>""", unsafe_allow_html=True)

    try:
        results = run_analysis(gemini_key, selected_team, yield_step)
        st.session_state.results = results
        st.session_state.running = False
        agent_placeholder.empty()
        st.rerun()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.session_state.running = False

# ── Results display ───────────────────────────────────────────────────────────
if st.session_state.results:
    r = st.session_state.results

    # ── Top metrics ──────────────────────────────────────────────────────────
    standings = r["standings"]
    team_row  = next((t for t in standings if t["team"] == selected_team), None)

    if team_row:
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: st.metric("Position",   f"{team_row['position']}th")
        with c2: st.metric("Points",      team_row["points"])
        with c3: st.metric("Wins",        team_row["won"])
        with c4: st.metric("Draws",       team_row["draw"])
        with c5: st.metric("Losses",      team_row["lost"])
        with c6:
            gd = team_row["gd"]
            st.metric("Goal Diff", f"+{gd}" if gd >= 0 else str(gd))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Recent form ──────────────────────────────────────────────────────────
    matches = r["matches"]
    if matches:
        form_html = "<div style='display:flex;align-items:center;gap:4px;margin-bottom:24px;flex-wrap:wrap'>"
        form_html += "<span style='font-family:DM Mono,monospace;font-size:10px;color:#555;margin-right:8px;letter-spacing:0.1em'>RECENT FORM</span>"
        for m in matches[-10:]:
            res = m["result"]
            form_html += f"<span class='form-badge form-{res}'>{res}</span>"
        form_html += "</div>"
        st.markdown(form_html, unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🧠 Final Verdict", "📊 Agent Reports", "📈 Stats & Charts", "📋 Standings", "⚽ Results", "🗓 Fixtures"
    ])

    # TAB 1: Final Verdict
    with tab1:
        st.markdown(f"""
        <div class="verdict-box">
            <div class="verdict-title">🧠 Orchestrator's Final Verdict</div>
            <div class="verdict-text">{r['orchestrator']}</div>
        </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h3 style='font-size:22px;color:#ff6b6b'>📰 Journalist's Report</h3>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:14px;color:#bbb;line-height:1.8;white-space:pre-wrap'>{r['journalist']}</div>", unsafe_allow_html=True)

    # TAB 2: Agent Reports
    with tab2:
        for agent_name, key, color in [
            ("📊 Data Analyst", "analyst",   "#00d4ff"),
            ("🔍 Scout",        "scout",     "#ffd700"),
            ("🎯 Tactician",    "tactician", "#c8ff00"),
        ]:
            with st.expander(agent_name, expanded=True):
                st.markdown(f"<div style='font-size:14px;color:#bbb;line-height:1.8;white-space:pre-wrap'>{r[key]}</div>", unsafe_allow_html=True)

    # TAB 3: Charts
    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            # Form W/D/L pie
            if matches:
                w = sum(1 for m in matches if m["result"] == "W")
                d = sum(1 for m in matches if m["result"] == "D")
                l = sum(1 for m in matches if m["result"] == "L")
                fig = go.Figure(data=[go.Pie(
                    labels=["Wins", "Draws", "Losses"],
                    values=[w, d, l],
                    hole=0.6,
                    marker_colors=["#4ade80", "#fbbf24", "#f87171"],
                    textfont=dict(family="DM Mono", size=12),
                )])
                fig.update_layout(
                    paper_bgcolor="#0d0d0d", plot_bgcolor="#0d0d0d",
                    font=dict(color="#f0f0f0", family="DM Mono"),
                    title=dict(text="Recent Result Breakdown", font=dict(size=16, family="Bebas Neue")),
                    showlegend=True, height=320,
                    legend=dict(font=dict(family="DM Mono", size=11)),
                    annotations=[dict(text=f"{w}W/{d}D/{l}L", x=0.5, y=0.5,
                                      font=dict(size=13, family="DM Mono", color="#f0f0f0"),
                                      showarrow=False)]
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Top 10 points bar chart
            top10 = standings[:10]
            colors = ["#da291c" if t["team"] == selected_team else "#2a2a2a" for t in top10]
            fig2 = go.Figure(go.Bar(
                x=[t["team"].replace(" FC","").replace(" United","").replace(" City","") for t in top10],
                y=[t["points"] for t in top10],
                marker_color=colors,
                text=[t["points"] for t in top10],
                textposition="outside",
                textfont=dict(family="DM Mono", size=11, color="#f0f0f0"),
            ))
            fig2.update_layout(
                paper_bgcolor="#0d0d0d", plot_bgcolor="#0d0d0d",
                font=dict(color="#f0f0f0", family="DM Mono"),
                title=dict(text="Top 10 Points", font=dict(size=16, family="Bebas Neue")),
                xaxis=dict(tickfont=dict(size=9), gridcolor="#1a1a1a"),
                yaxis=dict(gridcolor="#1a1a1a"),
                height=320, showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Top scorers bar chart
        scorers = r["scorers"]
        if scorers:
            fig3 = go.Figure(go.Bar(
                y=[s["player"] for s in scorers],
                x=[s["goals"] for s in scorers],
                orientation="h",
                marker_color=["#da291c" if selected_team in s["team"] else "#2a2a2a" for s in scorers],
                text=[f"{s['goals']} goals" for s in scorers],
                textposition="outside",
                textfont=dict(family="DM Mono", size=11, color="#f0f0f0"),
            ))
            fig3.update_layout(
                paper_bgcolor="#0d0d0d", plot_bgcolor="#0d0d0d",
                font=dict(color="#f0f0f0", family="DM Mono"),
                title=dict(text="Top Premier League Scorers", font=dict(size=16, family="Bebas Neue")),
                xaxis=dict(gridcolor="#1a1a1a"),
                yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                height=380, showlegend=False,
            )
            st.plotly_chart(fig3, use_container_width=True)

    # TAB 4: Standings
    with tab4:
        df = pd.DataFrame(standings)
        df["GD"] = df["gd"].apply(lambda x: f"+{x}" if x >= 0 else str(x))
        df = df.rename(columns={"position":"#","team":"Team","played":"P","won":"W","draw":"D","lost":"L","gf":"GF","ga":"GA","points":"Pts"})
        df = df[["#","Team","P","W","D","L","GF","GA","GD","Pts"]]

        def highlight_team(row):
            if row["Team"] == selected_team:
                return ["background-color: rgba(218,41,28,0.15); color: #f0f0f0"] * len(row)
            elif row["#"] <= 4:
                return ["color: #60a5fa"] * len(row)
            elif row["#"] >= 18:
                return ["color: #f87171"] * len(row)
            return [""] * len(row)

        st.dataframe(
            df.style.apply(highlight_team, axis=1),
            use_container_width=True, hide_index=True, height=640,
        )

    # TAB 5: Recent Results
    with tab5:
        if matches:
            for m in reversed(matches):
                res_color = {"W":"#4ade80","D":"#fbbf24","L":"#f87171"}.get(m["result"],"#888")
                st.markdown(f"""
                <div style='background:#131313;border:1px solid #222;border-left:3px solid {res_color};
                     padding:14px 20px;margin:6px 0;display:flex;align-items:center;gap:20px;flex-wrap:wrap'>
                    <span style='font-family:DM Mono,monospace;font-size:10px;color:#555;width:90px'>{m['date']}</span>
                    <span style='font-family:DM Mono,monospace;font-size:10px;color:#555;width:20px'>{m['venue']}</span>
                    <span style='font-size:14px;font-weight:500;color:#f0f0f0;flex:1'>vs {m['opponent']}</span>
                    <span style='font-family:DM Mono,monospace;font-size:16px;font-weight:600;color:#f0f0f0'>{m['score']}</span>
                    <span style='font-family:DM Mono,monospace;font-size:12px;font-weight:700;color:{res_color};width:20px'>{m['result']}</span>
                    <span style='font-family:DM Mono,monospace;font-size:10px;color:#444'>{m['competition']}</span>
                </div>""", unsafe_allow_html=True)

    # TAB 6: Upcoming Fixtures
    with tab6:
        upcoming = r["upcoming"]
        if upcoming:
            for u in upcoming:
                venue_color = "#da291c" if u["venue"] == "H" else "#60a5fa"
                st.markdown(f"""
                <div style='background:#131313;border:1px solid #222;
                     padding:16px 20px;margin:6px 0;display:flex;align-items:center;gap:20px;flex-wrap:wrap'>
                    <span style='font-family:DM Mono,monospace;font-size:10px;color:#555;width:90px'>{u['date']}</span>
                    <span style='font-family:DM Mono,monospace;font-size:10px;color:#555;width:40px'>{u['time']}</span>
                    <span style='font-family:DM Mono,monospace;font-size:10px;font-weight:700;color:{venue_color};width:16px'>{u['venue']}</span>
                    <span style='font-size:14px;font-weight:500;color:#f0f0f0;flex:1'>vs {u['opponent']}</span>
                    <span style='font-family:DM Mono,monospace;font-size:10px;color:#444'>{u['competition']}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No upcoming fixtures found.")

else:
    # Landing state
    if not st.session_state.running:
        st.markdown("""
        <div style='background:#131313;border:1px solid #2a2a2a;border-top:3px solid #da291c;
             padding:48px;text-align:center;margin-top:40px'>
            <div style='font-family:Bebas Neue,sans-serif;font-size:42px;color:#da291c;margin-bottom:16px'>
                5 AI Agents. 1 Team. Full Analysis.
            </div>
            <div style='font-family:DM Mono,monospace;font-size:13px;color:#666;line-height:2;max-width:600px;margin:0 auto'>
                Select a team → Enter your OpenAI API key → Click Run Analysis<br><br>
                The system will fetch live Premier League data and run it through<br>
                5 specialised AI agents to produce a complete tactical report.
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns(5)
        for col, (name, info) in zip([col1,col2,col3,col4,col5], AGENTS.items()):
            with col:
                st.markdown(f"""
                <div style='background:#131313;border:1px solid #222;border-top:2px solid {info["color"]};
                     padding:20px 16px;text-align:center;margin-top:20px'>
                    <div style='font-size:24px;margin-bottom:8px'>{name.split()[0]}</div>
                    <div style='font-family:DM Mono,monospace;font-size:10px;color:{info["color"]};
                         letter-spacing:0.1em;margin-bottom:8px'>{name.split(" ",1)[1]}</div>
                    <div style='font-size:12px;color:#666'>{info["description"]}</div>
                </div>""", unsafe_allow_html=True)
