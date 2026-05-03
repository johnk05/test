import html
import io
import joblib
import sqlite3
import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from streamlit_player import st_player
from learning_content import VIDEO_MODULES
from db_utils import get_connection, init_db
from nlp_utils import analyze_sentiment, extract_topics_from_feedback
from rec_engine import generate_recommendations, fetch_active_recommendations

# Initialize DB on startup
init_db()

papaparse_uploader = components.declare_component("papaparse_uploader", path="papaparse_component")


DATA_PATH = "synthetic_student_data.csv"
MODEL_PATHS = {
    "Logistic Regression": "logistic_model.pkl",
    "Random Forest": "rf_model.pkl",
}
REQUIRED_DATA_COLUMNS = [
    "student_id",
    "region",
    "time_spent",
    "modules_completed",
    "quiz_score",
    "assignment_timeliness",
    "interaction_level",
    "consistency_index",
    "engagement_score",
    "learning_trend",
]


def format_value(value, decimals=2):
    """Format numeric values for cleaner display."""
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return value


def escape_html(value):
    """Escape dynamic values before inserting them into custom HTML."""
    return html.escape(str(value), quote=True)


def inject_styles():
    """Apply professional premium dashboard styling."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        
        html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
        
        :root {
            --surface: rgba(13, 17, 23, 0.7);
            --surface-strong: rgba(255, 255, 255, 0.08);
            --surface-hover: rgba(255, 255, 255, 0.12);
            --line: rgba(255, 255, 255, 0.1);
            --line-strong: rgba(255, 255, 255, 0.2);
            --text: #f0f4ff;
            --text-muted: rgba(200, 210, 240, 0.6);
            --text-soft: rgba(220, 228, 255, 0.8);
            --blue: #4f9eff;
            --blue-glow: rgba(79, 158, 255, 0.25);
            --green: #3dd68c;
            --amber: #f5c542;
            --red: #ff6b6b;
            --purple: #a78bfa;
            --radius: 20px;
            --radius-sm: 12px;
        }

        .stApp {
            background: radial-gradient(circle at 0% 0%, rgba(79, 158, 255, 0.05) 0%, transparent 50%),
                        radial-gradient(circle at 100% 100%, rgba(167, 139, 250, 0.05) 0%, transparent 50%),
                        #05070a;
        }

        .block-container { padding: 2rem 3rem 4rem; max-width: 1400px; }
        
        /* Glassmorphism base */
        .glass {
            background: var(--surface);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--line);
            border-radius: var(--radius);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }

        h1, h2, h3, h4 { font-family: 'Inter', sans-serif !important; letter-spacing: -0.03em !important; color: var(--text) !important; }
        h1 { font-size: 3.2rem !important; font-weight: 900 !important; line-height: 1.05 !important; }
        h2 { font-size: 1.8rem !important; font-weight: 800 !important; }

        .stButton > button {
            border-radius: var(--radius-sm); 
            min-height: 3rem; 
            font-weight: 700;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
            letter-spacing: 0.02em;
            border: 1px solid var(--line);
            background: var(--surface-strong);
            color: var(--text);
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #4f9eff, #7c3aed);
            border: none; 
            box-shadow: 0 4px 15px rgba(79, 158, 255, 0.3);
        }

        .stButton > button[kind="primary"]:hover { 
            transform: translateY(-2px) scale(1.02); 
            box-shadow: 0 10px 30px rgba(79, 158, 255, 0.5); 
        }

        .mode-card {
            background: var(--surface);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--line);
            border-radius: var(--radius);
            padding: 3rem 2.5rem;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .mode-card:hover {
            border-color: var(--blue);
            transform: translateY(-10px);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5), 0 0 20px rgba(79, 158, 255, 0.15);
        }

        .login-card {
            max-width: 520px;
            margin: 5rem auto;
            background: var(--surface);
            backdrop-filter: blur(20px);
            border: 1px solid var(--line-strong);
            border-radius: var(--radius);
            padding: 4rem 3rem;
            box-shadow: 0 30px 70px rgba(0, 0, 0, 0.6);
            text-align: center;
        }

        .video-card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: var(--radius-sm);
            padding: 1.8rem;
            transition: all 0.3s ease;
        }

        .video-card:hover {
            border-color: var(--blue);
            background: var(--surface-strong);
            transform: scale(1.02);
        }

        .quiz-container {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: var(--radius);
            padding: 2.5rem;
            margin-top: 2rem;
        }

        /* Metrics styling */
        div[data-testid="stMetric"] {
            background: var(--surface);
            backdrop-filter: blur(8px);
            border: 1px solid var(--line);
            border-radius: var(--radius-sm);
            padding: 1.2rem;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #080a0f !important;
            border-right: 1px solid var(--line);
        }

        /* Cinematic Background Particles */
        .stApp::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at 20% 30%, rgba(79, 158, 255, 0.03) 0%, transparent 40%),
                        radial-gradient(circle at 80% 70%, rgba(167, 139, 250, 0.03) 0%, transparent 40%);
            z-index: -1;
            pointer-events: none;
        }

        @keyframes drift {
            0% { transform: translate(0, 0) scale(1); opacity: 0.3; }
            50% { transform: translate(30px, -30px) scale(1.1); opacity: 0.6; }
            100% { transform: translate(0, 0) scale(1); opacity: 0.3; }
        }

        .particle {
            position: fixed;
            width: 4px; height: 4px;
            background: var(--blue);
            border-radius: 50%;
            filter: blur(2px);
            z-index: -1;
            opacity: 0.4;
            animation: drift 12s infinite ease-in-out;
        }

        .app-header {
            position: relative; overflow: hidden;
            border: 1px solid var(--line); border-radius: var(--radius);
            padding: 2.5rem; margin-bottom: 2rem;
            background: linear-gradient(135deg, #0d1117 0%, #111827 100%);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }
        .app-header::after { content:""; position:absolute; inset:auto 0 0 0; height:3px; background:linear-gradient(90deg,var(--blue),var(--purple),var(--green)); }
        .app-eyebrow { color: var(--blue); font-size: 0.85rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 0.8rem; }
        .app-title { color: #fff; font-size: 2.5rem; font-weight: 900; line-height: 1.1; margin-bottom: 0.8rem; }
        .app-subtitle { color: var(--text-muted); font-size: 1rem; line-height: 1.6; max-width: 800px; margin-bottom: 1.5rem; }
        .header-chip { display: inline-block; border-radius: 999px; padding: 0.4rem 1rem; margin: 0.5rem 0.5rem 0 0; font-size: 0.85rem; font-weight: 700; color: var(--text-soft); background: var(--surface-strong); border: 1px solid var(--line); }

        .learning-card { 
            border: 1px solid var(--line); border-radius: var(--radius-sm); 
            background: linear-gradient(180deg, var(--surface-strong), var(--surface)); 
            padding: 1.5rem; min-height: 140px; 
            box-shadow: 0 8px 24px rgba(0,0,0,0.2); 
            transition: transform 0.3s;
        }
        .learning-card:hover { transform: translateY(-5px); border-color: var(--blue); }
        .learning-card-label { color: var(--text-muted); font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.8rem; }
        .learning-card-value { color: #fff; font-size: 2rem; font-weight: 900; line-height: 1; }
        .learning-card-note { color: var(--text-muted); font-size: 0.85rem; margin-top: 0.8rem; }

        .profile-hero { 
            border: 1px solid var(--line); border-radius: var(--radius); 
            padding: 2.5rem; background: linear-gradient(135deg, #111827, #0d1117); 
            box-shadow: 0 15px 45px rgba(0,0,0,0.3); margin-bottom: 2rem; 
        }
        .profile-name { font-size: 2.2rem; font-weight: 900; color: #fff; margin-bottom: 0.5rem; }
        .profile-meta { color: var(--text-muted); font-size: 1rem; }
        .profile-score-value { font-size: 3rem; font-weight: 900; color: #fff; line-height: 1; }

        /* Command Center Layout */
        .command-center {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .narrative-box {
            background: rgba(79, 158, 255, 0.05);
            border: 1px solid var(--blue);
            border-radius: var(--radius-sm);
            padding: 1.5rem;
            margin: 1.5rem 0;
            line-height: 1.8;
            font-size: 1.05rem;
            color: var(--text-soft);
        }

        .status-pill { display: inline-block; border-radius: 999px; padding: 0.4rem 1rem; font-size: 0.85rem; font-weight: 700; margin-top: 1rem; }
        .status-good { color: var(--green); background: rgba(61, 214, 140, 0.1); border: 1px solid var(--green); }
        .status-watch { color: var(--amber); background: rgba(245, 197, 66, 0.1); border: 1px solid var(--amber); }
        .status-risk { color: var(--red); background: rgba(255, 107, 107, 0.1); border: 1px solid var(--red); }

        .rec-item, .risk-card { 
            border: 1px solid var(--line); border-radius: var(--radius-sm); 
            padding: 1.2rem; margin: 0.8rem 0; background: var(--surface); 
            color: var(--text-soft); line-height: 1.6; transition: all 0.2s; 
        }
        .rec-item:hover { background: var(--surface-strong); transform: translateX(5px); border-color: var(--blue); }
        .rec-index { display: inline-flex; align-items: center; justify-content: center; width: 1.8rem; height: 1.8rem; border-radius: 50%; margin-right: 0.8rem; background: var(--blue); color: #fff; font-size: 0.8rem; font-weight: 800; }
        .risk-card { border-left: 4px solid var(--red); background: rgba(255, 107, 107, 0.05); }

        .section-kicker { color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1.5rem; }
        .action-strip { background: var(--blue-glow); border: 1px solid var(--blue); border-radius: var(--radius-sm); padding: 1.2rem; margin-bottom: 2rem; color: var(--text-soft); }

        .badge-pending { border-radius: 999px; padding: 0.3rem 0.8rem; font-size: 0.8rem; font-weight: 700; background: rgba(245, 197, 66, 0.1); color: var(--amber); border: 1px solid var(--amber); }
        .badge-done { border-radius: 999px; padding: 0.3rem 0.8rem; font-size: 0.8rem; font-weight: 700; background: rgba(61, 214, 140, 0.1); color: var(--green); border: 1px solid var(--green); }
        .progress-bar-wrap { background: var(--surface-strong); border-radius: 999px; height: 8px; margin: 1.5rem 0; overflow: hidden; }

        .hub-header {
            background: linear-gradient(135deg, rgba(79, 158, 255, 0.1), rgba(167, 139, 250, 0.1));
            border: 1px solid var(--line);
            border-radius: var(--radius);
            padding: 2.5rem;
            margin-bottom: 2rem;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .fade-in { animation: fadeIn 0.8s ease-out forwards; }

        </style>
        """,
        unsafe_allow_html=True,
    )



