import re
import unicodedata


def slugify(value: str, *, max_length: int = 200) -> str:
    """Generate a URL-safe slug from a string."""
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[-\s]+", "-", value).strip("-")
    return value[:max_length] or "item"


def estimate_reading_time(markdown: str, *, wpm: int = 220) -> int:
    words = len(re.findall(r"\w+", markdown or ""))
    minutes = max(1, round(words / wpm))
    return minutes
