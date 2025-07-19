
import requests
from bs4 import BeautifulSoup

def estrai_blocco_smart(keyword):
    url = "https://docs.google.com/document/d/e/2PACX-1vSqy0-FZAqOGvnCFZwwuBfT1cwXFpmSpkWfrRiT8RlbQpdQy-_1hOaqIslih5ULSa0XhVt0V8QeWJDP/pub"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]

        # Cerca riga che contiene la parola chiave
        for i, p in enumerate(paragraphs):
            if keyword.lower() in p.lower():
                start = max(0, i - 2)
                end = min(len(paragraphs), i + 4)
                blocco = paragraphs[start:end]
                return "\n".join(blocco).strip()

        return ""
    except Exception as e:
        return f"[ERRORE estrai_blocco_smart] {e}"
