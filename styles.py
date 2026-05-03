"""Professional EduGrowth Design System - CSS Module"""

EDUGROWTH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Poppins:wght@600;700;800;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

:root {
    --primary: #2E5CFF;
    --primary-light: rgba(46,92,255,0.12);
    --primary-glow: rgba(46,92,255,0.25);
    --secondary: #6C63FF;
    --success: #00D4AA;
    --success-light: rgba(0,212,170,0.12);
    --warning: #FFB020;
    --warning-light: rgba(255,176,32,0.12);
    --danger: #FF4D6A;
    --danger-light: rgba(255,77,106,0.12);

    --surface: rgba(12,14,20,0.85);
    --surface-strong: rgba(255,255,255,0.07);
    --surface-hover: rgba(255,255,255,0.11);
    --card-bg: rgba(18,22,32,0.92);

    --line: rgba(255,255,255,0.08);
    --line-strong: rgba(255,255,255,0.16);

    --text: #EDF0F7;
    --text-muted: rgba(180,190,220,0.55);
    --text-soft: rgba(210,218,240,0.78);

    --blue: #2E5CFF;
    --blue-glow: var(--primary-glow);
    --green: #00D4AA;
    --amber: #FFB020;
    --red: #FF4D6A;
    --purple: #6C63FF;

    --radius: 16px;
    --radius-sm: 10px;
}

/* ── App Background ── */
.stApp {
    background: linear-gradient(160deg, #080b14 0%, #0d1120 40%, #0a0e1a 100%);
}
.stApp::before {
    content:""; position:fixed; inset:0; z-index:-1; pointer-events:none;
    background: radial-gradient(ellipse 60% 50% at 15% 20%, rgba(46,92,255,0.06) 0%, transparent 70%),
                radial-gradient(ellipse 50% 40% at 85% 75%, rgba(108,99,255,0.05) 0%, transparent 70%),
                radial-gradient(ellipse 40% 30% at 50% 50%, rgba(0,212,170,0.03) 0%, transparent 60%);
}

.block-container { padding:1.8rem 2.8rem 4rem; max-width:1440px; }

/* ── Hide Streamlit Branding ── */
#MainMenu {visibility:hidden;} footer {visibility:hidden;}
header[data-testid="stHeader"] {background:transparent;}

/* ── Typography ── */
h1,h2,h3,h4 { font-family:'Poppins',sans-serif !important; letter-spacing:-0.02em !important; color:var(--text) !important; }
h1 { font-size:2.8rem !important; font-weight:800 !important; line-height:1.1 !important; }
h2 { font-size:1.65rem !important; font-weight:700 !important; }
h3 { font-size:1.2rem !important; font-weight:700 !important; }

/* ── Glassmorphism ── */
.glass {
    background:var(--card-bg); backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);
    border:1px solid var(--line); border-radius:var(--radius);
    box-shadow:0 8px 32px rgba(0,0,0,0.35);
}

/* ── Buttons ── */
.stButton > button {
    border-radius:var(--radius-sm); min-height:2.8rem; font-weight:700; font-family:'Inter',sans-serif !important;
    transition:all .25s cubic-bezier(.4,0,.2,1); letter-spacing:.02em;
    border:1px solid var(--line); background:var(--surface-strong); color:var(--text);
}
.stButton > button:hover { background:var(--surface-hover); border-color:var(--primary); transform:translateY(-1px); }
.stButton > button[kind="primary"] {
    background:linear-gradient(135deg,var(--primary),var(--secondary));
    border:none; box-shadow:0 4px 18px rgba(46,92,255,0.35); color:#fff;
}
.stButton > button[kind="primary"]:hover {
    transform:translateY(-2px) scale(1.01); box-shadow:0 8px 28px rgba(46,92,255,0.5);
}

/* ── Mode Cards (Landing) ── */
.mode-card {
    background:var(--card-bg); backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
    border:1px solid var(--line); border-radius:var(--radius);
    padding:3rem 2.5rem; text-align:center;
    transition:all .35s cubic-bezier(.175,.885,.32,1.275);
    height:100%; display:flex; flex-direction:column; justify-content:space-between;
}
.mode-card:hover {
    border-color:var(--primary); transform:translateY(-8px);
    box-shadow:0 20px 50px rgba(0,0,0,0.45), 0 0 25px rgba(46,92,255,0.1);
}

/* ── Login Card ── */
.login-card {
    max-width:520px; margin:5rem auto; background:var(--card-bg);
    backdrop-filter:blur(20px); border:1px solid var(--line-strong);
    border-radius:var(--radius); padding:4rem 3rem;
    box-shadow:0 30px 70px rgba(0,0,0,0.5); text-align:center;
}

/* ── Video Card ── */
.video-card {
    background:var(--card-bg); border:1px solid var(--line);
    border-radius:var(--radius-sm); padding:1.6rem;
    transition:all .25s ease;
}
.video-card:hover { border-color:var(--primary); background:var(--surface-hover); transform:translateY(-3px); box-shadow:0 12px 30px rgba(0,0,0,0.3); }

