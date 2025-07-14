import requests
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile
import shutil
import random

# List of user-agent strings to use
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
]

# Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("window-size=1920x1080")

# KickassTorrents search base URL
base_url = "https://kickasstorrents.to/usearch/"

def get_kickass_torrents(encoded_query: str, page: int = 1):
    if page == 1:
        final_encoded_query = encoded_query
    else:
        final_encoded_query = f"{encoded_query}/{page}"

    # Create a temporary user data dir and attach a random user-agent
    user_data_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

    # Step 1: Fetch raw HTML using requests
    search_url = f"{base_url}{final_encoded_query}/"
    headers = {"User-Agent": random.choice(user_agents)}
    response = requests.get(search_url, headers=headers)
    html_content = response.text

    # Step 2: Encode HTML and load into Selenium using data URL
    encoded_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    data_url = f"data:text/html;base64,{encoded_html}"

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(data_url)

    # Wait until search results load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "cellMainLink")))

    # Get pagination links
    pagination_links = driver.find_elements(By.CSS_SELECTOR, "a.turnoverButton")
    page_urls = set()
    for link in pagination_links:
        href = link.get_attribute("href")
        if href:
            page_urls.add(href.strip())

    # Extract search result info
    links = driver.find_elements(By.CLASS_NAME, "cellMainLink")
    sizes = driver.find_elements(By.CSS_SELECTOR, "td.nobr.center")
    uploaders = driver.find_elements(By.CSS_SELECTOR, "div.mainpart .plain")
    ages = driver.find_elements(By.CSS_SELECTOR, "td.center[title]")
    seeds = driver.find_elements(By.CSS_SELECTOR, "td.green.center")

    list_of_uploader = []
    for uploader in uploaders:
        uploader_name = uploader.text.strip()
        if 'results' not in uploader_name:
            list_of_uploader.append(uploader_name)
    list_of_uploader = [name.strip() for name in list_of_uploader if name.strip()]

    results = {}
    for idx, (link, size, uploader, age, seed) in enumerate(
        zip(links, sizes, list_of_uploader, ages, seeds), start=1
    ):
        title = link.text.strip()
        page_url = link.get_attribute("href")
        size_text = size.text.strip()
        age_text = age.text.strip()
        seed_text = seed.text.strip()

        results[idx] = {
            "title": title,
            "page_url": page_url,
            "size": size_text,
            "uploader": uploader,
            "age": age_text,
            "seed": seed_text
        }

    # Now fetch magnet links
    # Now fetch magnet links using requests + Selenium (data URL)
    for idx, result in results.items():
        try:
            # Step 1: Get the HTML of the detail page using requests
            headers = {"User-Agent": random.choice(user_agents)}
            detail_response = requests.get(f"https://kickasstorrents.to{result["page_url"]}", headers=headers)
            detail_html = detail_response.text

            # Step 2: Encode HTML as base64 and pass to Selenium
            encoded_detail_html = base64.b64encode(detail_html.encode("utf-8")).decode("utf-8")
            data_url = f"data:text/html;base64,{encoded_detail_html}"

            driver.get(data_url)

            # Step 3: Try locating the magnet button(s)
            try:
                magnet_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.kaGiantButton"))
                )
            except:
                magnet_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.siteButton.giantButton"))
                )

            magnet = magnet_element.get_attribute("href")

        except Exception as e:
            print(f"Error getting magnet for {result['title']}: {e}")
            magnet = "N/A"

        result["magnet"] = magnet

    driver.quit()
    shutil.rmtree(user_data_dir, ignore_errors=True)
    return results, len(page_urls)
