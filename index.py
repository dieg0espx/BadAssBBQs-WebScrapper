#!/usr/bin/env python3
"""
index.py: Orchestrates daily scraping, processing, cleaning, uploading, and logging for a rotating set of brands.
"""

import datetime
import logging
import subprocess
import sys

# Define brand groups for each day (example brands, replace with your actual brands)
BRAND_SCHEDULE = {
    'Monday': [
        'https://www.bbqguys.com/d/17994/brands/alfresco-grills/shop-all',
        'https://www.bbqguys.com/d/19795/brands/american-made-grills/shop-all',
        'https://www.bbqguys.com/d/13928/brands/american-outdoor-grill/shop-all',
        'https://www.bbqguys.com/d/20399/brands/artisan-grills/shop-all'
    ],
    'Tuesday': [
        'https://www.bbqguys.com/d/24062/brands/blackstone-grills/shop-all',
        'https://www.bbqguys.com/d/17960/brands/blaze-grills/shop-all',
        'https://www.bbqguys.com/d/25317/brands/breeo/shop-all',
        'https://www.bbqguys.com/d/20880/brands/bromic-heating/shop-all'
    ],
    'Wednesday': [
        # 'https://www.bbqguys.com/d/20396/brands/coyote-outdoor-living/shop-all',
        # 'https://www.bbqguys.com/d/518/brands/delta-heat/shop-all',
        # 'https://www.bbqguys.com/d/17978/brands/fire-magic-grills/shop-all',
        'https://www.bbqguys.com/d/22965/brands/fontana-forni/shop-all'
    ],
    'Thursday': [
        'https://www.bbqguys.com/d/24176/brands/green-mountain-grills/shop-all',
        'https://www.bbqguys.com/d/17946/brands/napoleon-shop-all',
        'https://www.bbqguys.com/d/10469/brands/twin-eagles-grills/shop-all',
        'https://www.bbqguys.com/d/18064/brands/primo-ceramic-grills/shop-all'
    ],
    'Friday': [
        'https://www.bbqguys.com/d/19816/brands/summerset-grills/shop-all',
        'https://www.bbqguys.com/d/23678/brands/mont-alpi/shop-all',
        'https://www.bbqguys.com/d/21363/brands/american-fyre-designs/shop-all',
        'https://www.bbqguys.com/d/22449/outdoor-living/fire-pits/the-outdoor-plus/top-fires'
    ],
    'Saturday':  ['https://www.bbqguys.com/d/25428/brands/ledge-lounger/shop-all'],
    'Sunday':    [],
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('index.log'), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def get_today_brands():
    today = datetime.datetime.now().strftime('%A')
    brands = BRAND_SCHEDULE.get(today, [])
    return today, brands

def run_step(script, brands):
    """Run a step script with the selected brands as argument."""
    try:
        logger.info(f"Running {script} for brands: {brands}")
        # Pass brands as a comma-separated string argument
        result = subprocess.run([
            sys.executable, script, ','.join(brands)
        ], capture_output=True, text=True)
        logger.info(f"{script} output:\n{result.stdout}")
        if result.stderr:
            logger.error(f"{script} error:\n{result.stderr}")
        if result.returncode != 0:
            logger.error(f"{script} exited with code {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Failed to run {script}: {e}")
        return False

def main():
    today, brands = get_today_brands()
    if not brands:
        logger.info(f"It's {today}. No brands scheduled. Taking the day off!")
        return
    logger.info(f"Today is {today}. Brands to process: {brands}")
    steps = ['Step1.py', 'Step2.py', 'Step3.py', 'Step4.py', 'Step5.py']
    for step in steps:
        success = run_step(step, brands)
        if not success:
            logger.error(f"Aborting pipeline due to failure in {step}.")
            break
    logger.info(f"Pipeline for {today} completed.")

if __name__ == "__main__":
    main() 