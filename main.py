
from flask import Flask, request, jsonify, render_template
import os
from bridge_scraper import estrai_testo_vocami
from scraper_tecnaria import scrape_tecnaria_results
from estrai_blocco_intelligente import estrai_blocco_tematico
from openai import OpenAI
from langdetect import detect

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def trova_keyword(dominio):
    parole = dominio.lower().split()
    parole_chiave = ["chiodatrice", "connettore", "software", "diapason", "p560", "pulsa", "cemento", "acciaio", "legno"]
    for parola in parole_chiave:
        if parola in parole:
            return parola
    return None

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        user_prompt = request.json.get("prompt", "").strip()

        try:
            lang = detect(user_prompt)
        except:
            lang = "en"

        system_prompts = {
            "it": "Sei un esperto tecnico dei prodotti Tecnaria. Rispondi usando solo il testo fornito, ma puoi riformulare, collegare concetti simili o impliciti se presenti. Non è necessario che il testo contenga le stesse parole della domanda.",
            "en": "You are a technical expert on Tecnaria products. Use only the provided text to answer, but you can reformulate and connect related or implicit concepts. Exact word matching is not required.",
            "fr": "Vous êtes un expert des produits Tecnaria. Utilisez uniquement le texte fourni, mais vous pouvez reformuler ou déduire si nécessaire. Une correspondance exacte n'est pas requise.",
            "de": "Sie sind ein Experte für Tecnaria-Produkte. Verwenden Sie ausschließlich den bereitgestellten Text, aber Sie dürfen Begriffe umformulieren oder logisch verknüpfen.",
            "es": "Eres un experto en productos Tecnaria. Usa únicamente el texto proporcionado, pero puedes reformular o deducir si es necesario."
        }
        system_prompt = system_prompts.get(lang, system_prompts["en"])

        # 🧠 Estrai il blocco giusto
        keyword = trova_keyword(user_prompt)
        context = ""
        if keyword:
            context = estrai_blocco_tematico(keyword)

        # Fallback
        if not context.strip():
            context = estrai_testo_vocami()
            if user_prompt.lower() not in context.lower():
                context = scrape_tecnaria_results(user_prompt)

        if not context.strip():
            return jsonify({"error": "Nessuna informazione trovata."}), 400

        prompt = f"""Il testo seguente contiene informazioni tecniche ufficiali di Tecnaria.
Puoi rispondere solo usando questo testo, ma sei autorizzato a riformulare, sintetizzare e collegare concetti anche se non sono scritti in modo identico.

TESTO:
{context}

DOMANDA:
{user_prompt}

RISPOSTA TECNICA:"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        answer = response.choices[0].message.content
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": f"Errore: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