def show_landing_page():
    """Display the initial selection screen for the two app modes."""
    st.markdown("""
    <div class='fade-in' style='text-align:center; padding: 6rem 0 4rem;'>
        <div style='font-size:0.9rem; font-weight:800; color:var(--blue); text-transform:uppercase; letter-spacing:0.2em; margin-bottom:1.5rem;'>🎓 EduGrowth Intelligence Platform</div>
        <h1 style='background:linear-gradient(135deg,#fff,#4f9eff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:1.2rem;'>Choose Your Intelligence Pathway</h1>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class='mode-card fade-in'>
            <div style='padding: 2rem 0;'>
                <div style='font-size:4.5rem; margin-bottom:2rem;'>📚</div>
                <h2 style='color:var(--blue); margin-bottom:0.5rem; font-size:2rem !important;'>Evaluation Hub</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀  Launch Evaluation Hub", type="primary", use_container_width=True, key="enter_hub"):
            st.session_state.app_mode = "Option 1"
            st.rerun()

    with col2:
        st.markdown("""
        <div class='mode-card fade-in'>
            <div style='padding: 2rem 0;'>
                <div style='font-size:4.5rem; margin-bottom:2rem;'>📉</div>
                <h2 style='color:var(--green); margin-bottom:0.5rem; font-size:2rem !important;'>Analytics Matrix</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊  Launch Analytics Matrix", type="primary", use_container_width=True, key="enter_dashboard"):
            st.session_state.app_mode = "Option 2"
            if "option2_animation_shown" in st.session_state:
                del st.session_state.option2_animation_shown
            st.rerun()


def fetch_student_profile(student_id):
    """Fetch complete student profile from SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Basic student data
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return None
        
    # Feedback history
    cursor.execute("SELECT * FROM feedback WHERE student_id = ?", (student_id,))
    feedback = cursor.fetchall()
    
    # Recommendations
    cursor.execute("SELECT * FROM recommendations WHERE student_id = ?", (student_id,))
    recommendations = cursor.fetchall()
    
    # Adaptivity logs
    cursor.execute("SELECT * FROM adaptivity_log WHERE student_id = ?", (student_id,))
    adaptivity = cursor.fetchall()
    
    conn.close()
    
    return {
        "profile": student,
        "feedback": feedback,
        "recommendations": recommendations,
        "adaptivity": adaptivity
    }


def run_student_evaluation_hub():
    """Option 1: The learning journey and quiz evaluation flow."""
    if "student_session" not in st.session_state:
        st.session_state.student_session = {
            "student_id": None,
            "current_step": "Login",
            "completed_modules": [],
            "scores": {},
            "assignments": {},
            "assignment_scores": {},
            "start_time": pd.Timestamp.now(),
            "module_times": {}
        }
    
    sess = st.session_state.student_session
    
    # Context-aware Back button
    if st.sidebar.button("← Back"):
        if sess["current_step"] == "Quiz":
            sess["current_step"] = "Learning"
        elif sess["current_step"] == "Learning":
            sess["current_step"] = "Login"
        else:
            st.session_state.app_mode = "Landing"
        st.rerun()

    if sess["current_step"] == "Login":
        st.markdown("""
        <div class='login-card fade-in'>
            <div style='font-size:4.5rem; margin-bottom:2rem;'>👤</div>
            <h2 style='margin-bottom:2.5rem;'>Student Evaluation Access</h2>
            <div style='text-align:left;'>
        """, unsafe_allow_html=True)
        _, center, _ = st.columns([1, 2, 1])
        with center:
            student_id_input = st.text_input("Student ID", placeholder="e.g. 1001", key="student_login_id", label_visibility="collapsed")
            st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
            if st.button("Initialize Evaluation Sequence  →", type="primary", use_container_width=True):
                if student_id_input:
                    try:
                        # Try to fetch existing profile
                        profile_data = fetch_student_profile(int(student_id_input))
                        if profile_data:
                            sess["student_id"] = student_id_input
                            sess["profile_data"] = profile_data
                            st.success(f"Welcome back, {profile_data['profile'][1]}!")
                        else:
                            sess["student_id"] = student_id_input
                            sess["profile_data"] = None
                            st.info("New student detected. Creating session...")
                        
                        sess["current_step"] = "Learning"
                        st.rerun()
                    except ValueError:
                        st.error("Please enter a numeric Student ID.")
                else:
                    st.warning("Please enter a valid Student ID.")
        st.markdown("</div></div>", unsafe_allow_html=True)

    elif sess["current_step"] == "Learning":
        completed = len(sess["completed_modules"])
        total = len(VIDEO_MODULES)
        pct = int((completed / total) * 100)
        st.markdown(f"""
        <div class='hub-header'>
            <div style='font-size:0.78rem; font-weight:800; color:#4f9eff; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.4rem;'>Learning Journey</div>
            <h2 style='margin-bottom:1.5rem;'>Welcome, Student #{sess['student_id']}</h2>
            <div style='display:flex; justify-content:space-between; font-size:0.85rem; color:rgba(200,210,240,0.65); margin-bottom:0.3rem;'>
                <span>{completed} of {total} modules completed</span><span>{pct}%</span>
            </div>
            <div class='progress-bar-wrap'>
                <div style='height:6px; border-radius:999px; background:linear-gradient(90deg,#4f9eff,#a78bfa); width:{pct}%;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(2)
        for i, mod in enumerate(VIDEO_MODULES):
            is_done = mod["id"] in sess["completed_modules"]
            score_text = f"Score: {sess['scores'].get(mod['id'], '-')}/15" if is_done else ""
            with cols[i % 2]:
                st.markdown(f"""<div class='video-card'>
<div style='font-size:0.75rem; font-weight:800; color:#4f9eff; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.4rem;'>Module {mod['id']}</div>
<div style='font-size:1.1rem; font-weight:800; color:#f0f4ff; margin-bottom:0.7rem;'>{mod['title']}</div>
<span class='{'badge-done' if is_done else 'badge-pending'}'>{'✅ Completed' if is_done else '⏳ Pending'}</span>
{'&nbsp;&nbsp;<span style="color:rgba(200,210,240,0.6);font-size:0.85rem;">' + score_text + '</span>' if score_text else ''}
<div style='margin-top:0.5rem; color:rgba(200,210,240,0.5); font-size:0.82rem;'>⏱ {mod['duration']}</div>
</div>""", unsafe_allow_html=True)
                btn_label = "✅ Review Module" if is_done else f"▶  Start Module {mod['id']}"
                if st.button(btn_label, key=f"btn_mod_{mod['id']}", use_container_width=True):
                    sess["active_module"] = mod
                    sess["module_start_time"] = pd.Timestamp.now()
                    sess["current_step"] = "Quiz"
                    st.rerun()

        if len(sess["completed_modules"]) > 0:
            if len(sess["completed_modules"]) == len(VIDEO_MODULES):
                st.markdown("""
                <div style='background:linear-gradient(135deg,rgba(61,214,140,0.08),rgba(79,158,255,0.08)); border:1px solid rgba(61,214,140,0.25); border-radius:14px; padding:2rem; text-align:center; margin-top:1.5rem;'>
                    <div style='font-size:2rem; margin-bottom:0.5rem;'>🎉</div>
                    <h3 style='color:#3dd68c; margin-bottom:0.4rem;'>All Modules Completed!</h3>
                    <p style='color:rgba(200,210,240,0.65); font-size:0.95rem;'>Your performance data is ready. Generate and download your evaluation report.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
            _, center, _ = st.columns([1, 2, 1])
            with center:
                btn_label = "📊  Generate & Export Evaluation Excel" if len(sess["completed_modules"]) == len(VIDEO_MODULES) else "📊  Submit Evaluation Early"
                if st.button(btn_label, type="primary", use_container_width=True):
                    export_student_data_to_excel(sess)
                    sess["current_step"] = "Finished"
                    st.rerun()

    elif sess["current_step"] == "Quiz":
        mod = sess["active_module"]
        st.markdown(f"""
        <div style='margin-bottom:1.5rem;'>
            <div style='font-size:0.78rem; font-weight:800; color:#4f9eff; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;'>Module {mod['id']} Learning Hub</div>
            <h2 style='margin-bottom:0;'>{mod['title']}</h2>
        </div>
        """, unsafe_allow_html=True)

        # Video Player with Dropout Tracking
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp_seconds FROM dropout_analysis WHERE video_id = ? AND is_critical_point = 1", (mod['id'],))
        critical_points = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Streamlit Player
        st_player(mod["url"], key=f"player_{mod['id']}")
        
        # Track time based on real-world duration since entering module
        if "module_entry_time" not in sess:
            sess["module_entry_time"] = pd.Timestamp.now()
            
        elapsed_seconds = (pd.Timestamp.now() - sess["module_entry_time"]).total_seconds()
        current_time = int(elapsed_seconds)
        
        # Check if this module was a recommendation
        if "recs_checked" not in sess:
            sess["recs_checked"] = []
        
        if mod['id'] not in sess["recs_checked"]:
            conn = get_connection()
            cursor = conn.cursor()
            # Find a pending recommendation for this video
            cursor.execute("""
                SELECT rec_id, module_id FROM recommendations 
                WHERE student_id = ? AND recommended_video_id = ? AND status = 'pending'
            """, (sess["student_id"], mod['id']))
            rec = cursor.fetchone()
            if rec:
                rec_id, trigger_module_id = rec
                # Get the score that triggered this recommendation
                cursor.execute("SELECT quiz_score FROM students WHERE student_id = ?", (sess["student_id"],))
                # Actually, let's look at the specific score for trigger_module_id if possible
                # But our current schema is a bit simple. Let's use the session score if available
                pre_score = sess["scores"].get(trigger_module_id, 0)
                
                # Log that student started recommended module
                cursor.execute("""
                    INSERT INTO adaptivity_log (student_id, recommendation_id, action_taken, module_id, pre_score)
                    VALUES (?, ?, ?, ?, ?)
                """, (sess["student_id"], rec_id, "started_recommended_video", mod['id'], pre_score))
                # Update recommendation status
                cursor.execute("UPDATE recommendations SET status = 'completed' WHERE rec_id = ?", (rec_id,))
                conn.commit()
                st.info("🌟 You are following a personalized recommendation!")
            conn.close()
            sess["recs_checked"].append(mod['id'])

        # Knowledge Check Interruption Logic
        if "interrupted_points" not in sess:
            sess["interrupted_points"] = []
            
        for cp in critical_points:
            if current_time >= cp and cp not in sess["interrupted_points"]:
                sess["interrupted_points"].append(cp)
                st.warning(f"🚀 Knowledge Check! You've reached a critical learning point at {cp}s.")
                with st.expander("📝 Mid-Module Knowledge Check", expanded=True):
                    st.write("Quick question to ensure you're following along:")
                    q_text = f"Based on the concept discussed around {cp} seconds, what is the main takeaway?"
                    st.text_input(q_text, key=f"kc_{mod['id']}_{cp}")
                    if st.button("Continue Learning", key=f"btn_kc_{cp}"):
                        st.success("Great! Keep watching.")
                break

        with st.expander("📄  View Video Transcript"):
            st.markdown(f"<p style='color:rgba(220,228,255,0.85); line-height:1.8; font-size:0.95rem;'>{mod['transcript']}</p>", unsafe_allow_html=True)

        st.markdown("<div class='quiz-container'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom:0.3rem;'>📝 Comprehensive Final Quiz</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:rgba(200,210,240,0.65); font-size:0.9rem; margin-bottom:1.5rem;'>Answer all 15 questions based on the video content above.</p>", unsafe_allow_html=True)

        if "user_answers_cache" not in sess:
            sess["user_answers_cache"] = {}
        if mod["id"] not in sess["user_answers_cache"]:
            sess["user_answers_cache"][mod["id"]] = {}

        user_answers = {}
        for idx, q in enumerate(mod["quiz"]):
            st.markdown(f"<div style='font-size:0.78rem; font-weight:700; color:#4f9eff; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.2rem;'>Question {idx+1} of 15</div>", unsafe_allow_html=True)
            
            # Determine default index if previously answered
            default_val = sess["user_answers_cache"][mod["id"]].get(idx)
            default_index = q["options"].index(default_val) if default_val in q["options"] else None
            
            user_answers[idx] = st.radio(
                q["q"], 
                q["options"], 
                key=f"q_{mod['id']}_{idx}", 
                label_visibility="visible", 
                index=default_index
            )
            st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.06); margin:0.8rem 0;'>", unsafe_allow_html=True)

        # Feedback Section
        st.markdown("<h3 style='margin-top:2rem;'>💬 Module Feedback</h3>", unsafe_allow_html=True)
        feedback_text = st.text_area(
            "How was your learning experience?",
            placeholder="Share your thoughts about this module, video, or learning experience...",
            max_chars=500,
            key=f"feedback_{mod['id']}"
        )

        if st.button("✅  Submit Quiz & Feedback", type="primary", use_container_width=True):
            if any(ans is None for ans in user_answers.values()):
                st.error("Please answer all 15 questions before submitting.")
            else:
                score = sum(1 for i, q in enumerate(mod["quiz"]) if user_answers[i] == q["a"])
                sess["scores"][mod["id"]] = score
                sess["user_answers_cache"][mod["id"]] = user_answers
                if mod["id"] not in sess["completed_modules"]:
                    sess["completed_modules"].append(mod["id"])
                
                # Analyze Sentiment
                sentiment_score, sentiment_label = analyze_sentiment(feedback_text)
                
                # Save Feedback to DB
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO feedback (student_id, module_id, feedback_text, sentiment_score, sentiment_label)
                    VALUES (?, ?, ?, ?, ?)
                """, (sess["student_id"], mod["id"], feedback_text, sentiment_score, sentiment_label))
                
                # Check if this was a recommended module and update post_score
                cursor.execute("""
                    UPDATE adaptivity_log 
                    SET post_score = ? 
                    WHERE student_id = ? AND module_id = ? AND post_score IS NULL
                """, (score, sess["student_id"], mod["id"]))
                
                conn.commit()
                conn.close()
                
                # Generate Personalized Recommendations
                recs = generate_recommendations(sess["student_id"], mod["id"], (score/15)*100, sentiment_label)
                sess["last_recs"] = recs
                
                # Calculate time spent on this module
                if "module_start_time" in sess:
                    time_diff = (pd.Timestamp.now() - sess["module_start_time"]).total_seconds() / 60
                    sess["module_times"][mod["id"]] = time_diff
                
                sess["current_step"] = "Learning"
                pct = int((score / 15) * 100)
                st.success(f"🎉 Module complete! You scored **{score}/15** ({pct}%)")
                if recs:
                    st.info(f"💡 New recommendation generated: {recs[0]['text']}")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif sess["current_step"] == "Finished":
        st.balloons()
        st.markdown(f"""
        <div class='fade-in' style='text-align:center; padding:2rem 0;'>
            <div style='font-size:4.5rem; margin-bottom:1rem;'>📜</div>
            <h2 style='margin-bottom:1rem;'>Assessment Certified</h2>
        </div>
        """, unsafe_allow_html=True)
        
        render_official_report_card(sess)
        
        _, center, _ = st.columns([1, 1.5, 1])
        with center:
            st.info(f"Session data for Student **#{sess['student_id']}** is now live in the Analytics Matrix.")
            st.markdown("<h4 style='text-align:center; margin-top:2rem; color:var(--text-soft);'>Access predictive insights?</h4>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            if col_a.button("📊 Yes, Analytics Hub", type="primary", use_container_width=True):
                st.session_state.last_eval_student_id = sess["student_id"]
                st.session_state.app_mode = "Option 2"
                st.rerun()
                
            if col_b.button("🏠 No, Logout", use_container_width=True):
                st.session_state.app_mode = "Landing"
                st.rerun()


def render_official_report_card(sess):
    """Render a premium HTML report card for the student."""
    avg_score = sum(sess["scores"].values()) / (len(VIDEO_MODULES) * 15) * 100
    level = "ELITE" if avg_score > 85 else "PROFICIENT" if avg_score > 60 else "DEVELOPING"
    color = "#3dd68c" if level == "ELITE" else "#4f9eff" if level == "PROFICIENT" else "#f5c542"
    
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.03); border:2px solid {color}; border-radius:20px; padding:3rem; max-width:800px; margin:0 auto 3rem; position:relative;'>
        <div style='position:absolute; top:20px; right:20px; border:2px solid {color}; border-radius:50%; width:80px; height:80px; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:900; color:{color}; transform:rotate(15deg);'>AI CERTIFIED</div>
        <div style='font-family:serif; font-size:1.5rem; color:var(--text-muted); text-align:center; margin-bottom:2rem;'>Official Performance Statement</div>
        <div style='text-align:center; margin-bottom:3rem;'>
            <div style='font-size:0.9rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.2em;'>This certifies that Student</div>
            <div style='font-size:2.5rem; font-weight:900; color:#fff; margin:0.5rem 0;'>#{sess['student_id']}</div>
            <div style='font-size:0.9rem; color:var(--text-muted);'>has successfully finalized the EduGrowth Intelligence Evaluation.</div>
        </div>
        <table style='width:100%; border-collapse:collapse; margin-bottom:2rem;'>
            <tr style='border-bottom:1px solid rgba(255,255,255,0.1);'>
                <td style='padding:1rem 0; color:var(--text-muted);'>Academic Efficiency</td>
                <td style='padding:1rem 0; text-align:right; font-weight:800; color:#fff;'>{avg_score:.1f}%</td>
            </tr>
            <tr style='border-bottom:1px solid rgba(255,255,255,0.1);'>
                <td style='padding:1rem 0; color:var(--text-muted);'>Interaction Level</td>
                <td style='padding:1rem 0; text-align:right; font-weight:800; color:#fff;'>ACTIVE</td>
            </tr>
            <tr style='border-bottom:1px solid rgba(255,255,255,0.1);'>
                <td style='padding:1rem 0; color:var(--text-muted);'>Classification</td>
                <td style='padding:1rem 0; text-align:right; font-weight:800; color:{color};'>{level}</td>
            </tr>
        </table>
        <div style='text-align:center; font-size:0.8rem; color:var(--text-muted);'>Issued by EduGrowth AI Engine • {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</div>
    </div>
    """, unsafe_allow_html=True)


def export_student_data_to_excel(sess):
    """Map results to model variables and export as per promp.txt."""
    total_quiz_score = sum(sess["scores"].values())
    avg_quiz_score = (total_quiz_score / (len(VIDEO_MODULES) * 15)) * 100
    
    # Mock assignment score for model compatibility
    avg_assign_score = 100.0
    
    total_time = sum(sess["module_times"].values())
    
    # Feature Engineering for Prediction Model
    # Feature Engineering for Prediction Model
    try:
        int_id = int(sess["student_id"])
    except ValueError:
        int_id = 999999 # Fallback if they entered non-numeric

    # Learning Velocity (Modules per Hour)
    velocity = len(sess["completed_modules"]) / (total_time / 60) if total_time > 0 else 0
    
    data = {
        "student_id": [int_id],
        "region": ["Urban"],
        "time_spent": [total_time],
        "modules_completed": [len(sess["completed_modules"])],
        "quiz_score": [avg_quiz_score],
        "assignment_timeliness": [avg_assign_score],
        "interaction_level": [85.0 + (len(sess["completed_modules"]) * 2)],
        "consistency_index": [0.9 if avg_quiz_score > 70 else 0.7],
        "engagement_score": [avg_quiz_score * 0.4 + avg_assign_score * 0.6],
        "learning_trend": ["Increasing" if avg_quiz_score > 60 else "Stable"],
        "learning_velocity": [velocity],
        "timestamp": [pd.Timestamp.now()]
    }
    
    df_new = pd.DataFrame(data)
    
    # Excel Automation (.xlsx)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_new.to_excel(writer, index=False, sheet_name='Performance_Report')
        # Add a detailed sheet
        details = []
        for mod in VIDEO_MODULES:
            details.append({
                "Module ID": mod["id"],
                "Title": mod["title"],
                "Quiz Score": sess["scores"].get(mod["id"], 0),
                "Time Spent (min)": round(sess["module_times"].get(mod["id"], 0), 2)
            })
        pd.DataFrame(details).to_excel(writer, index=False, sheet_name='Module_Details')
    
    st.download_button(
        label="📥 Download Performance Report (.xlsx)",
        data=output.getvalue(),
        file_name=f"Student_{int_id}_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Automate integration with the Prediction DB
    try:
        import os
        if os.path.exists(DATA_PATH):
            main_db = pd.read_csv(DATA_PATH)
            # Remove old entry if student is retaking
            main_db = main_db[main_db["student_id"] != int_id]
            
            # Match columns exactly
            append_df = df_new.drop(columns=["timestamp"], errors="ignore")
            main_db = pd.concat([main_db, append_df], ignore_index=True)
            main_db.to_csv(DATA_PATH, index=False)
            
            # Clear Streamlit cache so Option 2 loads the fresh DB immediately
            load_data.clear()
    except Exception as e:
        st.error(f"Failed to sync with Prediction DB: {e}")

    # Save locally for Option 2 reflection
    df_new.to_csv(f"eval_student_{int_id}.csv", index=False)
    st.session_state.last_eval_student_id = int_id


def render_startup_loader():
    """Show a first-load black screen with a centered animated learning icon."""
    st.markdown(
        """
        <style>
        .startup-loader {
            position: fixed;
            inset: 0;
            z-index: 999999;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: rgba(5, 7, 11, 0.7);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            animation: loaderFade 0.8s ease forwards;
            animation-delay: 2.2s;
        }
        .loader-text {
            margin-top: 1.5rem;
            color: var(--blue);
            font-size: 1.1rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            animation: markPulse 1.1s ease-in-out infinite;
        }
        .loader-mark {
            position: relative;
            width: 76px;
            height: 76px;
            animation: markPulse 1.1s ease-in-out infinite;
        }
        .loader-dot {
            position: absolute;
            top: 13px;
            left: 28px;
            width: 9px;
            height: 9px;
            border-radius: 999px;
            background: #a8abb2;
        }
        .loader-body {
            position: absolute;
            top: 25px;
            left: 23px;
            width: 24px;
            height: 5px;
            border-radius: 999px;
            background: #a8abb2;
            transform: rotate(35deg);
            transform-origin: left center;
        }
        .loader-arm {
            position: absolute;
            top: 19px;
            left: 39px;
            width: 17px;
            height: 5px;
            border-radius: 999px;
            background: #a8abb2;
            transform: rotate(-48deg);
            transform-origin: left center;
        }
        .loader-waves {
            position: absolute;
            left: 17px;
            right: 13px;
            bottom: 17px;
        }
        .loader-waves span {
            display: block;
            height: 4px;
            margin: 5px 0;
            border-radius: 999px;
            background: #8d9097;
            transform-origin: center;
            animation: waveMove 0.9s ease-in-out infinite;
        }
        .loader-waves span:nth-child(2) {
            animation-delay: 0.13s;
            opacity: 0.82;
        }
        .loader-waves span:nth-child(3) {
            animation-delay: 0.26s;
            opacity: 0.68;
        }
        @keyframes waveMove {
            0%, 100% {
                transform: scaleX(0.78) translateX(-3px);
            }
            50% {
                transform: scaleX(1) translateX(4px);
            }
        }
        @keyframes markPulse {
            0%, 100% {
                transform: translateY(0);
                opacity: 0.78;
            }
            50% {
                transform: translateY(-3px);
                opacity: 1;
            }
        }
        @keyframes loaderFade {
            to {
                opacity: 0;
                visibility: hidden;
                pointer-events: none;
            }
        }
        </style>
        <div class="startup-loader">
            <div class="loader-mark" aria-label="Loading dashboard">
                <div class="loader-dot"></div>
                <div class="loader-body"></div>
                <div class="loader-arm"></div>
                <div class="loader-waves">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
            <div class="loader-text">Initializing AI Intelligence...</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def load_model(model_name):
    """Load the selected trained model."""
    return joblib.load(MODEL_PATHS[model_name])


@st.cache_resource
def load_artifacts():
    """Load preprocessing artifacts used during training."""
    scaler = joblib.load("scaler.pkl")
    label_encoder = joblib.load("label_encoder.pkl")
    columns = joblib.load("columns.pkl")
    return scaler, label_encoder, columns


@st.cache_data
def load_data():
    """Load student dataset."""
    return pd.read_csv(DATA_PATH)


def load_active_dataset(papaparse_data=None):
    """Load the primary student dataset with Demo Mode fallback."""
    if papaparse_data:
        df = pd.DataFrame(papaparse_data)
        return df, "📂 Custom Uploaded Dataset", "custom"
    
    # Check for existing sync file
    import os
    if os.path.exists("synthetic_student_data.csv"):
        try:
            df = pd.read_csv("synthetic_student_data.csv")
            return df, "📊 Active Student Database (Synced)", "synced"
        except:
            pass

    # Demo Mode Fallback
    st.sidebar.warning("🛠️ Demo Mode Active: No dataset uploaded.")
    demo_data = []
    for i in range(100):
        demo_data.append({
            "student_id": 20001 + i,
            "region": "Urban",
            "time_spent": 10.0 + (i % 5),
            "modules_completed": 4,
            "quiz_score": 75.0 + (i % 25),
            "assignment_timeliness": 85.0 + (i % 15),
            "interaction_level": 70.0 + (i % 30),
            "consistency_index": 0.85,
            "engagement_score": 80.0,
            "learning_trend": "Increasing"
        })
    return pd.DataFrame(demo_data), "✨ Institutional Demo Dataset (Auto-Generated)", "demo"


def validate_dataset(df):
    """Return missing required columns for dashboard and prediction use."""
    return [column for column in REQUIRED_DATA_COLUMNS if column not in df.columns]


def prepare_dataset_for_dashboard(df, model, scaler, label_encoder, columns):
    """Prepare an uploaded dataset and add predicted labels when needed."""
    prepared_df = df.copy()
    prepared_df["student_id"] = pd.to_numeric(prepared_df["student_id"], errors="raise").astype(int)

    if "performance_label" not in prepared_df.columns:
        feature_data = prepared_df.drop(columns=["performance_label"], errors="ignore")
        feature_data = pd.get_dummies(feature_data)
        feature_data = feature_data.reindex(columns=columns, fill_value=0)
        feature_data_scaled = scaler.transform(feature_data)
        predictions = model.predict(feature_data_scaled)
        prepared_df["performance_label"] = label_encoder.inverse_transform(predictions)
        prepared_df["label_source"] = "Predicted"
    else:
        prepared_df["label_source"] = "Dataset"

    return prepared_df


def predict_student(student_row, model, scaler, label_encoder, columns):
    """Preprocess a student row and predict the performance label."""
    data = student_row.drop(columns=["performance_label"], errors="ignore")
    data = pd.get_dummies(data)
    data = data.reindex(columns=columns, fill_value=0)
    data_scaled = scaler.transform(data)

    prediction = model.predict(data_scaled)
    return label_encoder.inverse_transform(prediction)[0]


def get_recommendation(label, row):
    """Generate rule-based recommendations and risk factors."""
    recommendations = []
    risk_factors = []

    if label == "Low":
        recommendations.append(
            "Focus on fundamentals, revise core concepts regularly, and practice basic problems."
        )
        recommendations.append("Start with one topic per day and complete a short quiz after every revision session.")
        recommendations.append("Ask for help early on difficult chapters instead of waiting until the next assessment.")
    elif label == "Medium":
        recommendations.append(
            "Improve weak areas with targeted practice and review recent quiz mistakes."
        )
        recommendations.append("Convert recent mistakes into a checklist and revise them twice a week.")
        recommendations.append("Attempt mixed-difficulty questions to move from average performance to high performance.")
    elif label == "High":
        recommendations.append(
            "Maintain your current learning rhythm and explore advanced learning materials."
        )
        recommendations.append("Practice higher-order application questions to strengthen long-term retention.")
        recommendations.append("Support peers or explain concepts aloud to reinforce your own understanding.")

    if row.get("consistency_index", 1) < 0.5:
        recommendations.append("Build a consistent daily study routine with short revision blocks.")
        recommendations.append("Use a fixed study slot and track completion for the next seven days.")
        risk_factors.append("Low consistency: consistency index is below 0.5.")
    elif row.get("consistency_index", 0) >= 0.75:
        recommendations.append("Your consistency is strong. Keep the same routine and avoid last-minute study spikes.")

    if row.get("quiz_score", 100) < 60:
        recommendations.append("Strengthen concept clarity and solve more quiz-style questions.")
        recommendations.append("Reattempt incorrect quiz questions after 24 hours to check whether concepts are retained.")
        recommendations.append("Spend 15 minutes daily on formulae, definitions, and core examples.")
        risk_factors.append("Low quiz score: quiz score is below 60.")
    elif row.get("quiz_score", 0) < 75:
        recommendations.append("Improve quiz accuracy by practicing timed quizzes and reviewing explanations immediately.")
    elif row.get("quiz_score", 0) >= 85:
        recommendations.append("Quiz performance is excellent. Move to advanced problem sets and challenge tests.")

    if row.get("interaction_level", 100) < 50:
        recommendations.append("Increase engagement through discussions, doubt clearing, and group learning.")
        recommendations.append("Participate in at least one class discussion or peer session each week.")
        risk_factors.append("Low engagement: interaction level is below 50.")
    elif row.get("interaction_level", 0) >= 80:
        recommendations.append("Your interaction level is healthy. Continue asking questions and sharing answers.")

    if row.get("engagement_score", 100) < 50:
        recommendations.append("Engagement is low. Break study sessions into smaller goals with visible progress tracking.")
        risk_factors.append("Low engagement score: engagement score is below 50.")
    elif row.get("engagement_score", 0) >= 80:
        recommendations.append("Engagement score is strong. Maintain active participation and regular practice.")

    if row.get("assignment_timeliness", 100) < 60:
        recommendations.append("Submit assignments earlier by splitting them into planning, drafting, and review stages.")
        risk_factors.append("Assignment delay risk: assignment timeliness is below 60.")
    elif row.get("assignment_timeliness", 0) >= 85:
        recommendations.append("Assignment timeliness is excellent. Keep using your current submission routine.")

    if row.get("modules_completed", 0) < 4:
        recommendations.append("Complete pending modules in order before moving to advanced topics.")
        recommendations.append("Set a target of finishing at least two modules this week.")
        risk_factors.append("Low module completion: fewer than 4 modules completed.")
    elif row.get("modules_completed", 0) >= 8:
        recommendations.append("Module completion is strong. Start revising completed modules to avoid forgetting.")

    if row.get("learning_trend") == "Decreasing":
        recommendations.append("Review recent topics because the learning trend is declining.")
        recommendations.append("Compare the last three weak topics and identify whether the issue is speed, accuracy, or understanding.")
        recommendations.append("Schedule a mentor or teacher check-in to stop the downward trend early.")
        risk_factors.append("Declining trend: learning trend is decreasing.")
    elif row.get("learning_trend") == "Stable":
        recommendations.append("Learning trend is stable. Add small weekly goals to create upward progress.")
    elif row.get("learning_trend") == "Increasing":
        recommendations.append("Learning trend is improving. Keep the same strategy and gradually raise difficulty.")

    if row.get("time_spent", 0) > 10 and row.get("quiz_score", 100) < 60:
        recommendations.append(
            "High study time with low quiz output suggests you should revise your study strategy."
        )
        recommendations.append("Use active recall instead of rereading notes for long study sessions.")
        recommendations.append("After every 30 minutes of study, solve 3-5 questions to test understanding.")

    if row.get("time_spent", 999) < 4 and row.get("quiz_score", 0) > 80:
        recommendations.append("You are learning efficiently; consider adding advanced topics.")
        recommendations.append("Keep short study sessions, but add spaced revision so performance remains consistent.")

    if row.get("time_spent", 0) < 4 and row.get("quiz_score", 0) < 60:
        recommendations.append("Increase study time gradually, starting with one focused 30-minute block daily.")
        risk_factors.append("Low effort risk: low time spent and low quiz score.")

    recommendations.append("Weekly plan: revise weak topics on Monday-Wednesday, practice quizzes on Thursday-Friday, and review mistakes on the weekend.")
    recommendations.append("Track quiz score, study time, and consistency every week to measure improvement.")

    return {
        "recommendations": list(dict.fromkeys(recommendations)),
        "risks": list(dict.fromkeys(risk_factors)),
    }


def analyze_quiz_performance(row):
    """Analyze quiz score category and learning efficiency."""
    quiz_score = float(row.get("quiz_score", 0))
    time_spent = float(row.get("time_spent", 0))

    if quiz_score < 50:
        category = "Poor performance"
        insight = "The quiz score shows major gaps in concept understanding. Focus on basics and guided practice."
    elif quiz_score <= 70:
        category = "Average performance"
        insight = "The quiz score is acceptable but needs improvement through revision and topic-wise practice."
    elif quiz_score <= 85:
        category = "Good performance"
        insight = "The quiz score is strong. Keep practicing and work on small weak areas."
    else:
        category = "Excellent performance"
        insight = "The quiz score is excellent. Maintain consistency and attempt advanced questions."

    interpretation = "Learning efficiency appears balanced."
    if time_spent > 10 and quiz_score < 60:
        interpretation = "Inefficient learning: high time spent but low quiz score. Improve study strategy."
    elif time_spent < 4 and quiz_score > 80:
        interpretation = "High efficiency: low time spent with a high quiz score."

    return {
        "score": quiz_score,
        "category": category,
        "insight": insight,
        "interpretation": interpretation,
    }


def quiz_category_from_score(score):
    """Return quiz category for chart grouping."""
    if score < 50:
        return "Poor"
    if score <= 70:
        return "Average"
    if score <= 85:
        return "Good"
    return "Excellent"


def clamp_score(value, lower=0, upper=100):
    """Keep a score inside display limits."""
    return max(lower, min(float(value), upper))


def score_status(score):
    """Return label and CSS class for a score."""
    if score >= 75:
        return "Strong", "status-good"
    if score >= 55:
        return "Watch", "status-watch"
    return "Needs Attention", "status-risk"


def performance_status_class(label):
    """Return a visual status class for a performance label."""
    if label == "High":
        return "status-good"
    if label == "Medium":
        return "status-watch"
    return "status-risk"


def calculate_profile_health(row):
    """Calculate a normalized profile health score."""
    scores = [
        clamp_score(row.get("quiz_score", 0)),
        clamp_score(row.get("assignment_timeliness", 0)),
        clamp_score(row.get("interaction_level", 0)),
        clamp_score(row.get("engagement_score", 0)),
        clamp_score(row.get("consistency_index", 0) * 100),
        clamp_score(row.get("modules_completed", 0) * 10),
    ]
    return round(sum(scores) / len(scores), 1)


def profile_card(label, value, note, status_class):
    """Render a compact dashboard card."""
    status_label = str(note).split(":")[0]
    st.markdown(
        f"""
        <div class="profile-card">
            <div class="profile-card-label">{escape_html(label)}</div>
            <div class="profile-card-value">{escape_html(value)}</div>
            <div class="profile-card-note">{escape_html(note)}</div>
            <span class="status-pill {status_class}">{escape_html(status_label)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_profile_strengths_and_attention(row, prediction):
    """Identify useful strengths and attention areas for the profile dashboard."""
    strengths = []
    attention = []

    if row.get("quiz_score", 0) >= 75:
        strengths.append("Quiz performance is supporting the current prediction.")
    elif row.get("quiz_score", 0) < 60:
        attention.append("Quiz score needs concept revision and timed practice.")

    if row.get("interaction_level", 0) >= 80:
        strengths.append("Interaction level shows strong participation.")
    elif row.get("interaction_level", 100) < 50:
        attention.append("Interaction level is low; participation should increase.")

    if row.get("modules_completed", 0) >= 8:
        strengths.append("Module completion is strong.")
    elif row.get("modules_completed", 0) < 4:
        attention.append("Module completion is behind schedule.")

    if row.get("assignment_timeliness", 100) < 60:
        attention.append("Assignment timeliness needs immediate improvement.")
    elif row.get("assignment_timeliness", 0) >= 85:
        strengths.append("Assignments are being submitted on time.")

    if row.get("consistency_index", 1) < 0.5:
        attention.append("Consistency is the biggest study habit risk.")
    elif row.get("consistency_index", 0) >= 0.75:
        strengths.append("Consistency is a reliable learning habit.")

    if row.get("learning_trend") == "Decreasing":
        attention.append("Learning trend is declining and should be monitored this week.")
    elif row.get("learning_trend") == "Increasing":
        strengths.append("Learning trend is improving.")

    if prediction == "High":
        strengths.append("Predicted performance is high; advanced practice is suitable.")
    elif prediction == "Low":
        attention.append("Predicted performance is low; focus on fundamentals first.")

    return strengths[:4], attention[:4]


def show_student_profile(row, prediction, model_name):
    """Display a professional student profile dashboard."""
    health_score = calculate_profile_health(row)
    health_status, health_class = score_status(health_score)
    trend = row.get("learning_trend", "N/A")
    actual_performance = row.get("performance_label", "N/A")
    prediction_class = performance_status_class(prediction)

    st.markdown(
        f"""
        <div class="profile-hero">
            <div class="profile-row">
                <div>
                    <div class="profile-name">Student #{int(row.get("student_id", 0))}</div>
                    <div class="profile-meta">
                        Region: {escape_html(row.get("region", "N/A"))} &nbsp;|&nbsp;
                        Model: {escape_html(model_name)} &nbsp;|&nbsp;
                        Actual: {escape_html(actual_performance)}
                    </div>
                    <span class="status-pill {health_class}">Profile Health: {escape_html(health_status)}</span>
                    <span class="status-pill status-watch">Trend: {escape_html(trend)}</span>
                    <span class="status-pill {prediction_class}">Prediction: {escape_html(prediction)}</span>
                </div>
                <div class="profile-score">
                    <div class="profile-meta">Overall Profile Health</div>
                    <div class="profile-score-value">{health_score:.1f}%</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(int(round(health_score)))

    quiz_status, quiz_class = score_status(row.get("quiz_score", 0))
    assignment_status, assignment_class = score_status(row.get("assignment_timeliness", 0))
    engagement_status, engagement_class = score_status(row.get("engagement_score", 0))
    consistency_status, consistency_class = score_status(row.get("consistency_index", 0) * 100)

    card_cols = st.columns(4)
    with card_cols[0]:
        profile_card("Quiz Score", f"{float(row.get('quiz_score', 0)):.2f}", f"{quiz_status}: assessment output", quiz_class)
    with card_cols[1]:
        profile_card(
            "Assignment Timeliness",
            f"{float(row.get('assignment_timeliness', 0)):.2f}",
            f"{assignment_status}: submission habit",
            assignment_class,
        )
    with card_cols[2]:
        profile_card(
            "Engagement Score",
            f"{float(row.get('engagement_score', 0)):.2f}",
            f"{engagement_status}: learning activity",
            engagement_class,
        )
    with card_cols[3]:
        profile_card(
            "Consistency",
            f"{float(row.get('consistency_index', 0)):.2f}",
            f"{consistency_status}: study regularity",
            consistency_class,
        )

    left_col, right_col = st.columns([1.15, 1])
    with left_col:
        st.subheader("Profile Health Breakdown")
        profile_metrics = build_student_metrics(row)
        profile_metrics.loc[len(profile_metrics)] = {
            "Metric": "Module Progress",
            "Score": clamp_score(row.get("modules_completed", 0) * 10),
        }
        chart = (
            alt.Chart(profile_metrics)
            .mark_bar(cornerRadiusEnd=4)
            .encode(
                x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 100]), title="Score"),
                y=alt.Y("Metric:N", sort="-x", title=None),
                color=alt.Color("Score:Q", scale=alt.Scale(scheme="redyellowgreen"), legend=None),
                tooltip=["Metric", alt.Tooltip("Score:Q", format=".2f")],
            )
            .properties(height=310)
        )
        st.altair_chart(chart, use_container_width=True)

    with right_col:
        st.subheader("Profile Snapshot")
        snapshot = pd.DataFrame(
            [
                {"Attribute": "Region", "Value": row.get("region", "N/A")},
                {"Attribute": "Learning Trend", "Value": trend},
                {"Attribute": "Time Spent", "Value": f"{float(row.get('time_spent', 0)):.2f} hours"},
                {"Attribute": "Modules Completed", "Value": int(row.get("modules_completed", 0))},
                {"Attribute": "Interaction Level", "Value": f"{float(row.get('interaction_level', 0)):.2f}"},
                {"Attribute": "Predicted Performance", "Value": prediction},
            ]
        )
        st.dataframe(snapshot, use_container_width=True, hide_index=True)

    strengths, attention = get_profile_strengths_and_attention(row, prediction)
    
    st.markdown("<div class='command-center'>", unsafe_allow_html=True)
    
    strength_col, attention_col = st.columns(2)
    with strength_col:
        st.subheader("Strengths")
        if strengths:
            for item in strengths:
                st.success(item)
        else:
            st.info("No major strengths detected yet. Focus on building consistency first.")
            
    with attention_col:
        st.subheader("Attention Areas")
        if attention:
            for item in attention:
                st.warning(item)
        else:
            st.success("No urgent attention areas detected.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    radar_col, narrative_col = st.columns([1, 1.2])
    
    with radar_col:
        st.subheader("Competency Matrix")
        render_performance_radar(row)
        
    with narrative_col:
        st.subheader("AI Smart Narrative")
        render_narrative_summary(row, prediction)


def show_quiz_analysis(row, quiz_analysis):
    """Display quiz analysis in a denser dashboard layout."""
    progress_value = max(0, min(int(round(quiz_analysis["score"])), 100))

    score_col, category_col, time_col, efficiency_col = st.columns([1, 1.25, 1, 1.5])
    score_col.metric("Quiz Score", f"{quiz_analysis['score']:.2f}")
    category_col.metric("Quiz Category", quiz_analysis["category"])
    time_col.metric("Time Spent", f"{format_value(row.get('time_spent', 0))} hours")
    efficiency_col.metric("Efficiency", quiz_analysis["interpretation"].split(":")[0])

    st.progress(progress_value)

    insight_col, interpretation_col = st.columns(2)
    with insight_col:
        st.info(quiz_analysis["insight"])
    with interpretation_col:
        st.info(quiz_analysis["interpretation"])

    st.subheader("Quiz What-If Simulator")
    simulated_score = st.slider(
        "Try a different quiz score",
        min_value=0,
        max_value=100,
        value=progress_value,
        step=1,
    )
    simulated_row = row.copy()
    simulated_row["quiz_score"] = simulated_score
    simulated_analysis = analyze_quiz_performance(simulated_row)

    sim_score_col, sim_category_col, sim_efficiency_col = st.columns(3)
    sim_score_col.metric("Simulated Score", f"{simulated_score:.0f}")
    sim_category_col.metric("New Category", simulated_analysis["category"])
    sim_efficiency_col.metric("Efficiency Signal", simulated_analysis["interpretation"].split(":")[0])
    st.info(simulated_analysis["insight"])


def get_percentile(series, value):
    """Return percentile rank for a value within a numeric series."""
    numeric_series = pd.to_numeric(series, errors="coerce").dropna()
    if numeric_series.empty:
        return 0.0
    return float((numeric_series <= value).mean() * 100)


def build_student_metrics(row):
    """Create normalized metrics for selected-student charts."""
    return pd.DataFrame(
        {
            "Metric": [
                "Quiz Score",
                "Assignment Timeliness",
                "Interaction Level",
                "Engagement Score",
                "Consistency Index",
            ],
            "Score": [
                float(row.get("quiz_score", 0)),
                float(row.get("assignment_timeliness", 0)),
                float(row.get("interaction_level", 0)),
                float(row.get("engagement_score", 0)),
                float(row.get("consistency_index", 0)) * 100,
            ],
        }
    )


def show_charts(df, row):
    """Display interactive charts for the selected student and overall dataset."""
    st.subheader("Interactive Analytics")
    st.markdown(
        '<div class="section-kicker">Filter the cohort, compare the selected learner to peers, and inspect distribution patterns. 💡 <i>Tip: Percentiles show where you stand relative to the current group.</i></div>',
        unsafe_allow_html=True,
    )

    filter_col, trend_col, label_col = st.columns(3)
    region_options = ["All"] + sorted(df["region"].dropna().unique().tolist())
    trend_options = ["All"] + sorted(df["learning_trend"].dropna().unique().tolist())
    label_options = ["All"] + sorted(df["performance_label"].dropna().unique().tolist())

    selected_region = filter_col.selectbox("Filter by Region", region_options)
    selected_trend = trend_col.selectbox("Filter by Learning Trend", trend_options)
    selected_label = label_col.selectbox("Filter by Performance", label_options)

    filtered_df = df.copy()
    if selected_region != "All":
        filtered_df = filtered_df[filtered_df["region"] == selected_region]
    if selected_trend != "All":
        filtered_df = filtered_df[filtered_df["learning_trend"] == selected_trend]
    if selected_label != "All":
        filtered_df = filtered_df[filtered_df["performance_label"] == selected_label]

    if filtered_df.empty:
        st.warning("No records match the selected filters.")
        return
    
    # Add a distribution overlay chart
    st.subheader("Quiz Score Distribution (Cohort)")
    dist_chart = alt.Chart(filtered_df).mark_area(
        opacity=0.3,
        interpolate='monotone',
        color='#4f9eff'
    ).encode(
        x=alt.X('quiz_score:Q', bin=True, title="Quiz Score"),
        y=alt.Y('count():Q', title="Student Count")
    ).properties(height=200)
    
    # Add a line for the selected student
    student_val = float(row.get('quiz_score', 0))
    rule = alt.Chart(pd.DataFrame({'x': [student_val]})).mark_rule(color='#3dd68c', size=2).encode(x='x:Q')
    text = rule.mark_text(align='left', dx=5, dy=-80, text='Selected Student', color='#3dd68c').encode(x='x:Q')
    
    st.altair_chart(dist_chart + rule + text, use_container_width=True)

    summary_col, quiz_col, engagement_col, consistency_col = st.columns(4)
    summary_col.metric("Filtered Students", f"{len(filtered_df):,}")
    quiz_col.metric("Average Quiz", f"{filtered_df['quiz_score'].mean():.2f}")
    engagement_col.metric("Average Engagement", f"{filtered_df['engagement_score'].mean():.2f}")
    consistency_col.metric("Average Consistency", f"{filtered_df['consistency_index'].mean():.2f}")

    st.subheader("Selected Student vs Class Average")
    metric_options = [
        "quiz_score",
        "assignment_timeliness",
        "interaction_level",
        "engagement_score",
        "consistency_index",
    ]
    selected_metrics = st.multiselect(
        "Choose metrics to compare",
        metric_options,
        default=["quiz_score", "interaction_level", "engagement_score", "consistency_index"],
    )

    if selected_metrics:
        comparison_rows = []
        for metric in selected_metrics:
            student_value = float(row.get(metric, 0))
            average_value = float(filtered_df[metric].mean())
            if metric == "consistency_index":
                student_value *= 100
                average_value *= 100
            comparison_rows.append(
                {"Metric": metric.replace("_", " ").title(), "Type": "Selected Student", "Value": student_value}
            )
            comparison_rows.append(
                {"Metric": metric.replace("_", " ").title(), "Type": "Filtered Average", "Value": average_value}
            )

        comparison_df = pd.DataFrame(comparison_rows)
        comparison_chart = (
            alt.Chart(comparison_df)
            .mark_bar()
            .encode(
                x=alt.X("Metric:N", title=None),
                y=alt.Y("Value:Q", title="Score"),
                color=alt.Color("Type:N", title=None),
                xOffset="Type:N",
                tooltip=["Metric", "Type", alt.Tooltip("Value:Q", format=".2f")],
            )
            .properties(height=330)
        )
        st.altair_chart(comparison_chart, use_container_width=True)

    st.subheader("Student Percentile Context")
    percentile_cols = st.columns(4)
    percentile_cols[0].metric(
        "Quiz Percentile",
        f"{get_percentile(filtered_df['quiz_score'], float(row.get('quiz_score', 0))):.1f}%",
    )
    percentile_cols[1].metric(
        "Engagement Percentile",
        f"{get_percentile(filtered_df['engagement_score'], float(row.get('engagement_score', 0))):.1f}%",
    )
    percentile_cols[2].metric(
        "Interaction Percentile",
        f"{get_percentile(filtered_df['interaction_level'], float(row.get('interaction_level', 0))):.1f}%",
    )
    percentile_cols[3].metric(
        "Consistency Percentile",
        f"{get_percentile(filtered_df['consistency_index'], float(row.get('consistency_index', 0))):.1f}%",
    )

    chart_choice = st.selectbox(
        "Choose chart",
        [
            "Student Score Breakdown",
            "Quiz Score by Performance",
            "Time Spent vs Quiz Score",
            "Performance Label Distribution",
            "Learning Trend Distribution",
            "Quiz Category Distribution",
        ],
    )

    if chart_choice == "Student Score Breakdown":
        student_metrics = build_student_metrics(row)
        chart = (
            alt.Chart(student_metrics)
            .mark_bar()
            .encode(
                x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 100])),
                y=alt.Y("Metric:N", sort="-x", title=None),
                tooltip=["Metric", alt.Tooltip("Score:Q", format=".2f")],
            )
            .properties(height=330)
        )
        st.altair_chart(chart, use_container_width=True)

    elif chart_choice == "Quiz Score by Performance":
        chart = (
            alt.Chart(filtered_df)
            .mark_boxplot(size=55)
            .encode(
                x=alt.X("performance_label:N", title="Performance"),
                y=alt.Y("quiz_score:Q", title="Quiz Score"),
                color=alt.Color("performance_label:N", legend=None),
                tooltip=["performance_label:N", "quiz_score:Q"],
            )
            .properties(height=360)
        )
        st.altair_chart(chart, use_container_width=True)

    elif chart_choice == "Time Spent vs Quiz Score":
        plot_df = filtered_df.copy()
        plot_df["Selected Student"] = plot_df["student_id"] == row.get("student_id")
        chart = (
            alt.Chart(plot_df)
            .mark_circle(size=70, opacity=0.55)
            .encode(
                x=alt.X("time_spent:Q", title="Time Spent"),
                y=alt.Y("quiz_score:Q", title="Quiz Score"),
                color=alt.Color("performance_label:N", title="Performance"),
                shape=alt.Shape("Selected Student:N", title="Selected Student"),
                tooltip=["student_id", "time_spent", "quiz_score", "performance_label"],
            )
            .interactive()
            .properties(height=390)
        )
        st.altair_chart(chart, use_container_width=True)

    elif chart_choice == "Performance Label Distribution":
        chart_df = filtered_df["performance_label"].value_counts().reset_index()
        chart_df.columns = ["Performance", "Count"]
        chart = (
            alt.Chart(chart_df)
            .mark_bar()
            .encode(
                x=alt.X("Performance:N", title=None),
                y=alt.Y("Count:Q"),
                tooltip=["Performance", "Count"],
            )
            .properties(height=330)
        )
        st.altair_chart(chart, use_container_width=True)

    elif chart_choice == "Learning Trend Distribution":
        chart_df = filtered_df["learning_trend"].value_counts().reset_index()
        chart_df.columns = ["Learning Trend", "Count"]
        chart = (
            alt.Chart(chart_df)
            .mark_arc(innerRadius=55)
            .encode(
                theta=alt.Theta("Count:Q"),
                color=alt.Color("Learning Trend:N"),
                tooltip=["Learning Trend", "Count"],
            )
            .properties(height=360)
        )
        st.altair_chart(chart, use_container_width=True)

    else:
        chart_df = filtered_df.copy()
        chart_df["Quiz Category"] = chart_df["quiz_score"].apply(quiz_category_from_score)
        category_counts = chart_df["Quiz Category"].value_counts().reset_index()
        category_counts.columns = ["Quiz Category", "Count"]
        category_counts["Quiz Category"] = pd.Categorical(
            category_counts["Quiz Category"],
            categories=["Poor", "Average", "Good", "Excellent"],
            ordered=True,
        )
        category_counts = category_counts.sort_values("Quiz Category")
        chart = (
            alt.Chart(category_counts)
            .mark_bar()
            .encode(
                x=alt.X("Quiz Category:N", title=None, sort=["Poor", "Average", "Good", "Excellent"]),
                y=alt.Y("Count:Q"),
                tooltip=["Quiz Category", "Count"],
            )
            .properties(height=330)
        )
        st.altair_chart(chart, use_container_width=True)


