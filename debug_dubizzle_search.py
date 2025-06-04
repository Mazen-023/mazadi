#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'commerce.settings')
django.setup()

from price_estimation.utils.web_scraping import WebScrapingUtils
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def debug_dubizzle_search():
    driver = WebScrapingUtils.get_webdriver()
    try:
        print("Loading Dubizzle homepage...")
        driver.get('https://www.dubizzle.com.eg')
        time.sleep(3)
        
        print(f'Homepage title: {driver.title}')
        
        # Try to find search box and perform search
        search_selectors = [
            'input[type="search"]',
            'input[placeholder*="بحث"]',
            'input[placeholder*="search"]',
            'input[name="q"]',
            'input[id*="search"]',
            '.search-input',
            '#search'
        ]
        
        search_box = None
        for selector in search_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    search_box = elements[0]
                    print(f'Found search box with selector: {selector}')
                    break
            except:
                continue
        
        if search_box:
            print("Performing search...")
            search_box.clear()
            search_box.send_keys("iPhone 13")
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)
            
            print(f'Search results page title: {driver.title}')
            print(f'Current URL: {driver.current_url}')
            
            # Now look for listings on the results page
            potential_selectors = [
                '[class*="listing"]', 
                '[class*="item"]', 
                '[class*="card"]', 
                '[class*="ad"]',
                'article',
                'div[data-testid]',
                '.result',
                '.product'
            ]
            
            for selector in potential_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f'Found {len(elements)} elements with selector: {selector}')
                        if elements:
                            first_element = elements[0]
                            print(f'First element class: {first_element.get_attribute("class")}')
                            print(f'First element data-testid: {first_element.get_attribute("data-testid")}')
                            text_preview = first_element.text[:100].replace('\n', ' ')
                            print(f'First element text preview: {text_preview}...')
                            print('---')
                except Exception as e:
                    print(f'Error with selector {selector}: {str(e)}')
            
            # Look for price elements
            print("\nLooking for price elements...")
            all_elements = driver.find_elements(By.CSS_SELECTOR, '*')
            price_count = 0
            for element in all_elements:
                try:
                    text = element.text
                    if text and ('ج.م' in text or 'EGP' in text or 'جنيه' in text) and any(c.isdigit() for c in text):
                        print(f'Found price element: {text.strip()[:50]}')
                        print(f'Element tag: {element.tag_name}, class: {element.get_attribute("class")}')
                        price_count += 1
                        if price_count >= 3:
                            break
                except:
                    continue
        else:
            print("Could not find search box")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_dubizzle_search()
