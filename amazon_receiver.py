from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep
import re

WISHLIST_URL = "https://www.amazon.com/hz/wishlist/ls/3RH0N2MBSGEG8/ref=nav_wishlist_lists_1"

def hex_to_text(hex_string):
    """Convert hex string → ASCII text"""
    
    try:
        # Convert hex → bytes
        byte_data = bytes.fromhex(hex_string)
        
        # Convert bytes → string
        return byte_data.decode("utf-8", errors="ignore")
    
    except Exception as e:
        print("Conversion error:", e)
        return None

def scroll_to_load_all(driver):
    """Scroll to load all wishlist items"""
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def extract_asin_from_url(url):
    """Extract ASIN from /dp/ URL"""
    match = re.search(r"/dp/([A-Z0-9]{10})", url)
    return match.group(1) if match else None


def char_to_hex(c):
    """Convert last ASIN character to hex using mod 16"""
    if c.isdigit():
        val = int(c)
    elif c.isalpha():
        val = ord(c.upper()) - ord('A') + 10
    else:
        return None

    return hex(val % 16)[2:].upper()


def main():
    decoded_chars = []

    options = webdriver.FirefoxOptions()
    options.set_preference("dom.webnotifications.enabled", False)

    driver = webdriver.Firefox(
        service=Service(GeckoDriverManager().install()),
        options=options
    )

    print("Opening wishlist...")
    driver.get(WISHLIST_URL)

    sleep(5)

    # Load all items
    scroll_to_load_all(driver)

    items = driver.find_elements(By.XPATH, "//div[contains(@id,'item_')]")

    print(f"Found {len(items)} wishlist items")

    for item in items:
        try:
            # Find product link inside this specific wishlist item
            link = item.find_element(By.XPATH, ".//a[contains(@href, '/dp/')]")
            href = link.get_attribute("href")

            asin = extract_asin_from_url(href)

            if asin:
                last_char = asin[-1]
                hex_char = char_to_hex(last_char)

                if hex_char:
                    decoded_chars.append(hex_char)
                    print(f"{asin} -> {last_char} -> {hex_char}")

        except Exception:
            # Skip items that don't match expected structure
            continue

    # Reverse order to reconstruct original message
    decoded_chars.reverse()

    hex_message = "".join(decoded_chars)

    print("\nHex Message:")
    print(hex_message)

    # Convert to ASCII
    text_message = hex_to_text(hex_message)

    print("\nDecoded Text:")
    print(text_message)

    driver.quit()


if __name__ == "__main__":
    main()