import random
import string
import hashlib
import re
from secrets import choice as secure_choice


def generate_otp(length: int = 6) -> str:
    """Generate secure numeric OTP."""
    return ''.join(secure_choice(string.digits) for _ in range(length))


def hash_otp(otp: str) -> str:
    """Hash OTP using SHA-256."""
    return hashlib.sha256(otp.encode()).hexdigest()


TEMPLATE_PATTERN = re.compile(r"{{\s*(\w+)\s*}}")


def render_template(template_content: str, variables: dict) -> str:
    """
    Render SMS template:
    - Supports {{var}}, {{ var }}, {{   var   }}
    - Leaves unknown variables untouched
    - Does not break if variable missing
    """

    def replacer(match):
        key = match.group(1)
        return str(variables.get(key, match.group(0)))

    return TEMPLATE_PATTERN.sub(replacer, template_content)
