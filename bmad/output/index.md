# BBQ Scraper - Documentation Index

**Generated:** 2025-11-10
**Project:** badassbbqs-scrapper
**Type:** Data Processing Pipeline (Brownfield)
**Scan Level:** Quick
**Documentation Mode:** Initial Scan

---

## Project Overview

### Quick Reference

- **Repository Type:** Monolith (single cohesive codebase)
- **Primary Language:** Python 3.x
- **Architecture Pattern:** Sequential ETL Pipeline (5 steps)
- **Entry Point:** `index.py` (orchestrator)
- **Purpose:** Daily automated scraping of BBQ product data from BBQGuys.com
- **Output:** PostgreSQL database (via Supabase)

### Technology Stack

| Category | Technology | Version |
|----------|-----------|---------|
| **Language** | Python | 3.x |
| **HTTP Client** | requests | ≥2.28.0 |
| **HTML Parsing** | beautifulsoup4 + lxml | ≥4.11.0 |
| **Browser Automation** | selenium | ≥4.8.0 |
| **Data Processing** | pandas | ≥1.5.0 |
| **Database** | Supabase (PostgreSQL) | Latest |
| **Environment Config** | python-dotenv | Latest |

### Pipeline Steps

1. **Step1.py** - Pagination Detection → `brand_pages_count.json`
2. **Step2.py** - URL Extraction → `brands.txt`
3. **Step3.py** - Product Scraping → `products.json`
4. **Step4.py** - Database Storage → Supabase
5. **Step5.py** - Cleanup → (removes temp files)

---

## Generated Documentation

### Core Documentation

- **[Project Overview](./project-overview.md)** - Executive summary, purpose, features, data flow
- **[Architecture](./architecture.md)** - System architecture, component design, data architecture, integration points
- **[Development Guide](./development-guide.md)** - Setup, configuration, running the scraper, debugging, maintenance
- **[Source Tree Analysis](./source-tree-analysis.md)** - Directory structure, file descriptions, code organization

### Workflow Documentation

- **[Workflow Status](./bmm-workflow-status.yaml)** - BMAD Method workflow progress tracking
- **[Project Scan Report](./project-scan-report.json)** - Detailed scan metadata and findings

---

## Getting Started

### For New Developers

1. Read [Project Overview](./project-overview.md) for high-level understanding
2. Review [Architecture](./architecture.md) to understand system design
3. Follow [Development Guide](./development-guide.md) for setup instructions
4. Refer to [Source Tree Analysis](./source-tree-analysis.md) for code navigation

### Quick Start Commands

```bash
# 1. Clone and navigate to project
cd ~/Desktop/badassbbqs-scrapper

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cat > .env << EOF
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
EOF

# 5. Run the scraper
python3 index.py
```

---

## Key Files Reference

### Entry Points
- **index.py** - Main orchestrator, daily scheduler
- **Step[1-5].py** - Individual processing steps

### Configuration
- **requirements.txt** - Python dependencies
- **.env** - Supabase credentials (gitignored)
- **bmad/bmm/config.yaml** - BMAD Method configuration

### Data Files (Temporary)
- **brand_pages_count.json** - Pagination metadata
- **brands.txt** - Product URL list
- **products.json** - Scraped product data

### Logs
- **index.log** - Execution logs

---

## Architecture at a Glance

```
┌──────────────────────────────────────────────────────────┐
│                   index.py (Orchestrator)                 │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ BRAND_SCHEDULE = {                                   │ │
│  │   'Monday': [brand_urls...],                        │ │
│  │   'Tuesday': [brand_urls...],                       │ │
│  │   ...                                                │ │
│  │ }                                                     │ │
│  └─────────────────────────────────────────────────────┘ │
└────────┬─────────────────────────────────────────────────┘
         │
         ├──► Step1: Detect Pagination
         │    └─► brand_pages_count.json
         │
         ├──► Step2: Extract URLs
         │    └─► brands.txt
         │
         ├──► Step3: Scrape Products
         │    └─► products.json
         │
         ├──► Step4: Store in Supabase
         │    └─► PostgreSQL Database
         │
         └──► Step5: Cleanup Temp Files
```

---

## Data Flow

```
BBQGuys.com
    ↓ (HTTP Requests)
Step1: Pagination Detection
    ↓ (JSON)
Step2: URL Extraction
    ↓ (Text File)
Step3: Product Scraping
    ↓ (JSON)
Step4: Database Storage
    ↓ (SQL)
Supabase PostgreSQL
    ↓ (Cleanup)
Step5: Delete Temp Files
```

---

## Common Tasks

### Running the Full Pipeline
```bash
python3 index.py
```

