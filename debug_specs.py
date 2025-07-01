#!/usr/bin/env python3
"""
Debug script to inspect the page structure and find specifications table
"""

import requests
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_page():
    url = 'https://www.bbqguys.com/i/3181132/blaze/lte-pro-5-burner-propane-gas-grill'
    
    # Set up session with headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    try:
        logger.info(f"Fetching: {url}")
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for tables with specifications
        logger.info("Looking for tables...")
        tables = soup.find_all('table')
        logger.info(f"Found {len(tables)} tables on the page")
        
        for i, table in enumerate(tables):
            logger.info(f"\nTable {i+1}:")
            logger.info(f"Classes: {table.get('class', [])}")
            logger.info(f"ID: {table.get('id', 'None')}")
            
            # Check if this table contains specification-like content
            rows = table.find_all('tr')
            logger.info(f"Number of rows: {len(rows)}")
            
            if rows:
                # Show first few rows to see the structure
                for j, row in enumerate(rows[:3]):
                    cells = row.find_all(['th', 'td'])
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    logger.info(f"  Row {j+1}: {cell_texts}")
        
        # Look for any elements containing specification-related text
        logger.info("\nLooking for elements containing specification-related text...")
        spec_keywords = ['Class', 'Fuel Type', 'Collection', 'Cutout', 'Burner', 'BTU', 'Material', 'Stainless']
        
        for keyword in spec_keywords:
            elements = soup.find_all(text=lambda text: text and keyword in text)
            if elements:
                logger.info(f"Found '{keyword}' in: {len(elements)} elements")
                for elem in elements[:2]:  # Show first 2 matches
                    parent = elem.parent
                    logger.info(f"  - {parent.name} (class: {parent.get('class', [])}): {elem.strip()}")
        
        # Look for any divs or sections that might contain specifications
        logger.info("\nLooking for divs with potential specification content...")
        all_divs = soup.find_all('div')
        spec_divs = []
        
        for div in all_divs:
            div_text = div.get_text(strip=True)
            if any(keyword in div_text for keyword in spec_keywords):
                spec_divs.append(div)
        
        logger.info(f"Found {len(spec_divs)} divs with potential specification content")
        
        # Show the first few spec divs
        for i, div in enumerate(spec_divs[:3]):
            logger.info(f"\nSpec div {i+1}:")
            logger.info(f"Classes: {div.get('class', [])}")
            logger.info(f"ID: {div.get('id', 'None')}")
            text = div.get_text(strip=True)[:200]  # First 200 chars
            logger.info(f"Text preview: {text}...")
        
        # Look for any elements with "specification" in class names
        logger.info("\nLooking for elements with 'specification' in class names...")
        spec_elements = soup.find_all(class_=lambda x: x and 'specification' in x.lower())
        for elem in spec_elements:
            logger.info(f"Found element with specification class: {elem.name} - {elem.get('class')}")
        
        # Look for MuiTable elements
        logger.info("\nLooking for MuiTable elements...")
        mui_tables = soup.find_all(class_=lambda x: x and 'MuiTable' in x)
        for table in mui_tables:
            logger.info(f"Found MuiTable: {table.get('class')}")
            rows = table.find_all('tr')
            logger.info(f"  Rows: {len(rows)}")
            if rows:
                for j, row in enumerate(rows[:2]):
                    cells = row.find_all(['th', 'td'])
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    logger.info(f"    Row {j+1}: {cell_texts}")
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    debug_page() 