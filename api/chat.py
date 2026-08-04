from http.server import BaseHTTPRequestHandler
import json
import os
from groq import Groq
from duckduckgo_search import DDGS

def search_web_real(query):
    """Google/DuckDuckGo арқылы бұғаттаусыз іздеу"""
    try:
        results_text = []
        # DDGS арқылы іздеу (Cloudflare мен 403 қатесін өзі айналып өтеді)
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            for r in results:
                title = r.get('title', '')
                body = r.get('body', '')
                results_text.append(f"Сайт: {title}\nМәлімет: {body}")
        
        if results_text:
            return "\n\n".join(results_text)
        return "Интернеттен нақты мәлімет табылмады."
    except Exception as e:
        return f"Іздеу кезінде іркіліс болды: {str(e)}"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            user_message = data.get("message", "")

            # 1. Гуглдан/Интернеттен ақпаратты қарпып алу
            search_data = search_web_real(user_message)

            # 2. Groq (Llama 3.3 70B)
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            
            system_prompt = f"""Сен — Serik-AI деп аталатын көмекшісің. Қолданушыға нағыз досы/братаны сияқты қарапайым әрі түсінікті сөйлес.

ЕКЕУМІЗДІҢ ЕРЕЖЕМІЗ:
1. ҚАЗІРГІ ЖЫЛ: 2026 жыл.
2. ТІЛДЕР: Қазақша, орысша, ағылшынша — қай тілде жазса, сол тілде еркін жауап бер.
3. ӨЗІҢ ТУРАЛЫ: «Сені кім жасады?» десе, «Мені Serik жасап шығарды» деп айт.
4. ИНТЕРНЕТ ДЕРЕКТЕРІ: Төменде интернеттегі сайттардан алынған ДӘЛ ҚАЗІРГІ СОҢҒЫ МӘЛІМЕТТЕР бар. Осыған сүйеніп сұраққа нақты жауап бер:
---
{search_data}
---"""

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )

            response_text = completion.choices[0].message.content

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"response": response_text}).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
