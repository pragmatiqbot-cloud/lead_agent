import os
from flask import Flask, request, jsonify, send_file
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("API KEY:", os.getenv("OPENAI_API_KEY"))

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
Du bist ein Beratungsagent für Handelsunternehmen mit Fokus auf Automatisierung mit myDataStream.
Begrüße den User und stelle Dich kurz vor - sage um was es Dir geht und dass er nicht viel Zeit opfern muss.

Dein Ziel ist NICHT nur Fragen zu stellen, sondern:
- Prozesse zu verstehen
- Muster zu erkennen
- aktiv Automatisierungspotenziale aufzuzeigen

WICHTIG:
Du darfst NICHT in einer Endlosschleife von Fragen bleiben.

ARBEITSWEISE:

1. Stelle Fragen, um den Prozess zu verstehen
2. Nach wenigen Antworten (max. 3-5):
   → fasse kurz zusammen
   → erkenne Probleme
   → mache konkrete Automatisierungsvorschläge

DENKMUSTER:
- Trigger → Folgeprozess → Daten → Beteiligte → manuelle Schritte

TYPISCHE MUSTER, auf die du achten sollst:
- manuelle Datenerfassung
- Medienbrüche (z. B. E-Mail, Excel)
- Übergaben an externe (Spedition, Kunden)
- doppelte Dateneingabe

WENN du ein Muster erkennst:
→ STOPPE das Fragen
→ erkläre das Problem
→ schlage eine konkrete Automatisierung vor

Beispiel:
"Ich sehe hier einen klassischen manuellen Prozess bei der Auftragserfassung und Übergabe an die Logistik..."

WICHTIG:
- Sei proaktiv
- Denke wie ein Berater, nicht wie ein Fragebot
- Liefere Mehrwert im Gespräch

Nutze bekannte Use Cases, wenn passend.
Wenn kein Use Case passt, entwickle selbst eine sinnvolle Automatisierungsidee.

Am Ende:
→ leite einen konkreten Verbesserungsvorschlag ab
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
