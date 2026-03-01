"""
Author: Sean Petyak
Last Updated: 2/22/2026
"""

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from time import sleep

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
            sleep(0.5)

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

    # travel to game page
    # add to wishlist

    for game in gameList:

        driver.get(game)

        sleep(3) # Sleeping to allow all page elements to load, may be able to reduce or eliminate later

        # ADD GAME TO WISHLIST
        s = driver.find_element(By.XPATH, '//*[@id="add_to_wishlist_area"]')
        a = webdriver.ActionChains(driver)
        a.click(s).perform()

    return



def main():

    global driver

    # Setup Selenium webdriver to use Google Chrome browser
    # Only display logs related to fatal errors, limit all other logs that are output
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
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
    # TODO: Repeatedly add various games to account wishlist via their URLs. Determine exact
    # method of encoding to determine which URLs to choose. 
    #
    # ==========================================================================================

    # REMOVE ALL PREVIOUS GAMES FROM WISHLIST
    removeAll()

    # ADD NEW GAMES TO WISHLIST
    gameList = getGames()
    add(gameList)

    

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
