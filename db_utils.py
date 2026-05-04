import sqlite3
import pandas as pd
import os

DB_NAME = "edugrowth.db"
PRESCRIPTIVE_DB = "prescriptive_analytics.db"
DATA_PATH = "synthetic_student_data.csv"

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
        typical_completion_rate REAL,
        quiz_json TEXT,
        duration TEXT
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

    # Activity Log table (Both DBs)
    for cur, con in [(cursor, conn), (cursor_p, conn_p)]:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS student_activity (
            activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            activity_type TEXT,
            description TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        """)
        con.commit()

    # Import existing data to BOTH if empty
    for cur, con, db_label in [(cursor, conn, "Live"), (cursor_p, conn_p, "Prescriptive")]:
        cur.execute("SELECT COUNT(*) FROM students")
        if cur.fetchone()[0] == 0:
            csv_path = DATA_PATH
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
        # 4 beginner alternatives (for students who scored < 60%)
        # 4 intermediate alternatives (for students who scored 60-80%)
        videos = [
            # Module 1 alternatives — ML Fundamentals (IDs 11, 12)
            (11, "ML for Beginners (Full Course)", "https://www.youtube.com/watch?v=NWONeJKn6kc", "ML", "beginner", 4.6, 0.82, '[{"q": "What is the goal of Supervised Learning?", "options": ["Predicting labels", "Finding hidden patterns", "Deleting data", "Gaming"], "a": "Predicting labels"}, {"q": "Is regression a part of ML?", "options": ["Yes", "No"], "a": "Yes"}]', "12:30"),
            (12, "Machine Learning Crash Course", "https://www.youtube.com/watch?v=i_LwzRVP7bg", "ML", "intermediate", 4.5, 0.76, '[{"q": "What is overfitting?", "options": ["Model too simple", "Model too complex", "No data", "Perfect model"], "a": "Model too complex"}, {"q": "What is a feature?", "options": ["Input variable", "Output variable", "Bug", "Hardware"], "a": "Input variable"}]', "15:45"),
            # Module 2 alternatives — Data Science Pipeline (IDs 13, 14)
            (13, "Data Science Full Course for Beginners", "https://www.youtube.com/watch?v=ua-CiDNNj30", "Data Science", "beginner", 4.3, 0.79, '[{"q": "What is the first step in DS pipeline?", "options": ["Cleaning", "Collection", "Modeling", "Reporting"], "a": "Collection"}, {"q": "Is EDA important?", "options": ["Yes", "No"], "a": "Yes"}]', "18:20"),
            (14, "Data Analysis with Python", "https://www.youtube.com/watch?v=r-uOLxNrNk8", "Data Science", "intermediate", 4.4, 0.74, '[{"q": "Which library is used for dataframes?", "options": ["Pandas", "NumPy", "Flask", "Django"], "a": "Pandas"}]', "11:15"),
            # Module 3 alternatives — Neural Networks (IDs 15, 16)
            (15, "Neural Networks from Scratch", "https://www.youtube.com/watch?v=Wo5dMEP_BbI", "AI", "beginner", 4.7, 0.71, '[{"q": "What is an activation function?", "options": ["Decides output", "Powers the PC", "Deletes nodes", "Saves data"], "a": "Decides output"}]', "14:50"),
            (16, "Deep Learning Specialization Overview", "https://www.youtube.com/watch?v=CS4cs9xVecg", "AI", "intermediate", 4.8, 0.68, '[{"q": "What is backpropagation?", "options": ["Weight update", "Data entry", "Forward pass", "Video play"], "a": "Weight update"}]', "9:40"),
            # Module 4 alternatives — Python for Data Analysis (IDs 17, 18)
            (17, "Python Pandas Tutorial for Beginners", "https://www.youtube.com/watch?v=vmEHCJofslg", "Python", "beginner", 4.9, 0.88, '[{"q": "What does read_csv do?", "options": ["Loads CSV", "Saves PDF", "Deletes file", "Sends email"], "a": "Loads CSV"}]', "13:10"),
            (18, "Advanced Pandas for Data Science", "https://www.youtube.com/watch?v=PcvsOaixUh8", "Python", "intermediate", 4.6, 0.80, '[{"q": "What is a groupby?", "options": ["Splitting data", "Merging files", "Deleting rows", "Sorting"], "a": "Splitting data"}]', "16:25"),
        ]
        cursor.executemany("INSERT OR IGNORE INTO video_library (video_id, title, youtube_url, topic, difficulty_level, avg_rating, typical_completion_rate, quiz_json, duration) VALUES (?,?,?,?,?,?,?,?,?)", videos)

    # Drop and recreate dropout_analysis to ensure it's fresh
    cursor.execute("DROP TABLE IF EXISTS dropout_analysis")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dropout_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            timestamp_seconds INTEGER,
            dropout_count INTEGER,
            dropout_percentage REAL,
            is_critical_point INTEGER DEFAULT 0
        )
    """)
    
    # Seed dropout points (Live DB only)
    dropouts = [
        (1, 120, 50, 0.35, 1), (1, 300, 45, 0.32, 1),
        (2, 200, 60, 0.40, 1), (3, 150, 40, 0.30, 1),
        (4, 400, 55, 0.38, 1)
    ]
    cursor.executemany("INSERT INTO dropout_analysis (video_id, timestamp_seconds, dropout_count, dropout_percentage, is_critical_point) VALUES (?,?,?,?,?)", dropouts)
    conn.commit()

    # Seed Adaptivity Log & Recommendations (Both DBs)
    for cur, con in [(cursor, conn), (cursor_p, conn_p)]:
        cur.execute("SELECT COUNT(*) FROM adaptivity_log")
        if cur.fetchone()[0] == 0:
            # Seed for Student 1001 & 9999
            for sid in [1001, 9999]:
                # 3 completed recommendations for each
                logs = [
                    (sid, 1, 'Completed Recommendation', 65.0, 85.0, 120.0, 1),
                    (sid, 2, 'Completed Recommendation', 70.0, 92.0, 150.0, 2),
                    (sid, 3, 'Completed Recommendation', 55.0, 78.0, 180.0, 3)
                ]
                cur.executemany("""
                    INSERT INTO adaptivity_log (student_id, recommendation_id, action_taken, pre_score, post_score, time_to_action, module_id)
                    VALUES (?,?,?,?,?,?,?)
                """, logs)
                
                recs = [
                    (sid, 1, 'Review ML Basics for better score', 11, 'completed'),
                    (sid, 2, 'Focus on Data Cleaning modules', 13, 'completed'),
                    (sid, 3, 'Advanced Neural Networks concepts', 15, 'completed')
                ]
                cur.executemany("""
                    INSERT INTO recommendations (student_id, module_id, recommendation_text, recommended_video_id, status)
                    VALUES (?,?,?,?,?)
                """, recs)
        con.commit()

    # 4. Add profile_photo column if missing (Migration)
    for db_file in [DB_NAME, PRESCRIPTIVE_DB]:
        try:
            c_temp = get_connection(db_file)
            c_temp.execute("ALTER TABLE students ADD COLUMN profile_photo TEXT DEFAULT 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&q=80&w=200&h=200'")
            c_temp.commit()
            c_temp.close()
        except:
            pass # Column already exists

    conn.close()
    conn_p.close()

