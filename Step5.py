#!/usr/bin/env python3
"""
Step 5: Clean up temporary data files after successful upload to Supabase
"""

import os
import logging
import sys

# List of temporary files to delete
TEMP_FILES = [
    'products.json',
    'products_fixed.csv',
    'brand_pages_count.json',
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def delete_file(filepath):
    try:
        os.remove(filepath)
        logger.info(f"Deleted: {filepath}")
    except FileNotFoundError:
        logger.warning(f"File not found, skipping: {filepath}")
    except Exception as e:
        logger.error(f"Error deleting {filepath}: {e}")

def main():
    logger.info("🧹 CLEANING UP TEMPORARY FILES")
    logger.info("=" * 50)
    
    if len(sys.argv) > 1:
        brands_arg = sys.argv[1]
        brands = brands_arg.split(",")
        logger.info(f"Brands processed: {brands}")
        
        logger.info("Cleaning up temporary data files...")
        for file in TEMP_FILES:
            delete_file(file)
        logger.info("Cleanup complete.")
        
    else:
        logger.error("No brands provided as command-line argument.")
        print("Usage: python Step5.py <comma_separated_brand_urls>")
        sys.exit(1)

if __name__ == "__main__":
    main() 