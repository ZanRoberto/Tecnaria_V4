import requests
from bs4 import BeautifulSoup

# Lista di URL pubblici (sia quello vecchio sia quello nuovo)
URLS = [
    "https://docs.google.com/document/d/e/2PACX-1vSqy0-FZAqOGvnCFZwwuBfT1cwXFpmSpkWfrRiT8RlbQpdQy-_1hOaqIslih5ULSa0XhVt0V8QeWJDP/pub",  # originale
    "https://docs.google.com/document/d/e/2PACX-1vQ-RO3DN4AexEZry9kSLhvOhikAO7FUAIxKCKlhIq9tBxXRnpzXLYfDS1oucujh9w/pub"  # nuovo
]

def estrai_blocco_smart(keyword):
    headers = {"User-Agent": "Mozilla/5.0"}

    for url in URLS:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]

            # Cerca la parola chiave in ogni documento
            for i, p in enumerate(paragraphs):
                if keyword.lower() in p.lower():
                    start = max(0, i - 2)
                    end = min(len(paragraphs), i + 4)
                    blocco = paragraphs[start:end]
                    return "\n".join(blocco).strip()
        except Exception as e:
            continue  # Prova il prossimo documento

    return ""  # Se non trovato in nessun documento
