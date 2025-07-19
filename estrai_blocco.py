
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
        salva = False
        for p in paragraphs:
            if keyword.lower() in p.lower():
                salva = True
            elif salva and (p.strip() == "" or len(p.strip()) <= 1):
                break
            if salva:
                blocco.append(p)
        return "\n".join(blocco).strip()
    except Exception as e:
        print(f"[ERRORE blocco tematico] {e}")
        return ""
