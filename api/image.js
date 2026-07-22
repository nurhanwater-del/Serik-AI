export default async function handler(req, res) {
  const { prompt } = req.query;

  if (!prompt) {
    return res.status(400).json({
      error: "Prompt is required"
    });
  }

  try {
    const imageUrl =
      `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?width=2048&height=2048&nologo=true&seed=${Math.floor(Math.random()*1000000000)}`;

    const response = await fetch(imageUrl);

    if (!response.ok) {
      return res.status(500).json({
        error: "Failed to generate image"
      });
    }

    const buffer = Buffer.from(await response.arrayBuffer());

    res.setHeader("Content-Type", "image/png");
    res.setHeader(
      "Content-Disposition",
      'attachment; filename="Serik_AI.png"'
    );

    return res.send(buffer);
  } catch (error) {
    return res.status(500).json({
      error: error.message
    });
  }
}