### Running Individual Steps
```bash
python3 Step1.py "brand_url1,brand_url2"
python3 Step2.py "brand_url1,brand_url2"
python3 Step3.py "brand_url1,brand_url2"
python3 Step4.py "brand_url1,brand_url2"
python3 Step5.py "brand_url1,brand_url2"
```

### Viewing Logs
```bash
tail -f index.log           # Live tail
tail -100 index.log         # Last 100 lines
grep "ERROR" index.log      # Search errors
```

### Checking Database
```sql
-- In Supabase SQL Editor
SELECT COUNT(*) FROM scrapped_products;
SELECT brand, COUNT(*) FROM scrapped_products GROUP BY brand;
```

---

## Troubleshooting Quick Reference

| Issue | Likely Cause | Solution |
|-------|-------------|----------|
| ModuleNotFoundError | Dependencies not installed | `pip install -r requirements.txt` |
| Supabase connection error | Missing/invalid .env | Check `.env` credentials |
| Empty results | Website structure changed | Update CSS selectors in Step3.py |
| Database insert failures | Schema mismatch | Verify table structure matches Step4.py |
| Script hangs | Network timeout | Check timeouts, add max retries |

---

## Documentation Scope

### What's Included
- ✅ Project structure and organization
- ✅ Architecture and design patterns
- ✅ Setup and configuration instructions
- ✅ Code file descriptions
- ✅ Data flow and processing steps
- ✅ Common tasks and troubleshooting

### What's Not Included (Quick Scan Limitations)
- ⏸️ Detailed API documentation
- ⏸️ Line-by-line code analysis
- ⏸️ Test coverage details
- ⏸️ Performance benchmarks
- ⏸️ Deployment configurations

**Note:** This documentation was generated with a Quick Scan (pattern-based analysis). For more detailed documentation, run the `document-project` workflow with Deep or Exhaustive scan level.

---

## Next Steps for Your Light Version

Based on your goal to create a **simplified scraper that only stores products in JSON**, here's what you should focus on:

### Recommended Approach

1. **Keep from current implementation:**
   - `Step1.py` - Pagination detection (essential)
   - `Step2.py` - URL extraction (essential)
   - `Step3.py` - Product scraping (modify to save JSON directly)

2. **Remove/Skip:**
   - `Step4.py` - Supabase upload (not needed)
   - `Step5.py` - Cleanup (not needed if you want to keep JSON)
   - `index.py` - Orchestrator (simplify or remove)

3. **Simplify:**
   - Create single entry script that runs Steps 1-3 only
   - Remove database dependencies from `requirements.txt`
   - Keep final `products.json` as the end result

### Sample Light Version Script

```python
#!/usr/bin/env python3
"""
Light BBQ Scraper - Simple version that outputs products.json
"""
import sys
from Step1 import PageCountExtractor
from Step2 import AllURLsExtractor
from Step3 import WebScraper

def main():
    if len(sys.argv) < 2:
        print("Usage: python light_scraper.py <brand_url>")
        sys.exit(1)

    brand_url = sys.argv[1]

    # Step 1: Get pagination
    print("Step 1: Detecting pagination...")
    # [pagination code]

    # Step 2: Get all URLs
    print("Step 2: Extracting product URLs...")
    # [URL extraction code]

    # Step 3: Scrape products
    print("Step 3: Scraping products...")
    # [scraping code]

    print(f"✅ Complete! Products saved to products.json")

if __name__ == "__main__":
    main()
```

---

## Support & Resources

### Documentation
- This index - Start here
- Individual docs linked above - Deep dives
- `index.log` - Execution history

### External Resources
- [Python Documentation](https://docs.python.org)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Supabase Documentation](https://supabase.com/docs)
- [Requests Documentation](https://docs.python-requests.org)

### BMAD Method
- **Workflow Status:** Check `bmad/output/bmm-workflow-status.yaml`
- **Next Step:** Run brainstorming workflow, then create tech-spec for the light version

---

## Document Metadata

- **Generated By:** BMAD Document Project Workflow
- **Scan Type:** Quick Scan (pattern-based, no deep file reading)
- **Scan Date:** 2025-11-10
- **Project Root:** `/Users/diego/Desktop/badassbbqs-scrapper`
- **Output Folder:** `bmad/output/`
- **Workflow Version:** 1.2.0

---

**Ready to proceed with your light version? The next workflow step is:**
- **Workflow:** Brainstorming (optional)
- **Then:** Tech-Spec creation for the simplified scraper
- **Agent:** Load PM agent and run `/bmad:bmm:workflows:brainstorm-project` or `/bmad:bmm:workflows:tech-spec`
