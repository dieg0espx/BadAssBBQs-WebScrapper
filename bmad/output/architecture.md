# BBQ Scraper - Architecture Documentation

**Generated:** 2025-11-10
**Project Type:** Data Processing Pipeline
**Architecture Pattern:** Sequential ETL with Orchestrated Steps

---

## Architecture Overview

The BBQ Scraper implements a **sequential ETL (Extract, Transform, Load) pipeline** architecture with clear separation of concerns across five processing steps. Each step is a self-contained Python script that performs a specific function in the data collection workflow.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         index.py                                 │
│                   (Orchestrator/Scheduler)                       │
│  - Determines today's brands based on schedule                  │
│  - Executes Steps 1-5 sequentially                              │
│  - Logs execution and handles failures                          │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ├──► Step 1: Pagination Detection
               │    ├─ Input: Brand URLs
               │    ├─ Process: Scrape first page, detect total pages
               │    └─ Output: brand_pages_count.json
               │
               ├──► Step 2: URL Extraction
               │    ├─ Input: brand_pages_count.json
               │    ├─ Process: Scrape all pages, extract product URLs
               │    └─ Output: brands.txt
               │
               ├──► Step 3: Product Scraping
               │    ├─ Input: brands.txt
               │    ├─ Process: Scrape each product page for details
               │    └─ Output: products.json
               │
               ├──► Step 4: Database Storage
               │    ├─ Input: products.json
               │    ├─ Process: Batch insert products into Supabase
               │    └─ Output: Database records
               │
               └──► Step 5: Cleanup
                    ├─ Input: None
                    ├─ Process: Delete temporary JSON/txt files
                    └─ Output: Clean working directory
```

---

## Component Architecture

### 1. Orchestrator (index.py)

**Responsibilities:**
- Daily schedule management (`BRAND_SCHEDULE` dictionary)
- Sequential step execution via subprocess
- Inter-step communication (via files and exit codes)
- Error handling and pipeline abort on failure
- Centralized logging

**Key Design Decisions:**
- Subprocess execution allows step isolation
- File-based communication enables restart from any step
- Exit code checking ensures pipeline integrity
- Day-based scheduling distributes load across week

**Schedule Structure:**
```python
BRAND_SCHEDULE = {
    'Monday': [brand_url_1, brand_url_2, ...],
    'Tuesday': [...],
    # ... through Sunday
}
```

### 2. Step 1: PageCountExtractor Class

**Purpose:** Determine pagination for each brand

**Key Methods:**
- `get_page(url)` - Fetch webpage with rate limiting
- `get_max_page_number(soup)` - Extract total pages using multiple strategies
- `extract_brand_name(url)` - Parse brand name from URL

**Pagination Detection Strategy:**
1. BBQGuys Material-UI pagination (aria-labels)
2. Generic MUI pagination components
3. Next button detection as fallback

**Output Schema:**
```json
{
  "brand_name": {
    "url": "...",
    "page_count": 15
  }
}
```

### 3. Step 2: AllURLsExtractor Class

**Purpose:** Extract all product URLs from all brand pages

**Key Methods:**
- `load_brand_page_counts()` - Load Step 1 output
- `generate_page_urls()` - Create page URLs with pagination params
- `extract_product_urls_from_page()` - Find product links via CSS selectors
- `extract_all_products_from_brand()` - Orchestrate full extraction

**URL Generation:**
- Base URL + `?page=N` for pages 2+
- Handles existing query parameters
- Deduplicates URLs

**Product URL Patterns:**
- Selector: `a[href*="/i/"]` (products have `/i/` in path)
- Converts relative to absolute URLs
- Strips query params and fragments for cleanliness

**Output:** Plain text file (`brands.txt`), one URL per line

### 4. Step 3: WebScraper Class

**Purpose:** Extract detailed product information

**Key Methods:**
- `get_page(url)` - HTTP fetching with session management
- `scrape_data(url, data_config)` - Config-driven extraction
- `extract_text()` / `extract_attributes()` / `extract_links()` - CSS-based extraction
- `save_to_json()` - Serialize products to JSON

**Data Extraction Configuration:**

The scraper uses a declarative configuration approach:

```python
data_config = {
    'Title': {'selector': 'h1', 'type': 'text'},
    'Price': {'selector': '.price', 'type': 'text'},
    'Image': {'selector': 'img', 'type': 'attribute', 'attribute': 'src'},
    'Specifications': {'selector': 'table', 'type': 'specifications_table'},
    # ... more fields
}
```

**Extraction Types:**
- `text` - Get text content
- `attribute` - Extract HTML attributes
- `links` - Extract and resolve hrefs
- `images_with_alt` - Images with alt text
- `config_options` - Product configuration options
- `specifications_table` - Parse spec tables into key-value pairs

**Data Transformations:**
1. **Price normalization:** `$1,234.56` → `1234.56` (float)
2. **ID/Model extraction:** Extract text after `#` character
3. **Image deduplication:** Main image moved to end of `Other_image` array
4. **Description combining:** Merge key features + description into single field
5. **Category as array:** Breadcrumb links → list of categories

