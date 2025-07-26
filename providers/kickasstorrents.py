import aiohttp
import asyncio
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# List of user-agent strings to use
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
]

BASE_URL = "https://kickasstorrents.to"
base_url = "https://kickasstorrents.to/usearch/"

async def fetch(session, url, headers):
    async with session.get(url, headers=headers) as response:
        if response.status != 200:
            print(f"Request failed: {response.status}")
        return await response.text()

async def fetch_magnet(session, page_url):
    try:
        headers = {"User-Agent": random.choice(user_agents)}
        html = await fetch(session, page_url, headers)
        soup = BeautifulSoup(html, "html.parser")

        magnet_elem = soup.select_one("a.kaGiantButton[href^='magnet:']") or \
                      soup.select_one("a.siteButton.giantButton[href^='magnet:']")

        if magnet_elem and magnet_elem.has_attr("href"):
            return magnet_elem["href"]
    except Exception as e:
        print(f"Error fetching magnet from {page_url}:", e)
    return "N/A"

async def get_kickass_torrents(encoded_query: str, page: int = 1):
    results = []
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp"
    }

    final_encoded_query = f"{encoded_query}/{page}" if page > 1 else encoded_query
    search_url = f"{base_url}{final_encoded_query}/"

    async with aiohttp.ClientSession() as session:
        html_content = await fetch(session, search_url, headers)
        soup = BeautifulSoup(html_content, "html.parser")

        tasks = []

        for row in soup.select("table.data.frontPageWidget > tbody > tr")[1:]:  # skip header row
            try:
                title_elem = row.select_one("a.cellMainLink")
                title = title_elem.get_text(strip=True) if title_elem else "N/A"
                page_url = urljoin(BASE_URL, title_elem['href']) if title_elem and 'href' in title_elem.attrs else "N/A"

                size_elem = row.select_one("td.nobr.center")
                size = size_elem.get_text(strip=True) if size_elem else "N/A"

                uploader_elem = row.select_one("a.plain[href^='/user/']")
                uploader = uploader_elem.get_text(strip=True) if uploader_elem else "N/A"

                age_elem = row.select_one("td[title]")
                age = age_elem['title'].replace('<br/>', ' ') if age_elem and 'title' in age_elem.attrs else "N/A"

                seed_elem = row.select_one("td.green.center")
                seeds = seed_elem.get_text(strip=True) if seed_elem else "0"

                # Schedule fetching of magnet link
                magnet_task = asyncio.create_task(fetch_magnet(session, page_url)) if page_url != "N/A" else "N/A"

                tasks.append((title, page_url, size, uploader, age, seeds, magnet_task))
            except Exception as e:
                print("Error parsing row:", e)

        torrents = []
        for title, page_url, size, uploader, age, seeds, magnet_task in tasks:
            magnet = await magnet_task if isinstance(magnet_task, asyncio.Task) else magnet_task
            torrents.append({
                "title": title,
                "page_url": page_url,
                "size": size,
                "uploader": uploader,
                "age": age,
                "seeds": seeds,
                "magnet": magnet
            })

        pagination = soup.select("div.pages.botmarg5px.floatright a.turnoverButton")
        page_numbers = [int(link.get_text(strip=True)) for link in pagination if link.get_text(strip=True).isdigit()]
        total_pages = max(page_numbers) if page_numbers else 1

        sorted_data = sorted(torrents, key=lambda x: int(x["seeds"]), reverse=True)

        return sorted_data, total_pages
