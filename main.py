from flask import Flask, request, jsonify, render_template
import os
from bridge_scraper import estrai_testo_vocami
from scraper_tecnaria import scrape_tecnaria_results
from estrai_blocco_smart import estrai_blocco_smart
from openai import OpenAI
from langdetect import detect

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Lista di frasi che indicano domanda generale
DOMANDE_GENERICHE = [
    "parlami di tecnaria",
    "cos'è tecnaria",
    "cosa fa tecnaria",
    "di cosa si occupa tecnaria",
    "tell me about tecnaria",
    "who is tecnaria",
    "what does tecnaria do"
]

def trova_keyword(dominio):
    parole = dominio.lower().split()
    parole_chiave = ["chiodatrice", "chiodatrici", "p560", "pulsa", "connettore", "software", "diapason", "tbs", "solaio", "blocco", "rinforzo", "collaborante"]
    for parola in parole_chiave:
        if parola in parole:
            return parola
    return None

def is_domanda_generica(prompt):
    return any(p in prompt.lower() for p in DOMANDE_GENERICHE)

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        user_prompt = request.json.get("prompt", "").strip()
        lang = detect(user_prompt)

        # Prompt GPT coerente con la lingua
        system_prompts = {
            "it": "Sei un esperto tecnico di Tecnaria. Rispondi in italiano. Usa il testo se è pertinente, altrimenti rispondi con le tue conoscenze.",
            "en": "You are a technical expert on Tecnaria. Answer in English. Use the text only if relevant, otherwise rely on your knowledge.",
            "fr": "Vous êtes un expert de Tecnaria. Répondez en français. Utilisez le texte s'il est pertinent, sinon utilisez vos connaissances.",
            "de": "Sie sind ein Experte für Tecnaria. Antworten Sie auf Deutsch. Verwenden Sie den Text nur, wenn er relevant ist.",
            "es": "Eres un experto de Tecnaria. Responde en español. Usa el texto si es relevante, si no, usa tu conocimiento."
        }
        system_prompt = system_prompts.get(lang, system_prompts["en"])

        # 🧠 Se domanda è GENERICA, ignora i documenti
        if is_domanda_generica(user_prompt):
            prompt = f"""Rispondi in modo chiaro e professionale alla domanda qui sotto, usando le tue conoscenze da esperto di Tecnaria.

DOMANDA:
{user_prompt}

RISPOSTA:"""
        else:
            # 🔍 Cerca testo tematico specifico
            keyword = trova_keyword(user_prompt)
            context = ""
            if keyword:
                context = estrai_blocco_smart(keyword)

            # 🧩 Fallback documento completo
            if not context.strip():
                context = estrai_testo_vocami()

            # 🌐 Fallback scraping
            if not context.strip():
                context = scrape_tecnaria_results(user_prompt)

            # 🧾 Prompt costruito con testo utile (se esiste)
            if context.strip():
                prompt = f"""Rispondi solo alla domanda sottostante. Usa il testo qui sotto se è pertinente.
Non aggiungere contenuti che non siano richiesti esplicitamente.

TESTO:
{context}

DOMANDA:
{user_prompt}

RISPOSTA:"""
            else:
                prompt = f"""Rispondi in modo chiaro e professionale alla domanda qui sotto, usando le tue conoscenze da esperto di Tecnaria.

DOMANDA:
{user_prompt}

RISPOSTA:"""

        # GPT chiamata finale
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        answer = response.choices[0].message.content
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": f"Errore: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
