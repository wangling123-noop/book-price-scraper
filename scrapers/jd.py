import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .proxy_driver import get_chrome_driver_with_proxy

logger = logging.getLogger(__name__)

PROXY_CONFIG = {
    'host': 'g416.kdltps.com',
    'port': 15818,
    'username': 't15419362286482',
    'password': 'g5hlxtk8',
    'backup_host': 'g417.kdltps.com'
}

def scrape_jd(books):
    results = {}

    try:
        driver = get_chrome_driver_with_proxy(
            PROXY_CONFIG['host'], PROXY_CONFIG['port'],
            PROXY_CONFIG['username'], PROXY_CONFIG['password']
        )
    except Exception as e:
        logger.warning(f"Failed to create ChromeDriver with main proxy: {e}, trying backup proxy")
        try:
            driver = get_chrome_driver_with_proxy(
                PROXY_CONFIG['backup_host'], PROXY_CONFIG['port'],
                PROXY_CONFIG['username'], PROXY_CONFIG['password']
            )
        except Exception as e2:
            logger.error(f"Failed to create ChromeDriver with backup proxy: {e2}")
            return {book: {'error': 'Failed to init driver with proxy'} for book in books}

    try:
        for book in books:
            try:
                url = f'https://search.jd.com/Search?keyword={book}'
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.gl-item'))
                )
                item_elems = driver.find_elements(By.CSS_SELECTOR, '.gl-item')
                if item_elems:
                    title = item_elems[0].find_element(By.CSS_SELECTOR, '.p-name em').text.strip()
                    results[book] = {'title': title, 'source': 'jd'}
                else:
                    results[book] = {'error': 'Title not found'}
            except Exception as e:
                logger.error(f"JD error for {book}: {e}")
                results[book] = {'error': str(e)}
    finally:
        driver.quit()

    return results
