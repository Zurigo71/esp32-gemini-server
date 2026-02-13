import asyncio
import websockets
import os
import google.generativeai as genai
from gtts import gTTS
import io
from pydub import AudioSegment

# Recupera la chiave API dalle variabili d'ambiente di Render
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

async def assistente(websocket):
    print("ESP32 connesso!")
    async for message in websocket:
        if isinstance(message, str) and message == "STOP":
            prompt = "Rispondi in modo molto breve: sono il tuo assistente ESP32, il server è attivo!"
            try:
                response = model.generate_content(prompt)
                print(f"Risposta Gemini: {response.text}")
                
                # Genera MP3 con gTTS
                tts = gTTS(text=response.text, lang='it')
                mp3_fp = io.BytesIO()
                tts.write_to_fp(mp3_fp)
                mp3_fp.seek(0)

                # Converti MP3 in PCM 16kHz Mono 16-bit usando pydub
                audio = AudioSegment.from_file(mp3_fp, format="mp3")
                audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
                pcm_data = audio.raw_data
                
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



