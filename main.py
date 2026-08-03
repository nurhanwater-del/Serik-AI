import os
from groq import Groq

# API кілтті қауіпсіз түрде беру
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

client = Groq(api_key=GROQ_API_KEY)

def get_system_prompt():
    try:
        with open("system_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "Сен — Serik-AI, ақылды әрі достық рухтағы ЖИ көмекшісің."

def ask_serik_ai(user_prompt):
    system_instruction = get_system_prompt()
    
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.8,
        max_tokens=1024,
    )
    
    return chat_completion.choices[0].message.content

if __name__ == "__main__":
    question = "Сәлем, Serik-AI! Бүгін қандай жаңалық бар?"
    print(f"Сұрақ: {question}\n")
    response = ask_serik_ai(question)
    print(f"Serik-AI жауабы:\n{response}")
