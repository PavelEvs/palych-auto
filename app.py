import flet as ft
import flet_audio as fta
from openai import OpenAI
import re, edge_tts, asyncio, os, time, threading, glob
import speech_recognition as sr

# Ваш ключ и модель
API_KEY = "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"
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)

def main(page: ft.Page):
    page.title = "Палыч Авто"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    audio_player = fta.Audio(src="", autoplay=True)
    page.overlay.append(audio_player)

    face_image = ft.Image(src="neutral.gif", width=250, height=250)
    chat_text = ft.Text("Палыч на связи!", size=18, text_align="center")
    user_input = ft.TextField(hint_text="Спроси Палыча...", expand=True)

    def play_voice(text, emotion):
        for f in glob.glob("voice_*.mp3"):
            try: os.remove(f)
            except: pass
        filename = f"voice_{int(time.time())}.mp3"
        rate = "+25%" if emotion == "HAPPY" else "+15%"
        async def _gen():
            comm = edge_tts.Communicate(text, "ru-RU-DmitryNeural", rate=rate)
            await comm.save(filename)
        asyncio.run(_gen())
        audio_player.src = filename
        page.update()

    def process_ai(command):
        if not command: return
        face_image.src = "thinking.gif"
        chat_text.value = "Палыч думает..."
        page.update()
        try:
            res = client.chat.completions.create(
                model="google/gemini-3.1-flash-lite-preview",
                messages=[{"role": "system", "content": "Ты Палыч. Начинай с [NEUTRAL], [HAPPY], [SAD] или [THINKING]."},
                          {"role": "user", "content": command}]
            )
            ans = res.choices[0].message.content
            emo = "NEUTRAL"
            match = re.search(r'\[(.*?)\]', ans)
            if match:
                emo = match.group(1).upper().strip()
                ans = re.sub(r'\[.*?\]', '', ans).strip()
            face_image.src = f"{emo.lower()}.gif"
            chat_text.value = ans
            page.update()
            play_voice(ans, emo)
        except Exception as e:
            chat_text.value = f"Ошибка: {e}"
            face_image.src = "sad.gif"
            page.update()

    def on_mic(e):
        chat_text.value = "Слушаю..."
        page.update()
        def _listen():
            r = sr.Recognizer()
            with sr.Microphone() as s:
                try:
                    r.adjust_for_ambient_noise(s)
                    audio = r.listen(s, timeout=5)
                    process_ai(r.recognize_google(audio, language="ru-RU"))
                except:
                    chat_text.value = "Повтори?"
                    page.update()
        threading.Thread(target=_listen).start()

    # --- КНОПКИ С ПРЯМЫМ КОНТЕНТОМ ---
    # Самый надежный способ: передаем строку "send" и "mic" первым аргументом
    btn_send = ft.IconButton(
        icon="send", 
        on_click=lambda _: process_ai(user_input.value)
    )
    
    btn_mic = ft.IconButton(
        icon="mic", 
        icon_color="blue",
        on_click=on_mic
    )

    page.add(
        face_image,
        chat_text,
        ft.Row([user_input, btn_send, btn_mic], alignment="center")
    )

ft.app(target=main, assets_dir="assets")
