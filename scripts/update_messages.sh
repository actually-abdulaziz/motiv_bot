#!/bin/bash
cd C:\Users\iamkr\Desktop\creative\Новая папка\motiv_bot
source .env
python3 bots/channel_scraper.py >> logs/scraper.log 2>&1