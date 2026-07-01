import os
import time
import requests
import http.server
import socketserver
import threading

# --- RENDER ПОРТЫ ҮШІН КІШКЕНТАЙ СЕРВЕР ---
def run_dummy_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 10000), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- БОТТЫҢ НАҚТЫ БАПТАУЛАРЫ ---
API_KEY = "AIzaSyD3F9WXOSoFm-UEPU-3lJbWbOu7jSfCUwE"
CHANNEL_ID = "UCZ63w9Xbe_i9M4mUu-G_C7Q"
LAST_COMMENT_FILE = "last_comment_id.txt"

def get_last_processed_id():
    if os.path.exists(LAST_COMMENT_FILE):
        with open(LAST_COMMENT_FILE, "r") as f:
            return f.read().strip()
    return None

def save_last_processed_id(comment_id):
    with open(LAST_COMMENT_FILE, "w") as f:
        f.write(comment_id)

def get_latest_comments():
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&allThreadsRelatedToChannelId={CHANNEL_ID}&maxResults=5&key={API_KEY}"
    try:
        response = requests.get(url).json()
        return response.get("items", [])
    except Exception as e:
        print(f"Қате ұсталынды: {e}")
        return []

def reply_to_comment(parent_id, text):
    reply_text = "Рақмет! Тіл қатқаныңызға қуаныштымыз. Мына сілтеме арқылы толық ақпарат ала аласыз: https://whatsapp.com/channel/0029VbDKgz8C1Fu46sZhH530"
    
    url = f"https://www.googleapis.com/youtube/v3/comments?part=snippet&key={API_KEY}"
    data = {
        "snippet": {
            "parentId": parent_id,
            "textOriginal": reply_text
        }
    }
    try:
        res = requests.post(url, json=data)
        if res.status_code == 200 or res.status_code == 201:
            print(f"Сәтті жауап берілді: {parent_id}")
        else:
            print(f"Жауап беру сәтсіз аяқталды: {res.json()}")
    except Exception as e:
        print(f"Жауап беру қатесі: {e}")

def main():
    print("Бот ресми түрде іске қосылды. Комменттер күтілуде...")
    last_id = get_last_processed_id()
    
    while True:
        comments = get_latest_comments()
        if comments:
            latest_comment = comments[0]
            comment_id = latest_comment["id"]
            
            if comment_id != last_id:
                author_channel = latest_comment["snippet"]["topLevelComment"]["snippet"].get("authorChannelId", {}).get("value", "")
                
                # Тіл таңдамай, келген комментке бірден жауап беру
                reply_to_comment(comment_id, "Рақмет!")
                last_id = comment_id
                save_last_processed_id(comment_id)
                
        # Әр 10 секунд сайын сразу тексеріп отырады
        time.sleep(10)

if __name__ == "__main__":
    main()
