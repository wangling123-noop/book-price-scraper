from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
import logging, time

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

        proxy = Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_host}:{proxy_config['port']}"
        proxy.http_proxy = proxy_url
        proxy.ssl_proxy = proxy_url

        capabilities = webdriver.DesiredCapabilities.CHROME.copy()
        proxy.add_to_capabilities(capabilities)

        return webdriver.Chrome(options=options, desired_capabilities=capabilities)

    def process_book(book):
        for host in [proxy_config['host'], proxy_config['backup_host']]:
            try:
                driver = create_driver(host)
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
                    return
                else:
                    results[book] = {'error': 'No results'}
                    driver.quit()
                    return
            except Exception as e:
                logger.warning(f"dangdang fallback proxy due to error: {str(e)}")
                try:
                    driver.quit()
                except: pass
        results[book] = {'error': 'All proxies failed'}

    for book in books:
        process_book(book)
        time.sleep(1)  # 防止请求过快

    return results
