import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def extract_brand(title):
    """Extract brand from laptop title"""
    brands = ['ASUS', 'Dell', 'HP', 'Lenovo', 'Acer', 'MSI', 'Apple', 'Samsung',
              'Microsoft', 'Razer', 'Alienware', 'LG', 'Huawei', 'Xiaomi', 'Realme']
    for brand in brands:
        if brand.lower() in title.lower():
            return brand
    return 'Unknown'


def scrape_product_reviews(product_url, headers, max_reviews=50):
    """
    Scrape up to max_reviews reviews from a product page.
    Paginates through Amazon review pages to collect the requested count.
    Returns: (specifications_str, review_text_str, comment_text_str)
    """
    specifications = 'N/A'
    all_reviews    = []
    all_titles     = []

    try:
        # ── Product detail page ───────────────────────────────────────────
        resp = requests.get(product_url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.content, 'html.parser')

        # Specifications
        feature_bullets = soup.find('div', {'id': 'feature-bullets'})
        if feature_bullets:
            features = feature_bullets.find_all('span', {'class': 'a-list-item'})
            specs = [f.text.strip() for f in features if f.text.strip()]
            if specs:
                specifications = ' | '.join(specs[:7])

        # Reviews on product page
        for r in soup.find_all('span', {'data-hook': 'review-body'}):
            all_reviews.append(r.text.strip())
        for t in soup.find_all('a', {'data-hook': 'review-title'}):
            all_titles.append(t.text.strip())

        # ── Paginate through /product-reviews/ ───────────────────────────
        # Extract ASIN from URL
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', product_url)
        if asin_match and len(all_reviews) < max_reviews:
            asin = asin_match.group(1)
            page = 2
            while len(all_reviews) < max_reviews:
                review_url = (
                    f"https://www.amazon.in/product-reviews/{asin}"
                    f"?pageNumber={page}&reviewerType=all_reviews"
                )
                try:
                    time.sleep(1.5)
                    r2 = requests.get(review_url, headers=headers, timeout=15)
                    s2 = BeautifulSoup(r2.content, 'html.parser')

                    page_reviews = s2.find_all('span', {'data-hook': 'review-body'})
                    page_titles  = s2.find_all('a',    {'data-hook': 'review-title'})

                    if not page_reviews:
                        break  # No more pages

                    for r in page_reviews:
                        all_reviews.append(r.text.strip())
                    for t in page_titles:
                        all_titles.append(t.text.strip())

                    page += 1
                except Exception:
                    break

    except Exception as e:
        print(f"  Could not fetch reviews: {e}")

    # Trim to max_reviews
    all_reviews = all_reviews[:max_reviews]
    all_titles  = all_titles[:max_reviews]

    review_text  = ' || '.join(all_reviews) if all_reviews else 'N/A'
    comment_text = ' || '.join(all_titles)  if all_titles  else 'N/A'

    return specifications, review_text, comment_text


def scrape_amazon_detailed(query, max_products=20, max_reviews=50, save_csv=True):
    """
    Scrape detailed laptop data from Amazon.
    max_reviews: how many reviews to collect per product (default 50, set up to any number)
    Returns: DataFrame with columns: laptop_name, brand, price, rating, specifications, review_text, comment_text
    """
    products = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }

    search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"

    try:
        print(f"Searching Amazon for: {query}")
        print(f"Target: {max_products} products, up to {max_reviews} reviews each\n")
        response = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')

        items = soup.find_all('div', {'data-component-type': 's-search-result'})
        print(f"Found {len(items)} products on search page")

        for idx, item in enumerate(items[:max_products], 1):
            try:
                print(f"Processing product {idx}/{min(max_products, len(items))}...")

                # Laptop name
                title_elem = item.find('h2')
                laptop_name = title_elem.text.strip() if title_elem else 'N/A'

                # Brand
                brand = extract_brand(laptop_name)

                # Price
                price_elem = item.find('span', 'a-price-whole')
                price = price_elem.text.strip().replace(',', '') if price_elem else 'N/A'

                # Rating
                rating_elem = item.find('span', 'a-icon-alt')
                rating = rating_elem.text.strip().split()[0] if rating_elem else 'N/A'

                # Specs (search page fallback)
                specs_list = []
                for spec in item.find_all('span', {'class': 'a-size-base'})[:5]:
                    t = spec.text.strip()
                    if t and len(t) > 5:
                        specs_list.append(t)
                specifications = ' | '.join(specs_list) if specs_list else 'N/A'

                # Product link
                product_link = None
                link_elem = item.find('a', {'class': 'a-link-normal s-no-outline'})
                if link_elem and 'href' in link_elem.attrs:
                    product_link = 'https://www.amazon.in' + link_elem['href']

                review_text  = 'N/A'
                comment_text = 'N/A'

                if product_link:
                    time.sleep(2)
                    specifications, review_text, comment_text = scrape_product_reviews(
                        product_link, headers, max_reviews=max_reviews
                    )
                    review_count = len(review_text.split(' || ')) if review_text != 'N/A' else 0
                    print(f"  Collected {review_count} reviews for: {laptop_name[:50]}")

                products.append({
                    'laptop_name':   laptop_name,
                    'brand':         brand,
                    'price':         price,
                    'rating':        rating,
                    'specifications': specifications,
                    'review_text':   review_text,
                    'comment_text':  comment_text
                })

            except Exception as e:
                print(f"  Error processing product: {e}")
                continue

        print(f"\nSuccessfully scraped {len(products)} products")

    except Exception as e:
        print(f"Error scraping Amazon: {e}")

    df = pd.DataFrame(products)

    if save_csv and not df.empty:
        df.to_csv('amazon.csv', index=False, encoding='utf-8-sig')
        print("✅ Data saved to amazon.csv")

    return df


