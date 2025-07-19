
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
            "it": "Sei un esperto tecnico dei prodotti Tecnaria. Usa solo il testo fornito per rispondere. Se non trovi una risposta nel testo, di' che non è presente.",
            "en": "You are a technical expert on Tecnaria products. Use only the provided text to answer. If no answer is found, say it is not present.",
            "fr": "Vous êtes un expert technique des produits Tecnaria. Utilisez uniquement le texte fourni pour répondre. Si vous ne trouvez pas la réponse, dites qu'elle n'est pas présente.",
            "de": "Sie sind ein technischer Experte für Tecnaria-Produkte. Verwenden Sie nur den bereitgestellten Text. Wenn Sie keine Antwort finden, sagen Sie, dass sie nicht vorhanden ist.",
            "es": "Eres un experto técnico en productos Tecnaria. Usa solo el texto proporcionado. Si no encuentras una respuesta, di que no está presente."
        }
        system_prompt = system_prompts.get(lang, system_prompts["en"])

        # ✅ Blocco mirato
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

        prompt = f"""Devi rispondere SOLO utilizzando il contenuto fornito qui sotto. Non inventare nulla. Se la risposta non è nel testo, rispondi chiaramente: 'Il documento non contiene questa informazione.'

Contenuto Tecnaria:
{context}

Domanda:
{user_prompt}

Risposta tecnica:"""

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