def show_recommendations(recommendations):
    """Display recommendations in a readable action-list format."""
    st.metric("Total Recommendations", len(recommendations))
    for index, recommendation in enumerate(recommendations, start=1):
        st.markdown(
            f"""
            <div class="rec-item">
                <span class="rec-index">{index}</span>{escape_html(recommendation)}
            </div>
            """,
            unsafe_allow_html=True,
        )


def build_improvement_plan(row, prediction, focus_goal=None, plan_intensity="Focused"):
    """Create a focused weekly improvement plan from student metrics."""
    quiz_score = float(row.get("quiz_score", 0))
    consistency = float(row.get("consistency_index", 0))
    interaction = float(row.get("interaction_level", 0))
    assignment_timeliness = float(row.get("assignment_timeliness", 0))
    modules_completed = float(row.get("modules_completed", 0))
    learning_trend = row.get("learning_trend", "Stable")

    priority_scores = {
        "Concept Revision": max(0, 75 - quiz_score),
        "Quiz Practice": max(0, 80 - quiz_score),
        "Consistency Building": max(0, (0.75 - consistency) * 100),
        "Assignments": max(0, 80 - assignment_timeliness),
        "Engagement": max(0, 70 - interaction),
        "Module Completion": max(0, 8 - modules_completed) * 8,
    }

    if prediction == "Low":
        priority_scores["Concept Revision"] += 25
        priority_scores["Quiz Practice"] += 15
    elif prediction == "Medium":
        priority_scores["Quiz Practice"] += 15
        priority_scores["Consistency Building"] += 10
    else:
        priority_scores["Quiz Practice"] += 10
        priority_scores["Module Completion"] += 10

    if learning_trend == "Decreasing":
        priority_scores["Concept Revision"] += 15
        priority_scores["Consistency Building"] += 15

    # Map goals to internal keys
    goal_map = {
        "Improve quiz score": "Quiz Practice",
        "Build consistency": "Consistency Building",
        "Finish modules": "Module Completion",
        "Improve assignments": "Assignments",
        "Increase engagement": "Engagement",
    }

    # Automatically determine the best goal if not provided
    if focus_goal is None or focus_goal == "Auto-Detect":
        best_internal_goal = max(priority_scores, key=priority_scores.get)
        # Find the human-readable version
        focus_goal = "Balanced improvement"
        for label, internal in goal_map.items():
            if internal == best_internal_goal and priority_scores[internal] > 20:
                focus_goal = label
                break

    boosted_area = goal_map.get(focus_goal)
    if boosted_area:
        priority_scores[boosted_area] += 35

    if plan_intensity == "Focused":
        selected_areas = sorted(priority_scores, key=priority_scores.get, reverse=True)[:3]
    elif plan_intensity == "Balanced":
        selected_areas = sorted(priority_scores, key=priority_scores.get, reverse=True)[:4]
    else:
        selected_areas = sorted(priority_scores, key=priority_scores.get, reverse=True)[:5]

    allocation_rows = []
    for area in selected_areas:
        score = priority_scores[area]
        allocation_rows.append({"Focus Area": area, "Priority Weight": round(score, 1)})

    actions = []
    if "Concept Revision" in selected_areas:
        actions.append("Revise weak concepts using short notes, examples, and active recall.")
    if "Quiz Practice" in selected_areas:
        actions.append("Take timed quizzes and review every incorrect answer immediately.")
    if "Consistency Building" in selected_areas:
        actions.append("Study at the same time each day and track completion for seven days.")
    if "Assignments" in selected_areas:
        actions.append("Split assignments into plan, draft, and final review sessions.")
    if "Engagement" in selected_areas:
        actions.append("Ask questions, join discussions, or study with a peer group at least twice.")
    if "Module Completion" in selected_areas:
        actions.append("Finish pending modules first, then revise completed modules briefly.")

    return pd.DataFrame(allocation_rows), actions, focus_goal


