from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from scrapers.dangdang import scrape_dangdang
from scrapers.taobao import scrape_taobao
from scrapers.jd import scrape_jd
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_books(data):
    if isinstance(data, list):
        return [item.get('book', '').strip("'\"") for item in data if isinstance(item, dict) and 'book' in item]
    elif isinstance(data, dict):
        if 'books' in data and isinstance(data['books'], list):
            return data['books']
        elif 'textArray' in data and isinstance(data['textArray'], list):
            return [item.get('book', '').strip("'\"") for item in data['textArray'] if isinstance(item, dict) and 'book' in item]
    return []

@app.route('/api/scrape_books', methods=['POST'])
def scrape_books():
    try:
        data = request.get_json()
        logger.info(f"Received data: {data}")
        books = extract_books(data)
        if not books:
            return jsonify({'error': 'Invalid input, expected list of book names'}), 400

        results = {'dangdang': {}, 'taobao': {}, 'jd': {}}
        with ThreadPoolExecutor(max_workers=3) as executor:
            dd = executor.submit(scrape_dangdang, books)
            tb = executor.submit(scrape_taobao, books)
            jd = executor.submit(scrape_jd, books)
            results['dangdang'] = dd.result()
            results['taobao'] = tb.result()
            results['jd'] = jd.result()

        return jsonify({'status': 'success', 'data': results}), 200
    except Exception as e:
        logger.error(f"Error in scrape_books: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/price', methods=['POST'])
def scrape_price():
    try:
        data = request.get_json()
        logger.info(f"Received data: {data}")
        books = extract_books(data)
        if not books:
            return jsonify({'error': 'Invalid input, expected list of book names'}), 400

        results = {'dangdang': {}, 'taobao': {}, 'jd': {}}
        with ThreadPoolExecutor(max_workers=3) as executor:
            dd = executor.submit(scrape_dangdang, books)
            tb = executor.submit(scrape_taobao, books)
            jd = executor.submit(scrape_jd, books)
            results['dangdang'] = dd.result()
            results['taobao'] = tb.result()
            results['jd'] = jd.result()

        prices = {
            'dangdang': {k: v.get('price', 'Price not found') for k, v in results['dangdang'].items()},
            'taobao': {k: v.get('price', 'Price not found') for k, v in results['taobao'].items()},
            'jd': {k: v.get('price', 'Price not found') for k, v in results['jd'].items()}
        }
        return jsonify({'status': 'success', 'data': prices}), 200
    except Exception as e:
        logger.error(f"Error in scrape_price: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
