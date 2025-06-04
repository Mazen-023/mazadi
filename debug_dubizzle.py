#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'commerce.settings')
django.setup()

from price_estimation.utils.web_scraping import WebScrapingUtils
import time

def debug_dubizzle_page():
    driver = WebScrapingUtils.get_webdriver()
    try:
        print("Loading Dubizzle search page...")
        driver.get('https://www.dubizzle.com.eg/search?q=iPhone%2013')
        time.sleep(5)
        
        # Check page title
        print(f'Page title: {driver.title}')
        
        # Check if there are any elements with common class patterns
        elements = driver.find_elements('css selector', 'div')
        print(f'Total div elements: {len(elements)}')
        
        # Look for elements that might contain listings
        potential_selectors = [
            '[class*="listing"]', 
            '[class*="item"]', 
            '[class*="card"]', 
            '[class*="ad"]',
            'article',
            '[data-testid*="listing"]',
            '[data-testid*="card"]'
        ]
        
        for selector in potential_selectors:
            try:
                elements = driver.find_elements('css selector', selector)
                if elements:
                    print(f'Found {len(elements)} elements with selector: {selector}')
                    if elements:
                        print(f'First element class: {elements[0].get_attribute("class")}')
                        text_preview = elements[0].text[:100].replace('\n', ' ')
                        print(f'First element text preview: {text_preview}...')
                        print('---')
                else:
                    print(f'No elements found with selector: {selector}')
            except Exception as e:
                print(f'Error with selector {selector}: {str(e)}')
                
        # Try to find any elements with price-like text
        print("\nLooking for price elements...")
        price_elements = driver.find_elements('css selector', '*')
        price_count = 0
        for element in price_elements[:50]:  # Check first 50 elements
            text = element.text
            if text and ('ج.م' in text or 'EGP' in text or 'جنيه' in text):
                print(f'Found potential price element: {text[:50]}')
                price_count += 1
                if price_count >= 5:  # Limit output
                    break
                    
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_dubizzle_page()
