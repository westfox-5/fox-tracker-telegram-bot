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
    schedule.every(1).hour.do(scrape_all)
    schedule.every(1).day.at("07:00").do(scrape_all)

    # do first scraping on start
    logging.info("Performing initial scraping..")
    scrape_all()
    
    # start bot
    logging.info("Starting bot..")
    bot.run()
    
    while True:
        schedule.run_pending()
        time.sleep(0.1)
if __name__ == '__main__':
    main()
