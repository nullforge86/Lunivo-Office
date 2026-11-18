import re

def _ohne_schalter(anweisung: str) -> str:
    return re.split(r"\s\\[#@*lohn]", " " + anweisung, maxsplit=1)[0].strip()
