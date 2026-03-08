from dotenv import load_dotenv
from TTS.api import TTS
from bs4 import BeautifulSoup
import requests
import os

load_dotenv()

TELEGRAM_CHANNEL_URL = "https:/t.me/s/bbbreaking"

def scrap_news() -> list[str]:
    response = requests.get(TELEGRAM_CHANNEL_URL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        news = []
        for message in soup.select(".js-message_text"):
            text = message.text.removeprefix("⚡️").removeprefix("❗️")
            news.append(text)
        news.reverse()
        return news


tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
def generate_speech(index: int, text: str) -> None:
    tts.tts_to_file(
        text=text, 
        file_path=f"./news/news{index}.wav", 
        split_sentences=True, 
        emotion="Neutral", 
        speed=1, 
        language="ru",
        speaker_wav="./speaker.wav"
    )
    print(f"Done: {index}")

def main():
    news = scrap_news()
    for i, text in enumerate(news[:3]):
        generate_speech(i, text)

if __name__ == "__main__":
    main()