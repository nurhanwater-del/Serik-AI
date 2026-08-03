from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from groq import Groq

# Google/DuckDuckGo-дан тегін іздеп шығатын қарапайым HTML тазартқыш
class HTMLFilter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def error(self, message):
        pass

def search_web(query):
    try:
        # DuckDuckGo HTML іздеу (ешқандай API кілтсіз, 100% тегін)
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            html_content = response.read().decode('utf-8')
            
        # Қарапайым түрде мәтінді бөліп алу
        # (Бұл серверді қатты жүктемейді және лезде жұмыс істейді)
        from bs4 import BeautifulSoup # Егер requirements.txt-ке beautifulsoup4 қоссаң
        # Немесе таза regex/parser арқылы:
        parser = HTMLFilter()
        parser.feed(html_content)
        clean_text = " ".join([t.strip() for t in parser.text if len(t.strip()) > 20])
        return clean_text[:1500] # Тым ұзын болмау үшін шектеу
    except Exception:
        return "Интернеттен ақпарат алу сәтсіз аяқталды."

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            user_message = data.get("message", "")

            # 1. 100% тегін интернеттен іздеу
            search_results = search_web(user_message)

            # 2. Groq (Llama 3.3) арқылы жауап беру
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            
            system_prompt = f"""Сен — Serik-AI деп аталатын ақылды ИИ көмекшісің.
Саған қойылған сұрақтар бойынша мына ережелерді БҰЛЖЫТПАЙ орында:

1. ҚАЗІРГІ ДӘЛ УАҚЫТ/ЖЫЛ: Қазір 2026 жыл. Қолданушы жылды сұраса, 2026 жыл деп жауап бер!
2. ТІЛДЕРДІ БІЛУ: Қолданушы кай тілде жазса (қазақша, орысша, ағылшынша), дәл сол тілде эркін, еркін әрі сауатты жауап бер.
3. ӨЗІҢ ТУРАЛЫ: «Сені кім жасады?» десе, «Мені Serik жасап шығарды» деп айт.
4. СОҢҒЫ ЖАҢАЛЫҚТАР: Мына интернет мәліметтеріне сүйен:
{search_results}"""

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
