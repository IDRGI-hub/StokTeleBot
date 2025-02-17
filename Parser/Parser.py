import asyncio
import json
import logging
import os
import re
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import MAYAK_URL, WILDBERRIES_URL_TEMPLATE, USERNAME, PASSWORD, ARTICLES, COOKIE_FILE, EXTENSION_PATH, OUTPUT_FILE

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def save_cookies(driver, filename):
    cookies = driver.get_cookies()
    with open(filename, "w") as f:
        json.dump(cookies, f)
        logging.info(f"Saved cookies to {filename}")

def load_cookies(driver, filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            cookies = json.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        logging.info(f"Loaded cookies from {filename}")

def setup_driver():
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36")
    
    service = FirefoxService()
    driver = webdriver.Firefox(service=service, options=options)
    logging.info("Driver set up with custom headers.")
    
    # Установка расширения
    if EXTENSION_PATH:
        driver.install_addon(EXTENSION_PATH, temporary=True)
        logging.info(f"Installed extension: {EXTENSION_PATH}")
    
    return driver

def check_captcha(driver):
    if "captcha" in driver.page_source.lower():
        logging.warning("CAPTCHA detected! Manual resolution required.")
        return True
    return False

async def login_mayak(driver):
    driver.get(MAYAK_URL)
    logging.info("Loading Mayak...")
    await asyncio.sleep(3)
    
    load_cookies(driver, COOKIE_FILE)
    driver.get(MAYAK_URL)
    Urltest = driver.current_url
    logging.info(f"go to {Urltest}")
    await asyncio.sleep(3)
    
    if "categories" in driver.current_url:
        logging.info("Already logged in with cookies.")
        return
    
    username_field = driver.find_element(By.NAME, "user[login]")
    password_field = driver.find_element(By.NAME, "user[password]")
    submit_button = driver.find_element(By.NAME, "commit")
    
    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)
    submit_button.click()
    
    await asyncio.sleep(5)
    
    if "categories" in driver.current_url:
        logging.info("Login successful.")
        save_cookies(driver, COOKIE_FILE)
    else:
        logging.error("Login failed.")

def extract_stock_info(html):
    soup = BeautifulSoup(html, "html.parser")

    # Найти блок с остатками
    stock_block = soup.find("div", class_="mayak-link mayak-toggle")
    if not stock_block:
        logging.warning("❌ Stock block not found in HTML")
        return None

    # Извлекаем текст с остатками
    stock_text = stock_block.get_text(strip=True)
    logging.info(f"✅ Found stock text: {stock_text}")
    
    stock_text = stock_text.replace("\u202f", "").replace("\xa0", "")  # Убираем неразрывные пробелы
    stock_parts = stock_text.split("Остаток:")[-1].strip().split("шт.")

    if len(stock_parts) < 2:
        logging.warning(f"⚠️ Stock info format incorrect: {stock_text}")
        return None

    try:
        total_stock = int(stock_parts[0].strip())
    except ValueError:
        logging.warning(f"❌ Failed to parse total stock: {stock_parts[0]}")
        return None

    # Найти блок со складами
    warehouse_details = {}
    warehouse_block = soup.find("div", class_="mayak-remains mayak-popover")

    if warehouse_block:
        for warehouse in warehouse_block.find_all("div"):
            warehouse_text = warehouse.get_text(strip=True).replace("\u202f", "").replace("\xa0", "")
            parts = warehouse_text.split(":")
            if len(parts) == 2:
                warehouse_name = parts[0].strip()
                try:
                    quantity = int(parts[1].replace("шт.", "").strip())
                    warehouse_details[warehouse_name] = quantity
                except ValueError:
                    logging.warning(f"⚠️ Failed to parse warehouse quantity: {parts[1]}")
    
    logging.info(f"✅ Extracted stock info: total_stock={total_stock}, warehouses={len(warehouse_details)}, details={warehouse_details}")

    return {
        "total_stock": total_stock,
        "warehouses": len(warehouse_details),
        "details": warehouse_details
    }



async def scrape_wildberries(driver):
    results = {}
    
    for article_id, product_name in ARTICLES.items():
        url = WILDBERRIES_URL_TEMPLATE.format(article_id)
        driver.get(url)
        await asyncio.sleep(25)
        
        if check_captcha(driver):
            logging.error(f"CAPTCHA detected on {url}. Skipping...")
            results[product_name] = "CAPTCHA encountered"
            continue
        
        try:
            logging.info(f"Attempting to scrape: {product_name}")
            html_content = driver.page_source
            stock_info = extract_stock_info(html_content)

            if stock_info:
                results[product_name] = stock_info
                logging.info(f"Scraped {product_name}: {stock_info}")
            else:
                results[product_name] = "Stock info not found"
                logging.warning(f"Stock info not found for {product_name}")
            
            html_file = f"wildberries_page_{article_id}.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            logging.info(f"Saved page HTML to {html_file}")
        except Exception as e:
            logging.error(f"Failed to scrape {product_name}: {e}")
            results[product_name] = "Error scraping data"
    
    return results

async def scrape_data():
    driver = setup_driver()
    try:
        await login_mayak(driver)
        results = await scrape_wildberries(driver)
    finally:
        driver.quit()
        logging.info("Driver closed.")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    return results
