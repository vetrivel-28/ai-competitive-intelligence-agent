"""
YouTube scraper for laptop review discussions
Saves to youtube.csv with columns: video_title, laptop_name, comment, reply
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import re

def extract_laptop_name(text):
    """Extract laptop name/model from text"""
    patterns = [
        r'(Dell\s+\w+\s*\d+)',
        r'(HP\s+\w+\s*\d+)',
        r'(Lenovo\s+\w+\s*\d+)',
        r'(ASUS\s+\w+\s*\d+)',
        r'(Acer\s+\w+\s*\d+)',
        r'(MSI\s+\w+\s*\d+)',
        r'(MacBook\s+\w+)',
        r'(ThinkPad\s+\w+\d+)',
        r'(Inspiron\s+\d+)',
        r'(Pavilion\s+\d+)',
        r'(ROG\s+\w+)',
        r'(Predator\s+\w+)',
        r'(Legion\s+\w+\d*)',
        r'(XPS\s+\d+)',
        r'(Spectre\s+\w+)',
        r'(VivoBook\s+\w+)',
        r'(ZenBook\s+\w+)',
    ]
    
    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # Fallback: check for brand names
    brands = ['Dell', 'HP', 'Lenovo', 'ASUS', 'Acer', 'MSI', 'Apple', 'MacBook', 'ThinkPad', 
              'Surface', 'Razer', 'Alienware']
    for brand in brands:
        if brand.lower() in text_lower:
            return brand
    
    return 'Generic Laptop'

def scrape_youtube(query, max_videos=5, comments_per_video=10, save_csv=True, headless=True):
    """
    Scrape YouTube video comments about laptops
    Returns: DataFrame with columns: video_title, laptop_name, comment, reply
    """
    
    print("=" * 70)
    print("YOUTUBE SCRAPER (ENHANCED)")
    print("=" * 70)
    print(f"\n🔍 Query: {query}")
    print(f"📊 Target: {max_videos} videos, {comments_per_video} comments each")
    print(f"⏳ Setting up browser...\n")
    
    # Setup Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--lang=en-US')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    comments_data = []
    driver = None
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.maximize_window()
        wait = WebDriverWait(driver, 15)
        
        # Search YouTube
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        print(f"🌐 Loading: {search_url}")
        driver.get(search_url)
        time.sleep(5)
        
        # Scroll to load videos
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)
        
        # Get video links - try multiple selectors
        video_links = []
        try:
            video_elements = driver.find_elements(By.CSS_SELECTOR, 'a#video-title')
            for elem in video_elements[:max_videos * 2]:  # Get more than needed
                href = elem.get_attribute('href')
                if href and '/watch?v=' in href and href not in video_links:
                    video_links.append(href)
                    if len(video_links) >= max_videos:
                        break
        except:
            print("   ⚠️ Could not find videos with primary selector")
        
        if not video_links:
            print("   ❌ No videos found. YouTube might be blocking access.")
            return pd.DataFrame()
        
        print(f"✅ Found {len(video_links)} videos\n")
        
        # Visit each video and scrape comments
        for video_idx, video_url in enumerate(video_links, 1):
            try:
                print(f"🎥 Processing video {video_idx}/{len(video_links)}...")
                driver.get(video_url)
                time.sleep(6)
                
                # Get video title - multiple attempts
                video_title = 'N/A'
                try:
                    title_selectors = [
                        'h1.ytd-watch-metadata yt-formatted-string',
                        'h1 yt-formatted-string.ytd-watch-metadata',
                        'h1.title yt-formatted-string',
                        'yt-formatted-string.ytd-watch-metadata'
                    ]
                    for selector in title_selectors:
                        try:
                            video_title = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                            if video_title:
                                break
                        except:
                            continue
                except:
                    pass
                
                if video_title == 'N/A':
                    print(f"   ⚠️ Could not get video title, skipping...")
                    continue
                
                print(f"   📹 {video_title[:60]}...")
                
                # Extract laptop name from title
                laptop_name = extract_laptop_name(video_title)
                
                # Scroll down to load comments
                print(f"   ⏳ Loading comments...")
                for scroll in range(5):
                    driver.execute_script("window.scrollBy(0, 600);")
                    time.sleep(1.5)
                
                # Wait for comments to load
                time.sleep(3)
                
                # Try multiple comment selectors
                comment_elements = []
                comment_selectors = [
                    'ytd-comment-thread-renderer #content-text',
                    'yt-formatted-string#content-text',
                    '#comment #content-text',
                    'ytd-comment-renderer #content-text'
                ]
                
                for selector in comment_selectors:
                    try:
                        comment_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if comment_elements:
                            break
                    except:
                        continue
                
                print(f"   💬 Found {len(comment_elements)} comment elements")
                
                comments_scraped = 0
                for comment_elem in comment_elements[:comments_per_video * 2]:  # Try more than needed
                    try:
                        comment_text = comment_elem.text.strip()
                        
                        if not comment_text or len(comment_text) < 5:
                            continue
                        
                        # Skip if it's a reply count or other metadata
                        if comment_text.isdigit() or 'ago' in comment_text.lower():
                            continue
                        
                        # Try to find replies
                        reply_text = 'N/A'
                        try:
                            parent = comment_elem.find_element(By.XPATH, './ancestor::ytd-comment-thread-renderer')
                            
                            # Check if there are replies
                            try:
                                reply_button = parent.find_element(By.CSS_SELECTOR, '#more-replies, #replies-button')
                                if reply_button.is_displayed():
                                    driver.execute_script("arguments[0].scrollIntoView(true);", reply_button)
                                    time.sleep(0.5)
                                    reply_button.click()
                                    time.sleep(2)
                                    
                                    # Get first reply
                                    reply_elements = parent.find_elements(By.CSS_SELECTOR, 'ytd-comment-replies-renderer #content-text')
                                    if reply_elements and len(reply_elements) > 1:  # Skip the original comment
                                        reply_text = reply_elements[1].text.strip()
                            except:
                                pass
                        except:
                            pass
                        
                        comments_data.append({
                            'video_title': video_title,
                            'laptop_name': laptop_name,
                            'comment': comment_text,
                            'reply': reply_text
                        })
                        
                        comments_scraped += 1
                        if comments_scraped >= comments_per_video:
                            break
                        
                    except Exception as e:
                        continue
                
                print(f"   ✅ Scraped {comments_scraped} comments")
                
            except Exception as e:
                print(f"   ❌ Error processing video: {e}")
                continue
        
        print(f"\n✅ Successfully scraped {len(comments_data)} comments from {len(video_links)} videos")
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
    
    # Create DataFrame
    df = pd.DataFrame(comments_data)
    
    # Save to CSV
    if save_csv and not df.empty:
        filename = 'youtube.csv'
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n💾 Data saved to {filename}")
    
    return df

if __name__ == "__main__":
    # Test run
    df = scrape_youtube("laptop review", max_videos=2, comments_per_video=5, headless=False)
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(df)
