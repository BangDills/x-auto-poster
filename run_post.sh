#!/bin/bash
# Navigate to the project directory
cd /root/sosmedauto/x-auto-poster || exit 1

# Export environment variables for cron
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export HOME="/root"

# Run posting and log output
echo "=== POSTING RUN AT $(date) ===" >> post.log
./venv/bin/python -u post.py >> post.log 2>&1
echo "=== POSTING FINISHED ===" >> post.log
