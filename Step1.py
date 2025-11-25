#!/usr/bin/env python3
"""
Get Amount of Pages - Extract the total number of pages for each brand
"""

import json
import time
import requests
from bs4 import BeautifulSoup
import random
import re
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PageCountExtractor:
    def __init__(self, delay_range=(1, 3)):
        """Initialize the page count extractor with rate limiting"""
        self.delay_range = delay_range
        self.session = requests.Session()
        self.base_url = 'https://www.bbqguys.com'
        
        # Set headers to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_page(self, url):
        """Fetch a webpage and return BeautifulSoup object"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Add delay to be respectful
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
            
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def get_max_page_number(self, soup):
        """Extract the maximum page number from BBQGuys Material-UI pagination"""
        max_page = 1
        
        # Method 1: BBQGuys-specific Material-UI pagination (most effective)
        # Look for the pagination navigation and find the highest page number
        pagination_nav = soup.select_one('nav[aria-label*="pagination"]')
        
        if pagination_nav:
            # Find all page buttons with aria-label containing "Go to page" or just "page"
            page_buttons = pagination_nav.select('button[aria-label*="page"]')
            
            for button in page_buttons:
                aria_label = button.get('aria-label', '').lower()
                
                # Extract page number from aria labels like:
                # "Go to page 15", "page 1", "Go to page 2"
                page_matches = re.findall(r'(?:go to )?page (\d+)', aria_label)
                
                for match in page_matches:
                    try:
                        page_num = int(match)
                        max_page = max(max_page, page_num)
                    except ValueError:
                        pass
            
            # Also check button text content for pure numbers
            number_buttons = pagination_nav.select('button.MuiPaginationItem-page')
            for button in number_buttons:
                button_text = button.get_text(strip=True)
                if button_text.isdigit():
                    try:
                        page_num = int(button_text)
                        max_page = max(max_page, page_num)
                    except ValueError:
                        pass
            
            if max_page > 1:
                logger.info(f"BBQGuys pagination detected: {max_page} pages")
                return max_page
        
        # Method 2: Generic Material-UI pagination fallback
        mui_pagination_buttons = soup.select('.MuiPaginationItem-page')
        for button in mui_pagination_buttons:
            # Check aria-label
            aria_label = button.get('aria-label', '')
            page_matches = re.findall(r'(?:go to )?page (\d+)', aria_label.lower())
            for match in page_matches:
                try:
                    page_num = int(match)
                    max_page = max(max_page, page_num)
                except ValueError:
                    pass
            
            # Check button text
            button_text = button.get_text(strip=True)
            if button_text.isdigit():
                try:
                    page_num = int(button_text)
                    max_page = max(max_page, page_num)
                except ValueError:
                    pass
        
        if max_page > 1:
            logger.info(f"Generic MUI pagination detected: {max_page} pages")
            return max_page
        
        # Method 3: Look for "Next" button to determine if there are multiple pages
        next_selectors = [
            'button[aria-label*="next" i]:not([disabled])',
            'a[aria-label*="next" i]',
            '.MuiPaginationItem-previousNext:not(.Mui-disabled)'
        ]
        
        has_next = any(soup.select(selector) for selector in next_selectors)
        if has_next:
            max_page = 2  # At least 2 pages if Next button exists and is enabled
            logger.info("Found enabled Next button, assuming at least 2 pages")
        
        logger.info(f"Final pagination result: {max_page} pages")
        return max_page



def extract_brand_name(url):
    """Extract brand name from URL"""
    parts = url.split('/')
    for i, part in enumerate(parts):
        if part == 'brands' and i + 1 < len(parts):
            return parts[i + 1].replace('-', ' ').title()
    
    # Handle special cases like top-fires
    if 'top-fires' in url:
        return 'The Outdoor Plus Top Fires'
    
    # Fallback - use the last meaningful part
    return url.split('/')[-2].replace('-', ' ').title() if len(url.split('/')) > 1 else 'Unknown'

def get_pages_for_all_brands():
    """Get the number of pages for each brand"""
    extractor = PageCountExtractor()
    brand_urls = get_brand_urls()
    
    pages_data = {
        'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_brands': len(brand_urls),
        'brands': {}
    }
    
    logger.info(f"Starting pagination detection for {len(brand_urls)} brands")
    
    for i, brand_url in enumerate(brand_urls, 1):
        try:
            brand_name = extract_brand_name(brand_url)
            logger.info(f"[{i}/{len(brand_urls)}] Processing: {brand_name}")
            
            # Get the first page to determine pagination
            soup = extractor.get_page(brand_url)
            
            if not soup:
                logger.error(f"Failed to fetch page for {brand_name}")
                pages_data['brands'][brand_name] = {
                    'brand_url': brand_url,
                    'total_pages': 0,
                    'status': 'failed',
                    'error': 'Failed to fetch page'
                }
                continue
            
            # Extract the maximum page number
            max_pages = extractor.get_max_page_number(soup)
            
            pages_data['brands'][brand_name] = {
                'brand_url': brand_url,
                'total_pages': max_pages,
                'status': 'success'
            }
            
            logger.info(f"✅ {brand_name}: {max_pages} pages")
            
        except Exception as e:
            logger.error(f"Error processing {brand_url}: {e}")
            brand_name = extract_brand_name(brand_url)
            pages_data['brands'][brand_name] = {
                'brand_url': brand_url,
                'total_pages': 0,
                'status': 'error',
                'error': str(e)
            }
        
        # Add a small delay between requests to be respectful
        time.sleep(1)
    
    return pages_data

def save_to_json(data, filename):
    """Save data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Data saved to {filename}")

def main():
    """Main function to extract page counts and save to JSON"""
    logger.info("🔍 BRAND PAGINATION DETECTION")
    logger.info("=" * 50)
    
    if len(sys.argv) > 1:
        brands_arg = sys.argv[1]
        brands = brands_arg.split(",")
        print("Brands to process:", brands)
        
        # Process only the passed brands
        extractor = PageCountExtractor()
        pages_data = {}
        for brand_url in brands:
            brand_name = extract_brand_name(brand_url)
            if brand_name:
                logger.info(f"Processing brand: {brand_name}")
                # Get the page and extract page count
                soup = extractor.get_page(brand_url)
                if soup:
                    page_count = extractor.get_max_page_number(soup)
                else:
                    page_count = 0
                    logger.error(f"Failed to fetch page for {brand_name}")
                
                pages_data[brand_name] = {
                    'url': brand_url,
                    'page_count': page_count
                }
                logger.info(f"Brand: {brand_name}, Pages: {page_count}")
            else:
                logger.warning(f"Could not extract brand name from URL: {brand_url}")
        
        # Save the results
        with open('brand_pages_count.json', 'w') as f:
            json.dump(pages_data, f, indent=2)
        
        logger.info(f"Saved page counts for {len(pages_data)} brands to brand_pages_count.json")
        
    else:
        logger.error("No brands provided as command-line argument.")
        print("Usage: python Step1.py <comma_separated_brand_urls>")
        sys.exit(1)

if __name__ == "__main__":
    main()











