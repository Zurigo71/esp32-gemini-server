import asyncio
import websockets
import os
import google.generativeai as genai
from gtts import gTTS
import io

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
                tts = gTTS(text=response.text, lang='it')
                mp3_fp = io.BytesIO()
                tts.write_to_fp(mp3_fp)
                await websocket.send(mp3_fp.getvalue())
            except Exception as e:
                print(f"Errore Gemini: {e}")

# Porta richiesta da Render
port = int(os.environ.get("PORT", 10000))

async def main():
    async with websockets.serve(assistente, "0.0.0.0", port):
        print(f"Server attivo sulla porta {port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())



