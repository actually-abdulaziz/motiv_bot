#!/bin/bash
cd /path/to/project
source .env
python3 bots/channel_scraper.py >> logs/scraper.log 2>&1