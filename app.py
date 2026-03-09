import flet as ft
import flet_audio as fta
from openai import OpenAI
import re, edge_tts, asyncio, os, time, glob

# ВСТАВЬТЕ СЮДА ВАШ НОВЫЙ КЛЮЧ ОТ OPENROUTER!
API_KEY = "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"
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)

def main(page: ft.Page):
    page.title = "Палыч Авто"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    # Инициализируем аудио плеер правильно
    audio_player = fta.Audio(src="", autoplay=True)
    page.overlay.append(audio_player)

    face_image = ft.Image(src="neutral.gif", width=250, height=250)
    chat_text = ft.Text("Палыч готов слушать!", size=20, text_align="center")
    
    # Поле ввода (при клике на него в Android откроется клавиатура с микрофоном)
    user_input = ft.TextField(hint_text="Нажмите сюда и используйте микрофон клавиатуры...", expand=True)

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
        
        user_input.value = ""
        face_image.src = "thinking.gif"
        chat_text.value = "Палыч думает..."
        page.update()
        
        try:
            res = client.chat.completions.create(
                model="google/gemini-3.1-flash-lite-preview",
                messages=[{"role": "system", "content": "Ты Палыч, мудрый мужик. Начинай с [NEUTRAL], [HAPPY], [SAD] или [THINKING]."},
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
            chat_text.value = f"Ошибка связи (обновите ключ!): {e}"
            face_image.src = "sad.gif"
            page.update()

    btn_send = ft.ElevatedButton("Отправить", on_click=lambda _: process_ai(user_input.value))

    page.add(
        face_image,
        chat_text,
        ft.Row([user_input, btn_send], alignment="center")
    )

ft.app(target=main, assets_dir="assets")
