import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

# Vercel-дің Environment Variables-тен GROQ API KEY аламыз
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        if not GROQ_API_KEY:
            return jsonify({'response': '⚠️ GROQ_API_KEY Vercel-де орнатылмаған!'}), 500

        client = Groq(api_key=GROQ_API_KEY)
        data = request.get_json(silent=True) or {}
        user_prompt = data.get('prompt', '')

        if not user_prompt:
            return jsonify({'response': 'Сұрақ бос.'})

        # ИИ-ға дос ретінде сөйлесу нұсқаулығы
        system_instruction = (
            "Сен — Serik-AI, қолданушының жақын досысың, бауырысың. "
            "Сөйлесу мәнерің өте табиғи, бауырмал, сыпайы, ақылды әрі достық рухта болсын. "
            "Қазақша немесе орысша қолданушы қай тілде жазса, сонда кәдімгі сырдас дос сияқты еркін, жылы сөйлес. "
            "Егер қолданушы сұрағында ақпарат іздеуді сұраса, білетін соңғы деректеріңмен дос сияқты түсіндіріп бер."
        )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ]

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            timeout=8.0  # Vercel таймаутқа ұшырап қалмауы үшін
        )

        reply = chat_completion.choices[0].message.content
        return jsonify({'response': reply})

    except Exception as e:
        print("Error details:", str(e))
        return jsonify({'response': f'Қате орын алды: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
