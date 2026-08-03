from http.server import BaseHTTPRequestHandler
import json
import os
from groq import Groq
from duckduckgo_search import DDGS

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. Frontend-тен келген сұрақты алу
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            user_message = data.get("message", "")

            # 2. Интернеттен (Google/DuckDuckGo) соңғы ақпаратты іздеу
            search_results = ""
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(user_message, max_results=3))
                    search_results = "\n".join([r['body'] for r in results])
            except Exception:
                search_results = "Интернеттен іздеу уақытша істемей тұр."

            # 3. Groq API баптау (Llama 3.3 70B)
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            
            system_prompt = f"""Сен — Serik-AI деп аталатын ақылды ИИ көмекшісің.

НЕГІЗГІ ЕРЕЖЕЛЕР:
1. Тек "Сәлем, бауырым!" деп қайталап тұрып алма! Қолданушының қойған СҰРАҒЫНА НАҚТЫ ЖАУАП БЕР.
2. Валюта курсы (доллар, евро т.б.), соңғы жаңалықтар немесе қазіргі ақпараттар сұралса, мына интернет мәліметтеріне сүйеніп жауап бер:
{search_results}
3. Жауапты қазақша (немесе сұрақ қойылған тілде), түсінікті, достық рухта әдемілеп жеткіз."""

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )

            response_text = completion.choices[0].message.content

            # 4. Жауапты қайтару (200 OK)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"response": response_text}).encode('utf-8'))

        except Exception as e:
            # Қате болса қайтару (500 Error)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
