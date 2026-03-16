"""
Author: Sean Petyak
Last Updated: 2/22/2026
"""

# from ... import ...
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import re
from time import sleep

def main():

    scraped_links = []

    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)

    driver.get("https://store.steampowered.com/wishlist/id/jd-pidcc/") # Open Steam login page

    # https://stackoverflow.com/questions/60097388/scraping-problem-inspect-element-different-from-view-page-source#:~:text=The%20page%20content%20is%20probably,render%20the%20javascript%20for%20you.

    
    sleep(10) # wait for page to fully load

    elements = driver.find_elements(By.TAG_NAME, "a")
    for link in elements:
       
        href_value = link.get_attribute("href")

        if href_value \
        and "app" in href_value \
        and href_value not in scraped_links:
            scraped_links.append(href_value)

    print("Scraped links:")
    for link in scraped_links:
        print(link)

    print("Scraped IDs:")
    for link in scraped_links:
        match = re.search("/(\\d+)/", link)
        print(match.group(1))

    # Stay on this page until the user sends a ^C signal to this script
    # !!! Delete this later, just for early testing. !!!
    # try: 
    #     while True:
    #         sleep(1)

    # except KeyboardInterrupt:
    #     driver.quit()
    #     exit(0)

    return

if __name__ == "__main__":
    main()
