import asyncio
import websockets
import os
import google.generativeai as genai
from gtts import gTTS
import io
import miniaudio

# Recupera la chiave API dalle variabili d'ambiente di Render
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

async def assistente(websocket):
    print("ESP32 connesso!")
    async for message in websocket:
        if isinstance(message, str) and message == "STOP":
            print("Richiesta risposta ricevuta...")
            prompt = "Rispondi in modo molto breve: sono il tuo assistente ESP32, il server è attivo!"
            try:
                # Genera testo con Gemini
                response = model.generate_content(prompt)
                text_response = response.text
                print(f"Risposta Gemini: {text_response}")
                
                # Genera MP3 con gTTS
                tts = gTTS(text=text_response, lang='it')
                mp3_fp = io.BytesIO()
                tts.write_to_fp(mp3_fp)
                mp3_data = mp3_fp.getvalue()

                # Decodifica MP3 direttamente in PCM 16kHz Mono 16-bit usando miniaudio
                # Non serve FFmpeg né audioop!
                decoded = miniaudio.decode(mp3_data, nchannels=1, sample_rate=16000)
                pcm_data = decoded.samples.tobytes()
                
                print(f"Invio PCM: {len(pcm_data)} bytes")
                await websocket.send(pcm_data)
            except Exception as e:
                print(f"Errore: {e}")

# Porta richiesta da Render
port = int(os.environ.get("PORT", 10000))

async def main():
    async with websockets.serve(assistente, "0.0.0.0", port):
        print(f"Server attivo sulla porta {port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
