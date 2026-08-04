const express = require("express");
const cors = require("cors");
const fetch = require("node-fetch");

const app = express();
app.use(cors());
app.use(express.json());

// Серик AI-дың жеке бэкенді
app.post("/chat", async (req, res) => {
  try {
    const { prompt, systemPrompt } = req.body;

    // Өзіміздің сервер арқылы тегін ИИ-ға сұраныс жіберу (HuggingFace / OpenRouter тегін моделі)
    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Бұл тегін ашық модель үшін API ключсіз де/тегін ключпен де жұмыс істейді
        "Authorization": "Bearer gsk_free_public_token" 
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
    const reply = data.choices?.[0]?.message?.content || "Жауап алу мүмкін болмады";
    
    res.json({ response: reply });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