**Output Schema:**
```json
[
  {
    "url": "...",
    "Title": "...",
    "Price": 1234.56,
    "brand": "...",
    "Image": "...",
    "Other_image": ["...", "..."],
    "Id": "...",
    "Model": "...",
    "configurations": [{label: "...", value: "..."}],
    "Category": ["Home", "Grills", "Gas Grills"],
    "Specifications": [{"Width": "48 inches"}, {...}],
    "Description": "..."
  }
]
```

### 5. Step 4: SupabaseManager Class

**Purpose:** Persist products to PostgreSQL (via Supabase)

**Key Methods:**
- `insert_product()` - Single product insert
- `insert_products_batch()` - Batch insert (50 per batch)
- `upsert_product()` - Insert or update by ID
- `get_product_count()` - Query total products

**Database Schema:**
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
```

**Batch Processing:**
- Batches of 50 products
- 1 second delay between batches (rate limiting)
- Error tracking per batch
- Transactional inserts

**Field Mappings:**
- `Id` → `product_id`
- `Title` → `title`
- `Price` → `price` (DECIMAL)
- `Other_image` → `other_images` (JSONB)
- `Specifications` → `specifications` (JSONB)

### 6. Step 5: Cleanup Script

**Purpose:** Remove temporary files after successful upload

**Files Deleted:**
- `products.json`
- `brand_pages_count.json`
- `products_fixed.csv` (if exists)

**Rationale:** Keep working directory clean, reduce disk usage

---

## Data Architecture

### Data Flow States

1. **Raw HTML** (BBQGuys.com)
2. **Pagination Metadata** (JSON)
3. **Product URLs** (Text file)
4. **Structured Products** (JSON)
5. **Database Records** (PostgreSQL/Supabase)

### Temporary vs Persistent Data

**Temporary (deleted by Step 5):**
- `brand_pages_count.json`
- `brands.txt`
- `products.json`

**Persistent:**
- Supabase database records
- `index.log` (execution history)
- `.env` (credentials)

### Data Retention

- **Source:** BBQGuys.com (external)
- **Intermediate:** Deleted after each successful run
- **Final:** Supabase database (indefinite retention)

---

## Integration Points

### External Services

1. **BBQGuys.com**
   - Protocol: HTTPS
   - Authentication: None (public web scraping)
   - Rate Limiting: Self-imposed delays (1-3 seconds)
   - Failure Mode: Graceful degradation, log errors

2. **Supabase (PostgreSQL)**
   - Protocol: HTTPS (REST API)
   - Authentication: API key (via `.env`)
   - Connection: Python `supabase-py` client
   - Failure Mode: Batch-level error handling

### File System

- **Read:** `requirements.txt`, `.env`, temp JSON/TXT files
- **Write:** Logs, temp data files
- **Delete:** Temp files (Step 5)

---

## Error Handling Strategy

### Step-Level Failures

**Detection:**
- Non-zero exit codes from subprocess
- Exception catching within each step

**Handling:**
- Log error with timestamp
- Abort pipeline (don't execute remaining steps)
- Preserve temp files for debugging

### Product-Level Failures

**Detection:**
- Missing required fields
- HTTP errors (4xx, 5xx)
- Parsing errors

**Handling:**
- Log warning with product URL
- Continue with remaining products
- Track failed count in summary

### Database Failures

**Detection:**
- Supabase API errors
- Batch insert failures

**Handling:**
- Log batch number and error
- Continue with next batch
- Report failed/successful counts at end

---

## Performance Characteristics

### Rate Limiting
- **Delay Range:** 1-3 seconds (random)
- **Location:** After each HTTP request
- **Batch Delays:** 1 second between database batches

### Execution Time (Estimated)

For a single brand with 100 products across 5 pages:
- **Step 1:** ~5-10 seconds (1 page)
- **Step 2:** ~15-30 seconds (5 pages)
- **Step 3:** ~3-8 minutes (100 products × 2 sec avg)
- **Step 4:** ~5-10 seconds (batch inserts)
- **Step 5:** <1 second

**Total:** ~4-10 minutes per brand

### Scalability

**Current Capacity:**
- Handles multiple brands sequentially
- No concurrency (single-threaded)
- Limited by rate limiting and network speed

**Bottlenecks:**
- HTTP request latency (Step 3 is slowest)
- Sequential execution (no parallelization)
- Single-threaded scraping

**Potential Optimizations:**
- Parallel scraping with thread pool
- Async HTTP requests (aiohttp)
- Distributed execution for multiple brands
- Caching of pagination data

---

## Security Considerations

### Credentials Management
- **Storage:** `.env` file (gitignored)
- **Required:** `SUPABASE_URL`, `SUPABASE_ANON_KEY`
- **Best Practice:** Use environment variables in production

### Web Scraping Ethics
- **Rate Limiting:** Respectful delays between requests
- **User-Agent:** Honest browser identification
- **robots.txt:** Not explicitly checked (should be added)
- **Terms of Service:** Responsibility of deployer to ensure compliance

### Data Privacy
- **PII:** No personal data collected (public product info only)
- **Storage:** Supabase with standard security practices
- **Access Control:** Managed via Supabase auth

---

## Testing Strategy

### Current State
- `test.py` exists but specific coverage unknown (Quick Scan)

### Recommended Testing
1. **Unit Tests:** Individual extraction methods
2. **Integration Tests:** Step-to-step data flow
3. **E2E Tests:** Full pipeline execution
4. **Mock Tests:** HTTP requests for faster testing

---

## Deployment Architecture

### Current Deployment
- **Environment:** Local execution
- **Trigger:** Manual or cron job
- **Dependencies:** Python 3.x + requirements.txt
- **Configuration:** `.env` file

### Recommended Production Setup
1. **Containerization:** Docker for consistency
2. **Orchestration:** Kubernetes or ECS
3. **Scheduling:** Airflow or cloud-native schedulers
4. **Monitoring:** Datadog, Sentry for error tracking
5. **Alerting:** Slack/email on pipeline failures

---

## Future Architecture Considerations

### Potential Enhancements
1. **Async Scraping:** Significantly faster execution
2. **Retry Logic:** Automatic retry for transient failures
3. **Incremental Updates:** Only scrape changed products
4. **Change Detection:** Track price/availability changes
5. **Multi-Source:** Extend to other BBQ retailers
6. **API Mode:** Expose scraped data via REST API

---

**Related Documentation:**
- [Project Overview](./project-overview.md)
- [Development Guide](./development-guide.md)
- [Data Models](./data-models.md) _(To be generated)_
