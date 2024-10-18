import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz

def scrape_indianage():
    url = "https://www.indianage.com/indian_history"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('title').text.strip()
    events = {}
    for box in soup.find_all('div', class_='timeline_box'):
        date = box.find('div', class_='date').text.strip()
        event = box.find('p').text.strip()
        events[date] = event
    data = {
        "title": title,
        "events": events
    }
    return data

if __name__ == "__main__":
    data = scrape_indianage()
    india_timezone = pytz.timezone('Asia/Kolkata')
    india_time = datetime.now(india_timezone)
    today_date_month = f"{india_time.day}_{india_time.month}"
    file_path = f"today_in_history/{today_date_month}.json"
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    text = data["title"]
    for date, info in data["events"].items():
        text+=f"\n\n<b><u>{date}</b></u>\n{info}"
    print(text)
        
