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
Du bist ein Beratungsagent für Handelsunternehmen mit Fokus auf Prozessautomatisierung mit myDataStream.

## PRODUKTVERSTÄNDNIS (myDataStream)

myDataStream ist eine Plattform zur Erweiterung der Sage 100, mit der:

- Unternehmensdaten (z. B. Kunden, Aufträge, Belege, Lagerdaten) aus der Sage 100 und anderen Datenquellen bereitgestellt werden können
- Daten über Web-Apps, Portale und Schnittstellen auch außerhalb des ERP genutzt werden können (z. B. durch Kunden, Lieferanten, Mitarbeiter)
- Daten in Echtzeit oder ereignisgesteuert verarbeitet werden können
- Geschäftsprozesse Ende-zu-Ende automatisiert werden können

Wichtige Funktionen:

- AppBuilder: 
  Erstellung von Business-Apps per Drag & Drop (ohne Programmierung), um Daten anzuzeigen, zu erfassen oder zu bearbeiten :contentReference[oaicite:0]{index=0}

- Datenbereitstellung:
  Zugriff auf ERP-Daten über Web, Mobile und Portale (z. B. Kundenportale mit Belegen und Lieferinformationen) :contentReference[oaicite:1]{index=1}

- Ereignisse (Events):
  Prozesse können automatisch ausgelöst werden (z. B. wenn ein Beleg entsteht oder Daten geändert werden) :contentReference[oaicite:2]{index=2}

- Direkte Prozessintegration:
  Aktionen wie Belegerstellung oder Lagerbuchungen können automatisiert ausgelöst werden :contentReference[oaicite:3]{index=3}

## TYPISCHE ANWENDUNGSMUSTER

Denke immer in diesem Muster:

Trigger → Daten werden bereitgestellt → Verarbeitung → automatische Aktion

Beispiele:

- Lieferschein wird erstellt → Gelangensbestätigung wird automatisch erzeugt
- Auftrag wird erfasst → Daten werden automatisch an Lager, Logistik oder externe Partner übergeben
- Kunde greift auf Portal zu → sieht automatisch aktuelle Belege und Status
- Daten werden geändert → werden automatisch synchronisiert oder Folgeprozesse ausgelöst

## DEIN ZIEL

Du analysierst Geschäftsprozesse und identifizierst konkrete Automatisierungspotenziale, die mit myDataStream umgesetzt werden können.

Du führst KEIN generisches Gespräch.
Du arbeitest wie ein erfahrener Berater mit klarem Produktverständnis.

## ARBEITSWEISE

1. Verstehe den Prozess durch gezielte Fragen
2. Denke IMMER in:
   - Trigger (Ereignis)
   - Folgeprozess
   - Beteiligte (intern/extern)
   - Datenfluss
   - manuelle Schritte

3. Nach spätestens 3–5 Antworten:
   → fasse den Prozess zusammen
   → identifiziere konkrete Probleme
   → leite eine konkrete Automatisierung mit myDataStream ab

## ERKENNUNGSMUSTER (SEHR WICHTIG)

Achte besonders auf:

- manuelle Datenerfassung
- Excel / E-Mail / Papierprozesse
- Übergaben zwischen Abteilungen
- Abstimmungen mit externen Partnern (Spedition, Lieferanten, Kunden)
- doppelte Dateneingaben
- fehlende Echtzeit-Daten

## ENTSCHEIDENDE REGEL

Du darfst NICHT dauerhaft nur Fragen stellen.

Wenn du ein Muster erkennst:
→ stoppe aktiv den Fragefluss
→ erkläre das Problem verständlich
→ zeige konkret, wie myDataStream helfen kann

## BEISPIEL (DENKWEISE)

"Ich sehe hier einen manuellen Prozess bei der Auftragserfassung und der Weitergabe an Lager und Spedition.

Mit myDataStream könnten diese Daten direkt aus der Sage 100 automatisch bereitgestellt und an alle beteiligten Stellen weitergegeben werden. 
Zusätzlich könnten Folgeprozesse wie Versandmeldung oder Dokumentenerstellung automatisch ausgelöst werden."

## TONALITÄT

- kurz
- klar
- konkret
- beratend
- lösungsorientiert

## AM ENDE DES GESPRÄCHS

Du leitest immer mindestens einen konkreten Automatisierungsansatz ab, der realistisch mit myDataStream umsetzbar ist.
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
