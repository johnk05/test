import sqlite3
import pandas as pd
import os

DB_NAME = "edugrowth.db"
PRESCRIPTIVE_DB = "prescriptive_analytics.db"

def get_connection(db=DB_NAME):
    return sqlite3.connect(db)

def init_db():
    # Live Operational DB
    conn = get_connection(DB_NAME)
    cursor = conn.cursor()
    
    # Prescriptive DB for Prediction Tab
    conn_p = get_connection(PRESCRIPTIVE_DB)
    cursor_p = conn_p.cursor()

    # Apply Students schema to both
    for cur, con in [(cursor, conn), (cursor_p, conn_p)]:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY,
            name TEXT,
            region TEXT,
            time_spent REAL,
            modules_completed INTEGER,
            quiz_score REAL,
            assignment_timeliness REAL,
            interaction_level REAL,
            consistency_index REAL,
            engagement_score REAL,
            learning_trend TEXT,
            performance_label TEXT,
            learning_velocity REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        con.commit()

    # Specific table for Prescriptive Constraints
    cursor_p.execute("""
    CREATE TABLE IF NOT EXISTS prescriptive_constraints (
        student_id INTEGER PRIMARY KEY,
        suggested_time_increase REAL,
        target_quiz_score REAL,
        recommended_engagement_boost REAL,
        predicted_impact_label TEXT,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )
    """)
    conn_p.commit()

    # Feedback table (Live DB only)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        module_id INTEGER,
        feedback_text TEXT,
        sentiment_score REAL,
        sentiment_label TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )
    """)
    
    # Dropout Analysis table (Live DB only)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dropout_analysis (
        video_id INTEGER,
        timestamp_seconds INTEGER,
        dropout_count INTEGER,
        dropout_percentage REAL,
        is_critical_point INTEGER DEFAULT 0,
        PRIMARY KEY (video_id, timestamp_seconds)
    )
    """)

    # Video Library table (Live DB only)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS video_library (
        video_id INTEGER PRIMARY KEY,
        title TEXT,
        youtube_url TEXT,
        topic TEXT,
        difficulty_level TEXT,
        avg_rating REAL,
        typical_completion_rate REAL
    )
    """)

    # Recommendations table (Both DBs)
    for cur, con in [(cursor, conn), (cursor_p, conn_p)]:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            module_id INTEGER,
            recommendation_text TEXT,
            recommended_video_id INTEGER,
            status TEXT DEFAULT 'pending',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        """)
        con.commit()

    # Adaptivity Log table (Both DBs)
    for cur, con in [(cursor, conn), (cursor_p, conn_p)]:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS adaptivity_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            recommendation_id INTEGER,
            action_taken TEXT,
            pre_score REAL,
            post_score REAL,
            time_to_action REAL,
            module_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        con.commit()

    # Import existing data to BOTH if empty
    for cur, con, db_label in [(cursor, conn, "Live"), (cursor_p, conn_p, "Prescriptive")]:
        cur.execute("SELECT COUNT(*) FROM students")
        if cur.fetchone()[0] == 0:
            csv_path = "synthetic_student_data.csv"
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                table_cols = [
                    "student_id", "name", "region", "time_spent", "modules_completed", 
                    "quiz_score", "assignment_timeliness", "interaction_level", 
                    "consistency_index", "engagement_score", "learning_trend", 
                    "performance_label", "learning_velocity"
                ]
                df_to_import = df[[col for col in df.columns if col in table_cols]]
                df_to_import.to_sql("students", con, if_exists="append", index=False)
                print(f"Imported {len(df_to_import)} students from {csv_path} to {db_label} DB")

    # Seed Video Library (Live DB only)
    cursor.execute("SELECT COUNT(*) FROM video_library")
    if cursor.fetchone()[0] == 0:
        videos = [
            (1, "Machine Learning Fundamentals", "https://www.youtube.com/watch?v=Gv9_4yMHFhI", "ML", "beginner", 4.5, 0.85),
            (2, "Data Science Pipeline", "https://www.youtube.com/watch?v=X3paOmcrTjQ", "Data Science", "beginner", 4.2, 0.78),
            (3, "Neural Networks Explained", "https://www.youtube.com/watch?v=aircAruvnKk", "AI", "intermediate", 4.7, 0.72),
            (4, "Python for Data Analysis", "https://www.youtube.com/watch?v=r-uOLxNrNk8", "Python", "beginner", 4.8, 0.90)
        ]
        cursor.executemany("INSERT INTO video_library (video_id, title, youtube_url, topic, difficulty_level, avg_rating, typical_completion_rate) VALUES (?,?,?,?,?,?,?)", videos)

    # Seed dropout points (Live DB only)
    cursor.execute("SELECT COUNT(*) FROM dropout_analysis")
    if cursor.fetchone()[0] == 0:
        dropouts = [
            (1, 120, 50, 0.35, 1), (1, 300, 45, 0.32, 1),
            (2, 200, 60, 0.40, 1), (3, 150, 40, 0.30, 1),
            (4, 400, 55, 0.38, 1)
        ]
        cursor.executemany("INSERT INTO dropout_analysis (video_id, timestamp_seconds, dropout_count, dropout_percentage, is_critical_point) VALUES (?,?,?,?,?)", dropouts)

    conn.close()
    conn_p.close()

if __name__ == "__main__":
    init_db()