def sync_student_data(student_id, new_data_df):
    """
    Syncs a student's metrics across edugrowth.db, prescriptive_analytics.db, 
    and the main synthetic_student_data.csv.
    """
    
    # 1. Update CSV
    try:
        if os.path.exists(DATA_PATH):
            main_df = pd.read_csv(DATA_PATH)
            # Remove old record if exists
            main_df = main_df[main_df["student_id"] != student_id]
            # Append new record
            append_df = new_data_df.drop(columns=["timestamp"], errors="ignore")
            main_df = pd.concat([main_df, append_df], ignore_index=True)
            main_df.to_csv(DATA_PATH, index=False)
    except Exception as e:
        print(f"CSV Sync Error: {e}")

    # 2. Update SQLite DBs
    for db_file in [DB_NAME, PRESCRIPTIVE_DB]:
        try:
            conn = get_connection(db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            insert_df = new_data_df.drop(columns=["timestamp"], errors="ignore")
            # Ensure student_id is first for table schema
            cols = insert_df.columns.tolist()
            if "student_id" in cols:
                cols.insert(0, cols.pop(cols.index("student_id")))
                insert_df = insert_df[cols]
            
            insert_df.to_sql("students", conn, if_exists="append", index=False)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DB Sync Error ({db_file}): {e}")
            insert_df.to_sql("students", conn, if_exists="append", index=False)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DB Sync Error ({db_file}): {e}")

if __name__ == "__main__":
    init_db()
