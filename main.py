import os
from groq import Groq

# 1. Groq API клиентін баптау
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_system_prompt():
    """Мінезін (System Prompt) файлдан оқып алу"""
    try:
        with open("system_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "Сен — Serik-AI, ақылды әрі достық рухтағы ЖИ көмекшісің."

def ask_serik_ai(user_prompt):
    system_instruction = get_system_prompt()
    
    # 2. ЖИ-ге сұраныс жіберу
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        model="llama-3.3-70b-versatile", # Өте мощный әрі жылдам Llama моделі
        temperature=0.8,                 # Бірдей жауап бермеу үшін креативтілік
        max_tokens=1024,
    )
    
    return chat_completion.choices[0].message.content

if __name__ == "__main__":
    # Тест жасау
    question = "Сәлем, Serik-AI! Бүгінгі жоспар қалай?"
    print(f"Сұрақ: {question}\n")
    response = ask_serik_ai(question)
    print(f"Serik-AI жауабы:\n{response}")

