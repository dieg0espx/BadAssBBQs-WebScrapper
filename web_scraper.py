#!/usr/bin/env python3
"""
Web Scraper - A flexible and robust web scraping tool
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import random
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Optional
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WebScraper:
    def __init__(self, base_url: str = None, delay_range: tuple = (1, 3)):
        """
        Initialize the web scraper
        
        Args:
            base_url: Base URL for relative link resolution
            delay_range: Tuple of (min, max) seconds to wait between requests
        """
        self.base_url = base_url
        self.delay_range = delay_range
        self.session = requests.Session()
        
        # Set common headers to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch a webpage and return BeautifulSoup object
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Add random delay to be respectful
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
            
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_text(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """
        Extract text from elements matching CSS selector
        
        Args:
            soup: BeautifulSoup object
            selector: CSS selector
            
        Returns:
            List of text content
        """
        elements = soup.select(selector)
        return [elem.get_text(strip=True) for elem in elements]
    
    def extract_attributes(self, soup: BeautifulSoup, selector: str, attribute: str) -> List[str]:
        """
        Extract specific attributes from elements
        
        Args:
            soup: BeautifulSoup object
            selector: CSS selector
            attribute: Attribute name to extract
            
        Returns:
            List of attribute values
        """
        elements = soup.select(selector)
        return [elem.get(attribute, '') for elem in elements if elem.get(attribute)]
    
    def extract_links(self, soup: BeautifulSoup, selector: str = 'a') -> List[str]:
        """
        Extract and resolve links from page
        
        Args:
            soup: BeautifulSoup object
            selector: CSS selector for link elements
            
        Returns:
            List of absolute URLs
        """
        links = self.extract_attributes(soup, selector, 'href')
        
        if self.base_url:
            # Convert relative URLs to absolute
            absolute_links = []
            for link in links:
                absolute_url = urljoin(self.base_url, link)
                absolute_links.append(absolute_url)
            return absolute_links
        
        return links
    
    def scrape_data(self, url: str, data_config: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Scrape structured data from a page based on configuration
        
        Args:
            url: URL to scrape
            data_config: Dictionary defining what to extract
                Example: {
                    'title': {'selector': 'h1', 'type': 'text'},
                    'price': {'selector': '.price', 'type': 'text'},
                    'images': {'selector': 'img', 'type': 'attribute', 'attribute': 'src'}
                }
        
        Returns:
            Dictionary with extracted data
        """
        soup = self.get_page(url)
        if not soup:
            return {}
        
        data = {'url': url}
        
        for field_name, config in data_config.items():
            selector = config['selector']
            extract_type = config['type']
            
            if extract_type == 'text':
                values = self.extract_text(soup, selector)
                # Always store only the first value for brand and price
                if field_name in ['brand', 'Price']:
                    extracted_value = values[0] if values else ''
                    # Convert Price to number
                    if field_name == 'Price' and extracted_value:
                        try:
                            # Remove $ and commas, then convert to float
                            price_clean = extracted_value.replace('$', '').replace(',', '').strip()
                            data[field_name] = float(price_clean)
                        except ValueError:
                            logger.warning(f"Could not convert price '{extracted_value}' to number")
                            data[field_name] = extracted_value  # Keep as string if conversion fails
                    else:
                        data[field_name] = extracted_value
                else:
                    data[field_name] = values[0] if len(values) == 1 else values
                
            elif extract_type == 'attribute':
                attribute = config['attribute']
                values = self.extract_attributes(soup, selector, attribute)
                data[field_name] = values[0] if len(values) == 1 else values
                
            elif extract_type == 'links':
                values = self.extract_links(soup, selector)
                data[field_name] = values[0] if len(values) == 1 else values
            
            elif extract_type == 'images_with_alt':
                other_images = {}
                image_links = soup.select(selector)
                for link in image_links:
                    href = link.get('href', '')
                    if href:
                        # Get alt text from img element inside the link
                        img_elem = link.select_one('img')
                        alt_text = ''
                        if img_elem:
                            alt_text = img_elem.get('alt', '')
                        
                        # If no alt text, use the href as fallback description
                        if not alt_text:
                            alt_text = href.split('/')[-1]  # Use filename as fallback
                        
                        other_images[href] = alt_text
                
                data[field_name] = other_images
            
            elif extract_type == 'config_options':
                options = []
                option_divs = soup.select(selector)
                for div in option_divs:
                    label_elem = div.select_one('label')
                    value_elem = div.select_one('span.MuiBox-root.bbq-1ivf7pa')
                    if label_elem and value_elem:
                        options.append({
                            'label': label_elem.get_text(strip=True).replace(':', ''),
                            'value': value_elem.get_text(strip=True)
                        })
                data[field_name] = options
            
            elif extract_type == 'specifications_table':
                specifications = []
                logger.info(f"Looking for specifications table with selector: {selector}")
                table_rows = soup.select(selector + ' tr')
                logger.info(f"Found {len(table_rows)} table rows")
                
                for i, row in enumerate(table_rows):
                    header_elem = row.select_one('th')
                    value_elem = row.select_one('td')
                    
                    if header_elem and value_elem:
                        # Remove any button elements from header before getting text
                        header_copy = header_elem.__copy__()
                        for button in header_copy.find_all('button'):
                            button.decompose()
                        
                        # Get the text content, removing any help buttons
                        header_text = header_copy.get_text(strip=True)
                        value_text = value_elem.get_text(strip=True)
                        
                        # Create single key-value object and add to array
                        spec_obj = {header_text: value_text}
                        specifications.append(spec_obj)
                        logger.info(f"Row {i}: {header_text} = {value_text}")
                    else:
                        logger.warning(f"Row {i}: Missing header or value element")
                
                logger.info(f"Total specifications extracted: {len(specifications)}")
                data[field_name] = specifications
            
            elif extract_type == 'specifications_json':
                # Extract the JSON array for specifications from the raw HTML
                html = str(soup)
                match = re.search(r'"specifications":\s*(\[.*?\])', html)
                specifications = {}
                if match:
                    import json
                    try:
                        specs_list = json.loads(match.group(1))
                        for spec in specs_list:
                            field = spec.get('fieldName')
                            value = spec.get('fieldValue')
                            if field and value:
                                specifications[field] = value
                    except Exception as e:
                        logger.error(f"Error parsing specifications JSON: {e}")
                else:
                    logger.warning("No specifications JSON found in HTML.")
                data[field_name] = specifications
            

        
        if 'Id' in data and isinstance(data['Id'], list):
            data['Id'] = data['Id'][0] if len(data['Id']) > 0 else ''
        if 'Model' in data and isinstance(data['Model'], list):
            data['Model'] = data['Model'][1] if len(data['Model']) > 1 else ''
        
        # Extract only the part after "#" for Id and Model
        if 'Id' in data and data['Id'] and '#' in data['Id']:
            data['Id'] = data['Id'].split('#')[-1].strip()
        if 'Model' in data and data['Model'] and '#' in data['Model']:
            data['Model'] = data['Model'].split('#')[-1].strip()
        
        # Handle Image field - make it a single string (first image)
        if 'Image' in data and isinstance(data['Image'], list):
            data['Image'] = data['Image'][0] if len(data['Image']) > 0 else ''
        
        # Ensure the main image appears as the LAST entry in Other_image
        if 'Image' in data and 'Other_image' in data and data['Image']:
            main_image = data['Image']
            if isinstance(data['Other_image'], dict):
                # Remove main image if it exists anywhere in Other_image
                main_image_desc = None
                if main_image in data['Other_image']:
                    main_image_desc = data['Other_image'][main_image]
                    del data['Other_image'][main_image]
                
                # If no description was found, create one
                if not main_image_desc:
                    main_image_desc = data.get('Title', 'Main Product Image')
                
                # Add the main image as the LAST entry
                data['Other_image'][main_image] = main_image_desc
        
        # After extracting all fields, combine key_features_title, key_features, and description into one string
        key_features_title = data.get('key_features_title', '')
        key_features = data.get('key_features', [])
        description = data.get('temp_description', [])

        # Ensure all are strings or lists of strings
        if isinstance(key_features, list):
            key_features_str = ' '.join(key_features)
        else:
            key_features_str = key_features

        if isinstance(description, list):
            description_str = ' '.join(description)
        else:
            description_str = description

        parts = [str(key_features_title).strip(), key_features_str.strip(), description_str.strip()]
        data['Description'] = ' '.join([p for p in parts if p])
        
        # Remove the temporary fields
        for temp_field in ['key_features', 'key_features_title', 'temp_description']:
            if temp_field in data:
                del data[temp_field]
        
        return data
    
    def scrape_multiple_pages(self, urls: List[str], data_config: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Scrape data from multiple pages
        
        Args:
            urls: List of URLs to scrape
            data_config: Data extraction configuration
            
        Returns:
            List of dictionaries with scraped data
        """
        all_data = []
        
        for url in urls:
            data = self.scrape_data(url, data_config)
            if data:
                all_data.append(data)
        
        return all_data
    
    def save_to_csv(self, data: List[Dict], filename: str):
        """
        Save scraped data to CSV file
        
        Args:
            data: List of dictionaries
            filename: Output filename
        """
        if not data:
            logger.warning("No data to save")
            return
        
        fieldnames = data[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        
        logger.info(f"Data saved to {filename}")
    
    def save_to_json(self, data: List[Dict], filename: str):
        """
        Save scraped data to JSON file
        
        Args:
            data: List of dictionaries
            filename: Output filename
        """
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"Data saved to {filename}")


def example_scraper():
    """
    Example usage of the WebScraper class
    """
    # Example: Scraping BBQ grill from bbqguys.com
    scraper = WebScraper(base_url='https://www.bbqguys.com')
    
    # Configuration for what data to extract from BBQ product page
    bbq_config = {
        'Title': {'selector': 'h1.product-name, .product-title, h1', 'type': 'text'},
        'Price': {
            'selector': 'span.MuiBox-root.bbq-0',
            'type': 'text'
        },
        'brand': {
            'selector': 'a.MuiTypography-root.MuiTypography-inherit.MuiLink-root.MuiLink-underlineAlways.bbq-1q6x5gb-MuiTypography-root-MuiLink-root',
            'type': 'text'
        },
        'key_features': {
            'selector': 'ul.bullets li',
            'type': 'text'
        },
        'key_features_title': {
            'selector': 'span.MuiTypography-root.MuiTypography-keyFeatureBullet',
            'type': 'text'
        },
        'Description': {
            'selector': 'div.MuiTypography-root.MuiTypography-body1.bbq-13af6c7-MuiTypography-root p',
            'type': 'text'
        },
       
                 'Image': {'selector': '.carousel__images a', 'type': 'attribute', 'attribute': 'href'},
         'Other_image': {'selector': '.carousel__images a', 'type': 'images_with_alt'},
        'Id': {
            'selector': 'span.MuiTypography-root.MuiTypography-body2.bbq-86swij-MuiTypography-root',
            'type': 'text'
        },
        'Model': {
            'selector': 'span.MuiTypography-root.MuiTypography-body2.bbq-86swij-MuiTypography-root',
            'type': 'text'
        },
        'configurations': {
            'selector': 'div[aria-description="Product configuration option"]',
            'type': 'config_options'
        },
        'Category': {
            'selector': 'ol.MuiBreadcrumbs-ol a',
            'type': 'text'
        },
        'Specifications': {
            'selector': 'tbody.MuiTableBody-root',
            'type': 'specifications_table'
        },

    }
    
    # Scrape data from the BBQ grill page
    urls = [
        'https://www.bbqguys.com/i/3181132/blaze/lte-pro-5-burner-propane-gas-grill',
    ]
    
    data = scraper.scrape_multiple_pages(urls, bbq_config)
    
    # Save results
    scraper.save_to_csv(data, 'bbq_grill.csv')
    scraper.save_to_json(data, 'bbq_grill.json')
    
    print(f"Scraped {len(data)} BBQ grill(s)!")
    
    # Print results
    for i, grill_data in enumerate(data):
        print(f"\nBBQ Grill {i+1}:")
        print(f"Title: {grill_data.get('Title', 'N/A')}")
        print(f"Price: ${grill_data.get('Price', 'N/A')}")
        print(f"Brand: {grill_data.get('brand', 'N/A')}")
        print(f"URL: {grill_data.get('url', 'N/A')}")
        
        # Print specifications if available
        if 'Specifications' in grill_data and grill_data['Specifications']:
            print("\nSpecifications:")
            for spec_obj in grill_data['Specifications']:
                for spec_name, spec_value in spec_obj.items():
                    print(f"  {spec_name}: {spec_value}")


if __name__ == "__main__":
    example_scraper() 