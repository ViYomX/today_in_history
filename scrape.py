import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz
import os
import random

def scrape_indianage():
    url = "https://www.indianage.com/indian_history"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('title').text.strip()
    title = title.replace("Today in Indian History - ", "")
    events = {}

    for box in soup.find_all('div', class_='timeline_box'):
        date = box.find('div', class_='date').text.strip()
        # Extract only the year
        year = date.split("-")[-1]
        event = box.find('p').text.strip()
        events[year] = event

    data = {
        "title": title,
        "events": events
    }
    return data

def send_telegram_message(message):
    chat_id = os.getenv("CHAT_ID")
    bot_token = os.getenv("BOT_TOKEN")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(response)
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e}")
        print(f"Response Text: {response.text}")

if __name__ == "__main__":
    data = scrape_indianage()
    india_timezone = pytz.timezone('Asia/Kolkata')
    india_time = datetime.now(india_timezone)
    today_date_month = f"{india_time.day}_{india_time.month}"
    file_path = f"today_in_history/{today_date_month}.json"
    os.makedirs('today_in_history', exist_ok=True)
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    text = f"<b>✨ {data['title']} ✨</b>\n\n"
    
    for date, info in data["events"].items():
        text += (
            f"📜 <b>Date:</b> <u>{date}</u>\n"
            f"🔸 <b>Highlights:</b>\n"
            f"{info}\n\n"
            "──────────\n"
        )
    max_length = 3900
    current_message = ""

    for line in text.split("\n"):
        if len(current_message) + len(line) + 1 > max_length:
            if current_message.strip():
                send_telegram_message(current_message)
            current_message = ""
        current_message += line + "\n"

    #if current_message.strip():
        #send_telegram_message(current_message)
