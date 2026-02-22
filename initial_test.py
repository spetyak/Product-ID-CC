from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

def main():

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

    # GO TO GAME PAGE
    driver.get('https://store.steampowered.com/app/848350/Katamari_Damacy_REROLL/')

    sleep(3) # Sleeping to allow all page elements to load, may be able to reduce or eliminate later

    # ADD GAME TO WISHLIST
    s = driver.find_element(By.XPATH, '//*[@id="add_to_wishlist_area"]')
    a = webdriver.ActionChains(driver)
    a.click(s).perform()

    

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
