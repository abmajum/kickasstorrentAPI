from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("headless")
chrome_options.add_argument("disable-gpu")
chrome_options.add_argument("window-size=1920x1080")

# Prepare search query
url = "https://kickasstorrents.to/usearch/"

def get_torrents(encoded_query: str, page: str = 1):
  
  if page == 1:
      final_encoded_query = encoded_query
  else:
      final_encoded_query = f"{encoded_query}/{str(page)}"

  # Start browser and go to the search results page
  driver = webdriver.Chrome(options=chrome_options)
  
  driver.get(f"{url}{final_encoded_query}/")
  # Wait until search results are loaded
  wait = WebDriverWait(driver, 10)
  wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "cellMainLink")))

  # --- Get pagination links ---
  pagination_links = driver.find_elements(By.CSS_SELECTOR, "a.turnoverButton")
  page_urls = set()
  for link in pagination_links:
      href = link.get_attribute("href")
      if href:
          page_urls.add(href.strip())
  # print("\nAll Pagination Pages:")
  # for page_url in sorted(page_urls):
  #     print(page_url)
  # Extract titles and links
  results = {}
  links = driver.find_elements(By.CLASS_NAME, "cellMainLink")
  sizes = driver.find_elements(By.CSS_SELECTOR, "td.nobr.center")
  uploaders = driver.find_elements(By.CSS_SELECTOR, "div.mainpart .plain")
  list_of_uploader = []
  for uploader in uploaders:
      uploader_name = uploader.text.strip()
      if 'results' not in uploader_name:
          list_of_uploader.append(uploader_name)
  list_of_uploader = [name.strip() for name in list_of_uploader if name.strip()]

  print(list_of_uploader)
  ages = driver.find_elements(By.CSS_SELECTOR, "td.center[title]")
  seeds = driver.find_elements(By.CSS_SELECTOR, "td.green.center")

  # for idx, link in enumerate(links, start=1):
  #     title = link.text.strip()
  #     page_url = link.get_attribute("href")
  #     results[idx] = {"title": title, "page_url": page_url}
  for idx, (link, size, uploader, age, seed) in enumerate(zip(links, sizes, list_of_uploader, ages, seeds), start=1):
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
  driver.quit()
  return results, len(page_urls)
