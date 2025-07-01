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

def get_brand_urls():
    """Get all brand URLs from the brads.txt file"""
    try:
        with open('brands.txt', 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        return urls
    except FileNotFoundError:
        logger.warning("brads.txt not found, using hardcoded list")
        # Fallback to hardcoded list if file doesn't exist
        return [
            'https://www.bbqguys.com/d/17994/brands/alfresco-grills/shop-all',
            'https://www.bbqguys.com/d/19795/brands/american-made-grills/shop-all',
            'https://www.bbqguys.com/d/13928/brands/american-outdoor-grill/shop-all',
            'https://www.bbqguys.com/d/20399/brands/artisan-grills/shop-all',
            'https://www.bbqguys.com/d/24062/brands/blackstone-grills/shop-all',
            'https://www.bbqguys.com/d/17960/brands/blaze-grills/shop-all',
            'https://www.bbqguys.com/d/25317/brands/breeo/shop-all',
            'https://www.bbqguys.com/d/20880/brands/bromic-heating/shop-all',
            'https://www.bbqguys.com/d/20396/brands/coyote-outdoor-living/shop-all',
            'https://www.bbqguys.com/d/518/brands/delta-heat/shop-all',
            'https://www.bbqguys.com/d/17978/brands/fire-magic-grills/shop-all',
            'https://www.bbqguys.com/d/22965/brands/fontana-forni/shop-all',
            'https://www.bbqguys.com/d/24176/brands/green-mountain-grills/shop-all',
            'https://www.bbqguys.com/d/17946/brands/napoleon-shop-all',
            'https://www.bbqguys.com/d/10469/brands/twin-eagles-grills/shop-all',
            'https://www.bbqguys.com/d/18064/brands/primo-ceramic-grills/shop-all',
            'https://www.bbqguys.com/d/19816/brands/summerset-grills/shop-all',
            'https://www.bbqguys.com/d/23678/brands/mont-alpi/shop-all',
            'https://www.bbqguys.com/d/21363/brands/american-fyre-designs/shop-all',
            'https://www.bbqguys.com/d/22449/outdoor-living/fire-pits/the-outdoor-plus/top-fires',
            'https://www.bbqguys.com/d/25428/brands/ledge-lounger/shop-all'
        ]

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
    
    # Get page counts for all brands
    pages_data = get_pages_for_all_brands()
    
    # Save to JSON file
    output_filename = 'brand_pages_count.json'
    save_to_json(pages_data, output_filename)
    
    # Print summary
    total_brands = pages_data['total_brands']
    successful_brands = sum(1 for brand in pages_data['brands'].values() if brand['status'] == 'success')
    total_pages = sum(brand['total_pages'] for brand in pages_data['brands'].values() if brand['status'] == 'success')
    
    logger.info("\n" + "=" * 50)
    logger.info("📊 SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total brands processed: {total_brands}")
    logger.info(f"Successful extractions: {successful_brands}")
    logger.info(f"Total pages across all brands: {total_pages}")
    logger.info(f"Results saved to: {output_filename}")
    
    # Show individual results
    logger.info("\n🏷️ BRAND PAGE COUNTS:")
    logger.info("-" * 30)
    for brand_name, brand_data in pages_data['brands'].items():
        if brand_data['status'] == 'success':
            logger.info(f"{brand_name}: {brand_data['total_pages']} pages")
        else:
            logger.info(f"{brand_name}: FAILED ({brand_data.get('error', 'Unknown error')})")

if __name__ == "__main__":
    main()











