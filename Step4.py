#!/usr/bin/env python3
"""
Step 4: Store scraped products data to Supabase
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import time
import sys

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SupabaseManager:
    def __init__(self):
        """
        Initialize Supabase client
        """
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("Supabase client initialized successfully")
    
    def create_tables(self):
        """
        Create necessary tables if they don't exist
        Note: This is a reference for the table structure. 
        Tables should be created manually in Supabase dashboard for production use.
        """
        logger.info("Table structure reference:")
        logger.info("""
        -- Products table
        CREATE TABLE scrapped_products (
            id SERIAL PRIMARY KEY,
            product_id VARCHAR(50) UNIQUE NOT NULL,
            url TEXT NOT NULL,
            title TEXT NOT NULL,
            price DECIMAL(10,2),
            brand VARCHAR(255),
            image TEXT,
            other_images JSONB,
            model VARCHAR(255),
            Configurations JSONB,
            category JSONB,
            specifications JSONB,
            description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create index on product_id for faster lookups
        CREATE INDEX idx_scrapped_products_product_id ON scrapped_products(product_id);
        
        -- Create index on brand for filtering
        CREATE INDEX idx_scrapped_products_brand ON scrapped_products(brand);
        """)
    
    def insert_product(self, product_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Insert a single product into the database
        
        Args:
            product_data: Product data dictionary
            
        Returns:
            Inserted record or None if failed
        """
        try:
            # Prepare data for insertion
            insert_data = {
                'Id': product_data.get('Id', ''),
                'url': product_data.get('url', ''),
                'Title': product_data.get('Title', ''),
                'Price': (product_data.get('Price') if (product_data.get('Price') not in [None, '']) else None),
                'brand': product_data.get('brand', ''),
                'Image': product_data.get('Image', ''),
                'Other_image': product_data.get('Other_image', []) if isinstance(product_data.get('Other_image', []), list) else [product_data.get('Other_image', [])],
                'Model': product_data.get('Model', ''),
                'Configurations': product_data.get('Configurations', []),
                'category': product_data.get('Category', []) if isinstance(product_data.get('Category', []), list) else [product_data.get('Category', [])],
                'Specifications': product_data.get('Specifications', []),
                'Description': product_data.get('Description', '')
            }
            
            # Insert into database
            result = self.client.table('scrapped_products').insert(insert_data).execute()
            
            if result.data:
                logger.info(f"Successfully inserted product: {product_data.get('Id', 'Unknown')}")
                return result.data[0]
            else:
                logger.error(f"Failed to insert product: {product_data.get('Id', 'Unknown')}")
                return None
                
        except Exception as e:
            logger.error(f"Error inserting product {product_data.get('Id', 'Unknown')}: {e}")
            return None
    
    def insert_products_batch(self, products: List[Dict[str, Any]], batch_size: int = 50) -> Dict[str, int]:
        """
        Insert multiple products in batches
        
        Args:
            products: List of product data dictionaries
            batch_size: Number of products to insert per batch
            
        Returns:
            Dictionary with success and failure counts
        """
        total_products = len(products)
        successful_inserts = 0
        failed_inserts = 0
        
        logger.info(f"Starting batch insertion of {total_products} products")
        
        for i in range(0, total_products, batch_size):
            batch = products[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_products + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} products)")
            
            # Prepare batch data
            batch_data = []
            for product in batch:
                insert_data = {
                    'Id': product.get('Id', ''),
                    'url': product.get('url', ''),
                    'Title': product.get('Title', ''),
                    'Price': (product.get('Price') if (product.get('Price') not in [None, '']) else None),
                    'brand': product.get('brand', ''),
                    'Image': product.get('Image', ''),
                    'Other_image': product.get('Other_image', []) if isinstance(product.get('Other_image', []), list) else [product.get('Other_image', [])],
                    'Model': product.get('Model', ''),
                    'Configurations': product.get('Configurations', []),
                    'category': product.get('Category', []) if isinstance(product.get('Category', []), list) else [product.get('Category', [])],
                    'Specifications': product.get('Specifications', []),
                    'Description': product.get('Description', '')
                }
                batch_data.append(insert_data)
            
            try:
                # Insert batch
                result = self.client.table('scrapped_products').insert(batch_data).execute()
                
                if result.data:
                    successful_inserts += len(result.data)
                    logger.info(f"Batch {batch_num} successful: {len(result.data)} products inserted")
                else:
                    failed_inserts += len(batch)
                    logger.error(f"Batch {batch_num} failed: no data returned")
                    
            except Exception as e:
                failed_inserts += len(batch)
                logger.error(f"Error in batch {batch_num}: {e}")
            
            # Add delay between batches to avoid rate limiting
            if i + batch_size < total_products:
                time.sleep(1)
        
        logger.info(f"Batch insertion completed. Success: {successful_inserts}, Failed: {failed_inserts}")
        return {
            'successful': successful_inserts,
            'failed': failed_inserts,
            'total': total_products
        }
    
    def upsert_product(self, product_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Upsert a product (insert if not exists, update if exists)
        
        Args:
            product_data: Product data dictionary
            
        Returns:
            Upserted record or None if failed
        """
        try:
            # Prepare data for upsertion
            upsert_data = {
                'Id': product_data.get('Id', ''),
                'url': product_data.get('url', ''),
                'Title': product_data.get('Title', ''),
                'Price': (product_data.get('Price') if (product_data.get('Price') not in [None, '']) else None),
                'brand': product_data.get('brand', ''),
                'Image': product_data.get('Image', ''),
                'Other_image': product_data.get('Other_image', []),
                'Model': product_data.get('Model', ''),
                'Configurations': product_data.get('Configurations', []),
                'category': product_data.get('Category', []),
                'Specifications': product_data.get('Specifications', []),
                'Description': product_data.get('Description', '')
            }
            
            # Upsert into database
            result = self.client.table('scrapped_products').upsert(upsert_data, on_conflict='Id').execute()
            
            if result.data:
                logger.info(f"Successfully upserted product: {product_data.get('Id', 'Unknown')}")
                return result.data[0]
            else:
                logger.error(f"Failed to upsert product: {product_data.get('Id', 'Unknown')}")
                return None
                
        except Exception as e:
            logger.error(f"Error upserting product {product_data.get('Id', 'Unknown')}: {e}")
            return None
    
    def get_product_count(self) -> int:
        """
        Get total number of products in the database
        
        Returns:
            Number of products
        """
        try:
            result = self.client.table('scrapped_products').select('id', count='exact').execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"Error getting product count: {e}")
            return 0
    
    def get_products_by_brand(self, brand: str, limit: int = 100) -> List[Dict]:
        """
        Get products by brand
        
        Args:
            brand: Brand name to filter by
            limit: Maximum number of products to return
            
        Returns:
            List of products
        """
        try:
            result = self.client.table('scrapped_products').select('*').eq('brand', brand).limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting products by brand {brand}: {e}")
            return []
    
    def search_products(self, search_term: str, limit: int = 100) -> List[Dict]:
        """
        Search products by title or description
        
        Args:
            search_term: Search term
            limit: Maximum number of products to return
            
        Returns:
            List of matching products
        """
        try:
            result = self.client.table('scrapped_products').select('*').or_(f'title.ilike.%{search_term}%,description.ilike.%{search_term}%').limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []


def load_products_from_json(filename: str = 'products.json') -> List[Dict[str, Any]]:
    """
    Load products data from JSON file
    
    Args:
        filename: JSON file path
        
    Returns:
        List of product dictionaries
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            products = json.load(f)
        logger.info(f"Loaded {len(products)} products from {filename}")
        return products
    except FileNotFoundError:
        logger.error(f"File {filename} not found")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON file {filename}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading products from {filename}: {e}")
        return []


def main():
    """
    Main function to store products in Supabase
    """
    logger.info("📤 STORING PRODUCTS IN SUPABASE")
    logger.info("=" * 50)
    
    # Load products from JSON file (generated by Step3)
    products = load_products_from_json()
    
    if not products:
        logger.error("No products to store. Run Step3 first to create products.json")
        print("❌ ERROR: No products to store. Run Step3 first to create products.json")
        sys.exit(1)
    
    try:
        # Initialize Supabase manager
        supabase_manager = SupabaseManager()
        
        # Show table structure reference
        supabase_manager.create_tables()
        
        # Get current product count
        initial_count = supabase_manager.get_product_count()
        logger.info(f"Current products in database: {initial_count}")
        print(f"📊 Current products in database: {initial_count}")
        
        # Store products in batches
        print(f"🚀 Starting to store {len(products)} products in batches...")
        results = supabase_manager.insert_products_batch(products, batch_size=50)
        
        # Get final product count
        final_count = supabase_manager.get_product_count()
        
        logger.info("=== STORAGE SUMMARY ===")
        print(f"\n📈 STORAGE SUMMARY:")
        print(f"=" * 50)
        logger.info(f"Products loaded from JSON: {len(products)}")
        print(f"Products loaded from JSON: {len(products)}")
        logger.info(f"Successfully stored: {results['successful']}")
        print(f"✅ Successfully stored: {results['successful']}")
        logger.info(f"Failed to store: {results['failed']}")
        print(f"❌ Failed to store: {results['failed']}")
        logger.info(f"Initial database count: {initial_count}")
        print(f"Initial database count: {initial_count}")
        logger.info(f"Final database count: {final_count}")
        print(f"Final database count: {final_count}")
        logger.info(f"Net increase: {final_count - initial_count}")
        print(f"Net increase: {final_count - initial_count}")
        
        if results['failed'] > 0:
            logger.warning(f"{results['failed']} products failed to store. Check logs for details.")
            print(f"⚠️  {results['failed']} products failed to store. Check logs for details.")
        
        logger.info("Step 4 completed successfully!")
        print(f"🎉 Step 4 completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        print(f"❌ ERROR: {e}")
        raise


if __name__ == "__main__":
    main() 