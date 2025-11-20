"""
Password strength checker
"""

import re
from typing import Dict

__all__ = ["check_password_strength"]


def check_password_strength(password: str) -> Dict:
    """
    Check password strength and return feedback.
    Returns example:
    {
        "strength": "weak" | "medium" | "strong",
        "score": 0-100,
        "feedback": [...]
    }
    """
    score = 0
    feedback = []

    # Length check
    if len(password) >= 12:
        score += 25
    elif len(password) >= 8:
        score += 15
        feedback.append("Use at least 12 characters for stronger security")
    else:
        feedback.append("Password must be at least 8 characters long")

    # Uppercase
    if re.search(r"[A-Z]", password):
        score += 15
    else:
        feedback.append("Add uppercase letters (A-Z)")

    # Lowercase
    if re.search(r"[a-z]", password):
        score += 15
    else:
        feedback.append("Add lowercase letters (a-z)")

    # Numbers
    if re.search(r"\d", password):
        score += 15
    else:
        feedback.append("Add numbers (0-9)")

    # Special characters
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 15
    else:
        feedback.append("Add special characters (!@#$%^&*)")

    # Variety bonus
    if len(set(password)) >= len(password) * 0.7:
        score += 10

    # Avoid common patterns
    common_patterns = ["123", "abc", "password", "qwerty"]
    if not any(pattern in password.lower() for pattern in common_patterns):
        score += 5

    # Strength level
    if score >= 80:
        strength = "strong"
    elif score >= 50:
        strength = "medium"
    else:
        strength = "weak"

    return {
        "strength": strength,
        "score": min(score, 100),
        "feedback": feedback or ["Password is strong!"]
    }