def scrape_amazon(query, max_products=10):
    """Simple scraper for dashboard compatibility"""
    products = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        for item in soup.find_all('div', {'data-component-type': 's-search-result'})[:max_products]:
            try:
                title      = item.find('h2').text.strip()
                price_elem = item.find('span', 'a-price-whole')
                price      = price_elem.text.strip() if price_elem else 'N/A'
                rating_elem = item.find('span', 'a-icon-alt')
                rating     = rating_elem.text.strip() if rating_elem else 'N/A'
                products.append({'source': 'Amazon', 'title': title, 'price': price, 'rating': rating})
            except:
                continue
    except Exception as e:
        print(f"Error scraping Amazon: {e}")
    return pd.DataFrame(products)
    """
    Scrape detailed laptop data from Amazon
    Returns: DataFrame with columns: laptop_name, brand, price, rating, specifications, review_text, comment_text
    """
    products = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    
    search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    
    try:
        print(f"Searching Amazon for: {query}")
        response = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        items = soup.find_all('div', {'data-component-type': 's-search-result'})
        print(f"Found {len(items)} products on search page")
        
        for idx, item in enumerate(items[:max_products], 1):
            try:
                print(f"Processing product {idx}/{min(max_products, len(items))}...")
                
                # Extract laptop name
                title_elem = item.find('h2')
                laptop_name = title_elem.text.strip() if title_elem else 'N/A'
                
                # Extract brand
                brand = extract_brand(laptop_name)
                
                # Extract price
                price_elem = item.find('span', 'a-price-whole')
                price = price_elem.text.strip().replace(',', '') if price_elem else 'N/A'
                
                # Extract rating
                rating_elem = item.find('span', 'a-icon-alt')
                rating = rating_elem.text.strip().split()[0] if rating_elem else 'N/A'
                
                # Extract specifications from bullet points
                specs_list = []
                spec_items = item.find_all('span', {'class': 'a-size-base'})
                for spec in spec_items[:5]:
                    spec_text = spec.text.strip()
                    if spec_text and len(spec_text) > 5:
                        specs_list.append(spec_text)
                
                specifications = ' | '.join(specs_list) if specs_list else 'N/A'
                
                # Get product link for detailed page
                product_link = None
                link_elem = item.find('a', {'class': 'a-link-normal s-no-outline'})
                if link_elem and 'href' in link_elem.attrs:
                    product_link = 'https://www.amazon.in' + link_elem['href']
                
                # Try to get reviews from product page
                review_text = 'N/A'
                comment_text = 'N/A'
                
                if product_link:
                    try:
                        time.sleep(2)  # Respectful delay
                        product_response = requests.get(product_link, headers=headers, timeout=15)
                        product_soup = BeautifulSoup(product_response.content, 'html.parser')
                        
                        # Extract specifications from product page
                        feature_bullets = product_soup.find('div', {'id': 'feature-bullets'})
                        if feature_bullets:
                            features = feature_bullets.find_all('span', {'class': 'a-list-item'})
                            detailed_specs = [f.text.strip() for f in features if f.text.strip()]
                            if detailed_specs:
                                specifications = ' | '.join(detailed_specs[:7])
                        
                        # Extract review text
                        reviews = product_soup.find_all('span', {'data-hook': 'review-body'})
                        if reviews:
                            review_texts = [r.text.strip() for r in reviews[:3]]
                            review_text = ' || '.join(review_texts)
                        
                        # Extract comment/review titles
                        review_titles = product_soup.find_all('a', {'data-hook': 'review-title'})
                        if review_titles:
                            comments = [rt.text.strip() for rt in review_titles[:3]]
                            comment_text = ' || '.join(comments)
                            
                    except Exception as e:
                        print(f"  Could not fetch detailed page: {e}")
                
                products.append({
                    'laptop_name': laptop_name,
                    'brand': brand,
                    'price': price,
                    'rating': rating,
                    'specifications': specifications,
                    'review_text': review_text,
                    'comment_text': comment_text
                })
                
            except Exception as e:
                print(f"  Error processing product: {e}")
                continue
        
        print(f"\nSuccessfully scraped {len(products)} products")
        
    except Exception as e:
        print(f"Error scraping Amazon: {e}")
    
    # Create DataFrame
    df = pd.DataFrame(products)
    
    # Save to CSV if requested
    if save_csv and not df.empty:
        filename = 'amazon.csv'
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ Data saved to {filename}")
    
    return df

def scrape_amazon(query, max_products=10):
    """Simple scraper for dashboard compatibility"""
    products = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        items = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        for item in items[:max_products]:
            try:
                title = item.find('h2').text.strip()
                price_elem = item.find('span', 'a-price-whole')
                price = price_elem.text.strip() if price_elem else 'N/A'
                rating_elem = item.find('span', 'a-icon-alt')
                rating = rating_elem.text.strip() if rating_elem else 'N/A'
                
                products.append({
                    'source': 'Amazon',
                    'title': title,
                    'price': price,
                    'rating': rating
                })
            except:
                continue
                
    except Exception as e:
        print(f"Error scraping Amazon: {e}")
    
    return pd.DataFrame(products)
