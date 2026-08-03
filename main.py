import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Vercel-дегі GROQ API кілтін оқу
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return jsonify({'response': '⚠️ GROQ_API_KEY Vercel-де табылмады! Settings-тен тексер.'}), 500

        client = Groq(api_key=api_key)
        data = request.get_json(silent=True) or {}
        user_prompt = data.get('prompt', '')

        if not user_prompt:
            return jsonify({'response': 'Сұрағың бос сияқты, бауырым!'})

        # ИИ-ға өзін қалай ұстау керектігін үйретеміз (System Prompt)
        system_instruction = (
            "Сен — Serik-AI, қолданушының жақын досысың, бауырысың. "
            "Сөйлесу мәнерің өте табиғи, бауырмал, сыпайы, ақылды әрі достық рухта болсын. "
            "Қазақша немесе орысша қолданушы қай тілде жазса, сонда кәдімгі сырдас дос сияқты еркін, жылы сөйлес. "
            "Өзіңді ешқашан қолданушымен шатастырма."
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile"
        )

        reply = chat_completion.choices[0].message.content
        return jsonify({'response': reply})

    except Exception as e:
        return jsonify({'response': f'Кате шықты, брат: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
