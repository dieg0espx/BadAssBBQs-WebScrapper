# BBQ Scraper - Development Guide

**Generated:** 2025-11-10

---

## Prerequisites

### Required Software
- **Python:** 3.7+ (tested with 3.x)
- **pip:** Python package manager
- **Git:** Version control
- **Supabase Account:** For database access

### System Requirements
- **OS:** macOS, Linux, or Windows
- **RAM:** 512MB minimum
- **Disk Space:** 100MB for dependencies + data files
- **Network:** Stable internet connection

---

## Initial Setup

### 1. Clone the Repository

```bash
cd ~/Desktop
# Repository already exists at: badassbbqs-scrapper
cd badassbbqs-scrapper
```

### 2. Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate venv
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- `requests>=2.28.0` - HTTP client
- `beautifulsoup4>=4.11.0` - HTML parsing
- `lxml>=4.9.0` - XML/HTML parser
- `selenium>=4.8.0` - Browser automation
- `pandas>=1.5.0` - Data manipulation

Additional dependencies (from code analysis):
- `supabase` - Supabase Python client
- `python-dotenv` - Environment variable management

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

**Getting Supabase Credentials:**
1. Sign up at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings → API
4. Copy `URL` and `anon public` key

### 5. Set Up Database Tables

Run the SQL in Step4.py `create_tables()` method on your Supabase SQL editor:

```sql
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

CREATE INDEX idx_scrapped_products_product_id ON scrapped_products(product_id);
CREATE INDEX idx_scrapped_products_brand ON scrapped_products(brand);
```

---

## Running the Scraper

### Full Pipeline Execution

```bash
# Activate virtual environment first
source venv/bin/activate

# Run the orchestrator (executes all 5 steps)
python3 index.py
```

**What happens:**
1. Determines today's brands from schedule
2. Runs Step1 → Step2 → Step3 → Step4 → Step5 sequentially
3. Logs output to `index.log` and console
4. Aborts on any step failure

### Running Individual Steps

```bash
# Step 1: Pagination detection
python3 Step1.py "https://www.bbqguys.com/d/22965/brands/fontana-forni/shop-all"

# Step 2: URL extraction
python3 Step2.py "https://www.bbqguys.com/d/22965/brands/fontana-forni/shop-all"

# Step 3: Product scraping
python3 Step3.py "https://www.bbqguys.com/d/22965/brands/fontana-forni/shop-all"

# Step 4: Upload to Supabase
python3 Step4.py "https://www.bbqguys.com/d/22965/brands/fontana-forni/shop-all"

# Step 5: Cleanup
python3 Step5.py "https://www.bbqguys.com/d/22965/brands/fontana-forni/shop-all"
```

**Note:** Each step expects comma-separated brand URLs as argument:
```bash
python3 Step1.py "url1,url2,url3"
```

---

## Configuration

### Modifying the Brand Schedule

Edit `index.py` and update the `BRAND_SCHEDULE` dictionary:

```python
BRAND_SCHEDULE = {
    'Monday': [
        'https://www.bbqguys.com/d/17994/brands/alfresco-grills/shop-all',
        # Add more brands...
    ],
    'Tuesday': [
        'https://www.bbqguys.com/d/24062/brands/blackstone-grills/shop-all',
    ],
    # ... other days
}
```

### Adjusting Rate Limiting

**In Step1.py, Step2.py, Step3.py:**

```python
# Change delay_range parameter (min, max) in seconds
extractor = PageCountExtractor(delay_range=(2, 5))  # Slower
scraper = WebScraper(delay_range=(0.5, 1))         # Faster (risky)
```

**Default:** `(1, 3)` seconds - balanced and respectful

### Customizing Data Extraction

**In Step3.py, modify `bbq_config` dictionary:**

```python
bbq_config = {
    'Title': {'selector': 'h1.product-name', 'type': 'text'},
    'NewField': {'selector': '.some-class', 'type': 'text'},
    # Add/remove fields as needed
}
```

**Supported extraction types:**
- `text` - Text content
- `attribute` - HTML attribute value
- `links` - Href attributes
- `images_with_alt` - Image URLs
- `config_options` - Configuration options
- `specifications_table` - Spec tables

### Database Batch Size

**In Step4.py `main()` function:**

```python
# Change batch_size parameter
results = supabase_manager.insert_products_batch(products, batch_size=100)
```

**Default:** 50 products per batch

---

## Testing

### Running Tests

```bash
# Run test file
python3 test.py
```

**Note:** Specific test coverage unknown (Quick Scan mode)

### Manual Testing Individual Components

```python
# Test pagination detection
from Step1 import PageCountExtractor
extractor = PageCountExtractor()
soup = extractor.get_page("brand_url_here")
pages = extractor.get_max_page_number(soup)
print(f"Pages: {pages}")

# Test product scraping
from Step3 import WebScraper
scraper = WebScraper(base_url='https://www.bbqguys.com')
data = scraper.scrape_data("product_url_here", config)
print(data)
```

---

## Debugging

### Viewing Logs