/* ── Quiz Container ── */
.quiz-container {
    background:var(--card-bg); border:1px solid var(--line);
    border-radius:var(--radius); padding:2.5rem; margin-top:2rem;
}

/* ── Metric Cards ── */
div[data-testid="stMetric"] {
    background:var(--card-bg); backdrop-filter:blur(8px);
    border:1px solid var(--line); border-radius:var(--radius-sm); padding:1.2rem;
    transition:border-color .2s;
}
div[data-testid="stMetric"]:hover { border-color:var(--primary); }
div[data-testid="stMetric"] label { color:var(--text-muted) !important; font-weight:600 !important; text-transform:uppercase; font-size:0.72rem !important; letter-spacing:0.06em; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color:var(--text) !important; font-family:'Poppins',sans-serif !important; font-weight:800 !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080b14 0%, #0c1022 100%) !important;
    border-right:1px solid var(--line);
}
[data-testid="stSidebar"] .stMarkdown h3 { color:var(--primary) !important; font-size:0.9rem !important; text-transform:uppercase; letter-spacing:0.08em; }

/* ── App Header ── */
.app-header {
    position:relative; overflow:hidden;
    border:1px solid var(--line); border-radius:var(--radius);
    padding:2.5rem; margin-bottom:2rem;
    background:linear-gradient(135deg, #0d1120 0%, #111930 100%);
    box-shadow:0 16px 40px rgba(0,0,0,0.35);
}
.app-header::after { content:""; position:absolute; inset:auto 0 0 0; height:3px; background:linear-gradient(90deg,var(--primary),var(--secondary),var(--success)); }
.app-eyebrow { color:var(--primary); font-size:0.82rem; font-weight:800; text-transform:uppercase; letter-spacing:0.14em; margin-bottom:0.8rem; }
.app-title { color:#fff; font-size:2.2rem; font-weight:800; font-family:'Poppins',sans-serif; line-height:1.15; margin-bottom:0.8rem; }
.app-subtitle { color:var(--text-muted); font-size:0.95rem; line-height:1.7; max-width:800px; margin-bottom:1.5rem; }
.header-chip { display:inline-block; border-radius:999px; padding:0.35rem 0.9rem; margin:0.4rem 0.4rem 0 0; font-size:0.8rem; font-weight:700; color:var(--text-soft); background:var(--surface-strong); border:1px solid var(--line); }

/* ── Learning Card ── */
.learning-card {
    border:1px solid var(--line); border-radius:var(--radius-sm);
    background:linear-gradient(180deg, rgba(255,255,255,0.06), var(--card-bg));
    padding:1.5rem; min-height:130px;
    box-shadow:0 6px 20px rgba(0,0,0,0.2); transition:all .25s;
}
.learning-card:hover { transform:translateY(-4px); border-color:var(--primary); box-shadow:0 12px 30px rgba(0,0,0,0.3); }
.learning-card-label { color:var(--text-muted); font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.7rem; }
.learning-card-value { color:#fff; font-size:1.9rem; font-weight:900; font-family:'Poppins',sans-serif; line-height:1; }
.learning-card-note { color:var(--text-muted); font-size:0.82rem; margin-top:0.7rem; }

/* ── Profile Hero ── */
.profile-hero {
    border:1px solid var(--line); border-radius:var(--radius);
    padding:2.5rem; background:linear-gradient(135deg, #111930, #0d1120);
    box-shadow:0 12px 40px rgba(0,0,0,0.3); margin-bottom:2rem;
}
.profile-name { font-size:2rem; font-weight:800; font-family:'Poppins',sans-serif; color:#fff; margin-bottom:0.5rem; }
.profile-meta { color:var(--text-muted); font-size:0.95rem; }
.profile-score-value { font-size:2.8rem; font-weight:900; font-family:'Poppins',sans-serif; color:#fff; line-height:1; }

/* ── Grid Layout ── */
.command-center { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:1.4rem; margin-bottom:2rem; }

/* ── Narrative Box ── */
.narrative-box {
    background:rgba(46,92,255,0.05); border:1px solid rgba(46,92,255,0.2);
    border-radius:var(--radius-sm); padding:1.5rem; margin:1.5rem 0;
    line-height:1.8; font-size:1rem; color:var(--text-soft);
}

/* ── Status Pills ── */
.status-pill { display:inline-block; border-radius:999px; padding:0.35rem 0.9rem; font-size:0.8rem; font-weight:700; margin-top:0.8rem; }
.status-good { color:var(--success); background:var(--success-light); border:1px solid var(--success); }
.status-watch { color:var(--warning); background:var(--warning-light); border:1px solid var(--warning); }
.status-risk { color:var(--danger); background:var(--danger-light); border:1px solid var(--danger); }

/* ── Rec/Risk Cards ── */
.rec-item, .risk-card {
    border:1px solid var(--line); border-radius:var(--radius-sm);
    padding:1.2rem; margin:0.7rem 0; background:var(--card-bg);
    color:var(--text-soft); line-height:1.6; transition:all .2s;
}
.rec-item:hover { background:var(--surface-hover); transform:translateX(4px); border-color:var(--primary); }
.rec-index { display:inline-flex; align-items:center; justify-content:center; width:1.7rem; height:1.7rem; border-radius:50%; margin-right:0.7rem; background:var(--primary); color:#fff; font-size:0.75rem; font-weight:800; }
.risk-card { border-left:4px solid var(--danger); background:var(--danger-light); }

/* ── Section Helpers ── */
.section-kicker { color:var(--text-muted); font-size:0.9rem; margin-bottom:1.4rem; }
.action-strip { background:var(--primary-light); border:1px solid rgba(46,92,255,0.25); border-radius:var(--radius-sm); padding:1.1rem; margin-bottom:1.8rem; color:var(--text-soft); }

/* ── Badges ── */
.badge-pending { border-radius:999px; padding:0.3rem 0.8rem; font-size:0.78rem; font-weight:700; background:var(--warning-light); color:var(--warning); border:1px solid var(--warning); }
.badge-done { border-radius:999px; padding:0.3rem 0.8rem; font-size:0.78rem; font-weight:700; background:var(--success-light); color:var(--success); border:1px solid var(--success); }

/* ── Progress Bar ── */
.progress-bar-wrap { background:rgba(255,255,255,0.06); border-radius:999px; height:7px; margin:1.4rem 0; overflow:hidden; }

/* ── Hub Header ── */
.hub-header {
    background:linear-gradient(135deg, rgba(46,92,255,0.08), rgba(108,99,255,0.08));
    border:1px solid var(--line); border-radius:var(--radius);
    padding:2.5rem; margin-bottom:2rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap:0.5rem; border-bottom:1px solid var(--line); }
.stTabs [data-baseweb="tab"] {
    border-radius:var(--radius-sm) var(--radius-sm) 0 0; padding:0.6rem 1.2rem;
    font-weight:600; color:var(--text-muted); background:transparent;
    transition:all .2s;
}
.stTabs [data-baseweb="tab"]:hover { color:var(--text); background:var(--surface-strong); }
.stTabs [aria-selected="true"] { color:var(--primary) !important; border-bottom:2px solid var(--primary) !important; background:var(--primary-light) !important; }

/* ── Dataframes ── */
.stDataFrame { border-radius:var(--radius-sm); overflow:hidden; }
.stDataFrame [data-testid="stDataFrameResizable"] { border:1px solid var(--line); border-radius:var(--radius-sm); }

/* ── Expander ── */
.streamlit-expanderHeader { font-weight:700 !important; color:var(--text) !important; }
details { border:1px solid var(--line) !important; border-radius:var(--radius-sm) !important; background:var(--card-bg) !important; }

/* ── Radio / Inputs ── */
.stRadio > div { gap:0.3rem; }
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    border-radius:var(--radius-sm) !important; border:1px solid var(--line) !important;
    background:var(--surface-strong) !important; color:var(--text) !important;
    transition:border-color .2s;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus { border-color:var(--primary) !important; box-shadow:0 0 0 2px var(--primary-light) !important; }

/* ── Selectbox ── */
.stSelectbox > div > div { border-radius:var(--radius-sm) !important; border-color:var(--line) !important; }

/* ── Progress Bar (Streamlit) ── */
.stProgress > div > div { background:linear-gradient(90deg,var(--primary),var(--secondary)) !important; border-radius:999px; }

/* ── Animations ── */
@keyframes fadeIn { from{opacity:0;transform:translateY(18px)} to{opacity:1;transform:translateY(0)} }
.fade-in { animation:fadeIn .7s ease-out forwards; }

@keyframes drift { 0%{transform:translate(0,0) scale(1);opacity:.25} 50%{transform:translate(25px,-25px) scale(1.08);opacity:.5} 100%{transform:translate(0,0) scale(1);opacity:.25} }
.particle { position:fixed; width:3px; height:3px; background:var(--primary); border-radius:50%; filter:blur(2px); z-index:-1; opacity:.3; animation:drift 14s infinite ease-in-out; }

/* ── Custom Footer ── */
.edu-footer {
    text-align:center; padding:2rem 0 1rem; margin-top:3rem;
    border-top:1px solid var(--line); color:var(--text-muted); font-size:0.75rem;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.12); border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:rgba(255,255,255,0.2); }

/* ── Altair Charts ── */
.vega-embed { border-radius:var(--radius-sm); overflow:hidden; }

/* ── Sidebar Logo ── */
.sidebar-logo {
    text-align:center; padding:1.5rem 0 1rem; margin-bottom:0.5rem;
    border-bottom:1px solid var(--line);
}
.sidebar-logo-icon { font-size:2.2rem; margin-bottom:0.3rem; }
.sidebar-logo-text { font-family:'Poppins',sans-serif; font-size:1.1rem; font-weight:800; color:var(--text);
    background:linear-gradient(135deg,var(--primary),var(--secondary)); -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.sidebar-logo-sub { font-size:0.65rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.12em; font-weight:600; }
</style>
"""
