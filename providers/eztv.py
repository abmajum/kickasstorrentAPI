import cloudscraper
import random
from bs4 import BeautifulSoup
import pprint

url='https://eztvx.to/search/'

# List of user-agent strings to use
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
]

headers = {"User-Agent": random.choice(user_agents)}
scraper = cloudscraper.create_scraper() 


def get_eztv_torrents(query_term: str, page: int):
    query_url = f"{url}{query_term}"
    payload = {
        'layout': 'def_wlinks'
    }
    response = scraper.post(query_url, headers=headers, data=payload)

    box = BeautifulSoup(response.text , "html.parser")
    tbles = box.find_all('table', class_='forum_header_border')
    results = []
    for tble in tbles:
        
        for row in tble.find_all('tr', attrs={"class":"forum_header_border", "name":"hover"}):
            cells = row.find_all('td')
            # pagelink = cells[1].find('a')['href']
            title = cells[1].find('a')['title']
            magnet = cells[2].find('a')['href'] if cells[2].find('a') and cells[2].find('a').has_attr('href') else "NA"
            size = cells[3].get_text()
            age = cells[4].get_text()
            seed_text = cells[5].get_text(strip=True)
            seeds = int(seed_text) if seed_text.isdigit() else 0
            result = {
                "title": title,
                "magnet": magnet,
                "size": size,
                "age": age,
                "seeds": seeds
            }
            results.append(result)

    sorted_data = sorted(results, key=lambda x: int(x["seeds"]), reverse=True)
    total_pages = 1
    return sorted_data, total_pages
  