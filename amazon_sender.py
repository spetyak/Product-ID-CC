from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep
import random
import json

driver = None


def text_to_hex(text):
    return text.encode("utf-8").hex().upper()


def load_mapping():
    try:
        with open("url_library.JSON", "r") as f:
            mapping = json.load(f)
            print(f"Loaded mapping for {len(mapping)} hex characters.")
            return mapping
    except Exception as e:
        print("ERROR: Could not load url_library.json:", e)
        return None


def build_pools(mapping):
    pools = {}
    for key in mapping:
        pools[key] = mapping[key].copy()
        random.shuffle(pools[key])
    return pools


def get_url_for_char(char, mapping, pools, last_url):
    if char not in mapping:
        print(f"[!] No mapping for hex char: {char}")
        return None, last_url

    # Refill pool if empty
    if not pools[char]:
        pools[char] = mapping[char].copy()
        random.shuffle(pools[char])

    # Avoid immediate repeat if possible
    for i in range(len(pools[char])):
        candidate = pools[char][i]
        if candidate != last_url:
            url = pools[char].pop(i)
            return url, url

    # fallback
    url = pools[char].pop()
    return url, url


def hex_to_urls(hex_string, mapping):

    used_urls = set()
    urls = []

    for char in hex_string:
        if char not in mapping:
            print(f"[!] No mapping for: {char}")
            continue

        # Filter out already used URLs
        available = [u for u in mapping[char] if u not in used_urls]

        if not available:
            raise Exception(
                f"No unused URLs left for hex '{char}'. "
                f"Add more URLs to url_library.json."
            )

        # Randomly pick from remaining valid URLs
        url = random.choice(available)

        urls.append(url)
        used_urls.add(url)

    return urls


def safe_click(element):
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)


def add_to_wishlist(url):
    global driver

    print(f"Visiting: {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        sleep(2)

        selectors = [
            (By.ID, "add-to-wishlist-button-submit"),
            (By.NAME, "submit.add-to-registry.wishlist"),
            (By.XPATH, "//input[contains(@aria-label,'Add to List')]"),
            (By.XPATH, "//span[contains(text(),'Add to List')]"),
        ]

        for by, value in selectors:
            try:
                btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by, value))
                )
                safe_click(btn)
                print(f"Added: {url}")
                break
            except TimeoutException:
                continue
        else:
            print(f"FAILED (no button found): {url}")
            return

        
        try:
            list_option = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[contains(text(),'Wish List')]")
                )
            )
            safe_click(list_option)
        except TimeoutException:
            pass

    except TimeoutException:
        print(f"FAILED (page load issue): {url}")


def main():
    global driver

    options = webdriver.FirefoxOptions()
    options.set_preference("dom.webnotifications.enabled", False)

    driver = webdriver.Firefox(
        service=Service(GeckoDriverManager().install()),
        options=options
    )

    driver.get("https://www.amazon.com/")
    input("Log into Amazon, then press Enter...")

    message = input("Enter message to send: ")

    hex_message = text_to_hex(message)
    print(f"\n[+] Hex Message: {hex_message}")

    mapping = load_mapping()
    if not mapping:
        return

    product_urls = hex_to_urls(hex_message, mapping)

    print(f"[+] Generated {len(product_urls)} URLs.\n")

    for url in product_urls:
        add_to_wishlist(url)
        sleep(random.uniform(2.5, 5))

    print("Finished sending message.")

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        driver.quit()


if __name__ == "__main__":
    main()