def show_interactive_recommendations(recommendations, row, prediction):
    """Interactive recommendation planner tailored to the student."""
    control_col, summary_col = st.columns([1, 1.2])

    with control_col:
        focus_goal = st.selectbox(
            "Main improvement goal",
            [
                "Auto-Detect",
                "Balanced improvement",
                "Improve quiz score",
                "Build consistency",
                "Finish modules",
                "Improve assignments",
                "Increase engagement",
            ],
        )
        plan_intensity = st.radio(
            "Plan style",
            ["Focused", "Balanced", "Detailed"],
            horizontal=True,
        )

    allocation_df, focused_actions, final_goal = build_improvement_plan(
        row=row,
        prediction=prediction,
        focus_goal=focus_goal,
        plan_intensity=plan_intensity,
    )

    with summary_col:
        st.metric("Detected Goal", final_goal)
        st.metric("Focused Actions", len(focused_actions))
        st.metric("Predicted Level", prediction)

    st.subheader("Your Weekly Focus Plan")
    st.markdown('<div class="section-kicker">Recommended focus areas based on your behavioral signals and performance prediction.</div>', unsafe_allow_html=True)
    st.dataframe(allocation_df, use_container_width=True, hide_index=True)
    
    # Use Priority Weight instead of Hours
    comparison_chart = (
        alt.Chart(allocation_df)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X("Priority Weight:Q", title="Priority Weight"),
            y=alt.Y("Focus Area:N", sort="-x", title=None),
            color=alt.Color("Priority Weight:Q", scale=alt.Scale(scheme="purples"), legend=None),
            tooltip=["Focus Area", "Priority Weight"],
        )
        .properties(height=260)
    )
    st.altair_chart(comparison_chart, use_container_width=True)

    st.subheader("Priority Actions")
    for index, action in enumerate(focused_actions, start=1):
        st.markdown(
            f"""
            <div class="rec-item">
                <span class="rec-index">{index}</span>{escape_html(action)}
            </div>
            """,
            unsafe_allow_html=True,
        )
        
    st.divider()
    render_roadmap(focused_actions)
    render_dashboard_summary(row, prediction)

    with st.expander("Show all recommendation rules"):
        show_recommendations(recommendations)

