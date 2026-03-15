"""
Enhanced Flipkart scraper using Selenium for better success rate
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
              'Microsoft', 'Razer', 'Alienware', 'LG', 'Huawei', 'Xiaomi', 'Realme', 
              'Avita', 'Infinix', 'RedmiBook', 'Mi', 'Honor', 'Vaio']
    
    for brand in brands:
        if brand.lower() in title.lower():
            return brand
    return 'Unknown'

def scrape_flipkart_selenium(query, max_products=20, max_reviews=50, save_csv=True, headless=True):
    """
    Scrape Flipkart using Selenium.
    max_reviews: how many reviews to collect per product (default 50)
    Returns: DataFrame with columns: laptop_name, brand, price, rating, specifications, reviews_comments
    """

    print("=" * 70)
    print("FLIPKART SELENIUM SCRAPER")
    print("=" * 70)
    print(f"\n🔍 Query: {query}")
    print(f"📊 Target: {max_products} products, up to {max_reviews} reviews each")
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
        
        # Search Flipkart
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
        print(f"🌐 Loading: {search_url}")
        driver.get(search_url)
        time.sleep(4)
        
        # Close login popup if appears
        try:
            close_button = driver.find_element(By.CSS_SELECTOR, 'button._2KpZ6l._2doB4z')
            close_button.click()
            time.sleep(1)
        except:
            pass
        
        # Find all product cards
        product_cards = driver.find_elements(By.CSS_SELECTOR, '[data-id]')
        print(f"✅ Found {len(product_cards)} products\n")
        
        for idx, card in enumerate(product_cards[:max_products], 1):
            try:
                print(f"📦 Processing product {idx}/{min(max_products, len(product_cards))}...")
                
                # Extract laptop name
                try:
                    laptop_name = card.find_element(By.CSS_SELECTOR, '.IRpwTa, ._4rR01T, .s1Q9rs').text.strip()
                except:
                    try:
                        laptop_name = card.find_element(By.CSS_SELECTOR, 'a.s1Q9rs').text.strip()
                    except:
                        laptop_name = 'N/A'
                
                # Extract brand
                brand = extract_brand(laptop_name)
                
                # Extract price
                try:
                    price = card.find_element(By.CSS_SELECTOR, '._30jeq3, .Nx9bqj').text.strip().replace('₹', '').replace(',', '')
                except:
                    price = 'N/A'
                
                # Extract rating
                try:
                    rating = card.find_element(By.CSS_SELECTOR, '._3LWZlK, .XQDdHH').text.strip()
                except:
                    rating = 'N/A'
                
                # Extract specifications from listing
                specifications = 'N/A'
                try:
                    spec_elements = card.find_elements(By.CSS_SELECTOR, 'li._7eSDEY, ul._1xgFaf li')
                    specs = [elem.text.strip() for elem in spec_elements if elem.text.strip()]
                    if specs:
                        specifications = ' | '.join(specs[:6])
                except:
                    pass
                
                # Get product link
                product_link = None
                try:
                    link_elem = card.find_element(By.CSS_SELECTOR, 'a.IRpwTa, a.s1Q9rs, a._1fQZEK')
                    product_link = link_elem.get_attribute('href')
                    if product_link and not product_link.startswith('http'):
                        product_link = 'https://www.flipkart.com' + product_link
                except:
                    pass
                
                # Visit product page for detailed info
                reviews_comments = 'N/A'

                if product_link:
                    try:
                        print(f"   📄 Fetching product details & reviews (up to {max_reviews})...")
                        driver.execute_script("window.open('');")
                        driver.switch_to.window(driver.window_handles[1])
                        driver.get(product_link)
                        time.sleep(3)

                        # Close login popup if appears
                        try:
                            close_button = driver.find_element(By.CSS_SELECTOR, 'button._2KpZ6l._2doB4z')
                            close_button.click()
                            time.sleep(1)
                        except:
                            pass

                        # Get detailed specifications
                        try:
                            spec_table = driver.find_elements(By.CSS_SELECTOR, '._1s_Smc, .col, ._2418kt')
                            if spec_table:
                                detailed_specs = []
                                for spec in spec_table[:8]:
                                    spec_text = spec.text.strip()
                                    if spec_text and len(spec_text) > 3:
                                        detailed_specs.append(spec_text)
                                if detailed_specs:
                                    specifications = ' | '.join(detailed_specs)
                        except:
                            pass

                        # ── Collect reviews with pagination ───────────────
                        all_reviews = []

                        while len(all_reviews) < max_reviews:
                            # Scroll to load reviews
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.6);")
                            time.sleep(2)

                            review_elements = driver.find_elements(
                                By.CSS_SELECTOR, '.t-ZTKy, ._2-N8zT, .ZmyHeo div, .row._2-N8zT'
                            )
                            for r in review_elements:
                                text = r.text.strip()
                                if text and len(text) > 10 and text not in all_reviews:
                                    all_reviews.append(text)

                            if len(all_reviews) >= max_reviews:
                                break

                            # Try clicking "Next" page of reviews
                            try:
                                next_btn = driver.find_element(
                                    By.XPATH,
                                    "//span[contains(text(),'Next')]//ancestor::a | //a[contains(@class,'_1LKTO3')]"
                                )
                                driver.execute_script("arguments[0].click();", next_btn)
                                time.sleep(2)
                            except:
                                break  # No more pages

                        all_reviews = all_reviews[:max_reviews]
                        if all_reviews:
                            reviews_comments = ' || '.join(all_reviews)
                            print(f"   ✅ Collected {len(all_reviews)} reviews")

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
                    'reviews_comments': reviews_comments
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
        filename = 'flipkart.csv'
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n💾 Data saved to {filename}")
    
    return df

if __name__ == "__main__":
    # Test run — change max_reviews to however many you want (e.g. 10, 25, 50)
    df = scrape_flipkart_selenium("laptop", max_products=5, max_reviews=50, headless=False)
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(df)
