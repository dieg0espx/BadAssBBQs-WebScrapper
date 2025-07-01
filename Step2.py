#!/usr/bin/env python3
"""
All URLs Extractor - Extract all product URLs from all BBQ brand pages
Uses pre-calculated page counts from brand_pages_count.json
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AllURLsExtractor:
    def __init__(self, delay_range=(1, 3)):
        """Initialize the URL extractor with rate limiting"""
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
    
    def load_brand_page_counts(self, filename='brand_pages_count.json'):
        """Load brand page counts from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data['brands']
        except FileNotFoundError:
            logger.error(f"File {filename} not found")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in {filename}")
            return {}
    
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
    
    def extract_product_urls_from_page(self, soup):
        """Extract product URLs from a single page"""
        product_urls = []
        
        # Look for product links - these are typically in product cards or listings
        # Common selectors for product links on BBQ Guys
        selectors = [
            'a[href*="/i/"]',  # Product pages typically have /i/ in the URL
            '.product-card a',
            '.product-item a',
            '.product-link',
            '[data-product-url]',
            '.tile-product a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute
                    full_url = urljoin(self.base_url, href)
                    # Only include product URLs (contain /i/)
                    if '/i/' in full_url and full_url not in product_urls:
                        # Clean up any fragment or query parameters except essential ones
                        parsed = urlparse(full_url)
                        clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
                        if clean_url not in product_urls:
                            product_urls.append(clean_url)
        
        return product_urls
    
    def generate_page_urls(self, base_url, total_pages):
        """Generate URLs for all pages using known page count"""
        page_urls = [base_url]  # Include the first page
        
        for page_num in range(2, total_pages + 1):
            # Add page parameter to the URL
            parsed = urlparse(base_url)
            query_params = parse_qs(parsed.query) if parsed.query else {}
            query_params['page'] = [str(page_num)]
            
            new_query = urlencode(query_params, doseq=True)
            page_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, ''))
            page_urls.append(page_url)
        
        return page_urls
    
    def extract_all_products_from_brand(self, brand_name, brand_data):
        """Extract all product URLs from a brand using known page count"""
        brand_url = brand_data['brand_url']
        total_pages = brand_data['total_pages']
        
        logger.info(f"Processing {brand_name}: {total_pages} pages")
        
        all_product_urls = []
        
        # Generate all page URLs
        page_urls = self.generate_page_urls(brand_url, total_pages)
        
        # Process each page
        for page_num, page_url in enumerate(page_urls, 1):
            logger.info(f"Processing {brand_name} - Page {page_num}/{total_pages}")
            
            soup = self.get_page(page_url)
            
            if soup:
                page_products = self.extract_product_urls_from_page(soup)
                all_product_urls.extend(page_products)
                logger.info(f"Found {len(page_products)} products on page {page_num}")
            else:
                logger.warning(f"Failed to fetch page {page_num} for {brand_name}")
        
        # Remove duplicates while preserving order
        unique_product_urls = []
        seen = set()
        for url in all_product_urls:
            if url not in seen:
                unique_product_urls.append(url)
                seen.add(url)
        
        logger.info(f"Total unique products found for {brand_name}: {len(unique_product_urls)}")
        return unique_product_urls
    
    def extract_all_urls(self):
        """Extract all product URLs from all brands"""
        # Load brand page counts
        brand_data = self.load_brand_page_counts()
        
        if not brand_data:
            logger.error("No brand data loaded. Exiting.")
            return {}
        
        all_results = {}
        total_processed = 0
        total_brands = len(brand_data)
        
        for brand_name, brand_info in brand_data.items():
            total_processed += 1
            logger.info(f"\n=== Processing brand {total_processed}/{total_brands}: {brand_name} ===")
            
            try:
                # Only process brands that were successfully analyzed
                if brand_info.get('status') == 'success':
                    product_urls = self.extract_all_products_from_brand(brand_name, brand_info)
                    
                    all_results[brand_name] = {
                        'brand_url': brand_info['brand_url'],
                        'total_pages': brand_info['total_pages'],
                        'product_count': len(product_urls),
                        'product_urls': product_urls,
                        'status': 'success'
                    }
                    
                    logger.info(f"✅ Completed {brand_name}: {len(product_urls)} products")
                else:
                    logger.warning(f"⚠️  Skipping {brand_name}: status is {brand_info.get('status', 'unknown')}")
                    all_results[brand_name] = {
                        'brand_url': brand_info['brand_url'],
                        'total_pages': brand_info.get('total_pages', 0),
                        'product_count': 0,
                        'product_urls': [],
                        'status': 'skipped'
                    }
                
            except Exception as e:
                logger.error(f"❌ Error processing {brand_name}: {e}")
                all_results[brand_name] = {
                    'brand_url': brand_info.get('brand_url', ''),
                    'total_pages': brand_info.get('total_pages', 0),
                    'product_count': 0,
                    'product_urls': [],
                    'status': 'error',
                    'error': str(e)
                }
                continue
        
        return all_results
    
    def save_to_json(self, data, filename):
        """Save data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Data saved to {filename}")

def main():
    extractor = AllURLsExtractor()
    
    logger.info("Starting extraction of all product URLs from all brands")
    
    # Extract all URLs
    all_brand_results = extractor.extract_all_urls()
    
    if not all_brand_results:
        logger.error("No results obtained. Exiting.")
        return
    
    # Calculate totals
    total_products = sum(brand_data['product_count'] for brand_data in all_brand_results.values())
    successful_brands = sum(1 for brand_data in all_brand_results.values() if brand_data['status'] == 'success')
    
    # Create comprehensive summary
    summary = {
        'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_brands_processed': len(all_brand_results),
        'successful_brands': successful_brands,
        'total_products_found': total_products,
        'brands': all_brand_results
    }
    
    # Save comprehensive data
    extractor.save_to_json(summary, 'all_urls_by_brand.json')
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("EXTRACTION COMPLETE!")
    logger.info("="*60)
    logger.info(f"📊 Total brands processed: {len(all_brand_results)}")
    logger.info(f"✅ Successful extractions: {successful_brands}")
    logger.info(f"🔗 Total product URLs found: {total_products}")
    logger.info("\n📁 Files created:")
    logger.info("   • all_urls_by_brand.json - Comprehensive data organized by brand")
    
    # Show per-brand summary
    logger.info(f"\n📋 Per-brand summary:")
    for brand_name, brand_data in all_brand_results.items():
        status_emoji = "✅" if brand_data['status'] == 'success' else "⚠️" if brand_data['status'] == 'skipped' else "❌"
        logger.info(f"   {status_emoji} {brand_name}: {brand_data['product_count']} products ({brand_data['total_pages']} pages)")

if __name__ == "__main__":
    main() 