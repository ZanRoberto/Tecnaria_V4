from flask import Flask, request, jsonify, render_template
import os
from bridge_scraper import estrai_testo_vocami
from scraper_tecnaria import scrape_tecnaria_results
from estrai_blocco_smart import estrai_blocco_smart
from openai import OpenAI
from langdetect import detect

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def trova_keyword(dominio):
    parole = dominio.lower().split()
    parole_chiave = ["chiodatrice", "chiodatrici", "p560", "pulsa", "connettore", "software", "diapason", "tbs", "accoppiamento", "solaio"]
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
        lang = detect(user_prompt)

        # Prompt system coerente con lingua
        system_prompts = {
            "it": "Sei un esperto tecnico di Tecnaria. Rispondi in italiano. Usa il testo solo se è utile alla domanda. Se la domanda è più generale o il testo è irrilevante, usa le tue conoscenze.",
            "en": "You are a technical expert on Tecnaria. Answer in English. Use the text only if it's relevant to the question. If the question is general or the text is not useful, rely on your knowledge.",
            "fr": "Vous êtes un expert des produits Tecnaria. Répondez en français. Utilisez le texte uniquement s'il est pertinent. Sinon, utilisez vos connaissances.",
            "de": "Sie sind ein Experte für Tecnaria. Antworten Sie auf Deutsch. Verwenden Sie den Text nur, wenn er relevant ist. Andernfalls verwenden Sie Ihr Wissen.",
            "es": "Eres un experto en productos Tecnaria. Responde en español. Usa el texto solo si es relevante. Si no, usa tu conocimiento."
        }
        system_prompt = system_prompts.get(lang, system_prompts["en"])

        # STEP 1: cerco keyword utile
        keyword = trova_keyword(user_prompt)
        context = ""
        if keyword:
            context = estrai_blocco_smart(keyword)

        # STEP 2: se ancora vuoto, provo a usare tutto il documento
        if not context.strip():
            context = estrai_testo_vocami()

        # STEP 3: se ancora nulla, provo lo scraping dal sito
        if not context.strip():
            context = scrape_tecnaria_results(user_prompt)

        # STEP 4: costruttore finale del prompt
        if context.strip():
            prompt = f"""Rispondi solo alla domanda sottostante.
Se il testo è utile alla domanda, usalo.
Se la domanda è più generale, o se il testo non è rilevante, puoi rispondere basandoti sulla tua conoscenza tecnica.

TESTO DISPONIBILE:
{context}

DOMANDA:
{user_prompt}

RISPOSTA:"""
        else:
            prompt = f"""Rispondi alla domanda qui sotto come esperto dei prodotti Tecnaria.
Puoi usare la tua conoscenza anche se nessun testo è stato fornito.

DOMANDA:
{user_prompt}

RISPOSTA:"""

        # Invio a GPT
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
