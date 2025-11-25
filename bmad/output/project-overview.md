# BBQ Scraper - Project Overview

**Generated:** 2025-11-10
**Project Type:** Data Processing Pipeline (Brownfield)
**Repository Structure:** Monolith

---

## Executive Summary

The BBQ Scraper is a Python-based web scraping and ETL pipeline designed to automatically extract product data from BBQGuys.com on a daily rotating schedule. The system scrapes BBQ product information including specifications, images, pricing, and descriptions, then stores the data in a Supabase database for downstream consumption.

## Purpose

- **Primary Goal:** Automate daily collection of BBQ product data from multiple brands
- **Data Output:** Structured product information stored in Supabase database
- **Schedule:** Daily execution with rotating brand assignments per weekday
- **Coverage:** Multiple BBQ brands across different product categories

## Technology Stack

### Core Technologies
- **Language:** Python 3.x
- **Web Scraping:**
  - `requests` - HTTP client
  - `beautifulsoup4` + `lxml` - HTML parsing
  - `selenium` - Dynamic content handling
- **Data Processing:** `pandas` - Data manipulation
- **Database:** Supabase (PostgreSQL) with Python client
- **Configuration:** `python-dotenv` - Environment variables

### Architecture Pattern
**Sequential ETL Pipeline** with 5 processing steps orchestrated by a scheduler

## Project Structure

```
badassbbqs-scrapper/
├── index.py                    # Main orchestrator (scheduler)
├── Step1.py                    # Pagination detection
├── Step2.py                    # URL extraction
├── Step3.py                    # Product scraping
├── Step4.py                    # Database storage (Supabase)
├── Step5.py                    # Cleanup
├── test.py                     # Testing utilities
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (Supabase credentials)
├── venv/                       # Python virtual environment
├── bmad/                       # BMAD Method documentation
│   ├── bmm/
│   └── output/                 # Generated documentation
├── products.json               # Scraped products (temp file)
├── brands.txt                  # Product URLs (temp file)
├── brand_pages_count.json      # Pagination data (temp file)
└── index.log                   # Execution logs
```

## Key Features

1. **Daily Scheduling:** Automated brand rotation by weekday
2. **Rate Limiting:** Respectful scraping with delays (1-3 seconds between requests)
3. **Pagination Handling:** Automatic detection and traversal of multi-page listings
4. **Robust Extraction:** Multiple CSS selectors for reliable data capture
5. **Data Validation:** Price conversion, image deduplication, field normalization
6. **Batch Processing:** Efficient database inserts (50 products per batch)
7. **Error Handling:** Comprehensive logging and graceful failure recovery
8. **Cleanup:** Automatic removal of temporary files after successful upload

## Data Flow

```
BBQGuys.com → Step1 (Pagination) → Step2 (URLs) → Step3 (Scraping) → Step4 (Supabase) → Step5 (Cleanup)
```

## Extracted Data Fields

- **Product Identification:** ID, Model, URL
- **Basic Info:** Title, Brand, Price, Category
- **Media:** Main Image, Other Images (array)
- **Details:** Description, Key Features, Configurations
- **Specifications:** Technical specs (JSON array)

## Execution Model

- **Trigger:** Daily execution via `index.py`
- **Input:** Brand URLs from `BRAND_SCHEDULE` dictionary
- **Processing:** Sequential execution of Steps 1-5
- **Output:** Products stored in Supabase `scrapped_products` table
- **Logging:** Timestamped logs in `index.log`

## Success Metrics

- Products successfully scraped and stored
- Minimal failures due to rate limiting or blocking
- Complete data capture per product specification
- Database records match scraped product count

---

**Related Documentation:**
- [Architecture](./architecture.md)
- [Development Guide](./development-guide.md)
- [Source Tree Analysis](./source-tree-analysis.md)
