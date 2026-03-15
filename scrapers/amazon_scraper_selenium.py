"""
Enhanced Amazon scraper using Selenium for better success rate
Handles dynamic content and avoids bot detection
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re

def extract_brand(title):
    """Extract brand from laptop title"""
    brands = ['ASUS', 'Dell', 'HP', 'Lenovo', 'Acer', 'MSI', 'Apple', 'Samsung', 
              'Microsoft', 'Razer', 'Alienware', 'LG', 'Huawei', 'Xiaomi', 'Realme', 'Avita']
    
    for brand in brands:
        if brand.lower() in title.lower():
            return brand
    return 'Unknown'

def scrape_amazon_selenium(query, max_products=20, save_csv=True, headless=True):
    """
    Scrape Amazon using Selenium (more reliable than requests)
    Returns: DataFrame with columns: laptop_name, brand, price, rating, specifications, review_text, comment_text
    """
    
    print("=" * 70)
    print("AMAZON SELENIUM SCRAPER")
    print("=" * 70)
    print(f"\n🔍 Query: {query}")
    print(f"📊 Target: {max_products} products")
    print(f"⏳ Setting up browser...\n")
    
    # Setup Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    products = []
    driver = None
    
    try:
        # Initialize driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.maximize_window()
        
        # Search Amazon
        search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        print(f"🌐 Loading: {search_url}")
        driver.get(search_url)
        time.sleep(3)
        
        # Find all product cards
        product_cards = driver.find_elements(By.CSS_SELECTOR, '[data-component-type="s-search-result"]')
        print(f"✅ Found {len(product_cards)} products\n")
        
        for idx, card in enumerate(product_cards[:max_products], 1):
            try:
                print(f"📦 Processing product {idx}/{min(max_products, len(product_cards))}...")
                
                # Extract laptop name
                try:
                    laptop_name = card.find_element(By.CSS_SELECTOR, 'h2 a span').text.strip()
                except:
                    laptop_name = 'N/A'
                
                # Extract brand
                brand = extract_brand(laptop_name)
                
                # Extract price
                try:
                    price = card.find_element(By.CSS_SELECTOR, '.a-price-whole').text.strip().replace(',', '')
                except:
                    price = 'N/A'
                
                # Extract rating
                try:
                    rating = card.find_element(By.CSS_SELECTOR, '.a-icon-alt').text.strip().split()[0]
                except:
                    rating = 'N/A'
                
                # Extract specifications
                specifications = 'N/A'
                try:
                    spec_elements = card.find_elements(By.CSS_SELECTOR, '.a-size-base')
                    specs = [elem.text.strip() for elem in spec_elements if elem.text.strip() and len(elem.text.strip()) > 5]
                    if specs:
                        specifications = ' | '.join(specs[:5])
                except:
                    pass
                
                # Get product link
                product_link = None
                try:
                    product_link = card.find_element(By.CSS_SELECTOR, 'h2 a').get_attribute('href')
                except:
                    pass
                
                # Visit product page for reviews
                review_text = 'N/A'
                comment_text = 'N/A'
                
                if product_link and idx <= 5:  # Only get reviews for first 5 products to save time
                    try:
                        print(f"   📄 Fetching product details...")
                        driver.execute_script("window.open('');")
                        driver.switch_to.window(driver.window_handles[1])
                        driver.get(product_link)
                        time.sleep(2)
                        
                        # Get detailed specifications
                        try:
                            feature_bullets = driver.find_elements(By.CSS_SELECTOR, '#feature-bullets li span.a-list-item')
                            if feature_bullets:
                                detailed_specs = [fb.text.strip() for fb in feature_bullets if fb.text.strip()]
                                if detailed_specs:
                                    specifications = ' | '.join(detailed_specs[:7])
                        except:
                            pass
                        
                        # Scroll to reviews section
                        try:
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                            time.sleep(1)
                        except:
                            pass
                        
                        # Get reviews
                        try:
                            review_elements = driver.find_elements(By.CSS_SELECTOR, '[data-hook="review-body"] span')
                            if review_elements:
                                reviews = [r.text.strip() for r in review_elements[:3] if r.text.strip()]
                                review_text = ' || '.join(reviews)
                        except:
                            pass
                        
                        # Get review titles/comments
                        try:
                            comment_elements = driver.find_elements(By.CSS_SELECTOR, '[data-hook="review-title"] span')
                            if comment_elements:
                                comments = [c.text.strip() for c in comment_elements[:3] if c.text.strip()]
                                comment_text = ' || '.join(comments)
                        except:
                            pass
                        
                        # Close tab and switch back
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        
                    except Exception as e:
                        print(f"   ⚠️ Could not fetch details: {e}")
                        try:
                            if len(driver.window_handles) > 1:
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                        except:
                            pass
                
                products.append({
                    'laptop_name': laptop_name,
                    'brand': brand,
                    'price': price,
                    'rating': rating,
                    'specifications': specifications,
                    'review_text': review_text,
                    'comment_text': comment_text
                })
                
                print(f"   ✅ {laptop_name[:50]}...")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        print(f"\n✅ Successfully scraped {len(products)} products")
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
    
    finally:
        if driver:
            driver.quit()
    
    # Create DataFrame
    df = pd.DataFrame(products)
    
    # Save to CSV
    if save_csv and not df.empty:
        filename = 'amazon.csv'
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n💾 Data saved to {filename}")
    
    return df

if __name__ == "__main__":
    # Test run
    df = scrape_amazon_selenium("laptop", max_products=5, headless=False)
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(df)
