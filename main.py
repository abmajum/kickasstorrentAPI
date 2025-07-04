from selenium import webdriver

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
  driver.quit()
