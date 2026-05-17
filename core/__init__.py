import re

# Normalize string inputs for friendlier API use
def normalize_input(value: str) -> str:
    return re.sub(r"[\s\-_]+", "-", value.strip().upper())