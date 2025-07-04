from selenium import webdriver

# Setup Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("headless")
chrome_options.add_argument("disable-gpu")
chrome_options.add_argument("window-size=1920x1080")
