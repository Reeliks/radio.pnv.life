from bs4 import BeautifulSoup
from telnetlib3 import open_connection as open_telnet_connection
from dotenv import load_dotenv
from pathlib import Path
from TTS.api import TTS
from TTS.utils.manage import ModelManager
import asyncio
import requests

load_dotenv()

TELEGRAM_CHANNEL_URL = "https://t.me/s/bbbreaking"
LIQUIDSOAP_TELNET_HOST = "liquidsoap"
LIQUIDSOAP_TELNET_PORT = 1234

def patched_ask_tos(*_):
    print("Automatically accepting non-commercial CPM License")
    return True

ModelManager.ask_tos = patched_ask_tos

def scrap_news() -> dict[int, str]:
    response = requests.get(TELEGRAM_CHANNEL_URL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        news = {}
        for message in soup.select(".js-widget_message"):
            message_id = int(message.get("data-post").split("/")[-1])

            contents = message.select_one(".js-message_text") 
            text = contents.text.removeprefix("⚡️").removeprefix("❗️")

            news[message_id] = text
        return news

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
def generate_speech(text: str, file_path: str = "/app/output.wav") -> None:
    tts.tts_to_file(
        text=text, 
        file_path=file_path, 
        split_sentences=True, 
        emotion="Neutral", 
        speed=1, 
        language="ru",
        speaker_wav="/app/speaker.wav"
    )

async def push_news(file_path: str) -> int | None:
    try:
        reader, writer = await open_telnet_connection(
            host=LIQUIDSOAP_TELNET_HOST, 
            port=LIQUIDSOAP_TELNET_PORT)

        writer.write(f"news.push {file_path}\n")
        await writer.drain()

        queue_place = await asyncio.wait_for(reader.read(1024), timeout=3.0)

        writer.write("exit\n")
        await writer.drain()

        writer.close()
        await writer.wait_closed()
        return queue_place
    except asyncio.TimeoutError:
        print(f"No response from Liquidsoap")
    except Exception as e:
        print(f"Error pushing news: {e}")

async def main():
    news = scrap_news()
    for message_id, text in news.items():
        print(f"{message_id}: {text}")
        file_path = f"/news/{message_id}.wav"
        if not Path(file_path).exists():
            generate_speech(text, file_path=file_path)
            print(f"Generated speech: {file_path}. Pushing...")
            queue_place = await push_news(file_path)
            print(f"Place in the news queue: {queue_place}")
        else:
            print(f"Speech already exists: {file_path}")

if __name__ == "__main__":
    asyncio.run(main())