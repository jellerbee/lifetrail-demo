import re
from typing import List

# very simple keyword extractor placeholder
def extract_keywords(text: str, k: int = 5) -> List[str]:
    words = re.findall(r"[A-Za-z0-9_]+", text.lower())
    freq = {}
    for w in words:
        if len(w) < 3: continue
        freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:k]]

# simple "AI" summarizer stub (replace with real LLM call)
async def summarize(text: str) -> str:
    return f"Life Moment: {text[:160]}..." if len(text) > 160 else f"Life Moment: {text}"