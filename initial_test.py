from selenium import webdriver
from time import sleep

def main():

    driver = webdriver.Chrome()

    driver.get("https://www.target.com/")

    try: 

        while True:

            sleep(1)

    except KeyboardInterrupt:

        driver.quit()
        exit(0)

    return

if __name__ == "__main__":
    main()