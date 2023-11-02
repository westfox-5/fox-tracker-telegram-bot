import os
import logging
import schedule
import time
from dotenv import load_dotenv 

from telegram_bot import TelegramBot
from scrapers.unieuro_scraper import UnieuroScraper

load_dotenv()

# init logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# init bot
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# init user whitelist
USERS_WHITELIST = os.getenv('USERS_WHITELIST')
users_whitelist = str(USERS_WHITELIST).split(',')

UNIEURO_URLS = os.getenv('UNIEURO_URLS')
unieuro_urls = str(UNIEURO_URLS).split(',')

bot = TelegramBot(token=TELEGRAM_BOT_TOKEN, users_whitelist=users_whitelist)

unieuro_scraper = UnieuroScraper(unieuro_urls)

def scrape_all():
    prices = unieuro_scraper.scrape_all()
    bot.update_prices(prices)

def send_prices_to_subscriptions():
    bot.send_prices_to_subscriptions()

def main():
    # start scraping job
    logging.info("Setting up scheduled jobs..")
    for h in range(0, 23):
        schedule.every().day.at(f"{'%02d'%h}:00").do(scrape_all)

    schedule.every().day.at("09:00").do(send_prices_to_subscriptions)

    # do first scraping on start
    logging.info("Performing initial scraping..")
    scrape_all()
    
    # start bot
    logging.info("Starting bot..")
    bot.run()

if __name__ == '__main__':
    main()
