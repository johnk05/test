import sqlite3
import pandas as pd
import os

DB_NAME = "edugrowth.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Students table
    cursor.execute("""
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
        learning_velocity REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Feedback table
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

    # Dropout Analysis table
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

    # Video Library table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS video_library (
        video_id INTEGER PRIMARY KEY,
        title TEXT,
        youtube_url TEXT,
        topic TEXT,
        difficulty_level TEXT, -- beginner, intermediate, advanced
        avg_rating REAL,
        typical_completion_rate REAL
    )
    """)

    # Recommendations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        module_id INTEGER,
        recommendation_text TEXT,
        recommended_video_id INTEGER,
        status TEXT DEFAULT 'pending', -- pending, completed
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (recommended_video_id) REFERENCES video_library(video_id)
    )
    """)

    # Adaptivity Log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS adaptivity_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        recommendation_id INTEGER,
        action_taken TEXT,
        pre_score REAL,
        post_score REAL,
        time_to_action REAL,
        module_id INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (recommendation_id) REFERENCES recommendations(rec_id)
    )
    """)

    conn.commit()
    
    # Import existing data if students table is empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        csv_path = "synthetic_student_data.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            # Ensure columns match
            # The CSV might not have all columns, so we'll only import what we have
            df.to_sql("students", conn, if_exists="append", index=False)
            print(f"Imported {len(df)} students from {csv_path}")

    # Seed Video Library if empty
    cursor.execute("SELECT COUNT(*) FROM video_library")
    if cursor.fetchone()[0] == 0:
        videos = [
            (1, "Machine Learning Fundamentals", "https://www.youtube.com/watch?v=Gv9_4yMHFhI", "ML", "beginner", 4.5, 0.85),
            (2, "Data Science Pipeline", "https://www.youtube.com/watch?v=X3paOmcrTjQ", "Data Science", "beginner", 4.2, 0.78),
            (3, "Neural Networks Explained", "https://www.youtube.com/watch?v=aircAruvnKk", "AI", "intermediate", 4.7, 0.72),
            (4, "Python for Data Analysis", "https://www.youtube.com/watch?v=r-uOLxNrNk8", "Python", "beginner", 4.8, 0.90)
        ]
        cursor.executemany("INSERT INTO video_library (video_id, title, youtube_url, topic, difficulty_level, avg_rating, typical_completion_rate) VALUES (?,?,?,?,?,?,?)", videos)
        print("Seeded video library")

    # Seed some mock dropout points for demonstration
    cursor.execute("SELECT COUNT(*) FROM dropout_analysis")
    if cursor.fetchone()[0] == 0:
        dropouts = [
            (1, 120, 50, 0.35, 1),
            (1, 300, 45, 0.32, 1),
            (2, 200, 60, 0.40, 1),
            (3, 150, 40, 0.30, 1),
            (4, 400, 55, 0.38, 1)
        ]
        cursor.executemany("INSERT INTO dropout_analysis (video_id, timestamp_seconds, dropout_count, dropout_percentage, is_critical_point) VALUES (?,?,?,?,?)", dropouts)
        print("Seeded dropout analysis points")

    conn.close()

if __name__ == "__main__":
    init_db()
