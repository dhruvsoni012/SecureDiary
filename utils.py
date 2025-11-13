# utils.py
from datetime import datetime

def format_timestamp(timestamp):
    """Format timestamp for display"""
    if not timestamp or timestamp == "N/A":
        return "N/A"
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp)
        else:
            dt = timestamp
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return str(timestamp)


def format_date_only(timestamp):
    """Format only date"""
    if not timestamp:
        return "N/A"
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp)
        else:
            dt = timestamp
        return dt.strftime("%B %d, %Y")
    except:
        return str(timestamp)


def count_words(text):
    """Count words in text"""
    if not text:
        return 0
    return len(text.split())


def get_preview(text, length=150):
    """Get preview of text"""
    if not text or len(text) <= length:
        return text
    return text[:length] + "..."


def get_mood_emoji(mood):
    """Get emoji for mood"""
    mood_emojis = {
        "Happy": "😊",
        "Sad": "😢",
        "Excited": "🎉",
        "Angry": "😠",
        "Calm": "😌",
        "Anxious": "😰",
        "Grateful": "🙏",
        "Reflective": "🤔",
        "Loved": "❤️",
        "Tired": "😴"
    }
    return mood_emojis.get(mood, "📝")