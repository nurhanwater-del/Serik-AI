from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse
import re
from groq import Groq

def search_internet_free(query):
    """Google/DuckDuckGo Lite арқылы 100% бұғаттаусыз тегін іздеу"""
    try:
        # DuckDuckGo Lite нұсқасы боттарды бұғаттамайды
        encoded_query = urllib.parse.quote(query)
        url = f"https://lite.duckduckgo.com/lite/"
        data = urllib.parse.urlencode({'q': query}).encode('utf-8')
        
        req = urllib.request.Request(
            url, 
            data=data,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # HTML ішінен тексттерді суырып алу
            # Реклама мен артық тегтерді тазалау
            clean_text = re.sub(r'<[^>]+>', ' ', html)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            # Мағыналы сөйлемдерді жинау
            words = clean_text.split()
            if len(words) > 50:
                return " ".join(words[30:300]) # Негізгі іздеу нәтижесі
            
        return "Интернеттен іздеу нәтижесі аз болды."
    except Exception as e:
        return "Интернеттен ақпарат алу кезінде уақытша іркіліс болды."

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            user_message = data.get("message", "")

            # 1. Интернеттен іздеу
            search_data = search_internet_free(user_message)

            # 2. Groq (Llama 3.3 70B)
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            
            system_prompt = f"""Сен — Serik-AI деп аталатын көмекшісің. Қолданушыға нағыз досы/братаны сияқты қарапайым әрі түсінікті сөйлес.

ЕКЕУМІЗДІҢ ЕРЕЖЕМІЗ:
1. ҚАЗІРГІ ЖЫЛ: 2026 жыл.
2. ТІЛДЕР: Қазақша, орысша, ағылшынша — қай тілде жазса, сол тілде еркін жауап бер.
3. ӨЗІҢ ТУРАЛЫ: «Сені кім жасады?» десе, «Мені Serik жасап шығарды» деп айт.
4. ИНТЕРНЕТ ДЕРЕКТЕРІ: «Интернеттен ештеңе іздей алмаймын» деп АЙТПА! Мына интернеттен табылған мәліметтерге сүйеніп жауап бер:
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
