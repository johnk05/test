import html

import joblib
import altair as alt
import pandas as pd
import streamlit as st


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
    """Apply professional dashboard styling."""
    st.markdown(
        """
        <style>
        :root {
            --surface: rgba(255, 255, 255, 0.055);
            --surface-strong: rgba(255, 255, 255, 0.088);
            --line: rgba(255, 255, 255, 0.11);
            --line-strong: rgba(255, 255, 255, 0.18);
            --text-muted: rgba(250, 250, 250, 0.68);
            --text-soft: rgba(250, 250, 250, 0.82);
            --blue: #74b8ff;
            --green: #7ee787;
            --amber: #ffd166;
            --red: #ff8b8b;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2.2rem;
            max-width: 1440px;
        }
        h1, h2, h3 {
            letter-spacing: 0 !important;
        }
        h1 {
            font-size: 2.45rem !important;
            line-height: 1.15 !important;
            margin-bottom: 0.75rem !important;
        }
        h2, h3 {
            margin-top: 1rem !important;
        }
        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: var(--text-muted);
        }
        [data-testid="stSidebar"] [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.045);
        }
        .stButton > button {
            border-radius: 7px;
            min-height: 2.65rem;
            font-weight: 750;
        }
        [data-baseweb="tab-list"] {
            gap: 0.35rem;
            border-bottom: 1px solid var(--line);
            padding-bottom: 0.2rem;
        }
        [data-baseweb="tab"] {
            border-radius: 7px 7px 0 0;
            padding: 0.55rem 0.85rem;
            font-weight: 700;
        }
        .app-header {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1.5rem 1.6rem;
            margin-bottom: 1.15rem;
            background:
                linear-gradient(135deg, rgba(13, 17, 23, 0.96), rgba(33, 38, 45, 0.88)),
                linear-gradient(90deg, rgba(116, 184, 255, 0.18), rgba(126, 231, 135, 0.09));
            box-shadow: 0 18px 44px rgba(0, 0, 0, 0.16);
        }
        .app-header::after {
            content: "";
            position: absolute;
            inset: auto 0 0 0;
            height: 3px;
            background: linear-gradient(90deg, var(--blue), var(--green), var(--amber));
            opacity: 0.9;
        }
        .app-eyebrow {
            color: var(--blue);
            font-size: 0.82rem;
            font-weight: 800;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }
        .app-title {
            color: #ffffff;
            font-size: 2.35rem;
            font-weight: 850;
            line-height: 1.12;
            margin-bottom: 0.35rem;
        }
        .app-subtitle {
            color: var(--text-soft);
            max-width: 820px;
            font-size: 1rem;
            line-height: 1.5;
        }
        .header-chip {
            display: inline-block;
            border: 1px solid rgba(116, 184, 255, 0.3);
            border-radius: 999px;
            padding: 0.32rem 0.72rem;
            margin: 0.85rem 0.35rem 0 0;
            color: rgba(250, 250, 250, 0.9);
            background: rgba(255, 255, 255, 0.065);
            font-size: 0.84rem;
            font-weight: 700;
        }
        .panel {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--surface);
            padding: 1rem;
        }
        .section-kicker {
            color: var(--text-muted);
            font-size: 0.86rem;
            line-height: 1.45;
            margin: -0.35rem 0 0.8rem 0;
        }
        .learning-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: linear-gradient(180deg, var(--surface-strong), var(--surface));
            padding: 1rem;
            min-height: 122px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.045);
        }
        .learning-card-label {
            color: var(--text-muted);
            font-size: 0.82rem;
            font-weight: 800;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }
        .learning-card-value {
            color: #ffffff;
            font-size: 1.6rem;
            font-weight: 850;
            line-height: 1.1;
        }
        .learning-card-note {
            color: var(--text-muted);
            font-size: 0.84rem;
            margin-top: 0.45rem;
        }
        .action-strip {
            border: 1px solid rgba(116, 184, 255, 0.19);
            border-left: 4px solid var(--blue);
            background: rgba(116, 184, 255, 0.09);
            border-radius: 8px;
            padding: 0.9rem 1rem;
            margin: 0.8rem 0 1rem 0;
            color: rgba(250, 250, 250, 0.88);
        }
        div[data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.045);
        }
        .profile-hero {
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1.25rem 1.35rem;
            background: linear-gradient(135deg, rgba(49, 51, 63, 0.58), rgba(23, 26, 33, 0.92));
            margin-bottom: 1rem;
        }
        .profile-row {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
        }
        .profile-name {
            font-size: 1.8rem;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 0.25rem;
        }
        .profile-meta {
            color: var(--text-muted);
            font-size: 0.96rem;
        }
        .profile-score {
            min-width: 190px;
            text-align: right;
        }
        .profile-score-value {
            font-size: 2.35rem;
            font-weight: 800;
            color: #ffffff;
            line-height: 1;
        }
        .status-pill {
            display: inline-block;
            border-radius: 999px;
            padding: 0.25rem 0.7rem;
            font-size: 0.82rem;
            font-weight: 700;
            margin-right: 0.4rem;
            margin-top: 0.65rem;
        }
        .status-good {
            color: var(--green);
            background: rgba(46, 160, 67, 0.16);
            border: 1px solid rgba(46, 160, 67, 0.35);
        }
        .status-watch {
            color: var(--amber);
            background: rgba(255, 193, 7, 0.14);
            border: 1px solid rgba(255, 193, 7, 0.35);
        }
        .status-risk {
            color: var(--red);
            background: rgba(248, 81, 73, 0.14);
            border: 1px solid rgba(248, 81, 73, 0.35);
        }
        .profile-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--surface);
            padding: 1rem;
            min-height: 118px;
        }
        .profile-card-label {
            color: var(--text-muted);
            font-size: 0.86rem;
            font-weight: 700;
            margin-bottom: 0.45rem;
        }
        .profile-card-value {
            color: #ffffff;
            font-size: 1.65rem;
            font-weight: 800;
            line-height: 1.1;
        }
        .profile-card-note {
            color: var(--text-muted);
            font-size: 0.82rem;
            margin-top: 0.45rem;
        }
        .rec-item, .risk-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.85rem 0.95rem;
            margin: 0.55rem 0;
            background: var(--surface);
            color: var(--text-soft);
            line-height: 1.45;
        }
        .rec-index {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.45rem;
            height: 1.45rem;
            border-radius: 999px;
            margin-right: 0.55rem;
            background: rgba(116, 184, 255, 0.15);
            border: 1px solid rgba(116, 184, 255, 0.28);
            color: var(--blue);
            font-size: 0.78rem;
            font-weight: 800;
        }
        .risk-card {
            border-left: 4px solid var(--red);
            background: rgba(248, 81, 73, 0.09);
        }
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
        }
        @media (max-width: 760px) {
            .app-title {
                font-size: 1.75rem;
            }
            .profile-score {
                text-align: left;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
            align-items: center;
            justify-content: center;
            background: #05070b;
            animation: loaderFade 0.7s ease forwards;
            animation-delay: 1.7s;
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


def load_active_dataset(uploaded_file):
    """Load the default dataset or a user-uploaded CSV."""
    if uploaded_file is None:
        return load_data().copy(), "Default dataset", "default"

    uploaded_df = pd.read_csv(uploaded_file)
    dataset_name = f"Uploaded: {uploaded_file.name}"
    dataset_key = f"{uploaded_file.name}:{uploaded_file.size}"
    return uploaded_df, dataset_name, dataset_key


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
        '<div class="section-kicker">Filter the cohort, compare the selected learner to peers, and inspect distribution patterns.</div>',
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

    with st.expander("Show all recommendation rules"):
        show_recommendations(recommendations)


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
        page_title="Student Performance Prediction System",
        page_icon="SP",
        layout="wide",
    )
    inject_styles()
    if "startup_loader_seen" not in st.session_state:
        render_startup_loader()
        st.session_state.startup_loader_seen = True

    try:
        scaler, label_encoder, columns = load_artifacts()
    except Exception as exc:
        st.error(f"Unable to load required files: {exc}")
        st.stop()

    with st.sidebar:
        st.markdown("### Learning Control Center")
        st.caption("Choose a trained model and inspect a learner profile.")
        model_name = st.selectbox("Select Model", list(MODEL_PATHS.keys()))
        uploaded_file = st.file_uploader(
            "Upload next student dataset",
            type=["csv"],
            help="Upload a CSV with the same feature columns used during training.",
        )

    try:
        raw_df, dataset_name, dataset_key = load_active_dataset(uploaded_file)
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

    active_context_key = f"{dataset_key}:{model_name}:{student_id}"
    if "prediction_result" not in st.session_state:
        st.session_state.prediction_result = None
    if st.session_state.get("active_context_key") != active_context_key:
        st.session_state.prediction_result = None
        st.session_state.active_context_key = active_context_key

    with st.sidebar:
        st.success(dataset_name)
        if "label_source" in df.columns:
            st.caption(f"Performance labels: {df['label_source'].iloc[0]}")
        st.divider()
        min_id = int(df["student_id"].min()) if "student_id" in df.columns else 1
        max_id = int(df["student_id"].max()) if "student_id" in df.columns else 100000
        student_id = st.number_input(
            "Student ID",
            min_value=min_id,
            max_value=max_id,
            value=min_id,
            step=1,
        )

        predict_clicked = st.button("Predict Performance", type="primary")
        st.divider()
        st.metric("Students", f"{len(df):,}")
        st.metric("Models", len(MODEL_PATHS))
        st.caption("Use the dashboard tabs to review prediction, profile, quiz behavior, charts, recommendations, and risks.")

    # Automate prediction when student selection changes
    if st.session_state.prediction_result is None:
        try:
            model = load_model(model_name)
            student_row = df[df["student_id"] == int(student_id)]

            if student_row.empty:
                st.session_state.prediction_result = None
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

    overview_tab, profile_tab, data_tab, quiz_tab, charts_tab, watchlist_tab, recommendation_tab, risk_tab = st.tabs(
        [
            "Overview",
            "Student Profile",
            "Student Data",
            "Quiz Analysis",
            "Charts",
            "Watchlist",
            "Recommendations",
            "Risk Factors",
        ]
    )

    with overview_tab:
        show_overview_dashboard(
            row,
            prediction,
            model_name,
            quiz_analysis,
            recommendation_result,
        )

    with profile_tab:
        st.subheader("Student Profile")
        show_student_profile(row, prediction, model_name)

    with data_tab:
        st.subheader("Student Data")
        st.caption(dataset_name)
        st.dataframe(student_row, use_container_width=True)
        with st.expander("View active dataset preview"):
            st.dataframe(df.head(100), use_container_width=True, hide_index=True)

    with quiz_tab:
        st.subheader("Quiz Performance Analysis")
        show_quiz_analysis(row, quiz_analysis)

    with charts_tab:
        show_charts(df, row)

    with watchlist_tab:
        show_watchlist(df)

    with recommendation_tab:
        st.subheader("Recommendations")
        show_interactive_recommendations(
            recommendation_result["recommendations"],
            row,
            prediction,
        )

    with risk_tab:
        st.subheader("Risk Factors")
        if recommendation_result["risks"]:
            for risk in recommendation_result["risks"]:
                st.markdown(
                    f'<div class="risk-card">{escape_html(risk)}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success("No major risk factors detected for this student.")


if __name__ == "__main__":
    main()
