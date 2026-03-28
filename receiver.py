"""
Author: Sean Petyak
Last Updated: 3/28/2026
"""

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import random
import re
import sys
from time import sleep



def getCharLSBBitVal(string, index):
    """
    Returns the least significant bit value of a character at a given index in a string.

    Args:
        string (str): A string representing a product ID
        index (int): The index of the string character of interest

    Returns:
        int: The value of the least significant bit of the targeted characters
    """

    if index >= len(string): # if id too short, treat missing indices as 0
        return 0
    
    return int(string[index]) & 1



def decode(productID):
    """
    Decodes a given product ID into a 0 or 1 by XORing the LSB of key characters 
    (1st, 3rd, and 5th rightmost characters).

    Args:
        productID (str): A string representing a product ID

    Returns:
        int: A 0 or 1 determined by the LSB of key characters in the product ID
    """

    productIDrev = productID[::-1] # reverse to have indexing work from right to left <--

    return getCharLSBBitVal(productIDrev, 1) \
            ^ getCharLSBBitVal(productIDrev, 3) \
            ^ getCharLSBBitVal(productIDrev, 5)



def main():

    if (len(sys.argv) != 2): # ensure caller uses proper calling format

        print(
            f"ERROR:\n" \
            "\tPlease call this program using the following format:\n" \
            "\tpython sender.py <output file path>\n"
        )

    outputMessageFile = None

    try:

        outputMessageFile = open(sys.argv[1], "w")

    except Exception:

        print(
            "ERROR:\n" \
            f"\tThere was an error opening {sys.argv[1]}, aborting process.\n"
        )
        exit(0)



    # Setup Selenium webdriver to use Google Chrome browser
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")   # only display logs related to fatal errors
    options.add_argument("--start-maximized")   # start with browser window maximized (more real)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        " AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/146.0.0.0 Safari/537.36"
    ) # use realistic user agent
    driver = webdriver.Chrome(options=options)
    # driver.execute_script("""
    # Object.defineProperty(navigator, 'webdriver', {
    #     get: () => undefined
    # })
    # """)



    # https://stackoverflow.com/questions/60097388/scraping-problem-inspect-element-different-from-view-page-source#:~:text=The%20page%20content%20is%20probably,render%20the%20javascript%20for%20you.

    last_links = []
    writeLine = []

    while True:

        driver.get("https://store.steampowered.com/wishlist/id/jd-pidcc/") # Open Steam login page
        sleep(10) # wait for page to fully load

        scraped_links = []

        elements = driver.find_elements(By.TAG_NAME, "a") # find all link elements on the wishlist webpage
        for link in elements:
        
            href_value = link.get_attribute("href") # get the specific URL the link points to

            # look for a new link that has the word "app" in its URL, signaling a Steam game
            if href_value \
            and "app" in href_value \
            and href_value not in scraped_links:
                scraped_links.append(href_value) # add to list of scraped links

        print(f"Checking... [{len(scraped_links) < 8} and {scraped_links == last_links}]")

        # if the wishlist cannot represent a byte or there has been no update to the list, wait
        if (len(scraped_links) < 8) or (scraped_links == last_links):
            sleep(random.randint(30, 50))
            continue

        

        readList = [] # a list of all product IDs read from the wishlist

        for link in scraped_links:
            match = re.search("/(\\d+)/", link) # search the string for just digits surrounded by "/"
            readList.append(match.group(1))     # add the first occurence of identified ID to list

        char = 0
        for i in range(8): # will always check first 8, so sender can add random cover items after

            char |= decode(readList[i]) << i # decode the product ID string to reconstruct byte

        decodedChar = chr(char)



        if decodedChar == '': # null character signals end of transmission

            if len(writeLine) != 0: # current output text line not empty

                outputMessageFile.write("".join(writeLine)) # write contents to file
                writeLine = []

            break

        else:

            print(f"Output: {decodedChar}")

            writeLine.append(decodedChar) # add decoded character to output text line
            
            if decodedChar == '\n': # end of current current output text line

                outputMessageFile.write("".join(writeLine)) # write contents to file
                writeLine = []
        
        

        last_links = scraped_links.copy() # copy current wishlist content to last list for checks

        sleep(random.randint(30, 60)) # sleep between 30-60 seconds then continue checking wishlist

    

    outputMessageFile.close()

    return

if __name__ == "__main__":
    main()
