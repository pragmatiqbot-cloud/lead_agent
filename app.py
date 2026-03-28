import os
from flask import Flask, request, jsonify, send_file
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------- USE CASES (einfach erweiterbar) --------
USE_CASES = """
[
  {
    "name": "Automatische Gelangensbestätigung",
    "prozessbereich": "Logistik",
    "trigger": "Lieferschein für EU-Kunden wird erstellt",
    "beschreibung": "Automatische Erstellung und Versand der Gelangensbestätigung"
  }
]
"""

# -------- SYSTEM PROMPT --------
SYSTEM_PROMPT = f"""
Du bist ein Beratungsagent für Handelsunternehmen mit Fokus auf Automatisierung.

Du analysierst Prozesse anhand von:
- Trigger (Ereignis)
- Folgeprozess
- Beteiligte
- Datenfluss
- manuelle Schritte

Stelle kurze, natürliche Fragen wie:
- "Was passiert danach?"
- "Wie gelangen diese Daten zu ...?"

Ziel:
Automatisierungspotenziale erkennen.

Bekannte Beispiele:
{USE_CASES}

Am Ende des Gesprächs soll ein strukturierter Lead erstellt werden.
"""

# -------- CHAT ENDPOINT --------
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
    )

    return jsonify({
        "reply": response.choices[0].message.content
    })

# -------- LEAD GENERIERUNG --------
@app.route("/lead", methods=["POST"])
def lead():
    conversation = request.json.get("conversation")

    prompt = f"""
    {conversation}

    Erstelle einen strukturierten Sales-Lead:

    - Prozessbereich
    - Trigger
    - Aktueller Ablauf
    - Probleme
    - Automatisierungsidee
    - Relevanz
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return jsonify({
        "lead": response.choices[0].message.content
    })

# -------- SIMPLE FRONTEND --------
@app.route("/")
def index():
    return """
    <html>
    <body style="font-family: Arial; max-width: 700px; margin: auto;">
    <h2>Automatisierungs-Check (Handel)</h2>

    <div id="chat"></div>

    <input id="input" style="width:80%;" placeholder="Ihre Antwort..." />
    <button onclick="send()">Senden</button>
    <button onclick="createLead()">Lead erstellen</button>

    <script>
    let history = "";

    async function send() {
        let input = document.getElementById("input");
        let msg = input.value;

        document.getElementById("chat").innerHTML += "<p><b>Du:</b> " + msg + "</p>";
        history += "User: " + msg + "\\n";

        let res = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: msg})
        });

        let data = await res.json();

        document.getElementById("chat").innerHTML += "<p><b>Bot:</b> " + data.reply + "</p>";
        history += "Bot: " + data.reply + "\\n";

        input.value = "";
    }

    async function createLead() {
        let res = await fetch("/lead", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({conversation: history})
        });

        let data = await res.json();

        document.getElementById("chat").innerHTML += "<hr><pre>" + data.lead + "</pre>";
    }
    </script>

    </body>
    </html>
    """

# -------- START --------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
