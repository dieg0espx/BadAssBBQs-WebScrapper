# BBQ Scraper - Source Tree Analysis

**Generated:** 2025-11-10

---

## Directory Structure

```
badassbbqs-scrapper/
├── .git/                           # Git version control
├── .claude/                        # Claude Code configuration
├── venv/                           # Python virtual environment (gitignored)
├── bmad/                           # BMAD Method framework
│   ├── bmm/                        # BMad Method module
│   │   └── config.yaml             # Project configuration
│   └── output/                     # Generated documentation
│       ├── project-overview.md
│       ├── architecture.md
│       ├── development-guide.md
│       ├── source-tree-analysis.md
│       ├── index.md
│       ├── project-scan-report.json
│       └── bmm-workflow-status.yaml
├── index.py                        # 🚀 Main orchestrator (entry point)
├── Step1.py                        # 📄 Pagination detection
├── Step2.py                        # 🔗 URL extraction
├── Step3.py                        # 📦 Product scraping
├── Step4.py                        # 💾 Database storage
├── Step5.py                        # 🧹 Cleanup
├── test.py                         # 🧪 Testing utilities
├── requirements.txt                # 📋 Python dependencies
├── .env                            # 🔐 Environment variables (gitignored)
├── .DS_Store                       # macOS metadata (gitignored)
├── products.json                   # 📊 Scraped products (temp, gitignored)
├── brands.txt                      # 🔗 Product URLs (temp, gitignored)
├── brand_pages_count.json          # 📄 Pagination data (temp, gitignored)
└── index.log                       # 📝 Execution logs
```

---

## Critical Files and Their Purpose

### Entry Points

#### **index.py** - Orchestrator
**Purpose:** Main entry point for daily scraper execution

**Key Components:**
- `BRAND_SCHEDULE`: Dictionary mapping weekdays to brand URL lists
- `get_today_brands()`: Returns brands for current day
- `run_step(script, brands)`: Executes a step script via subprocess
- `main()`: Orchestrates sequential step execution

**Execution Flow:**
1. Determine today's brands
2. Execute Steps 1-5 sequentially
3. Log output and errors
4. Abort pipeline on any step failure

**Usage:**
```bash
python3 index.py
```

---

### Processing Steps

#### **Step1.py** - Pagination Detection
**Purpose:** Determine the number of pages for each brand

**Key Classes:**
- `PageCountExtractor`: Scrapes first page to detect pagination

**Key Methods:**
- `get_page(url)`: Fetch page with rate limiting
- `get_max_page_number(soup)`: Extract total pages using multiple detection methods
- `extract_brand_name(url)`: Parse brand name from URL

**Detection Strategies:**
1. BBQGuys Material-UI pagination (primary)
2. Generic MUI pagination (fallback)
3. Next button detection (minimal)

**Input:** Brand URLs (command-line arg)
**Output:** `brand_pages_count.json`

**Output Schema:**
```json
{
  "Brand Name": {
    "url": "https://...",
    "page_count": 15
  }
}
```

---

#### **Step2.py** - URL Extraction
**Purpose:** Extract all product URLs from all brand pages

**Key Classes:**
- `AllURLsExtractor`: Scrapes all pages to collect product URLs

**Key Methods:**
- `load_brand_page_counts()`: Load Step 1 output
- `generate_page_urls(base_url, total_pages)`: Create page URLs with pagination
- `extract_product_urls_from_page(soup)`: Find product links
- `extract_all_products_from_brand()`: Orchestrate extraction

**URL Patterns:**
- Selector: `a[href*="/i/"]` (product pages have `/i/` in path)
- Deduplicates URLs
- Cleans query parameters

**Input:** `brand_pages_count.json`
**Output:** `brands.txt` (one URL per line)

---

#### **Step3.py** - Product Scraping
**Purpose:** Extract detailed product information from each URL

**Key Classes:**
- `WebScraper`: General-purpose web scraping class

**Key Methods:**
- `get_page(url)`: HTTP fetching with session management
- `scrape_data(url, data_config)`: Config-driven extraction
- `extract_text()` / `extract_attributes()` / `extract_links()`: CSS selectors
- `save_to_json()`: Serialize to JSON

**Data Configuration:**
Declarative extraction config in `bbq_config` dictionary:
```python
{
    'Title': {'selector': 'h1', 'type': 'text'},
    'Price': {'selector': '.price', 'type': 'text'},
    'Specifications': {'selector': 'table', 'type': 'specifications_table'},
    # ... more fields
}
```

**Supported Types:**
- `text` - Text content
- `attribute` - HTML attributes
- `links` - Href resolution
- `images_with_alt` - Image URLs
- `config_options` - Product configurations
- `specifications_table` - Parse spec tables

**Data Transformations:**
1. Price: `$1,234.56` → `1234.56` (float)
2. ID/Model: Extract after `#` character
3. Images: Deduplicate, main image to end of array
4. Description: Combine key features + description
5. Category: Breadcrumb links → array

**Input:** `brands.txt`
**Output:** `products.json`

---

#### **Step4.py** - Database Storage
**Purpose:** Upload scraped products to Supabase PostgreSQL

**Key Classes:**
- `SupabaseManager`: Supabase client wrapper

