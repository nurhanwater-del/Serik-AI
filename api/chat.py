from http.server import BaseHTTPRequestHandler
import json
import os
from groq import Groq
from duckduckgo_search import DDGS

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            user_message = data.get("message", "")

            # Интернеттен іздеу
            search_results = ""
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(user_message, max_results=3))
                    search_results = "\n".join([r['body'] for r in results])
            except Exception:
                search_results = "Интернеттен іздеу уақытша қолжетімсіз."

            # Groq API арқылы жауап алу
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            
            system_prompt = f"""Сен — Serik-AI көмекшісің. Қолданушыға жылы, достық рухта, қазақша (немесе сұрақ қойылған тілде) жауап бер.
            Интернеттен алынған мәліметтер:
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
