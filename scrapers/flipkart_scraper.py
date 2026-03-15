import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_flipkart(query, max_products=10):
    """Scrape laptop data from Flipkart"""
    products = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        items = soup.find_all('div', {'class': '_1AtVbE'})
        
        for item in items[:max_products]:
            try:
                title = item.find('div', {'class': '_4rR01T'}).text.strip()
                price = item.find('div', {'class': '_30jeq3'}).text.strip()
                rating_elem = item.find('div', {'class': '_3LWZlK'})
                rating = rating_elem.text.strip() if rating_elem else 'N/A'
                
                products.append({
                    'source': 'Flipkart',
                    'title': title,
                    'price': price,
                    'rating': rating
                })
            except:
                continue
                
    except Exception as e:
        print(f"Error scraping Flipkart: {e}")
    
    return pd.DataFrame(products)
