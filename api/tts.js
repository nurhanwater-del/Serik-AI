const { MsEdgeTTS, OUTPUT_FORMAT } = require("msedge-tts");

module.exports = async (req, res) => {
    // URL-ден мәтін мен тілді аламыз
    const text = req.query.text;
    const lang = req.query.lang || 'ru';

    if (!text) {
        return res.status(400).send("Мәтін енгізілмеді");
    }

    try {
        const tts = new MsEdgeTTS();
        
        // Егер мәтін қазақша болса "Дәулеттің" дауысын, орысша болса "Дмитрийді" қосамыз
        const voice = lang === 'kk' ? "kk-KZ-DauletNeural" : "ru-RU-DmitryNeural";
        
        // Сапасын баптау (MP3 формат)
        await tts.setMetadata(voice, OUTPUT_FORMAT.AUDIO_24KHZ_48KBITRATE_MONO_MP3);
        
        // Дыбысты жазып, оны бірден сайтқа жіберу
        const audioStream = tts.toStream(text);
        
        res.setHeader('Content-Type', 'audio/mpeg');
        audioStream.pipe(res);
        
    } catch (error) {
        console.error("Озвучка қателігі:", error);
        res.status(500).send("Дауыс генерациялау кезінде қате шықты");
    }
};
