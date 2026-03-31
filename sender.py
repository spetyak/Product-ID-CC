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

# globals
driver = None



def getGames():
    """
    Creates a list of Steam game links from a file containing the links named "game_links".

    Returns:
        list[str]: A list of Steam game link strings
    """

    f = None

    try:

        f = open("game_links", "r")
    
    except Exception:

        print(
            "ERROR:\n" \
            "\tThere was an issue opening the game_link file, process aborting." \
            "\tPlease confirm the game_link file exists and that the user has correct permissions."
        )
        return None # signifies caller an error occured and process should terminate
    
    gameList = []
    for line in f:
        gameList.append(line.strip()) # add game link string to list, remove newline from end
    f.close()
    return gameList



def getCharLSBBitVal(string, index):
    """
    Returns the least significant bit value of a character at a given index in a string.

    Args:
        string (str): A string representing a product ID
        index (int): The index of the string character of interest

    Returns:
        int: The value of the least significant bit of the targeted characters
    """

    if index >= len(string): # if ID too short, treat missing indices as 0
        return 0
    
    return int(string[index]) & 1



def encode(productID):
    """
    Encodes a given product ID into a 0 or 1 by XORing the LSB of key characters 
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



def splitList(idList):
    """
    Takes a given list of product ID links, extracts the product IDs, encodes the ID, and sorts 
    product links into a list of IDs that resolve to 0 or a list of IDs that resolve to 1.

    Args:
        idList (list[str]): A list of ALL product IDs to be used for encoding

    Returns:
        tuple(list[str], list[str]): A tuple containing:
            zeroList: A list of product links that resolve to 0 when encoded
            oneList: A list of product links that resolve to 1 when encoded
    """

    zeroList = []
    oneList = []

    for link in idList:

        match = re.search("/(\\d+)/", link) # search the string for just digits surrounded by "/"
        productID = match.group(1)          # get the first occurence of identified digits
        encoded = encode(productID)         # encode the product ID string

        # sort the products based on their ID encodings
        if encoded == 0:
            zeroList.append(link)
        else:
            oneList.append(link)

    return zeroList, oneList



def removeAll():
    """
    Removes all current wishlist items from the public wishlist.
    """

    global driver



    # confirm on wishlist page
    if "wishlist" not in driver.current_url:
        
        driver.get("https://store.steampowered.com/wishlist/id/jd-pidcc/") # go to wishlist page
        sleep(2) # allow page to load

    
    
    # REMOVE GAMES FROM WISHLIST
    try:

        while True:

            element = driver.find_element(By.XPATH, "//button[text()='remove']") # look for a button object with text "remove"
            mouse = webdriver.ActionChains(driver)  # can be moved elsewhere to avoid repetition
            mouse.click(element).perform()          # click on wishlist item remove button
            sleep(random.uniform(0.5, 1.5))         # wait a moment and repeat

    except NoSuchElementException:
        # print("All previous wishlist entries successfully removed.")
        return

    return



def add(gameList):
    """
    Add the given list of Steam games to the user's public wishlist.

    Args:
        gameList (list[str]): A list of Steam game link strings
    """

    global driver



    for game in gameList:

        driver.get(game)            # go to game page using current link
        sleep(random.randint(2, 5)) # sleep to allow page elements to load, may reduce later

        # ADD GAME TO WISHLIST
        try:
            
            s = driver.find_element(By.XPATH, '//*[@id="add_to_wishlist_area"]') # look for the "add to wishlist" page element
            a = webdriver.ActionChains(driver)  # can be moved elsewhere to avoid repetition
            a.click(s).perform()                # click on wishlist item remove button

        except NoSuchElementException:

            print("Handing control back to user to troubleshoot, press enter when done")
            userInput = input() 
            continue

    return



def main():

    global driver



    if (len(sys.argv) != 2): # ensure caller uses proper calling format

        print(
            f"ERROR:\n" \
            "\tPlease call this program using the following format:\n" \
            "\tpython sender.py <input file path>\n"
        )

    inputMessageFile = None

    try:

        inputMessageFile = open(sys.argv[1], "r")

    except Exception:

        print(
            "ERROR:\n" \
            f"\tThere was an error opening {sys.argv[1]}, aborting process." \
            "Please ensure the file exists."
        )
        exit(0)



    # Setup Selenium webdriver to use Google Chrome browser
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")   # only display logs related to fatal errors
    options.add_argument("--start-maximized")   # start with browser window maximized (more real)
    # options.add_argument("user-data-dir=./chrome_profile")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        " AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/146.0.0.0 Safari/537.36"
    ) # use realistic user agent
    driver = webdriver.Chrome(options=options)



    driver.get("https://store.steampowered.com/login/") # Open Steam login page

    # Hand over execution to human to login, then return control once in
    print("Log in via the spawned Chrome window. Press enter once logged in.")

    userInput = input()

    if userInput != None:
        print("Input received, returning to normal process execution")



    # ==========================================================================================
    #
    # ENTER MAIN SENDER LOOP
    #
    # ==========================================================================================

    gameList = getGames()
    zeroList, oneList = splitList(gameList)
    addList = []

    char = inputMessageFile.read(1)
    while char != '':

        print(f"Sending \"{char}\"")

        addList = []

        # (reset) lists to track use of product IDs to avoid attempting reuse in the same message
        zeroUsedList = [False for i in range(len(zeroList))]
        oneUsedList = [False for i in range(len(oneList))]

        # REMOVE ALL PREVIOUS GAMES FROM WISHLIST
        removeAll()

        binary = ord(char)

        # PREPARE NEW GAMES FOR WISHLIST
        for i in range(8):

            currentBit = (binary & (1 << i)) >> i # get ith bit from binary of current char

            if currentBit == 0:

                while True:

                    index = random.randint(0, len(zeroList)-1)  # select random game from zero list

                    if zeroUsedList[index] == True: # check if game was used in this message yet
                        continue

                    else: # if ok, add game and mark as used for this transmission

                        addList.append(zeroList[index])
                        # print(f"0. Adding {zeroList[index]} to the list")
                        zeroUsedList[index] = True
                        break

               

            else:

                while True:

                    index = random.randint(0, len(oneList)-1)  # select random game from one list

                    if oneUsedList[index] == True: # check if game was used in this message yet
                        continue

                    else: # if ok, add game and mark as used for this transmission

                        addList.append(oneList[index])
                        # print(f"1. Adding {oneList[index]} to the list")
                        oneUsedList[index] = True
                        break

        # ADD NEW GAMES TO WISHLIST
        add(addList)

        sleep(60)

        char = inputMessageFile.read(1)



    inputMessageFile.close()
    removeAll()

    print(f"Sending ending null character")

    # send null byte to communicate no longer transmitting
    addList = []
    zeroUsedList = [False for i in range(len(zeroList))]
    for i in range(8):

        while True:

            index = random.randint(0, len(zeroList)-1)  # select random game from zero list

            if zeroUsedList[index] == True: # check if game has been used in this message yet
                continue

            else: # if ok, add game and mark as used for this transmission

                addList.append(zeroList[index])
                # print(f"0. Adding {zeroList[index]} to the list")
                zeroUsedList[index] = True
                break

    add(addList)



    print("Finished main loop actions, log out and then use ^C to end process.")

    # Stay on this page until the user sends a ^C signal to this script
    # !!! Delete this later, just for early testing. !!!
    try: 
        while True:
            sleep(1)

    except KeyboardInterrupt:
        driver.quit()
        exit(0)

    return

if __name__ == "__main__":
    main()
