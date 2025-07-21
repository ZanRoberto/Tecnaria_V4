import requests
from bs4 import BeautifulSoup

# Entrambi i documenti pubblici: quello originale e quello aggiunto
URLS = [
    "https://docs.google.com/document/d/e/2PACX-1vSqy0-FZAqOGvnCFZwwuBfT1cwXFpmSpkWfrRiT8RlbQpdQy-_1hOaqIslih5ULSa0XhVt0V8QeWJDP/pub",  # documento base
    "https://docs.google.com/document/d/e/2PACX-1vQ-RO3DN4AexEZry9kSLhvOhikAO7FUAIxKCKlhIq9tBxXRnpzXLYfDS1oucujh9w/pub"  # nuovo documento con elenco connettori
]

def estrai_blocco_smart(keyword):
    headers = {"User-Agent": "Mozilla/5.0"}
    blocchi_trovati = []

    for url in URLS:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]

            # Cerca blocchi attorno alla parola chiave
            for i, p in enumerate(paragraphs):
                if keyword.lower() in p.lower():
                    start = max(0, i - 2)
                    end = min(len(paragraphs), i + 4)
                    blocco = paragraphs[start:end]
                    blocchi_trovati.append("\n".join(blocco))
                    break  # Se trovi una volta è sufficiente
        except Exception as e:
            continue

    if blocchi_trovati:
        return "\n\n".join(blocchi_trovati).strip()

    # Fallback: ritorna tutto il contenuto del documento nuovo
    try:
        response = requests.get(URLS[1], headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
        return "\n".join(paragraphs).strip()
    except Exception:
        return ""
