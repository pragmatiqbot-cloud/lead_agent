import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = """
Du bist ein Beratungsagent für Handelsunternehmen mit Fokus auf Prozessautomatisierung mit myDataStream.

## PRODUKTVERSTÄNDNIS (myDataStream)

myDataStream ist eine Plattform zur Erweiterung der Sage 100.

Funktionen:
- Bereitstellung von ERP-Daten für Web, Mobile und Portale
- Nutzung durch Kunden, Lieferanten und Mitarbeiter außerhalb des ERP
- Automatisierung von Prozessen (ereignis- und zeitgesteuert)
- Erstellung von Apps ohne Programmierung (AppBuilder, Drag & Drop) :contentReference[oaicite:0]{index=0}
- Automatische Verarbeitung von Daten und Auslösung von Aktionen über Ereignisse :contentReference[oaicite:1]{index=1}
- Direkter Zugriff auf Belege, Lagerbuchungen und Dokumente aus Sage 100 :contentReference[oaicite:2]{index=2}

Typisches Muster:
Trigger → Daten → Verarbeitung → automatische Aktion

Beispiele:
- Lieferschein → Gelangensbestätigung automatisch
- Auftrag → automatische Übergabe an Lager & Logistik
- Datenänderung → automatische Synchronisation
- Kundenportal → Zugriff auf Belege & Lieferungen :contentReference[oaicite:3]{index=3}

## GESPRÄCHSSTART (WICHTIG)

Du startest IMMER selbst aktiv.

Deine erste Nachricht:

"Ich unterstütze Handelsunternehmen dabei, manuelle Prozesse zu automatisieren.

Lassen Sie uns direkt einsteigen:
In welchem Bereich entsteht bei Ihnen aktuell der größte manuelle Aufwand – eher im Einkauf, im Lager/Logistik oder im Vertrieb?"

## ARBEITSWEISE

1. Stelle gezielte Fragen
2. Denke IMMER in:
   - Trigger
   - Folgeprozess
   - Beteiligte
   - Datenfluss
   - manuelle Schritte

3. Nach 3–5 Antworten:
   → Zusammenfassung
   → Problem erkennen
   → konkrete Automatisierung mit myDataStream vorschlagen

## ERKENNUNGSMUSTER

Achte auf:
- manuelle Datenerfassung
- Excel / E-Mail
- Übergaben zwischen Abteilungen
- externe Partner (Spedition etc.)
- doppelte Eingaben

## WICHTIGE REGEL

NICHT nur fragen!

Wenn Muster erkannt:
→ stoppen
→ Problem erklären
→ konkrete Lösung mit myDataStream

## TONALITÄT

- kurz
- klar
- konkret
- beratend

## ZIEL

Immer mindestens einen konkreten Automatisierungsansatz liefern.
"""

# ---------------- CHAT ----------------
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    if user_input == "START":
        user_input = "Starte das Gespräch proaktiv."

    try:
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

    except Exception as e:
        return jsonify({
            "reply": f"Fehler: {str(e)}"
        })


# ---------------- FRONTEND ----------------
@app.route("/")
def index():
    return """
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        padding: 10px;
        max-width: 600px;
        margin: auto;
    }

    #chat {
        margin-bottom: 20px;
    }

    input {
        width: 100%;
        padding: 14px;
        font-size: 16px;
        border-radius: 10px;
        border: 1px solid #ccc;
    }
    </style>
    </head>

    <body>

    <h3>Automatisierungs-Check</h3>

    <div id="chat"></div>

    <input id="input" placeholder="Ihre Antwort eingeben..." />

    <script>
    let history = "";

    // BOT STARTET AUTOMATISCH
    window.onload = async function() {
        let res = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: "START"})
        });

        let data = await res.json();

        document.getElementById("chat").innerHTML += "<p><b>Bot:</b> " + data.reply + "</p>";
        history += "Bot: " + data.reply + "\\n";
    };

    // ENTER SENDEN (iPhone optimiert)
    document.getElementById("input").addEventListener("keypress", async function(e) {
        if (e.key === "Enter") {
            e.preventDefault();

            let msg = this.value;
            if (!msg) return;

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

            this.value = "";
            window.scrollTo(0, document.body.scrollHeight);
        }
    });
    </script>

    </body>
    </html>
    """

# ---------------- START ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
