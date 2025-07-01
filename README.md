# Web Scraper

A comprehensive Python web scraping toolkit with support for both static and JavaScript-heavy websites.

## Features

- **Basic Web Scraper** (`web_scraper.py`): For static websites using requests + BeautifulSoup
- **Advanced Scraper** (`advanced_scraper.py`): For JavaScript-heavy sites using Selenium
- Built-in rate limiting and respectful scraping practices
- CSV and JSON export functionality
- Flexible data extraction configuration
- Error handling and logging
- Support for infinite scroll and dynamic content

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. For the advanced scraper, you'll also need Chrome browser installed. The ChromeDriver will be automatically downloaded.

## Basic Usage

### Static Website Scraping

```python
from web_scraper import WebScraper

# Initialize scraper
scraper = WebScraper(base_url='https://example.com')

# Configure what data to extract
data_config = {
    'title': {'selector': 'h1', 'type': 'text'},
    'price': {'selector': '.price', 'type': 'text'},
    'images': {'selector': 'img', 'type': 'attribute', 'attribute': 'src'}
}

# Scrape a single page
data = scraper.scrape_data('https://example.com/product/1', data_config)

# Scrape multiple pages
urls = ['https://example.com/page/1', 'https://example.com/page/2']
all_data = scraper.scrape_multiple_pages(urls, data_config)

# Save results
scraper.save_to_csv(all_data, 'results.csv')
scraper.save_to_json(all_data, 'results.json')
```

### JavaScript-Heavy Website Scraping

```python
from advanced_scraper import AdvancedScraper

# Configuration for data extraction
selectors_config = {
    'title': '.product-title',
    'price': '.price-value',
    'rating': '.rating-stars'
}

# Use context manager for automatic cleanup
with AdvancedScraper(headless=True) as scraper:
    data = scraper.scrape_spa_content(
        url='https://spa-website.com/products',
        selectors_config=selectors_config,
        load_more_selector='.load-more-btn',  # Optional: for infinite scroll
        max_clicks=5
    )
    
    scraper.save_to_csv(data, 'spa_data.csv')
```

## Data Configuration

The data configuration dictionary defines what and how to extract data:

```python
data_config = {
    'field_name': {
        'selector': 'CSS_SELECTOR',  # CSS selector to find elements
        'type': 'EXTRACTION_TYPE',   # 'text', 'attribute', or 'links'
        'attribute': 'ATTR_NAME'     # Required only for 'attribute' type
    }
}
```

### Extraction Types

- **text**: Extract the text content of elements
- **attribute**: Extract a specific attribute value (href, src, etc.)
- **links**: Extract and resolve href attributes to absolute URLs

## Examples

### Example 1: Scraping News Articles

```python
from web_scraper import WebScraper

scraper = WebScraper(base_url='https://news-site.com')

news_config = {
    'headline': {'selector': 'h1.headline', 'type': 'text'},
    'author': {'selector': '.author', 'type': 'text'},
    'date': {'selector': '.publish-date', 'type': 'text'},
    'content': {'selector': '.article-body', 'type': 'text'},
    'image': {'selector': '.featured-image img', 'type': 'attribute', 'attribute': 'src'}
}

# Get article URLs from main page
main_page = scraper.get_page('https://news-site.com')
article_links = scraper.extract_links(main_page, '.article-link')

# Scrape all articles
articles = scraper.scrape_multiple_pages(article_links[:10], news_config)
scraper.save_to_csv(articles, 'news_articles.csv')
```

### Example 2: E-commerce Product Scraping

```python
from advanced_scraper import AdvancedScraper

product_config = {
    'name': '.product-name',
    'price': '.price-current',
    'original_price': '.price-original',
    'rating': '.rating-value',
    'reviews_count': '.reviews-count',
    'availability': '.stock-status'
}

with AdvancedScraper(headless=False) as scraper:
    # Navigate to product listing
    scraper.get_page('https://shop.com/products', wait_for_element='.product-grid')
    
    # Scroll to load all products (for infinite scroll)
    scraper.scroll_to_bottom(pause_time=2)
    
    # Extract product data
    products = scraper.extract_elements_data(product_config)
    
    scraper.save_to_json(products, 'products.json')
    print(f"Scraped {len(products)} products")
```

## Best Practices

1. **Be Respectful**: Always check robots.txt and respect rate limits
2. **Handle Errors**: The scrapers include error handling, but always verify your data
3. **Use Delays**: Built-in random delays help avoid being blocked
4. **Test Selectors**: Verify your CSS selectors work correctly before large scrapes
5. **Monitor Changes**: Websites change their structure; monitor your scrapers

## Rate Limiting

The basic scraper includes random delays between requests (1-3 seconds by default). You can customize this:

```python
scraper = WebScraper(delay_range=(2, 5))  # 2-5 second delays
```

## Legal Considerations

- Always check the website's robots.txt file
- Respect terms of service
- Don't overload servers with too many requests
- Consider reaching out to site owners for permission
- Be aware of copyright and data protection laws

## Troubleshooting

### Common Issues

1. **Elements not found**: Check if the CSS selectors are correct
2. **Blocked requests**: Try adding delays or changing user agent
3. **JavaScript content not loading**: Use the advanced scraper with Selenium
4. **Chrome driver issues**: The driver auto-downloads, but ensure Chrome is installed

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Run the advanced scraper with `headless=False` to see what's happening in the browser. 