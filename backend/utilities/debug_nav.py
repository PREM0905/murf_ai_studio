text = "navigate to Delhi"
print(f"Input: '{text}'")
print(f"Contains 'navigate': {'navigate' in text}")
print(f"Contains 'directions': {'directions' in text}")
print(f"Contains 'route': {'route' in text}")

import re
patterns = [
    r"navigate to ([a-zA-Z\s,]+)",
    r"directions to ([a-zA-Z\s,]+)",
    r"route to ([a-zA-Z\s,]+)",
    r"go to ([a-zA-Z\s,]+)"
]

for pattern in patterns:
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        print(f"Pattern '{pattern}' matched: '{match.group(1)}'")
    else:
        print(f"Pattern '{pattern}' did not match")