const express = require("express");
const cors = require("cors");
const fetch = require("node-fetch");

const app = express();
app.use(cors());
app.use(express.json());

// 🤖 Серік AI-дың текстік бэкенд функциясы
app.post("/api/chat", async (req, res) => {
  try {
    const { prompt, systemPrompt } = req.body;

    // Өзіміздің жеке серверіміз арқылы тегін Llama-3.1 моделіне сұраныс жіберу
    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "meta-llama/llama-3.1-8b-instruct:free",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: prompt }
        ]
      })
    });

    const data = await response.json();
    
    if (data.choices && data.choices[0] && data.choices[0].message) {
      res.json({ response: data.choices[0].message.content });
    } else {
      res.status(500).json({ error: "Жауап генерациялау мүмкін болмады" });
    }

  } catch (error) {
    console.error("Ошибка сервера:", error);
    res.status(500).json({ error: "Серверде ішкі қате болды" });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Сервер ${PORT} портында іске қосылды!`);
});

