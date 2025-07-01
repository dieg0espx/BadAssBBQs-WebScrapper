#!/usr/bin/env python3
"""
Utility functions for web scraping tasks
"""

import re
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import time
import random


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing extra whitespace and special characters
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common unwanted characters
    text = text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    
    return text


def extract_numbers(text: str) -> List[float]:
    """
    Extract numbers from text (useful for prices, quantities, etc.)
    
    Args:
        text: Text containing numbers
        
    Returns:
        List of extracted numbers
    """
    if not text:
        return []
    
    # Pattern to match numbers (including decimals)
    pattern = r'[\d,]+\.?\d*'
    matches = re.findall(pattern, text.replace(',', ''))
    
    return [float(match) for match in matches if match]


def extract_price(text: str) -> float:
    """
    Extract price from text (handles common currency formats)
    
    Args:
        text: Text containing price
        
    Returns:
        Price as float, or 0.0 if not found
    """
    if not text:
        return 0.0
    
    # Remove currency symbols and extract number
    clean_text_price = re.sub(r'[^\d.,]', '', text)
    numbers = extract_numbers(clean_text_price)
    
    return numbers[0] if numbers else 0.0


def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def get_domain(url: str) -> str:
    """
    Extract domain from URL
    
    Args:
        url: Full URL
        
    Returns:
        Domain name
    """
    try:
        return urlparse(url).netloc
    except:
        return ""


def generate_pagination_urls(base_url: str, start_page: int = 1, end_page: int = 10, 
                           page_param: str = 'page') -> List[str]:
    """
    Generate URLs for pagination
    
    Args:
        base_url: Base URL (e.g., 'https://example.com/products')
        start_page: Starting page number
        end_page: Ending page number
        page_param: Parameter name for page (e.g., 'page', 'p')
        
    Returns:
        List of pagination URLs
    """
    urls = []
    
    for page in range(start_page, end_page + 1):
        if '?' in base_url:
            url = f"{base_url}&{page_param}={page}"
        else:
            url = f"{base_url}?{page_param}={page}"
        urls.append(url)
    
    return urls


def smart_delay(min_delay: float = 1.0, max_delay: float = 3.0, 
               randomize: bool = True) -> None:
    """
    Add intelligent delay between requests
    
    Args:
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds
        randomize: Whether to randomize the delay
    """
    if randomize:
        delay = random.uniform(min_delay, max_delay)
    else:
        delay = (min_delay + max_delay) / 2
    
    time.sleep(delay)


class CommonSelectors:
    """
    Common CSS selectors for popular websites and elements
    """
    
    # E-commerce
    PRICE = ['.price', '.cost', '.amount', '[class*="price"]', '[class*="cost"]']
    TITLE = ['h1', '.title', '.product-title', '.name', '[class*="title"]']
    RATING = ['.rating', '.stars', '.score', '[class*="rating"]', '[class*="star"]']
    DESCRIPTION = ['.description', '.details', '.summary', '[class*="description"]']
    IMAGE = ['img', '.image img', '.photo img', '.picture img']
    
    # News/Articles
    HEADLINE = ['h1', '.headline', '.title', 'h1.title', '[class*="headline"]']
    AUTHOR = ['.author', '.by', '.writer', '[class*="author"]', '[class*="byline"]']
    DATE = ['.date', '.published', '.time', '[class*="date"]', '[class*="time"]']
    CONTENT = ['.content', '.article-body', '.text', 'p', '[class*="content"]']
    
    # Social Media
    POST_TEXT = ['.post-text', '.content', '.message', '[class*="post"]']
    LIKES = ['.likes', '.hearts', '.reactions', '[class*="like"]']
    SHARES = ['.shares', '.retweets', '[class*="share"]']
    COMMENTS = ['.comments', '.replies', '[class*="comment"]']
    
    # General
    LINKS = ['a', 'a[href]']
    BUTTONS = ['button', '.btn', '.button', '[role="button"]']
    FORMS = ['form', '.form']
    NAVIGATION = ['nav', '.nav', '.navigation', '.menu']


def find_best_selector(soup, selectors: List[str], content_hint: str = None) -> str:
    """
    Find the best CSS selector from a list of common selectors
    
    Args:
        soup: BeautifulSoup object
        selectors: List of CSS selectors to try
        content_hint: Optional text that should be present in the element
        
    Returns:
        Best matching selector or empty string
    """
    for selector in selectors:
        try:
            elements = soup.select(selector)
            if elements:
                # If content hint provided, check if any element contains it
                if content_hint:
                    for elem in elements:
                        if content_hint.lower() in elem.get_text().lower():
                            return selector
                else:
                    return selector
        except:
            continue
    
    return ""


def extract_structured_data(soup, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract structured data using common selectors and cleaning
    
    Args:
        soup: BeautifulSoup object
        config: Configuration with field mappings
        
    Returns:
        Dictionary with extracted and cleaned data
    """
    data = {}
    
    for field, settings in config.items():
        if isinstance(settings, str):
            # Simple selector string
            selector = settings
            clean_func = clean_text
        elif isinstance(settings, dict):
            selector = settings.get('selector', '')
            clean_func = settings.get('cleaner', clean_text)
            extract_type = settings.get('type', 'text')
        else:
            continue
        
        try:
            elements = soup.select(selector)
            if elements:
                if extract_type == 'text':
                    raw_value = elements[0].get_text(strip=True)
                    data[field] = clean_func(raw_value)
                elif extract_type == 'attribute':
                    attr = settings.get('attribute', 'href')
                    data[field] = elements[0].get(attr, '')
                elif extract_type == 'price':
                    raw_value = elements[0].get_text(strip=True)
                    data[field] = extract_price(raw_value)
            else:
                data[field] = ""
        except Exception as e:
            data[field] = ""
    
    return data


# Pre-configured extraction configs for common use cases
ECOMMERCE_CONFIG = {
    'title': {'selector': 'h1, .product-title, .title', 'cleaner': clean_text},
    'price': {'selector': '.price, .cost, .amount', 'type': 'price'},
    'rating': {'selector': '.rating, .stars, .score', 'cleaner': clean_text},
    'description': {'selector': '.description, .details, .summary', 'cleaner': clean_text},
    'image': {'selector': 'img, .image img', 'type': 'attribute', 'attribute': 'src'}
}

NEWS_CONFIG = {
    'headline': {'selector': 'h1, .headline, .title', 'cleaner': clean_text},
    'author': {'selector': '.author, .by, .writer', 'cleaner': clean_text},
    'date': {'selector': '.date, .published, .time', 'cleaner': clean_text},
    'content': {'selector': '.content, .article-body, .text', 'cleaner': clean_text}
} 