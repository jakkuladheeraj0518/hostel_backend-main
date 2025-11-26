"""
Content filtering and spam detection utilities for reviews
"""
import re
from typing import Tuple, List

# Spam detection keywords
SPAM_KEYWORDS = [
    "spam", "fake", "bot", "advertisement", "promo", "promotion", 
    "click here", "visit", "website", "link", "buy now", "discount",
    "offer", "deal", "free", "win", "prize", "lottery", "money"
]

# Inappropriate content keywords
INAPPROPRIATE_KEYWORDS = [
    "hate", "racist", "sexist", "offensive", "inappropriate", 
    "violence", "threat", "abuse", "harassment", "discrimination"
]

# Quality indicators
QUALITY_INDICATORS = {
    "positive": ["clean", "good", "excellent", "great", "amazing", "wonderful", "helpful", "friendly"],
    "negative": ["dirty", "bad", "terrible", "awful", "horrible", "rude", "unhelpful", "noisy"],
    "specific": ["room", "bathroom", "kitchen", "wifi", "food", "staff", "location", "price", "facilities"]
}

def detect_spam(text: str) -> Tuple[bool, List[str]]:
    """
    Detect potential spam content in review text
    Returns: (is_spam, found_keywords)
    """
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in SPAM_KEYWORDS:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    # Additional spam patterns
    spam_patterns = [
        r'\b\d{10,}\b',  # Long numbers (phone numbers)
        r'http[s]?://\S+',  # URLs
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
        r'(.)\1{4,}',  # Repeated characters (aaaaa)
    ]
    
    for pattern in spam_patterns:
        if re.search(pattern, text):
            found_keywords.append("suspicious_pattern")
            break
    
    # Check for excessive capitalization
    if len(text) > 20 and sum(1 for c in text if c.isupper()) / len(text) > 0.5:
        found_keywords.append("excessive_caps")
    
    is_spam = len(found_keywords) >= 2 or any(keyword in ["advertisement", "promo", "click here"] for keyword in found_keywords)
    
    return is_spam, found_keywords

def detect_inappropriate_content(text: str) -> Tuple[bool, List[str]]:
    """
    Detect inappropriate content in review text
    Returns: (is_inappropriate, found_keywords)
    """
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in INAPPROPRIATE_KEYWORDS:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    # Check for excessive profanity patterns
    profanity_patterns = [
        r'\b[f][u][c][k]\b',
        r'\b[s][h][i][t]\b',
        r'\b[d][a][m][n]\b'
    ]
    
    for pattern in profanity_patterns:
        if re.search(pattern, text_lower):
            found_keywords.append("profanity")
            break
    
    is_inappropriate = len(found_keywords) > 0
    
    return is_inappropriate, found_keywords

def content_quality_score(text: str, rating: int) -> float:
    """
    Calculate content quality score (0.0 to 1.0)
    Higher score indicates better quality content
    """
    score = 0.0
    text_lower = text.lower()
    
    # Length factor (optimal length 50-500 characters)
    length = len(text)
    if 50 <= length <= 500:
        score += 0.3
    elif 20 <= length < 50 or 500 < length <= 1000:
        score += 0.2
    elif length < 20:
        score += 0.1
    
    # Specific details factor
    specific_count = sum(1 for word in QUALITY_INDICATORS["specific"] if word in text_lower)
    score += min(specific_count * 0.1, 0.3)
    
    # Balanced sentiment (not all positive or all negative)
    positive_count = sum(1 for word in QUALITY_INDICATORS["positive"] if word in text_lower)
    negative_count = sum(1 for word in QUALITY_INDICATORS["negative"] if word in text_lower)
    
    if positive_count > 0 and negative_count > 0:
        score += 0.2  # Balanced review
    elif positive_count > 0 or negative_count > 0:
        score += 0.1  # Some sentiment
    
    # Rating consistency (extreme ratings should have strong sentiment)
    if rating in [1, 2] and negative_count > 0:
        score += 0.1
    elif rating in [4, 5] and positive_count > 0:
        score += 0.1
    elif rating == 3:  # Neutral rating
        score += 0.1
    
    # Grammar and structure (basic check)
    sentences = text.split('.')
    if len(sentences) > 1:
        score += 0.1  # Multiple sentences
    
    return min(score, 1.0)

def moderate_content(text: str, rating: int) -> dict:
    """
    Comprehensive content moderation
    Returns moderation results and recommendations
    """
    is_spam, spam_keywords = detect_spam(text)
    is_inappropriate, inappropriate_keywords = detect_inappropriate_content(text)
    quality_score = content_quality_score(text, rating)
    
    # Determine action
    if is_inappropriate:
        action = "reject"
        reason = f"Inappropriate content detected: {', '.join(inappropriate_keywords)}"
    elif is_spam:
        action = "flag_spam"
        reason = f"Potential spam detected: {', '.join(spam_keywords)}"
    elif quality_score >= 0.7:
        action = "auto_approve"
        reason = "High quality content"
    elif quality_score >= 0.4:
        action = "manual_review"
        reason = "Moderate quality content - manual review recommended"
    else:
        action = "flag_low_quality"
        reason = "Low quality content detected"
    
    return {
        "action": action,
        "reason": reason,
        "quality_score": quality_score,
        "is_spam": is_spam,
        "is_inappropriate": is_inappropriate,
        "spam_keywords": spam_keywords,
        "inappropriate_keywords": inappropriate_keywords
    }
