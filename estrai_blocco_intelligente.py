
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
        for i, p in enumerate(paragraphs):
            if keyword.lower() in p.lower():
                found = True
                blocco = paragraphs[i:i+6]  # Prendi i prossimi 6 paragrafi
                break

        if found and blocco:
            return "\n".join(blocco).strip()
        else:
            return "❌ Nessun blocco trovato con la parola chiave: " + keyword

    except Exception as e:
        return f"[ERRORE] {e}"

if __name__ == "__main__":
    keyword = "chiodatrice"
    print("🔍 Blocco tematico per:", keyword)
    print("-" * 60)
    testo = estrai_blocco_tematico(keyword)
    print(testo)
