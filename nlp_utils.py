from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """
    Analyzes sentiment using VADER and TextBlob.
    Returns: score (-1 to 1), label (Positive, Neutral, Negative)
    """
    if not text or len(text.strip()) == 0:
        return 0.0, "Neutral"

    # VADER score (compound)
    vader_scores = analyzer.polarity_scores(text)
    compound_score = vader_scores['compound']
    
    # TextBlob for polarity as a backup/validation
    blob = TextBlob(text)
    blob_polarity = blob.sentiment.polarity
    
    # Combined score
    combined_score = (compound_score + blob_polarity) / 2
    
    # Classify
    if combined_score > 0.05:
        label = "Positive"
    elif combined_score < -0.05:
        label = "Negative"
    else:
        label = "Neutral"
        
    return round(combined_score, 4), label

def extract_topics_from_feedback(text):
    """
    Simple keyword extraction to identify pain points or topics of interest.
    """
    keywords = ["machine learning", "neural network", "python", "data science", "cleaning", "modeling", "math", "code", "assignment"]
    found = []
    text_lower = text.lower()
    for kw in keywords:
        if kw in text_lower:
            found.append(kw)
    return found

if __name__ == "__main__":
    test_text = "I really enjoyed the machine learning module, but the neural network part was a bit confusing."
    score, label = analyze_sentiment(test_text)
    topics = extract_topics_from_feedback(test_text)
    print(f"Score: {score}, Label: {label}, Topics: {topics}")