```bash
# Tail live logs
tail -f index.log

# View recent entries
tail -100 index.log

# Search for errors
grep "ERROR" index.log
```

### Common Issues

**1. Import Errors**

```
ModuleNotFoundError: No module named 'requests'
```

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

**2. Supabase Connection Failures**

```
ValueError: SUPABASE_URL and SUPABASE_ANON_KEY must be set
```

**Solution:** Check `.env` file exists and contains correct credentials

**3. Empty Results**

**Possible causes:**
- Website structure changed (CSS selectors outdated)
- Rate limiting or IP blocking
- Network issues

**Solution:**
- Inspect HTML manually
- Update selectors in data_config
- Increase delays
- Rotate user agents

**4. Database Insert Failures**

```
Error inserting product: ...
```

**Solution:**
- Check Supabase table exists
- Verify field names match
- Check for data type mismatches (e.g., string in decimal field)

---

## Development Workflow

### Adding a New Brand

1. Find the brand's shop-all URL on BBQGuys.com
2. Add to `BRAND_SCHEDULE` in `index.py`
3. Test with individual step execution first
4. Monitor logs for issues

### Modifying Extraction Logic

1. Inspect target webpage HTML (browser DevTools)
2. Update CSS selectors in `Step3.py` config
3. Test on single product first
4. Run full brand scrape
5. Verify data in Supabase

### Adding New Data Fields

1. Add field to `bbq_config` in `Step3.py`
2. Update `SupabaseManager.insert_product()` in `Step4.py`
3. Add column to Supabase table if needed
4. Test end-to-end

---

## Code Style & Standards

### Python Conventions
- **Style:** PEP 8
- **Docstrings:** Google style (used in Step3.py)
- **Imports:** Standard → Third-party → Local
- **Naming:**
  - `snake_case` for functions/variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

### Logging Standards
- **Levels:** INFO, WARNING, ERROR
- **Format:** `%(asctime)s - %(levelname)s - %(message)s`
- **Usage:**
  - INFO: Normal execution flow
  - WARNING: Recoverable issues
  - ERROR: Failures requiring attention

---

## Performance Optimization

### Current Bottlenecks
1. **Sequential HTTP requests** (Step 3 is slowest)
2. **Single-threaded execution**
3. **No caching**

### Optimization Strategies

**1. Parallel Scraping (Step 3)**

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(scraper.scrape_data, url, config)
               for url in product_urls]
    results = [f.result() for f in futures]
```

**2. Async Requests**

```python
import aiohttp
import asyncio

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

**3. Caching Pagination Data**

Cache `brand_pages_count.json` and only refresh weekly

---

## Security Best Practices

### Credentials
- ✅ Use `.env` for secrets
- ✅ Add `.env` to `.gitignore`
- ❌ Never commit credentials to Git
- ✅ Use environment variables in production

### Web Scraping
- ✅ Respect rate limits
- ✅ Honor robots.txt (add check)
- ✅ Use descriptive User-Agent
- ❌ Don't overwhelm servers
- ✅ Handle 429 (Too Many Requests) gracefully

### Data Handling
- ✅ Validate/sanitize scraped data
- ✅ Handle PII appropriately (none currently)
- ✅ Secure database connections (HTTPS)

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor `index.log` for errors
- Check Supabase storage usage

**Weekly:**
- Review scraping success rates
- Update brand list if needed
- Test selector validity

**Monthly:**
- Update dependencies
- Review and optimize database indexes
- Audit for website structure changes

### Updating Dependencies

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade requests

# Update all packages (careful!)
pip install --upgrade -r requirements.txt

# Regenerate requirements
pip freeze > requirements.txt
```

---

## Troubleshooting Guide

### Issue: Script hangs indefinitely

**Causes:**
- Network timeout
- Infinite loop in pagination
- Blocked by website

**Solutions:**
- Check timeout settings in `requests.get()`
- Add max page limit safety check
- Verify not rate limited/blocked

### Issue: Incomplete data in database

**Causes:**
- Missing required fields in extraction
- Field name mismatches
- Database constraints

**Solutions:**
- Log extracted data before insert
- Verify field names match between scraper and database
- Check for NOT NULL constraints

### Issue: High failure rate

**Causes:**
- Website structure changed
- Aggressive rate limiting
- CSS selectors outdated

**Solutions:**
- Inspect current website HTML
- Update selectors
- Increase delays
- Implement retry logic

---

## Getting Help

### Resources
- **Python Docs:** [docs.python.org](https://docs.python.org)
- **BeautifulSoup Docs:** [crummy.com/software/BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- **Supabase Docs:** [supabase.com/docs](https://supabase.com/docs)
- **Project Documentation:** `bmad/output/`

### Reporting Issues
- Check `index.log` for error details
- Document steps to reproduce
- Include relevant error messages
- Note brand/product URLs that failed

---

**Related Documentation:**
- [Project Overview](./project-overview.md)
- [Architecture](./architecture.md)
- [Source Tree Analysis](./source-tree-analysis.md)
