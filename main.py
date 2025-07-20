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
        lang = detect(user_prompt)

        system_prompts = {
            "it": "Sei un esperto tecnico dei prodotti Tecnaria. Rispondi in italiano solo alla domanda, usando il testo fornito se presente. Se non c'è una risposta nel testo, puoi usare la tua conoscenza.",
            "en": "You are a technical expert on Tecnaria products. Answer in English using only the provided text if available. If it's missing, rely on your own knowledge.",
            "fr": "Vous êtes un expert technique des produits Tecnaria. Répondez en français en utilisant le texte fourni si disponible, sinon utilisez vos connaissances.",
            "de": "Sie sind ein technischer Experte für Tecnaria-Produkte. Antworten Sie auf Deutsch nur mit dem bereitgestellten Text oder Ihrem Wissen.",
            "es": "Eres un experto técnico en productos Tecnaria. Responde en español usando el texto si está disponible; si no, usa tus conocimientos."
        }
        system_prompt = system_prompts.get(lang, system_prompts["en"])

        # STEP 1: Prova estrazione smart se c'è una keyword
        keyword = trova_keyword(user_prompt)
        context = ""
        if keyword:
            context = estrai_blocco_smart(keyword)

        # STEP 2: Prova a prendere tutto il documento
        if not context.strip():
            context = estrai_testo_vocami()

        # STEP 3: Prova scraping sito
        if not context.strip():
            context = scrape_tecnaria_results(user_prompt)

        # STEP 4: Se ancora nulla, GPT può rispondere liberamente
        if context.strip():
            prompt = f"""Rispondi solo alla domanda sottostante, usando il testo fornito. Non includere contenuti aggiuntivi se non richiesti esplicitamente nella domanda. Se un concetto è implicito ma presente, puoi usarlo.

TESTO:
{context}

DOMANDA:
{user_prompt}

RISPOSTA:"""
        else:
            prompt = f"""Rispondi con precisione alla domanda qui sotto basandoti sulle tue conoscenze tecniche aggiornate, come se fossi un esperto dei prodotti e dei servizi di Tecnaria.

DOMANDA:
{user_prompt}

RISPOSTA:"""

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
