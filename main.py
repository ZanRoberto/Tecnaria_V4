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

        try:
            lang = detect(user_prompt)
        except:
            lang = "en"

        system_prompts = {
            "it": "Sei un esperto tecnico dei prodotti Tecnaria. Rispondi usando il testo fornito, collegando concetti impliciti se necessario. Se non trovi risposta lì, puoi attingere da altre fonti ufficiali Tecnaria.",
            "en": "You are a technical expert on Tecnaria products. Use the provided text to answer, connecting related concepts. If the answer is not there, refer to other official Tecnaria sources.",
            "fr": "Vous êtes un expert technique des produits Tecnaria. Utilisez le texte fourni pour répondre, ou appuyez-vous sur d'autres sources officielles si nécessaire.",
            "de": "Sie sind ein technischer Experte für Tecnaria-Produkte. Verwenden Sie den bereitgestellten Text oder greifen Sie bei Bedarf auf andere offizielle Quellen zurück.",
            "es": "Eres un experto técnico en productos Tecnaria. Usa el texto proporcionado y si es necesario, apóyate en otras fuentes oficiales."
        }
        system_prompt = system_prompts.get(lang, system_prompts["en"])

        # 🔍 Prova prima blocco smart
        keyword = trova_keyword(user_prompt)
        context = ""
        if keyword:
            context = estrai_blocco_smart(keyword)

        # 🔁 Fallback su intero documento
        if not context.strip():
            context = estrai_testo_vocami()

        # 🔁 Fallback finale su scraping sito
        if not context.strip():
            context = scrape_tecnaria_results(user_prompt)

        if not context.strip():
            return jsonify({"error": "Nessuna informazione trovata."}), 400

        prompt = f"""Il testo seguente è stato raccolto da fonti ufficiali Tecnaria. Usa solo questo contenuto per rispondere, riformulando se necessario. Se qualcosa è implicito ma chiaro, puoi includerlo nella risposta.

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
            temperature=0.3
        )

        answer = response.choices[0].message.content
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": f"Errore: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
