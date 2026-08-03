from http.server import BaseHTTPRequestHandler
import json
import os
from groq import Groq
from duckduckgo_search import DDGS

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Frontend-тен келген сұрақты алу
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        user_message = data.get("message", "")

        # 2. Гуглдан/Интернеттен соңғы жаңалықты іздеу
        search_results = ""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(user_message, max_results=3))
                search_results = "\n".join([r['body'] for r in results])
        except Exception:
            search_results = "Интернеттен іздеу мүмкін болмады."

        # 3. Groq API (Llama 3.3 70B) арқылы жауап генерациялау
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        system_prompt = f"""Сен — Serik-AI көмекшісің. Қолданушыға достық рухта, қазақша жауап бер.
        Егер сұрақ соңғы жаңалықтарға қатысты болса, мына интернет мәліметтерін қолдан:
        {search_results}"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )

        response_text = completion.choices[0].message.content

        # 4. Жауапты Vercel арқылы кайтару
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"response": response_text}).encode('utf-8'))

