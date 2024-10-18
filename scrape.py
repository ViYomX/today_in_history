import requests
from bs4 import BeautifulSoup
import json

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

    json_data = json.dumps(data, indent=4)
    return json_data
