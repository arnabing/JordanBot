import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import pandas as pd
import time
import logging
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def download_image(url, folder, filename):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            filepath = os.path.join(folder, filename)
            with open(filepath, 'wb') as out_file:
                out_file.write(response.content)
            logging.info(f"Image downloaded: {filepath}")
            return filepath
        else:
            logging.warning(f"Failed to download image: {url}")
    except Exception as e:
        logging.warning(f"Error downloading image {url}: {e}")
    return None


def scrape_product_data():
    # Setup Firefox options
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Ensure GUI is off
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")

    # Set path to geckodriver as per your configuration
    # Ensure this is the correct path and binary
    webdriver_service = Service('./geckodriver')

    # Choose Firefox Browser
    driver = webdriver.Firefox(
        service=webdriver_service, options=firefox_options)

    driver.get("https://www.nike.com/w/mens-jordan-shoes-37eefznik1zy7ok")

    # Scroll to the bottom to load all products
    SCROLL_PAUSE_TIME = 3

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Ensure the images folder exists
    os.makedirs('images', exist_ok=True)

    product_data = []

    products = driver.find_elements(By.CLASS_NAME, 'product-card__body')
    for item in products:
        try:
            name = item.find_element(By.CLASS_NAME, 'product-card__title').text
            category = item.find_element(
                By.CLASS_NAME, 'product-card__subtitle').text

            # Handle cases where price may not be available
            try:
                price = item.find_element(By.CLASS_NAME, 'product-price').text
            except:
                price = 'N/A'

            image_url = item.find_element(
                By.TAG_NAME, 'img').get_attribute('src')
            product_url = item.find_element(
                By.CLASS_NAME, 'product-card__link-overlay').get_attribute('href')

            product_id = str(uuid.uuid4())
            image_path = download_image(
                image_url, 'images', f"{product_id}.jpg")

            product_data.append({
                'product_id': product_id,
                'name': name,
                'category': category,
                'price': price,
                'image_url': image_url,
                'image_path': image_path,
                'product_url': product_url
            })
        except Exception as e:
            logging.warning(f"Error encountered: {e}")

    driver.quit()
    return pd.DataFrame(product_data)


if __name__ == "__main__":
    df = scrape_product_data()
    df.to_csv('products.csv', index=False)
    print("Product data saved to products.csv")
