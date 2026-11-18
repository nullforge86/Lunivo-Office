from datetime import datetime

def _jetzt() -> str:
    return datetime.now().replace(microsecond=0).isoformat()
