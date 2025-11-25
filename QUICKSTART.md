# Quick Start Guide

## Local Testing (Before Railway)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` and set:**
   - `TEST_MODE=2` (for quick testing)
   - `USE_SUPABASE=false` (to test without database)

4. **Run the scraper:**
   ```bash
   python light/light_scraper.py
   ```

5. **Check output:**
   - JSON file: `light/products.json`
   - Logs will show progress

## Deploy to Railway (Production)

Follow the detailed guide in `RAILWAY_DEPLOY.md`

### Quick Railway Setup:

1. **Set up Supabase** (create database table)
2. **Push to GitHub**
3. **Deploy on Railway** (connect GitHub repo)
4. **Set environment variables** in Railway dashboard
5. **Enable cron schedule:** `0 0 * * *`

## Important Files

- `light/light_scraper.py` - Main scraper script
- `light/url_list.json` - List of brands to scrape
- `requirements.txt` - Python dependencies
- `.env` - Local environment variables (not committed)
- `RAILWAY_DEPLOY.md` - Detailed deployment guide

## Environment Variables Explained

- **TEST_MODE**:
  - `0` = Full scrape (all products)
  - `1` = Quick test (1 product from 1 brand)
  - `2` = Standard test (2 products per brand)

- **USE_SUPABASE**: `true` or `false` - Enable database storage

- **SUPABASE_URL**: Your Supabase project URL

- **SUPABASE_KEY**: Your Supabase anon/public key

## Troubleshooting

**"ModuleNotFoundError"**: Run `pip install -r requirements.txt`

**"url_list.json not found"**: Make sure you're in the project root directory

**Supabase errors**: Check your credentials and table exists

**Rate limiting**: Increase delay in scraper or reduce TEST_MODE
