"""
Author: Sean Petyak
Last Updated: 2/22/2026
"""

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from time import sleep
import sys
import re
import random

# globals
driver = None



def getGames():
    """
    Description

    Returns:
        _type_: _description_
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
        gameList.append(line.strip())
    f.close()
    return gameList



def getCharLSBBitVal(string, index):

    if index >= len(string): # if id too short, treat missing indices as 0
        return 0
    
    return int(string[index]) & 1

def encode(productID):

    productIDrev = productID[::-1] # reverse to have indexing work from right to left <--

    return getCharLSBBitVal(productIDrev, 1) ^ getCharLSBBitVal(productIDrev, 3) ^ getCharLSBBitVal(productIDrev, 5)



def splitList(idList):

    zeroList = []
    oneList = []

    for link in idList:

        match = re.search("/(\\d+)/", link)
        productID = match.group(1)
        encoded = encode(productID)

        if encoded == 0:
            zeroList.append(link)
        else:
            oneList.append(link)

    return zeroList, oneList



def removeAll():
    """
    Description
    """

    global driver

    # confirm on wishlist page
    if "wishlist" not in driver.current_url:
        # redirect to wishlist page
        driver.get("https://store.steampowered.com/wishlist/id/jd-pidcc/")
        sleep(2) # allow page to load

    # look for all button objects with text "remove"
    # L click on remove button
    # L wait a moment and repeat (0.1s maybe?)
    try:
        while True:

            element = driver.find_element(By.XPATH, "//button[text()='remove']")
            mouse = webdriver.ActionChains(driver) # can be moved elsewhere to avoid repetition
            mouse.click(element).perform()
            sleep(random.uniform(0.5, 1.5))

    except NoSuchElementException:
        print("All previous wishlist entries successfully removed.")
        return

    return



def add(gameList):
    """
    Description

    Args:
        gameList (_type_): _description_
    """

    global driver



    for game in gameList:

        driver.get(game)

        sleep(random.randint(2, 5)) # Sleeping to allow all page elements to load, may be able to reduce or eliminate later

        # ADD GAME TO WISHLIST
        try:
            
            s = driver.find_element(By.XPATH, '//*[@id="add_to_wishlist_area"]')
            a = webdriver.ActionChains(driver)
            a.click(s).perform()

        except NoSuchElementException:

            print("Handing control back to user to troubleshoot, press enter when done")
            userInput = input()
            continue

    return



def main():

    global driver



    f = None

    try:

        f = open(sys.argv[1], "r")

    except Exception:

        print(
            "ERROR:\n" \
            f"\tThere was an error opening {sys.argv[1]}, aborting process." \
            "Please ensure the file exists."
        )
        exit(0)

    # Setup Selenium webdriver to use Google Chrome browser
    # Only display logs related to fatal errors, limit all other logs that are output
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument("--start-maximized")
    # options.add_argument("user-data-dir=./chrome_profile")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        " AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/146.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)

    driver.get("https://store.steampowered.com/login/") # Open Steam login page

    # Hand over execution to human to login, then return control once in
    print("Log in via the spawned Chrome window. Press enter once logged in.")

    userInput = input()

    if userInput != None:
        print("Input received, returning to normal process execution")



    gameList = getGames()
    zeroList, oneList = splitList(gameList)
    addList = []

    # ==========================================================================================
    #
    # ENTER MAIN SENDER LOOP
    #
    # TODO: Repeatedly add various games to account wishlist via their URLs. Determine exact
    # method of encoding to determine which URLs to choose. 
    #
    # ==========================================================================================

    char = f.read(1)
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

            currentBit = (binary & (1 << i)) >> i

            if currentBit == 0:

                while True:

                    index = random.randint(0, len(zeroList)-1)  # select random game from zero list

                    if zeroUsedList[index] == True: # check if game has been used in this message yet
                        continue

                    else: # if ok, add game and mark as used for this transmission

                        addList.append(zeroList[index])
                        print(f"0. Adding {zeroList[index]} to the list")
                        zeroUsedList[index] = True
                        break

               

            else:

                while True:

                    index = random.randint(0, len(oneList)-1)  # select random game from one list

                    if oneUsedList[index] == True: # check if game has been used in this message yet
                        continue

                    else: # if ok, add game and mark as used for this transmission

                        addList.append(oneList[index])
                        print(f"1. Adding {oneList[index]} to the list")
                        oneUsedList[index] = True
                        break

        # ADD NEW GAMES TO WISHLIST
        add(addList)

        sleep(60)
        # print(f"Sent \"{char}\", press enter to continue.")
        # userInput = input()

        char = f.read(1)



    removeAll()

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
                print(f"0. Adding {zeroList[index]} to the list")
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
