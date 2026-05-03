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

    # Fetch a recommended video from the library
    conn = get_connection()
    cursor = conn.cursor()
    
    # Try to find a video with the target difficulty and different from current module
    cursor.execute("""
        SELECT video_id, title, youtube_url FROM video_library 
        WHERE difficulty_level = ? AND video_id != ?
        LIMIT 1
    """, (difficulty_target, module_id))
    
    video = cursor.fetchone()
    
    if not video:
        # Fallback if no matching video
        cursor.execute("SELECT video_id, title, youtube_url FROM video_library WHERE video_id != ? LIMIT 1", (module_id,))
        video = cursor.fetchone()

    if video:
        rec_id, title, url = video
        full_rec_text = f"{rec_text} Suggested resource: {title}"
        
        # Save recommendation to DB
        cursor.execute("""
            INSERT INTO recommendations (student_id, module_id, recommendation_text, recommended_video_id)
            VALUES (?, ?, ?, ?)
        """, (student_id, module_id, full_rec_text, rec_id))
        conn.commit()
        
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
