import asyncio
import websockets
import os
import google.generativeai as genai
from gtts import gTTS
import io
from pydub import AudioSegment

# Recupera la chiave API e verifica se presente
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ ERRORE: Variabile GEMINI_API_KEY non trovata!")
    # Non usciamo per permettere a Render di tenere l'istanza "attiva" per debug, 
    # ma il servizio non funzionerà.
else:
    genai.configure(api_key=api_key)
    print("✅ API Key configurata correttamente.")

model = genai.GenerativeModel('gemini-1.5-flash')

async def assistente(websocket):
    print(f"📩 Nuova connessione da: {websocket.remote_address}")
    try:
        async for message in websocket:
            if isinstance(message, str):
                print(f"📝 Testo ricevuto: {message}")
                if message == "STOP":
                    print("🤖 Elaborazione risposta Gemini...")
                    prompt = "Rispondi in modo molto breve: sono il tuo assistente ESP32, il server è attivo!"
                    try:
                        # Genera testo con Gemini
                        response = model.generate_content(prompt)
                        text_response = response.text
                        print(f"✅ Risposta Gemini: {text_response}")
                        
                        # Genera MP3 con gTTS
                        tts = gTTS(text=text_response, lang='it')
                        mp3_fp = io.BytesIO()
                        tts.write_to_fp(mp3_fp)
                        mp3_fp.seek(0)

                        # Converti MP3 in PCM 16kHz Mono usando pydub
                        audio = AudioSegment.from_file(mp3_fp, format="mp3")
                        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
                        pcm_data = audio.raw_data
                        
                        print(f"📤 Invio PCM: {len(pcm_data)} bytes")
                        await websocket.send(pcm_data)
                    except Exception as e:
                        print(f"❌ Errore generazione/conversione: {e}")
            else:
                # Se è un messaggio binario (audio dall'ESP32)
                # print(f"🎤 Ricevuti {len(message)} byte audio") # Troppo spam, loggiamo solo l'inizio
                pass
    except websockets.exceptions.ConnectionClosed:
        print("🔌 ESP32 disconnesso.")
    except Exception as e:
        print(f"⚠️ Errore imprevisto: {e}")

# Porta richiesta da Render
port = int(os.environ.get("PORT", 10000))

async def main():
    async with websockets.serve(assistente, "0.0.0.0", port):
        print(f"Server attivo sulla porta {port}")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
