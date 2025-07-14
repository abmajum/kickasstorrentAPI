import requests
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# List of user-agent strings to use
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
]

BASE_URL="https://kickasstorrents.to"
base_url = "https://kickasstorrents.to/usearch/"
headers = {"User-Agent": random.choice(user_agents)}


# KickassTorrents search base URL
base_url = "https://kickasstorrents.to/usearch/"

def get_kickass_torrents(encoded_query: str, page: int = 1):
    if page == 1:
        final_encoded_query = encoded_query
    else:
        final_encoded_query = f"{encoded_query}/{page}"

    # Step 1: Fetch raw HTML using requests
    search_url = f"{base_url}{final_encoded_query}/"
    headers = {"User-Agent": random.choice(user_agents)}
    response = requests.get(search_url, headers=headers)
    html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")

    results = []
    # Find all rows that contain torrent entries
    for row in soup.select("table.data.frontPageWidget > tbody > tr")[1:]:  # skip header row
        try:
            # Title
            title_elem = row.select_one("a.cellMainLink")
            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            page_url = urljoin(BASE_URL, title_elem['href']) if title_elem and 'href' in title_elem.attrs else "N/A"

            # Size
            size_elem = row.select_one("td.nobr.center")
            size = size_elem.get_text(strip=True) if size_elem else "N/A"

            # Uploader
            uploader_elem = row.select_one("a.plain[href^='/user/']")
            uploader = uploader_elem.get_text(strip=True) if uploader_elem else "N/A"

            # Age (tooltip)
            age_elem = row.select_one("td[title]")
            age = age_elem['title'].replace('<br/>', ' ') if age_elem and 'title' in age_elem.attrs else "N/A"

            # Seeds
            seed_elem = row.select_one("td.green.center")
            seeds = seed_elem.get_text(strip=True) if seed_elem else "0"
            # Fetch magnet link from detailed page
            # Fetch magnet link from detailed page
            magnet = "N/A"
            if page_url != "N/A":
                try:
                    detail_response = requests.get(page_url, headers={"User-Agent": random.choice(user_agents)})
                    detail_soup = BeautifulSoup(detail_response.text, "html.parser")

                    # Try primary selector
                    magnet_elem = detail_soup.select_one("a.kaGiantButton[href^='magnet:']")
                    if magnet_elem and magnet_elem.has_attr("href"):
                        magnet = magnet_elem["href"]
                    else:
                        # Try fallback selector
                        magnet_elem = detail_soup.select_one("a.siteButton.giantButton[href^='magnet:']")
                        if magnet_elem and magnet_elem.has_attr("href"):
                            magnet = magnet_elem["href"]

                except Exception as e:
                    print(f"Error fetching magnet from {page_url}:", e)
            results.append({
                "title": title,
                "page_url": page_url,
                "size": size,
                "uploader": uploader,
                "age": age,
                "seeds": seeds,
                "magnet": magnet
            })
        except Exception as e:
            print("Error parsing row:", e)

    pagination = soup.select("div.pages.botmarg5px.floatright a.turnoverButton")

    # Extract numeric page numbers
    page_numbers = []
    for link in pagination:
        text = link.get_text(strip=True)
        if text.isdigit():
            page_numbers.append(int(text))

    total_pages = max(page_numbers) if page_numbers else 1

    sorted_data = sorted(results, key=lambda x: int(x["seeds"]), reverse=True)

    return sorted_data, total_pages
