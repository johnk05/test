import sqlite3
from db_utils import get_connection

def generate_recommendations(student_id, module_id, quiz_score, sentiment_label=None):
    """
    Generates personalized recommendations based on score and sentiment.
    """
    recommendations = []
    
    # Base logic on quiz score
    if quiz_score < 60:
        rec_text = "It seems you struggled with this module. We recommend revisiting the fundamental concepts."
        difficulty_target = "beginner"
        adjustment = "revision"
    elif quiz_score < 80:
        rec_text = "Good progress! A bit more practice on these concepts will make you proficient."
        difficulty_target = "beginner"
        adjustment = "practice"
    else:
        rec_text = "Excellent performance! You're ready for more advanced topics."
        difficulty_target = "intermediate"
        adjustment = "advanced"

    if sentiment_label == "Negative":
        rec_text += " We noticed you found this challenging. Don't worry, here is a highly-rated alternative resource."

    # Map module_id to topic for targeted alternative video selection
    topic_map = {1: "ML", 2: "Data Science", 3: "AI", 4: "Python"}
    topic = topic_map.get(module_id, "ML")

    # Fetch a recommended video with matching topic and target difficulty (exclude original module videos 1-4)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT video_id, title, youtube_url FROM video_library 
        WHERE topic = ? AND difficulty_level = ? AND video_id > 10
        LIMIT 1
    """, (topic, difficulty_target))
    
    video = cursor.fetchone()
    
    if not video:
        # Fallback if no matching video
        cursor.execute("SELECT video_id, title, youtube_url FROM video_library WHERE video_id != ? LIMIT 1", (module_id,))
        video = cursor.fetchone()

    if video:
        rec_id_val, title, url = video
        full_rec_text = f"{rec_text} Suggested resource: {title}"
        
        # Save recommendation to BOTH DBs
        from db_utils import DB_NAME, PRESCRIPTIVE_DB
        for db_name in [DB_NAME, PRESCRIPTIVE_DB]:
            db_conn = get_connection(db_name)
            cursor_db = db_conn.cursor()
            cursor_db.execute("""
                INSERT INTO recommendations (student_id, module_id, recommendation_text, recommended_video_id)
                VALUES (?, ?, ?, ?)
            """, (student_id, module_id, full_rec_text, rec_id_val))
            db_conn.commit()
            db_conn.close()
        
        # Generate Prescriptive Constraints for Prediction Tab
        # We calculate the "Optimized" state based on the recommendation
        target_quiz = min(100, quiz_score + 15) # Assume 15% improvement
        engagement_boost = 20.0 # Assume 20% engagement boost
        
        conn_p = get_connection(PRESCRIPTIVE_DB)
        cursor_p = conn_p.cursor()
        cursor_p.execute("""
            INSERT OR REPLACE INTO prescriptive_constraints 
            (student_id, suggested_time_increase, target_quiz_score, recommended_engagement_boost, predicted_impact_label)
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, 0.5, target_quiz, engagement_boost, "Expected Improvement"))
        
        # Also update the 'students' table in prescriptive DB to reflect the target state
        cursor_p.execute("""
            UPDATE students 
            SET quiz_score = ?, engagement_score = engagement_score + ?
            WHERE student_id = ?
        """, (target_quiz, engagement_boost, student_id))
        
        conn_p.commit()
        conn_p.close()

        recommendations.append({
            "text": full_rec_text,
            "video_url": url,
            "video_title": title
        })
        
    conn.close()
    return recommendations

def fetch_active_recommendations(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.rec_id, r.recommendation_text, v.youtube_url, v.title, r.status
        FROM recommendations r
        JOIN video_library v ON r.recommended_video_id = v.video_id
        WHERE r.student_id = ? AND r.status = 'pending'
        ORDER BY r.timestamp DESC
    """, (student_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "text": row[1],
        "url": row[2],
        "title": row[3],
        "status": row[4]
    } for row in rows]
