import re
import time
import requests
import schedule
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import URL, BASE_URL
from logger import error_logger
from models import Car


def driver_chrome():
    chrome_op = webdriver.ChromeOptions()
    chrome_op.add_argument('--disable-gpu')
    chrome_op.add_argument('--no-sandbox')
    try:
        driver = webdriver.Chrome(options=chrome_op)
        return driver
    except TimeoutException as e:
        error_logger.error(e)


def get_count_of_pages():
    base_html = requests.get(BASE_URL).content
    soup = BeautifulSoup(base_html, 'html.parser')
    script_tags = soup.find_all('script')
    js_code = str()
    for script_tag in script_tags:
        js_code += script_tag.string or ''
    count_match = re.search(r'window\.ria\.server\.resultsCount = Number\((\d+)\);', js_code)
    if count_match:
        count = int(count_match.group(1))
        return (count // 100) + 1
    return 0


def scrape_card(url):
    odometer = None
    driver = driver_chrome()
    try:
        loaded_html = requests.get(url).content
        soup = BeautifulSoup(loaded_html, 'html.parser')
        title = soup.find(class_='auto-content_title')
        price = soup.find(class_='price_value').find('strong')
        if price and '$' not in price.text:
            price = soup.find('span', {'data-currency': 'USD'})
        pic_url = soup.find(id='photosBlock').find('picture').find('source')
        odometer_div = soup.find(class_='base-information')
        if odometer_div:
            odometer = odometer_div.find('span', class_='size18')
        username = soup.find(class_='seller_info_name')
        if username and not username.text:
            username = username.find('a')
        images_count = soup.find('span', class_='count').find('span', class_='mhide')
        car_number = soup.find('span', class_='state-num')
        vin = soup.find('span', class_='label-vin')
        if not vin:
            vin = soup.find('span', class_='vin-code')

        driver.get(url)
        show_link_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'phone_show_link'))
        )
        if show_link_element.is_displayed():
            driver.execute_script("arguments[0].click();", show_link_element)
            time.sleep(0.1)

        full_phone_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'phone'))
        )
        process_data(url, pic_url, title, price, odometer, username, images_count, car_number, vin, full_phone_element)

    except Exception as e:
        error_logger.error(e)
    finally:
        driver.quit()


def process_data(car_url, pic_url, title, price, odometer, username, images_count, car_number, vin, phone):
    data = {
        'url': car_url,
        'image_url': pic_url.get('srcset') if pic_url else None,
        'title': title.text.strip() if title else None,
        'price_usd': float(price.text.replace(' ', '').replace('$', '')) if price else None,
        'odometer': int(odometer.text.replace(' ', '')) * 1000 if odometer else None,
        'username': username.text.strip() if username else None,
        'images_count': int(images_count.text.split()[-1]) if images_count else 0,
        'car_number': car_number.text.replace(' ', '')[:9] if car_number else None,
        'car_vin': vin.text.replace(' ', '') if vin else None,
        'phone_number': f"+38{phone.text.replace(' ', '').replace('(', '').replace(')', '')}" if phone and phone.text != '' else None
    }
    Car.insert_data(Car.connect_db(), data)


def scrape_pages():
    pages = get_count_of_pages()
    for page in range(0, pages + 1):
        try:
            url = URL.format(page=page)
            loaded_html = requests.get(url).content
            soup = BeautifulSoup(loaded_html, 'html.parser')
            car_cards_links_tags = soup.find_all('a', class_='address')
            car_cards_links = [car_card.get('href') for car_card in car_cards_links_tags]
            try:
                for link in car_cards_links:
                    if not Car.check_car_exists(Car.connect_db(), link):
                        scrape_card(link)
            except Exception as e:
                error_logger.error(e)
                continue

        except Exception as e:
            error_logger.error(e)
            continue


table_created = False


def scrape():
    global table_created

    try:
        with Car.connect_db() as session:
            if not table_created:
                Car.create_table()
                table_created = True

            scrape_pages()

    except Exception as e:
        error_logger.error(f"An error occurred during scraping: {str(e)}")


def make_dump():
    try:
        with Car.connect_db() as session:
            session.commit()
            Car.dump_database()

    except Exception as e:
        error_logger.error(f"An error occurred during database dump: {str(e)}")


if __name__ == '__main__':
    schedule.every().day.at("12:00").do(scrape)
    schedule.every().day.at("00:00").do(make_dump)

    while True:
        schedule.run_pending()
        time.sleep(1)
