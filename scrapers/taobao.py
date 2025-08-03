# scrapers/taobao.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

logger = logging.getLogger(__name__)

def scrape_taobao(books):
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
        # 淘宝反爬，建议加User-Agent模拟浏览器
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')

        proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_host}:{proxy_config['port']}"
        options.add_argument(f'--proxy-server={proxy_url}')

        driver = webdriver.Chrome(options=options)
        return driver

    for book in books:
        for proxy_host in [proxy_config['host'], proxy_config['backup_host']]:
            try:
                driver = create_driver(proxy_host)
                driver.get(f'https://s.taobao.com/search?q={book}')
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.item.J_MouserOnverReq'))
                )
                items = driver.find_elements(By.CSS_SELECTOR, '.item.J_MouserOnverReq')
                if items:
                    title_elem = items[0].find_element(By.CSS_SELECTOR, '.title')
                    price_elem = items[0].find_element(By.CSS_SELECTOR, '.price')
                    title = title_elem.text.strip()
                    price = price_elem.text.strip()
                    results[book] = {'title': title, 'price': price, 'source': 'taobao'}
                    driver.quit()
                    break
                else:
                    results[book] = {'error': 'No results'}
                    driver.quit()
                    break
            except Exception as e:
                logger.warning(f"taobao fallback proxy due to error: {str(e)}")
                try:
                    driver.quit()
                except:
                    pass
        else:
            results[book] = {'error': 'All proxies failed'}
        time.sleep(1)

    return results
