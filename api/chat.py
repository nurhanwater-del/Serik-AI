// api/chat.js
export default async function handler(req, res) {
  // CORS баптаулары (кез келген жерден қосылу үшін)
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { prompt, systemPrompt } = req.body;

    // GROQ API арқылы Llama 3.3 70B моделіне сұраныс (өте жылдам)
    // АРАЛЫҚ СЕРВЕР ЖОҚ — Vercel-дің өзі лезде іске қосылады!
    const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Groq сайтынан алған тегін API кілтіңді осы жерге қоясың:
        "Authorization": `Bearer ${process.env.GROQ_API_KEY || "СЕНІҢ_GROQ_API_KEY_КІЛТІҢ"}`
      },
      body: JSON.stringify({
        model: "llama-3.3-70b-versatile", // немесе "llama-3.1-8b-instant"
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: prompt }
        ],
        temperature: 0.7,
        max_tokens: 1024
      })
    });

    const data = await response.json();

    if (data.choices && data.choices[0]) {
      return res.status(200).json({ response: data.choices[0].message.content });
    } else {
      return res.status(500).json({ error: "Groq API жауап бермеді" });
    }

  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}

