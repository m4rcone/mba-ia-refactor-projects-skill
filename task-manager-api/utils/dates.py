from datetime import datetime, timezone


def utcnow():
    """Naive UTC timestamp, replacing the deprecated datetime.utcnow()."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
