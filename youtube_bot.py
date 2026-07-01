import http.server
import socketserver
import threading

def run_dummy_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 10000), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()
import googleapiclient.discovery
import requests
import time

# БАПТАУЛАР (Түзетілген нұсқасы)
YT_API_KEY = "AIzaSyD3F9WXOSoFm-UEPU-3lJbWbOu7jSfCUwE"  # Сенің Google Cloud-тан алған кілтің
CHANNEL_ID = "UCZ63w9Xbe_i9M4mUu-G_C7Q"  # Сенің Ютуб Канал ID-ің
SYSTEM_PROMPT = "Ты всезнающий ИИ Serik-AI из Казахстана. Пиши как живой человек, мудрым и естественным текстом без списков."

# Ютуб клиентін іске қосу
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YT_API_KEY)

def get_ai_response(user_text):
    url = "https://text.pollinations.ai/"
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "model": "openai",
        "private": True
    }
    try:
        res = requests.post(url, json=payload)
        return res.text.strip()
    except:
        return None

def get_latest_video_ids(channel_id):
    """Каналдағы соңғы 3 видеоны анықтау"""
    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        maxResults=3,
        order="date",
        type="video"
    )
    response = request.execute()
    return [item['id']['videoId'] for item in response.get('items', [])]

def check_and_reply_to_videos():
    video_ids = get_latest_video_ids(CHANNEL_ID)
    
    for video_id in video_ids:
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=5
            )
            response = request.execute()

            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                text = comment['textDisplay']
                comment_id = item['snippet']['topLevelComment']['id']
                author_id = comment['authorChannelId']['value']
                
                # Егер комментті сен жазсаң, ИИ жауап бермейді
                if author_id == CHANNEL_ID:
                    print("Бұл сенің коментің, бауырым. Жауап бермеймін.")
                    continue
                
                # Басқа адамдарға ИИ-ден жауап алу
                ai_reply = get_ai_response(text)
                if ai_reply:
                    youtube.comments().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "parentId": comment_id,
                                "textOriginal": ai_reply
                            }
                        }
                    ).execute()
                    print("Жаңа қолданушының комментіне жауап берілді!")
        except Exception as e:
            print("Видеоны тексеруде қате:", e)
            continue

# Әр 5 минут сайын автоматты тексеру
while True:
    print("Каналды тексеру басталды...")
    try:
        check_and_reply_to_videos()
    except Exception as e:
        print("Басты қате:", e)
    time.sleep(300)


