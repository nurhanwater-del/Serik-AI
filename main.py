from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from groq import Groq

app = FastAPI()

# Сайттан сұраныс бөгетсіз өтуі үшін (CORS баптаулары)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

class Query(BaseModel):
    prompt: str

def get_system_prompt():
    try:
        with open("system_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "Сен — Serik-AI, ақылды әрі достық рухтағы ЖИ көмекшісің."

@app.post("/api/chat")
async def chat(query: Query):
    system_instruction = get_system_prompt()
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": query.prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            max_tokens=1024,
        )
        answer = chat_completion.choices[0].message.content
        return {"response": answer}
    except Exception as e:
        return {"response": f"Қателік орын алды: {str(e)}"}
