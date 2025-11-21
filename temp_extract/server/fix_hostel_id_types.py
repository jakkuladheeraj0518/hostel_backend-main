"""
Quick fix script to change all hostel_id from str to int in schemas
"""

import re
from pathlib import Path

def fix_hostel_id_in_file(filepath):
    """Fix hostel_id type from str to int in a schema file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace hostel_id: str with hostel_id: int
    original = content
    content = re.sub(r'hostel_id:\s*str', 'hostel_id: int  # Changed from str to int to match database', content)
    content = re.sub(r'hostel_id:\s*Optional\[str\]', 'hostel_id: Optional[int]  # Changed from str to int to match database', content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Files to fix
schema_files = [
    'app/schemas/room.py',
    'app/schemas/payment.py',
    'app/schemas/notice.py',
    'app/schemas/booking.py',
]

print("Fixing hostel_id types in schema files...")
print("=" * 60)

for filepath in schema_files:
    if Path(filepath).exists():
        if fix_hostel_id_in_file(filepath):
            print(f"✓ Fixed: {filepath}")
        else:
            print(f"- Skipped (no changes needed): {filepath}")
    else:
        print(f"✗ Not found: {filepath}")

print("=" * 60)
print("Done! All hostel_id fields updated to int type.")
