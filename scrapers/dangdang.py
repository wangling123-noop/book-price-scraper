from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

logger = logging.getLogger(__name__)

def scrape_dangdang(books):
    results = {}

    proxy_config = {
        'host': 'g416.kdltps.com',
        'port': '15818',
        'username': 't15419362286482',
        'password': 'g5hlxtk8',
        'backup_host': 'g417.kdltps.com'
    }

    def create_driver(proxy_host):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920x1080')

        proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_host}:{proxy_config['port']}"
        options.add_argument(f'--proxy-server={proxy_url}')

        driver = webdriver.Chrome(options=options)
        return driver

    for book in books:
        for proxy_host in [proxy_config['host'], proxy_config['backup_host']]:
            try:
                driver = create_driver(proxy_host)
                driver.get(f'http://search.dangdang.com/?key={book}')
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'name'))
                )
                elems = driver.find_elements(By.CLASS_NAME, 'name')
                prices = driver.find_elements(By.CLASS_NAME, 'price')
                if elems:
                    title = elems[0].text.strip()
                    price = prices[0].text.strip() if prices else 'N/A'
                    results[book] = {'title': title, 'price': price, 'source': 'dangdang'}
                    driver.quit()
                    break
                else:
                    results[book] = {'error': 'No results'}
                    driver.quit()
                    break
            except Exception as e:
                logger.warning(f"dangdang fallback proxy due to error: {str(e)}")
                try:
                    driver.quit()
                except:
                    pass
        else:
            results[book] = {'error': 'All proxies failed'}
        time.sleep(1)

    return results
