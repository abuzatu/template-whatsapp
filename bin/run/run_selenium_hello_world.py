"""Module to run in one go the selenium hello world."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

print("test")
# CHROME_PROFILE_PATH="user-data-dir=$HOME/.config/google-chrome/Whatsapp"
CHROME_PROFILE_PATH = (
    "user-data-dir=/home/seluser/.config/chromium/google-chrome/Whatsapp"
)
# remove Default from below and replace with our new folder called "Whatsapp"
# MacOS: /Users/abuzatu/Library/Application Support/Google/Chrome/Default
# Linux: home/abuzatu/.config/google-chrome/default

print("test2")
# Set up Chrome options
chrome_options = Options()
# chrome_options.add_argument('--headless') # Commented out
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(CHROME_PROFILE_PATH)

print("test3")
# Start ChromeDriver
driver = webdriver.Remote(
    command_executor="http://standalone-chromium:4444/wd/hub", options=chrome_options
)
print("test4")
driver.maximize_window()

driver.get("https://www.google.com")
print("test5")
time.sleep(5)

driver.get("https://www.hotnews.ro/sport")
time.sleep(5)

driver.get("https://web.whatsapp.com")
time.sleep(30)
