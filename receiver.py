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

def getCharLSBBitVal(string, index):

    if index >= len(string): # if id too short, treat missing indices as 0
        return 0
    
    return int(string[index]) & 1

def decode(productID):

    productIDrev = productID[::-1] # reverse to have indexing work from right to left <--

    return getCharLSBBitVal(productIDrev, 1) ^ getCharLSBBitVal(productIDrev, 3) ^ getCharLSBBitVal(productIDrev, 5)



def main():

    scraped_links = []

    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)

    driver.get("https://store.steampowered.com/wishlist/id/jd-pidcc/") # Open Steam login page

    # https://stackoverflow.com/questions/60097388/scraping-problem-inspect-element-different-from-view-page-source#:~:text=The%20page%20content%20is%20probably,render%20the%20javascript%20for%20you.

    
    sleep(2) # wait for page to fully load

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

    readList = []

    print("Scraped IDs:")
    for link in scraped_links:
        match = re.search("/(\\d+)/", link)
        readList.append(match.group(1))
        print(match.group(1))

    char = 0
    for i in range(len(readList)): # should be length 8

        char |= decode(readList[i]) << i
    
    print(f"Output: {chr(char)}")

    return

if __name__ == "__main__":
    main()
