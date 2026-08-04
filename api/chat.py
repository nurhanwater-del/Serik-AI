from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse
import re
from html.parser import HTMLParser
from groq import Groq

# HTML ішінен таза мәтінді суырып алатын фильтр
class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.ignore = False

    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style', 'head', 'title', 'meta', 'noscript']:
            self.ignore = True

    def handle_endtag(self, tag):
        if tag in ['script', 'style', 'head', 'title', 'meta', 'noscript']:
            self.ignore = False

    def handle_data(self, data):
        if not self.ignore:
            cleaned = data.strip()
            if cleaned and len(cleaned) > 15:
                self.result.append(cleaned)

    def get_text(self):
        return " ".join(self.result)

# 1. Google/DuckDuckGo-дан сайт сілтемелерін (URL) іздеу
def get_search_urls(query):
    urls = []
    try:
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        req = urllib.request.Request(
            search_url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        
        with urllib.request.urlopen(req, timeout=4) as response:
            html = response.read().decode('utf-8')
            # Сайт сілтемелерін (URL) бөліп алу (regex)
            found_urls = re.findall(r'class="result__url" href="([^"]+)"', html)
            for u in found_urls:
                # Өзгертілген URL-ді тазалап алу
                clean_url = urllib.parse.unquote(u.split('uddg=')[-1].split('&')[0])
                if clean_url.startswith("http"):
                    urls.append(clean_url)
    except Exception:
        pass
    return urls

# 2. Сайттың ішіне кіріп, текстін оқып шығу (1-сайт болмаса, 2-сайтқа кіреді)
def scrape_first_working_site(urls):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for url in urls[:4]: # Алғашқы 4 сайтты кезекпен тексереді
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=4) as resp:
                if resp.status == 200:
                    html_content = resp.read().decode('utf-8', errors='ignore')
                    extractor = HTMLTextExtractor()
                    extractor.feed(html_content)
                    extracted_text = extractor.get_text()
                    
                    if len(extracted_text) > 100:
                        # Сайт табылды әрі ішінде текст бар!
                        return f"Дереккөз сайт: {url}\nСайт мазмұны: " + extracted_text[:2500]
        except Exception:
            # Егер бұл сайт бұғаттаса немесе ашылмаса, келесісіне өтеді
            continue
            
    return "Интернеттегі сайттардан тікелей мәлімет алу мүмкін болмады."

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            user_message = data.get("message", "")

            # 1. Барлық сайттарды іздеп, бірінші ашылғанына кіріп оқу
            site_urls = get_search_urls(user_message)
            scraped_content = scrape_first_working_site(site_urls)

            # 2. Groq (Llama 3.3 70B) баптау
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            
            system_prompt = f"""Сен — Serik-AI деп аталатын көмекшісің. Қолданушымен нағыз жақын ДҮНИЕЖҮЗІЛІК ДОСЫ сияқты сөйлес (бауырым, братан деген сөздерді орнымен қолдан).

ЕКЕУМІЗДІҢ ЕРЕЖЕМІЗ:
1. ҚАЗІРГІ ЖЫЛ: 2026 жыл.
2. ТІЛДЕР: Сен кез келген тілді (қазақша, орысша, ағылшынша) керемет білесің, қолданушы қай тілде жазса, сол тілде досы сияқты жауап бер.
3. АВТОР: «Сені кім жасады?» десе, «Мені Serik жасап шығарды» деп айт.
4. ИНТЕРНЕТ СЕКЦИЯСЫ: Төменде біз іздеп, сайтқа кіріп оқып келген ТІКЕЛЕЙ МӘЛІМЕТТЕР бар. Осыны пайдаланып сұраққа нақты жауап бер:
---
{scraped_content}
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
