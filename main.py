import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

# Сенің API кілтің мен настройкаң
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

def get_system_prompt():
    try:
        with open("system_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "Сен — Serik-AI, қолданушының жақын досысың, ақылды әрі достық рухтағы ЖИ көмекшісің."

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        user_prompt = data.get('prompt', '')

        if not user_prompt:
            return jsonify({'response': 'Сұрақ бос.'})

        system_instruction = get_system_prompt()

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            max_tokens=1024,
        )

        reply = chat_completion.choices[0].message.content
        return jsonify({'response': reply})

    except Exception as e:
        return jsonify({'response': f'Қате орын алды: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