def render_roadmap(actions):
    """Render a visual 4-week roadmap for the student."""
    st.subheader("4-Week Improvement Roadmap")
    cols = st.columns(4)
    icons = ["🌱", "🌿", "🌳", "🏆"]
    titles = ["Foundation", "Momentum", "Optimization", "Mastery"]
    
    for i in range(4):
        with cols[i]:
            action_snippet = actions[i % len(actions)] if actions else "Consistency"
            st.markdown(f"""
            <div style='background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:1.2rem; text-align:center; height:100%;'>
                <div style='font-size:2rem; margin-bottom:0.8rem;'>{icons[i]}</div>
                <div style='font-size:0.8rem; font-weight:800; color:var(--blue); text-transform:uppercase;'>Week {i+1}</div>
                <div style='font-size:1rem; font-weight:800; margin:0.4rem 0;'>{titles[i]}</div>
                <div style='font-size:0.82rem; color:var(--text-muted); line-height:1.4;'>{action_snippet[:60]}...</div>
            </div>
            """, unsafe_allow_html=True)

def render_dashboard_summary(row, prediction):
    """Render a formal summary card for the student in the dashboard view."""
    st.subheader("Performance Intelligence Summary")
    color = "#3dd68c" if prediction == "High" else "#4f9eff" if prediction == "Medium" else "#ff6b6b"
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.03); border:1px solid {color}; padding:2rem; border-radius:14px; box-shadow:0 10px 30px rgba(0,0,0,0.2);'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <h3 style='margin:0; color:#fff;'>AI Predictive Insight</h3>
            <span style='background:{color}; color:#000; padding:4px 12px; border-radius:999px; font-weight:800; font-size:0.8rem;'>{prediction.upper()} MATCH</span>
        </div>
        <p style='color:var(--text-muted); margin-top:1.5rem; line-height:1.6;'>
            This learner is currently tracking towards a <b>{prediction}</b> performance outcome. 
            Behavioral signals indicate a <b>{row.get('learning_trend', 'Stable')}</b> trend with a 
            quiz efficacy of <b>{float(row.get('quiz_score', 0)):.1f}%</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_performance_radar(row):
    """Render a Polar Bar chart as a surrogate for a Radar chart using Altair."""
    metrics = {
        "Quiz": float(row.get("quiz_score", 0)),
        "Engagement": float(row.get("engagement_score", 0)),
        "Consistency": float(row.get("consistency_index", 0)) * 100,
        "Interaction": float(row.get("interaction_level", 0)),
        "Momentum": min(100, float(row.get("modules_completed", 0)) * 12.5)
    }
    
    df_radar = pd.DataFrame([{"Metric": k, "Value": v} for k, v in metrics.items()])
    
    chart = alt.Chart(df_radar).mark_arc(innerRadius=20, stroke="#fff").encode(
        theta=alt.Theta("Value:Q", scale=alt.Scale(domain=[0, 100])),
        radius=alt.Radius("Value:Q", scale=alt.Scale(type="sqrt", rangeMin=20, rangeMax=120)),
        color=alt.Color("Metric:N", scale=alt.Scale(scheme="plasma"), legend=None),
        tooltip=["Metric", alt.Tooltip("Value:Q", format=".1f")]
    ).properties(width=300, height=300)
    
    st.altair_chart(chart, use_container_width=True)

