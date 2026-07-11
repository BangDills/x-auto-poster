#!/bin/bash
# Navigate to the project directory
cd /root/sosmedauto/x-auto-poster || exit 1

# Export environment variables for cron
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export HOME="/root"

# Run scraping and log output
echo "=== SCRAPING RUN AT $(date) ===" >> scrape.log
./venv/bin/python -u scrape.py >> scrape.log 2>&1
echo "=== SCRAPING FINISHED ===" >> scrape.log