**Key Methods:**
- `insert_product(product_data)`: Single product insert
- `insert_products_batch(products, batch_size)`: Batch insert
- `upsert_product(product_data)`: Insert or update by ID
- `get_product_count()`: Query total products
- `get_products_by_brand(brand)`: Filter by brand
- `search_products(term)`: Search by title/description

**Database Schema:**
```sql
scrapped_products (
    id, product_id, url, title, price, brand,
    image, other_images, model, Configurations,
    category, specifications, description,
    created_at, updated_at
)
```

**Batch Processing:**
- 50 products per batch (configurable)
- 1 second delay between batches
- Error tracking per batch

**Input:** `products.json`
**Output:** Database records in Supabase

---

#### **Step5.py** - Cleanup
**Purpose:** Remove temporary files after successful upload

**Files Deleted:**
- `products.json`
- `brand_pages_count.json`
- `products_fixed.csv` (if exists)

**Rationale:** Keep working directory clean

**Input:** None
**Output:** Clean directory state

---

### Configuration Files

#### **requirements.txt** - Python Dependencies
```
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
selenium>=4.8.0
pandas>=1.5.0
```

Additional (inferred from code):
- `supabase` - Database client
- `python-dotenv` - Environment variables

#### **.env** - Environment Variables (NOT IN REPO)
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

**Security:** This file must be gitignored and never committed

---

### Output Files

#### **index.log** - Execution Log
**Format:** `%(asctime)s - %(levelname)s - %(message)s`
**Levels:** INFO, WARNING, ERROR
**Purpose:** Track execution history and debug issues

**Example Entry:**
```
2025-11-10 10:30:15 - INFO - Today is Monday. Brands to process: [...]
2025-11-10 10:30:20 - INFO - Running Step1.py for brands: [...]
```

#### **Temporary Data Files** (Deleted by Step 5)

**brand_pages_count.json**
```json
{
  "Brand Name": {
    "url": "...",
    "page_count": 15
  }
}
```

**brands.txt**
```
https://www.bbqguys.com/i/12345/product-1
https://www.bbqguys.com/i/12346/product-2
...
```

**products.json**
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
    "configurations": [...],
    "Category": [...],
    "Specifications": [...],
    "Description": "..."
  }
]
```

---

## File Dependencies

```
┌─────────────┐
│  index.py   │ (orchestrator)
└──────┬──────┘
       │
       ├──► Step1.py ───► brand_pages_count.json
       │
       ├──► Step2.py ───► brands.txt
       │        ▲
       │        └─────── brand_pages_count.json
       │
       ├──► Step3.py ───► products.json
       │        ▲
       │        └─────── brands.txt
       │
       ├──► Step4.py ───► Supabase DB
       │        ▲
       │        └─────── products.json
       │
       └──► Step5.py ───► (deletes temp files)
                ▲
                └─────── (cleanup only, no input)
```

---

## Code Organization Patterns

### Class Structure

**Step1.py:**
- `PageCountExtractor`: Pagination detection

**Step2.py:**
- `AllURLsExtractor`: URL extraction

**Step3.py:**
- `WebScraper`: Generic scraping framework

**Step4.py:**
- `SupabaseManager`: Database operations

**Step5.py:**
- No classes (simple script)

### Function Organization

Each step follows similar pattern:
1. Helper functions (extraction, parsing, etc.)
2. Main class (if applicable)
3. `main()` function for CLI execution
4. `if __name__ == "__main__": main()`

### Configuration Pattern

**Declarative configs** used in Step3:
```python
data_config = {
    'field_name': {
        'selector': 'css_selector',
        'type': 'extraction_type',
        'attribute': 'optional_attribute'
    }
}
```

---

## Critical Directories

### **bmad/** - BMAD Method Framework
Contains project documentation and workflow tracking generated by the BMAD (Business Mad) development methodology

**Key Files:**
- `bmad/bmm/config.yaml` - User preferences and project settings
- `bmad/output/bmm-workflow-status.yaml` - Workflow progress tracking
- `bmad/output/*.md` - Generated documentation

### **venv/** - Virtual Environment
Python virtual environment for isolated dependency management

**Should be:**
- ✅ Gitignored
- ✅ Recreated on new setups
- ❌ Never committed to repository

### **.git/** - Version Control
Git repository metadata

**Contains:**
- Commit history
- Branch information
- Remote tracking

---

## Naming Conventions

### Files
- **Scripts:** `PascalCase.py` (e.g., `Step1.py`)
- **Entry point:** `lowercase.py` (e.g., `index.py`)
- **Data files:** `snake_case.json/txt` (e.g., `brand_pages_count.json`)
- **Logs:** `lowercase.log` (e.g., `index.log`)

### Code
- **Classes:** `PascalCase` (e.g., `PageCountExtractor`)
- **Functions:** `snake_case` (e.g., `get_page`)
- **Variables:** `snake_case` (e.g., `brand_urls`)
- **Constants:** `UPPER_CASE` (e.g., `BRAND_SCHEDULE`)

---

## Integration Points

### External Systems
1. **BBQGuys.com** - Source website
2. **Supabase** - PostgreSQL database
3. **File System** - Temp file storage

### Inter-Step Communication
- **Method:** File-based (JSON, TXT)
- **Pattern:** Producer/consumer
- **Cleanup:** Step 5 removes intermediate files

---

**Related Documentation:**
- [Project Overview](./project-overview.md)
- [Architecture](./architecture.md)
- [Development Guide](./development-guide.md)