def render_narrative_summary(row, prediction):
    """Generate a high-fidelity natural language summary of student performance."""
    quiz = float(row.get("quiz_score", 0))
    trend = row.get("learning_trend", "Stable")
    
    if prediction == "High":
        status = "demonstrating exceptional mastery"
        path = "accelerated enrichment and peer leadership"
    elif prediction == "Medium":
        status = "maintaining a steady trajectory"
        path = "targeted consistency building to break into the top tier"
    else:
        status = "encountering significant behavioral friction"
        path = "immediate diagnostic intervention and foundational support"
        
    narrative = f"""
    The intelligence engine identifies this student as **{status}**. 
    With a current quiz efficiency of **{quiz:.1f}%** and a **{trend}** learning momentum, 
    the optimal pathway involves **{path}**. 
    <br><br>
    Key behavioral signals suggest that maintaining current interaction levels while 
    refining specific concept gaps will yield a predicted 15% improvement in the next evaluation cycle.
    """
    st.markdown(f"<div class='narrative-box'>{narrative}</div>", unsafe_allow_html=True)


def render_app_header(df, result=None):
    """Render a polished edutech dashboard header."""
    if result is None:
        chips = [
            f"{len(df):,} student records",
            "ML prediction",
            "Quiz analytics",
            "Personalized planning",
        ]
    else:
        chips = [
            f"Student #{int(result['row'].get('student_id', 0))}",
            f"Model: {result['model_name']}",
            f"Prediction: {result['prediction']}",
            f"Quiz: {float(result['row'].get('quiz_score', 0)):.1f}",
        ]

    chip_html = "".join(f'<span class="header-chip">{escape_html(chip)}</span>' for chip in chips)
    st.markdown(
        f"""
        <div class="app-header">
            <div class="app-eyebrow">Edutech Learning Analytics</div>
            <div class="app-title">Student Performance Prediction System</div>
            <div class="app-subtitle">
                A professional dashboard for predicting learner outcomes, reviewing behavior signals,
                analyzing quiz performance, and converting insights into weekly improvement plans.
            </div>
            <div>{chip_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def learning_card(label, value, note):
    """Render a compact overview card."""
    st.markdown(
        f"""
        <div class="learning-card">
            <div class="learning-card-label">{escape_html(label)}</div>
            <div class="learning-card-value">{escape_html(value)}</div>
            <div class="learning-card-note">{escape_html(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_landing_dashboard(df):
    """Display a professional initial dashboard before prediction."""
    st.markdown(
        """
        <div class="action-strip">
            Use the control center to select a model, choose a student, and open the learner dashboard.
        </div>
        """,
        unsafe_allow_html=True,
    )

    total_students = len(df)
    avg_quiz = df["quiz_score"].mean() if "quiz_score" in df.columns else 0
    avg_engagement = df["engagement_score"].mean() if "engagement_score" in df.columns else 0
    avg_consistency = df["consistency_index"].mean() if "consistency_index" in df.columns else 0

    card_cols = st.columns(4)
    with card_cols[0]:
        learning_card("Dataset", f"{total_students:,}", "student learning records")
    with card_cols[1]:
        learning_card("Average Quiz", f"{avg_quiz:.1f}", "class assessment signal")
    with card_cols[2]:
        learning_card("Average Engagement", f"{avg_engagement:.1f}", "activity and participation")
    with card_cols[3]:
        learning_card("Average Consistency", f"{avg_consistency:.2f}", "study habit index")

    left_col, right_col = st.columns([1.15, 1])
    with left_col:
        st.subheader("Performance Overview")
        st.markdown(
            '<div class="section-kicker">Distribution of learner performance labels in the active dataset.</div>',
            unsafe_allow_html=True,
        )
        performance_counts = df["performance_label"].value_counts().reset_index()
        performance_counts.columns = ["Performance", "Students"]
        chart = (
            alt.Chart(performance_counts)
            .mark_bar(cornerRadiusEnd=4)
            .encode(
                x=alt.X("Performance:N", title=None),
                y=alt.Y("Students:Q", title="Students"),
                color=alt.Color("Performance:N", legend=None),
                tooltip=["Performance", "Students"],
            )
            .properties(height=290)
        )
        st.altair_chart(chart, use_container_width=True)

    with right_col:
        st.subheader("Dataset Preview")
        st.markdown(
            '<div class="section-kicker">First records from the selected dataset for quick validation.</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(df.head(8), use_container_width=True, hide_index=True)


def show_overview_dashboard(row, prediction, model_name, quiz_analysis, recommendation_result):
    """Display a professional top-level dashboard for the selected learner."""
    health_score = calculate_profile_health(row)
    risk_count = len(recommendation_result["risks"])
    quiz_category = quiz_analysis["category"]
    trend = row.get("learning_trend", "N/A")

    card_cols = st.columns(4)
    with card_cols[0]:
        learning_card("Predicted Performance", prediction, f"model: {model_name}")
    with card_cols[1]:
        learning_card("Profile Health", f"{health_score:.1f}%", "combined learning signal")
    with card_cols[2]:
        learning_card("Quiz Category", quiz_category, f"score: {float(row.get('quiz_score', 0)):.2f}")
    with card_cols[3]:
        learning_card("Risk Signals", risk_count, f"trend: {trend}")

    st.markdown(
        f"""
        <div class="action-strip">
            Model used: <strong>{escape_html(model_name)}</strong>. Current learning signal: predicted as
            <strong>{escape_html(prediction)}</strong>, with <strong>{escape_html(quiz_category)}</strong>
            quiz performance and <strong>{escape_html(trend)}</strong> learning trend.
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1.2, 1])
    with left_col:
        st.subheader("Learner Signal Mix")
        st.markdown(
            '<div class="section-kicker">Normalized behavior and performance indicators for the selected learner.</div>',
            unsafe_allow_html=True,
        )
        signal_df = build_student_metrics(row)
        chart = (
            alt.Chart(signal_df)
            .mark_bar(cornerRadiusEnd=4)
            .encode(
                x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 100]), title="Score"),
                y=alt.Y("Metric:N", sort="-x", title=None),
                color=alt.Color("Score:Q", scale=alt.Scale(scheme="tealblues"), legend=None),
                tooltip=["Metric", alt.Tooltip("Score:Q", format=".2f")],
            )
            .properties(height=310)
        )
        st.altair_chart(chart, use_container_width=True)

    with right_col:
        st.subheader("Next Best Focus")
        if recommendation_result["recommendations"]:
            for index, item in enumerate(recommendation_result["recommendations"][:4], start=1):
                st.markdown(
                    f"""
                    <div class="rec-item">
                        <span class="rec-index">{index}</span>{escape_html(item)}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("No immediate focus items detected.")


def build_watchlists(df):
    """Create intervention and enrichment watchlists from the full dataset."""
    watch_df = df.copy()

    low_score = (
        (watch_df["performance_label"].eq("Low")).astype(int) * 35
        + (watch_df["quiz_score"] < 60).astype(int) * 25
        + (watch_df["consistency_index"] < 0.5).astype(int) * 20
        + (watch_df["interaction_level"] < 50).astype(int) * 10
        + (watch_df["learning_trend"].eq("Decreasing")).astype(int) * 10
    )
    high_score = (
        (watch_df["performance_label"].eq("High")).astype(int) * 35
        + (watch_df["quiz_score"] >= 85).astype(int) * 25
        + (watch_df["engagement_score"] >= 80).astype(int) * 15
        + (watch_df["interaction_level"] >= 80).astype(int) * 10
        + (watch_df["learning_trend"].eq("Increasing")).astype(int) * 15
    )

    low_watchlist = watch_df[
        (watch_df["performance_label"].eq("Low"))
        | (watch_df["quiz_score"] < 60)
        | (
            (watch_df["consistency_index"] < 0.5)
            & (watch_df["learning_trend"].eq("Decreasing"))
        )
    ].copy()
    high_watchlist = watch_df[
        (watch_df["performance_label"].eq("High"))
        | (
            (watch_df["quiz_score"] >= 85)
            & (watch_df["engagement_score"] >= 75)
        )
    ].copy()

    low_watchlist["priority_score"] = low_score.loc[low_watchlist.index]
    high_watchlist["priority_score"] = high_score.loc[high_watchlist.index]

    low_watchlist["watchlist_reason"] = low_watchlist.apply(low_watchlist_reason, axis=1)
    high_watchlist["watchlist_reason"] = high_watchlist.apply(high_watchlist_reason, axis=1)

    display_columns = [
        "student_id",
        "performance_label",
        "quiz_score",
        "consistency_index",
        "engagement_score",
        "interaction_level",
        "learning_trend",
        "priority_score",
        "watchlist_reason",
    ]

    low_watchlist = low_watchlist.sort_values(
        ["priority_score", "quiz_score"],
        ascending=[False, True],
    )[display_columns]
    high_watchlist = high_watchlist.sort_values(
        ["priority_score", "quiz_score"],
        ascending=[False, False],
    )[display_columns]

    return low_watchlist, high_watchlist


def low_watchlist_reason(row):
    """Explain why a student appears in the low-performance watchlist."""
    reasons = []
    if row.get("performance_label") == "Low":
        reasons.append("low performance label")
    if row.get("quiz_score", 100) < 60:
        reasons.append("quiz below 60")
    if row.get("consistency_index", 1) < 0.5:
        reasons.append("low consistency")
    if row.get("interaction_level", 100) < 50:
        reasons.append("low interaction")
    if row.get("learning_trend") == "Decreasing":
        reasons.append("declining trend")
    return ", ".join(reasons) if reasons else "needs review"


def high_watchlist_reason(row):
    """Explain why a student appears in the high-performance watchlist."""
    reasons = []
    if row.get("performance_label") == "High":
        reasons.append("high performance label")
    if row.get("quiz_score", 0) >= 85:
        reasons.append("excellent quiz score")
    if row.get("engagement_score", 0) >= 80:
        reasons.append("strong engagement")
    if row.get("interaction_level", 0) >= 80:
        reasons.append("strong interaction")
    if row.get("learning_trend") == "Increasing":
        reasons.append("improving trend")
    return ", ".join(reasons) if reasons else "enrichment candidate"


def show_watchlist(df):
    """Display low-performance and high-performance student watchlists."""
    low_watchlist, high_watchlist = build_watchlists(df)
    avg_low_quiz = low_watchlist["quiz_score"].mean() if not low_watchlist.empty else 0
    avg_high_quiz = high_watchlist["quiz_score"].mean() if not high_watchlist.empty else 0

    st.subheader("Student Watchlist")
    st.markdown(
        """
        <div class="action-strip">
            Use this section to identify students who need intervention and students who are ready for enrichment.
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Low Performance Watchlist", f"{len(low_watchlist):,}")
    metric_cols[1].metric("High Performance Watchlist", f"{len(high_watchlist):,}")
    metric_cols[2].metric("Avg Low Quiz", f"{avg_low_quiz:.1f}")
    metric_cols[3].metric("Avg High Quiz", f"{avg_high_quiz:.1f}")

    view_col, rows_col = st.columns([1, 1])
    watchlist_view = view_col.radio(
        "Watchlist view",
        ["Both", "Low Performance", "High Performance"],
        horizontal=True,
    )
    rows_to_show = rows_col.slider("Students to show per list", 5, 50, 15, 5)

    if watchlist_view in ["Both", "Low Performance"]:
        st.subheader("Low Performance Intervention List")
        st.caption("Prioritize these students for revision support, consistency tracking, and mentor follow-up.")
        st.dataframe(
            low_watchlist.head(rows_to_show),
            use_container_width=True,
            hide_index=True,
        )

    if watchlist_view in ["Both", "High Performance"]:
        st.subheader("High Performance Enrichment List")
        st.caption("Use this list for advanced learning, peer mentoring, challenge quizzes, and leadership opportunities.")
        st.dataframe(
            high_watchlist.head(rows_to_show),
            use_container_width=True,
            hide_index=True,
        )

    chart_df = pd.DataFrame(
        {
            "Watchlist": ["Low Performance", "High Performance"],
            "Students": [len(low_watchlist), len(high_watchlist)],
        }
    )
    st.subheader("Watchlist Size Comparison")
    st.bar_chart(chart_df.set_index("Watchlist"), use_container_width=True)


def main():
    st.set_page_config(
        page_title="EduGrowth: Learning & Prediction",
        page_icon="🎓",
        layout="wide",
    )
    inject_styles()
    
    # Show loading animation on first load
    if "startup_animation_shown" not in st.session_state:
        render_startup_loader()
        st.session_state.startup_animation_shown = True
    
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "Landing"
    
    if st.session_state.app_mode == "Landing":
        show_landing_page()
        return

    if st.session_state.app_mode == "Option 1":
        run_student_evaluation_hub()
        return

    try:
        # Show loading animation when entering Option 2 (Analytics Matrix)
        if "option2_animation_shown" not in st.session_state:
            render_startup_loader()
            import time
            time.sleep(2.2) # Sync with CSS animation delay
            st.session_state.option2_animation_shown = True
            st.rerun()

        scaler, label_encoder, columns = load_artifacts()
    except Exception as exc:
        st.error(f"Unable to load required files: {exc}")
        st.stop()

    with st.sidebar:
        if st.button("← Back to Learning Hub"):
            st.session_state.app_mode = "Landing"
            st.rerun()
        st.markdown("---")
        st.markdown("### Learning Control Center")
        st.caption("Choose a trained model and inspect a learner profile.")
        
        # Highlight last evaluated student
        if "last_eval_student_id" in st.session_state:
            st.info(f"LIVE FEED: Student #{st.session_state.last_eval_student_id} just completed a quiz!")
            
        model_name = st.selectbox("Select Model", list(MODEL_PATHS.keys()))
        
        st.markdown("<div style='margin-bottom:0.4rem;font-size:0.85rem;font-weight:700;color:var(--text-soft);'>Upload next student dataset</div>", unsafe_allow_html=True)
        papaparse_data = papaparse_uploader()

    try:
        raw_df, dataset_name, dataset_key = load_active_dataset(papaparse_data)
        missing_columns = validate_dataset(raw_df)
        if missing_columns:
            st.error(
                "Uploaded dataset is missing required columns: "
                + ", ".join(missing_columns)
            )
            st.stop()

        active_model = load_model(model_name)
        df = prepare_dataset_for_dashboard(raw_df, active_model, scaler, label_encoder, columns)
    except Exception as exc:
        st.error(f"Unable to load selected dataset: {exc}")
        st.stop()

    if df.empty:
        st.error("The selected dataset has no rows.")
        st.stop()

    with st.sidebar:
        st.success(dataset_name)
        if "label_source" in df.columns:
            st.caption(f"Performance labels: {df['label_source'].iloc[0]}")
        st.divider()
        min_id = int(df["student_id"].min()) if "student_id" in df.columns else 1
        
        # Auto-select the latest student if they just came from the hub
        default_id = min_id
        if "last_eval_student_id" in st.session_state:
            try:
                candidate_id = int(st.session_state.last_eval_student_id)
                if candidate_id in df["student_id"].values:
                    default_id = candidate_id
            except:
                pass

        student_id = st.number_input(
            "Student ID",
            min_value=1,
            value=default_id,
            step=1,
        )

        active_context_key = f"{dataset_key}:{model_name}:{student_id}"
        if "prediction_result" not in st.session_state:
            st.session_state.prediction_result = None
        if st.session_state.get("active_context_key") != active_context_key:
            st.session_state.prediction_result = None
            st.session_state.active_context_key = active_context_key

        predict_clicked = st.button("Predict Performance", type="primary")
        st.divider()
        st.metric("Students", f"{len(df):,}")
        st.metric("Models", len(MODEL_PATHS))
        st.caption("Use the dashboard tabs to review prediction, profile, quiz behavior, charts, recommendations, and risks.")

    # Automate prediction when student selection changes
    student_not_found = False
    if st.session_state.prediction_result is None:
        try:
            model = load_model(model_name)
            student_row = df[df["student_id"] == int(student_id)]

            if student_row.empty:
                st.session_state.prediction_result = None
                student_not_found = True
            else:
                student_row = student_row.copy()
                row = student_row.iloc[0]
                prediction = predict_student(student_row, model, scaler, label_encoder, columns)
                recommendation_result = get_recommendation(prediction, row)
                quiz_analysis = analyze_quiz_performance(row)

                st.session_state.prediction_result = {
                    "model_name": model_name,
                    "dataset_name": dataset_name,
                    "student_row": student_row,
                    "row": row,
                    "prediction": prediction,
                    "recommendation_result": recommendation_result,
                    "quiz_analysis": quiz_analysis,
                }
        except Exception as exc:
            st.session_state.prediction_result = None
            st.error(f"Automatic prediction failed: {exc}")

    render_app_header(df, st.session_state.prediction_result)

    if student_not_found:
        st.warning(f"⚠️ No student found with ID **{int(student_id)}** in the current dataset. Please verify the ID or upload a new dataset.")

    if st.session_state.prediction_result is None:
        show_landing_dashboard(df)
        return

    result = st.session_state.prediction_result
    model_name = result["model_name"]
    student_row = result["student_row"]
    row = result["row"]
    prediction = result["prediction"]
    recommendation_result = result["recommendation_result"]
    quiz_analysis = result["quiz_analysis"]

def show_sentiment_dashboard(student_id):
    """Display student sentiment trends and feedback analysis."""
    conn = get_connection()
    df_feedback = pd.read_sql("SELECT * FROM feedback WHERE student_id = ?", conn, params=(student_id,))
    df_all_feedback = pd.read_sql("SELECT * FROM feedback", conn)
    conn.close()
    
    if df_feedback.empty:
        st.info("No feedback data available for this student yet.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sentiment Distribution")
        sentiment_counts = df_all_feedback['sentiment_label'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        chart = alt.Chart(sentiment_counts).mark_arc().encode(
            theta=alt.Theta(field="Count", type="quantitative"),
            color=alt.Color(field="Sentiment", type="nominal", scale=alt.Scale(domain=['Positive', 'Neutral', 'Negative'], range=['#3dd68c', '#f5c542', '#ff6b6b'])),
            tooltip=['Sentiment', 'Count']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

    with col2:
        st.subheader("Sentiment Trend")
        df_feedback['timestamp'] = pd.to_datetime(df_feedback['timestamp'])
        chart = alt.Chart(df_feedback).mark_line(point=True).encode(
            x='timestamp:T',
            y=alt.Y('sentiment_score:Q', scale=alt.Scale(domain=[-1, 1])),
            tooltip=['timestamp', 'sentiment_score', 'feedback_text']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

    st.subheader("Recent Feedback Stream")
    for _, row in df_feedback.tail(5).iterrows():
        color = "#3dd68c" if row['sentiment_label'] == "Positive" else "#f5c542" if row['sentiment_label'] == "Neutral" else "#ff6b6b"
        st.markdown(f"""
        <div style='border-left: 5px solid {color}; background: var(--surface); padding: 1rem; margin-bottom: 1rem; border-radius: 0 10px 10px 0;'>
            <div style='font-size: 0.8rem; color: var(--text-muted);'>{row['timestamp']}</div>
            <div style='color: var(--text-soft);'>{row['feedback_text']}</div>
            <div style='font-weight: 800; color: {color}; font-size: 0.75rem; text-transform: uppercase;'>{row['sentiment_label']} ({row['sentiment_score']})</div>
        </div>
        """, unsafe_allow_html=True)

def show_recommendations_accuracy(student_id):
    """Measure effectiveness of recommendations based on actual student behavior."""
    st.subheader("Recommendations Effectiveness")
    
    conn = get_connection()
    # Fetch real improvements from adaptivity_log
    # For simplicity, we compare the score of the module where rec was generated vs the next one
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(post_score - pre_score) FROM adaptivity_log 
        WHERE student_id = ? AND action_taken = 'started_recommended_video' AND post_score IS NOT NULL
    """, (student_id,))
    avg_improvement = cursor.fetchone()[0] or 0
    
    # Track completion of recommended videos
    cursor.execute("SELECT COUNT(*) FROM recommendations WHERE student_id = ? AND status = 'completed'", (student_id,))
    completed_recs = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM recommendations WHERE student_id = ?", (student_id,))
    total_recs = cursor.fetchone()[0]
    completion_rate = (completed_recs / total_recs * 100) if total_recs > 0 else 0

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Avg. Improvement (Points)", f"{avg_improvement:.2f}")
    with col2:
        st.metric("Recommendation Completion Rate", f"{completion_rate:.1f}%")

    df_recs = pd.read_sql("SELECT timestamp, recommendation_text, status FROM recommendations WHERE student_id = ?", conn, params=(student_id,))
    conn.close()
    
    if not df_recs.empty:
        st.subheader("Individual Recommendation Tracking")
        st.dataframe(df_recs, use_container_width=True)
    else:
        st.info("No personalized recommendations tracked for this student yet.")

def show_adaptivity_monitoring(student_id):
    """Statistical impact of personalized learning pathways using real student data."""
    st.subheader("Adaptivity Impact Analysis")
    
    conn = get_connection()
    df_logs = pd.read_sql("SELECT * FROM adaptivity_log WHERE student_id = ?", conn, params=(student_id,))
    conn.close()

    if df_logs.empty:
        st.info("No adaptivity logs found for this student. Complete a recommended module to see analysis.")
        return

    col1, col2 = st.columns(2)
    with col1:
        count = len(df_logs)
        st.metric("Total Interventions Tracked", count)
        st.caption("Includes started videos and completed exercises.")
    
    with col2:
        # Show a summary of actions
        action_counts = df_logs['action_taken'].value_counts().reset_index()
        action_counts.columns = ['Action', 'Count']
        chart = alt.Chart(action_counts).mark_bar().encode(
            x='Action',
            y='Count',
            color='Action'
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

def show_video_engagement(student_id):
    """Analyze video dropout and engagement metrics."""
    st.subheader("Video Engagement Heatmap")
    conn = get_connection()
    df_dropout = pd.read_sql("SELECT * FROM dropout_analysis", conn)
    conn.close()
    
    if not df_dropout.empty:
        chart = alt.Chart(df_dropout).mark_bar().encode(
            x='timestamp_seconds:O',
            y='dropout_percentage:Q',
            color=alt.condition(
                alt.datum.is_critical_point == 1,
                alt.value('#ff6b6b'),
                alt.value('#4f9eff')
            ),
            tooltip=['timestamp_seconds', 'dropout_count', 'dropout_percentage']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
        st.caption("Red bars indicate critical knowledge check points.")
    else:
        st.info("No video engagement data available.")


def main():
    st.set_page_config(
        page_title="EduGrowth: Learning & Prediction",
        page_icon="🎓",
        layout="wide",
    )
    inject_styles()
    
    # Show loading animation on first load
    if "startup_animation_shown" not in st.session_state:
        render_startup_loader()
        st.session_state.startup_animation_shown = True
    
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "Landing"
    
    if st.session_state.app_mode == "Landing":
        show_landing_page()
        return

    if st.session_state.app_mode == "Option 1":
        run_student_evaluation_hub()
        return

    try:
        # Show loading animation when entering Option 2 (Analytics Matrix)
        if "option2_animation_shown" not in st.session_state:
            render_startup_loader()
            import time
            time.sleep(2.2) # Sync with CSS animation delay
            st.session_state.option2_animation_shown = True
            st.rerun()

        scaler, label_encoder, columns = load_artifacts()
    except Exception as exc:
        st.error(f"Unable to load required files: {exc}")
        st.stop()

    with st.sidebar:
        if st.button("← Back to Learning Hub"):
            st.session_state.app_mode = "Landing"
            st.rerun()
        st.markdown("---")
        st.markdown("### Learning Control Center")
        st.caption("Choose a trained model and inspect a learner profile.")
        
        # Highlight last evaluated student
        if "last_eval_student_id" in st.session_state:
            st.info(f"LIVE FEED: Student #{st.session_state.last_eval_student_id} just completed a quiz!")
            
        model_name = st.selectbox("Select Model", list(MODEL_PATHS.keys()))
        
        st.markdown("<div style='margin-bottom:0.4rem;font-size:0.85rem;font-weight:700;color:var(--text-soft);'>Upload next student dataset</div>", unsafe_allow_html=True)
        papaparse_data = papaparse_uploader()

    try:
        raw_df, dataset_name, dataset_key = load_active_dataset(papaparse_data)
        missing_columns = validate_dataset(raw_df)
        if missing_columns:
            st.error(
                "Uploaded dataset is missing required columns: "
                + ", ".join(missing_columns)
            )
            st.stop()

        active_model = load_model(model_name)
        df = prepare_dataset_for_dashboard(raw_df, active_model, scaler, label_encoder, columns)
    except Exception as exc:
        st.error(f"Unable to load selected dataset: {exc}")
        st.stop()

    if df.empty:
        st.error("The selected dataset has no rows.")
        st.stop()

    with st.sidebar:
        st.success(dataset_name)
        if "label_source" in df.columns:
            st.caption(f"Performance labels: {df['label_source'].iloc[0]}")
        st.divider()
        min_id = int(df["student_id"].min()) if "student_id" in df.columns else 1
        
        # Auto-select the latest student if they just came from the hub
        default_id = min_id
        if "last_eval_student_id" in st.session_state:
            try:
                candidate_id = int(st.session_state.last_eval_student_id)
                if candidate_id in df["student_id"].values:
                    default_id = candidate_id
            except:
                pass

        student_id = st.number_input(
            "Student ID",
            min_value=1,
            value=default_id,
            step=1,
        )

        active_context_key = f"{dataset_key}:{model_name}:{student_id}"
        if "prediction_result" not in st.session_state:
            st.session_state.prediction_result = None
        if st.session_state.get("active_context_key") != active_context_key:
            st.session_state.prediction_result = None
            st.session_state.active_context_key = active_context_key

        predict_clicked = st.button("Predict Performance", type="primary")
        st.divider()
        st.metric("Students", f"{len(df):,}")
        st.metric("Models", len(MODEL_PATHS))
        st.caption("Use the dashboard tabs to review prediction, profile, quiz behavior, charts, recommendations, and risks.")

    # Automate prediction when student selection changes
    student_not_found = False
    if st.session_state.prediction_result is None:
        try:
            model = load_model(model_name)
            student_row = df[df["student_id"] == int(student_id)]

            if student_row.empty:
                st.session_state.prediction_result = None
                student_not_found = True
            else:
                student_row = student_row.copy()
                row = student_row.iloc[0]
                prediction = predict_student(student_row, model, scaler, label_encoder, columns)
                recommendation_result = get_recommendation(prediction, row)
                quiz_analysis = analyze_quiz_performance(row)

                st.session_state.prediction_result = {
                    "model_name": model_name,
                    "dataset_name": dataset_name,
                    "student_row": student_row,
                    "row": row,
                    "prediction": prediction,
                    "recommendation_result": recommendation_result,
                    "quiz_analysis": quiz_analysis,
                }
        except Exception as exc:
            st.session_state.prediction_result = None
            st.error(f"Automatic prediction failed: {exc}")

    render_app_header(df, st.session_state.prediction_result)

    if student_not_found:
        st.warning(f"⚠️ No student found with ID **{int(student_id)}** in the current dataset. Please verify the ID or upload a new dataset.")

    if st.session_state.prediction_result is None:
        show_landing_dashboard(df)
        return

    result = st.session_state.prediction_result
    model_name = result["model_name"]
    student_row = result["student_row"]
    row = result["row"]
    prediction = result["prediction"]
    recommendation_result = result["recommendation_result"]
    quiz_analysis = result["quiz_analysis"]

    tab_titles = [
        "Overview", "Student Profile", "Student Data", "Quiz Analysis", 
        "Charts", "Watchlist", "Recommendations", "Sentiment Analysis",
        "Video Engagement", "Recommendations Accuracy", "Adaptivity Monitoring", "Risk Factors"
    ]
    tabs = st.tabs(tab_titles)

    with tabs[0]: # Overview
        show_overview_dashboard(row, prediction, model_name, quiz_analysis, recommendation_result)

    with tabs[1]: # Profile
        st.subheader("Student Profile")
        show_student_profile(row, prediction, model_name)

    with tabs[2]: # Data
        st.subheader("Student Data")
        st.caption(dataset_name)
        st.dataframe(student_row, use_container_width=True)
        with st.expander("View active dataset preview"):
            st.dataframe(df.head(100), use_container_width=True, hide_index=True)

    with tabs[3]: # Quiz
        st.subheader("Quiz Performance Analysis")
        show_quiz_analysis(row, quiz_analysis)

    with tabs[4]: # Charts
        show_charts(df, row)

    with tabs[5]: # Watchlist
        show_watchlist(df)

    with tabs[6]: # Recommendations
        st.subheader("Recommendations")
        show_interactive_recommendations(recommendation_result["recommendations"], row, prediction)

    with tabs[7]: # Sentiment
        show_sentiment_dashboard(int(student_id))

    with tabs[8]: # Video Engagement
        show_video_engagement(int(student_id))

    with tabs[9]: # Recommendations Accuracy
        show_recommendations_accuracy(int(student_id))

    with tabs[10]: # Adaptivity
        show_adaptivity_monitoring(int(student_id))

    with tabs[11]: # Risk Factors
        st.subheader("Risk Factors")
        if recommendation_result["risks"]:
            for risk in recommendation_result["risks"]:
                st.markdown(f'<div class="risk-card">{escape_html(risk)}</div>', unsafe_allow_html=True)
        else:
            st.success("No major risk factors detected for this student.")


if __name__ == "__main__":
    main()
