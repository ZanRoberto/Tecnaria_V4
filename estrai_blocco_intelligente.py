
import requests
from bs4 import BeautifulSoup

def estrai_blocco_tematico(keyword):
    url = "https://docs.google.com/document/d/e/2PACX-1vSqy0-FZAqOGvnCFZwwuBfT1cwXFpmSpkWfrRiT8RlbQpdQy-_1hOaqIslih5ULSa0XhVt0V8QeWJDP/pub"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]

        blocco = []
        found = False
        buffer = []

        for i, p in enumerate(paragraphs):
            if keyword.lower() in p.lower() or p.strip().lower().startswith("### " + keyword.lower()):
                found = True
                buffer = paragraphs[i:i+6]  # prendi fino a 5 paragrafi dopo il match
                break

        if found:
            blocco.extend(buffer)

        return "\n".join(blocco).strip()
    except Exception as e:
        print(f"[ERRORE blocco tematico intelligente] {e}")
        return ""
