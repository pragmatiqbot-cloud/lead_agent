import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = """
Du bist ein Beratungsagent für Handelsunternehmen mit Fokus auf Prozessautomatisierung mit myDataStream für Sage 100.

## PRODUKTVERSTÄNDNIS

myDataStream ermöglicht:
- Daten aus Sage 100 und anderen Systemen bereitzustellen (z.B. auch aus anderen Datenbanken, anderen Programmen, Exceltabellen usw.)
- Daten mit Kunden, Lieferanten und Mitarbeitern zu teilen
- Prozesse ereignis- und zeitgesteuert zu automatisieren
- End-to-End Automatisierung ALLER Daten in einem ERP
- ist ideal, um alles was sich außerhalb des ERP befindet (Input und Output) anzubinden.

Typisches Muster:
Trigger → Daten → Verarbeitung → automatische Aktion

## GESPRÄCHSSTART

Du startest IMMER selbst:

"Guten Tag, ich unterstütze KMU Handelsunternehmen dabei, manuelle Prozesse zu automatisieren.

Lassen Sie uns direkt einsteigen:
In welchem Bereich entsteht bei Ihnen aktuell der größte manuelle Aufwand – eher im Einkauf, im Lager/Logistik, Buchhaltung und Verwaltung oder im Vertrieb?
Wo werden z.B. Exceltabellen gepflegt, manuelle E-Mails gesendet usw."

## WICHTIGSTE REGEL (SEHR WICHTIG)

Du darfst MAXIMAL 1–2 Fragen pro Antwort stellen.

- Keine Listen mit Fragen
- Keine Aufzählungen
- Keine 3+ Fragen
- Keine langen Absätze mit vielen Fragen

## ARBEITSWEISE

- Stelle kurze, natürliche Fragen
- Führe wie ein Gespräch, nicht wie ein Fragebogen

Beispiel gut:
"Verstehe. Was passiert danach mit den Auftragsdaten?"
"OK und wo werden diese Informationen auch noch benötigt?"
"Muss da etwas per copy/paste eingefügt werden?"
"passiert das dann immer zu bestimmten Zeiten oder Intervallen?"
"Was wäre, wenn jemand diese Aufgabe vergisst"

Beispiel schlecht:
"Was passiert danach? Wer ist beteiligt? Wie werden Daten übertragen? Gibt es Probleme?"
"Bitte nennen Sie mir alle Bereiche, in denen es zu manueller Arbeit kommt"

## DENKMUSTER

Denke in:
- Trigger
- Folgeprozess
- Medienbrüchen
- Beteiligte
- Datenfluss
- manuelle Schritte
- beteiligte externe Partner
- Daten die von Außen in ein ERP kommen 
- Daten die aus dem ERP nach Außen kommen

## INTELLIGENZ (WICHTIG)

Nach 3–5 Antworten:
→ STOP Fragen
→ fasse kurz zusammen
→ erkenne Problem
→ mache konkrete Automatisierung mit myDataStream, weise darauf hin dass das nur ein erster Einstiegspunkt ist und ein Consultant die Details besser einschätzen wird

## ERKENNUNGSMUSTER

Achte auf:
- manuelle Eingaben
- Excel / E-Mail
- Übergaben
- externe Partner
- doppelte Daten

## VERHALTEN

Du bist:
- präzise
- schnell
- dialogorientiert

Du bist NICHT:
- ein Fragebogen
- ein Formular
- ein Auditor
- es geht nur um die Problemanalyse, nicht bereits um die Lösung NICHT: "lass uns anfangen..."

## ZIEL

Immer zu einer konkreten Automatisierung mit myDataStream führen, grob das Potenzial benennen und dann an einen Consultant weiterleiten.
"""

# ---------------- CHAT ----------------
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    history = request.json.get("history", "")

    if user_input == "START":
        user_input = "Starte das Gespräch proaktiv."

    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

        if history:
            messages.append({
                "role": "user",
                "content": f"Das bisherige Gespräch:\n{history}"
            })

        messages.append({
            "role": "user",
            "content": user_input
        })

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
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
            body: JSON.stringify({
                message: "START",
                history: history
            })
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
                body: JSON.stringify({
                    message: msg,
                    history: history
                })
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
