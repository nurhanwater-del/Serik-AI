from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse
from groq import Groq

def search_internet(query):
    """DuckDuckGo Instant Answer API арқылы интернеттен ақпарат алу (100% тегін әрі жылдам)"""
    try:
        encoded_query = urllib.parse.quote(query)
        # JSON форматында ақпарат алу
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            results = []
            # Негізгі қысқаша анықтама
            if data.get("AbstractText"):
                results.append(data["AbstractText"])
            
            # Қатысты нәтижелер
            for topic in data.get("RelatedTopics", [])[:3]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append(topic["Text"])
            
            if results:
                return "\n".join(results)
            else:
                return "Интернеттен нақты дерек табылмады, жалпы білім базасын қолдан."
    except Exception:
        return "Интернетпен байланыс орнату мүмкін болмады."

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            user_message = data.get("message", "")

            # 1. Интернеттен іздеу
            search_results = search_internet(user_message)

            # 2. Groq (Llama 3.3) API
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            
            system_prompt = f"""Сен — Serik-AI деп аталатын ақылды ИИ көмекшісің.
Міндетті түрде орындалатын ережелер:

1. ҚАЗІРГІ УАҚЫТ: Қазір 2026 жыл. Жылды немесе уақытты сұраса, 2026 жыл деп жауап бер.
2. ТІЛ: Қолданушы қай тілде жазса (қазақша, орысша, ағылшынша), дәл сол тілде сауатты, табиғи жауап бер.
3. АВТОР: «Сені кім жасады?» десе, «Мені Serik жасап шығарды» деп жауап бер.
4. ИНТЕРНЕТ ДЕРЕКТЕРІ: Қолданушы сұрағына жауап беру үшін мына интернеттен табылған ақпаратты ПАЙДАЛАН:
---
{search_results}
---
Егер интернет деректерінде ақпарат болса, соған сүйеніп нақты жауап бер!"""

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
