# Railway Deployment Guide

## Prerequisites
1. Railway account (sign up at https://railway.app)
2. Supabase account (sign up at https://supabase.com)
3. Git repository pushed to GitHub

## Step 1: Set up Supabase

1. Create a new project in Supabase
2. Go to Table Editor and create a table named `products` with the following structure:

```sql
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  url TEXT UNIQUE,
  "Title" TEXT,
  "Price" NUMERIC,
  brand TEXT,
  "Image" TEXT,
  "Other_image" JSONB,
  "Id" TEXT,
  "Model" TEXT,
  category JSONB,
  "Description" TEXT,
  "Specifications" JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

3. Get your Supabase URL and anon key from Settings > API

## Step 2: Deploy to Railway

### Option A: Deploy from GitHub (Recommended)

1. Push your code to GitHub
2. Go to https://railway.app/new
3. Click "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect your Python app

### Option B: Deploy using Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

## Step 3: Configure Environment Variables

In Railway dashboard, go to your project > Variables and add:

```
TEST_MODE=0
USE_SUPABASE=true
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
```

## Step 4: Set up Cron Job

Railway supports cron jobs through their cron service:

1. In Railway dashboard, click "+ New Service"
2. Select "Cron Job"
3. Set schedule: `0 0 * * *` (runs daily at midnight UTC)
4. Point to your existing service
5. Or set environment variable: `RAILWAY_CRON_SCHEDULE=0 0 * * *`

## Step 5: Monitor Logs

```bash
# Using Railway CLI
railway logs

# Or view in Railway dashboard > Deployments > Logs
```

## Cron Schedule Examples

```
# Every day at midnight UTC
0 0 * * *

# Every day at 2 AM UTC
0 2 * * *

# Every 12 hours
0 */12 * * *

# Every Monday at 9 AM UTC
0 9 * * 1

# Every hour
0 * * * *
```

## Testing Before Production

1. Set `TEST_MODE=2` to scrape only 2 products per brand
2. Check logs to ensure scraping works
3. Verify data appears in Supabase
4. Once confirmed, set `TEST_MODE=0` for full scrape

## Troubleshooting

### Scraper times out
- Railway has generous timeouts, but if needed, consider:
  - Reducing number of brands in url_list.json
  - Increasing delay between requests
  - Running multiple smaller cron jobs for different brand groups

### Supabase connection fails
- Verify SUPABASE_URL and SUPABASE_KEY are correct
- Check Supabase project is active
- Ensure table 'products' exists with correct schema

### File not found errors
- Ensure `url_list.json` is in the `light/` directory
- Check Railway build logs for file structure

## Cost Estimation

Railway pricing (as of 2024):
- Hobby plan: $5/month (500 hours execution time)
- Pro plan: $20/month (more resources)

Running daily for ~1-2 hours = ~30-60 hours/month (well within Hobby plan)

Supabase:
- Free tier: Up to 500MB database, 2GB bandwidth
- Should be sufficient for this use case
