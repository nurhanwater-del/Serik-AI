import os
import requests
from flask import Flask, request, jsonify
from groq import Groq
from duckduckgo_search import DDGS  # Тегін Google/Веб іздеу үшін

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# 1. Сұрақтың түрін анықтау (Әңгіме ме, әлде факт/іздеу ме?)
def check_intent(user_prompt):
    intent_prompt = f"""
    Анализируй запрос пользователя: "{user_prompt}"
    Если это просто разговор, приветствие, мнение или обсуждение — ответь "CHAT".
    Если запрос требует свежих фактов, новостей, поиска информации или конкретных данных — ответь "SEARCH".
    Отвечай ТОЛЬКО одним словом: CHAT или SEARCH.
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": intent_prompt}],
        max_tokens=5
    )
    return response.choices[0].message.content.strip()

# 2. Интернеттен ақпарат іздеу
def search_web(query):
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=3):
                results.append(r['body'])
        return "\n".join(results)
    except Exception as e:
        return ""

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_prompt = data.get('prompt', '')

    if not user_prompt:
        return jsonify({'response': 'Сұрақ бос.'})

    # ФИЛЬТР: Сұрақты тексереміз
    intent = check_intent(user_prompt)

    context = ""
    if "SEARCH" in intent:
        # Егер іздеу керек болса — гуглдаймыз
        search_data = search_web(user_prompt)
        if search_data:
            context = f"\n[Интернеттен алынған деректер]:\n{search_data}\nОсы деректерді қолданып жауап бер."

    # Llama-ға дос ретиде жауап бергізу үшін System Prompt
    system_instruction = (
        "Сен — Serik-AI, қолданушының жақын досысың. "
        "Сөйлесу мәнерің өте табиғи, бауыррмал, сыпайы, ақылды әрі достық рухта болсын. "
        "Қазақша немесе орысша қолданушының тілінде кәдімгі сырдас дос сияқты еркін сөйлес. "
        "Егер контексте интернеттен алынған мәлімет болса, оны өз сөзіңмен досыңа түсіндіргендей жеткіз."
    )

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"{user_prompt}{context}"}
    ]

    # Llama 3.3-тен жауап алу
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
    )

    reply = chat_completion.choices[0].message.content
    return jsonify({'response': reply})

if __name__ == '__main__':
    app.run()
