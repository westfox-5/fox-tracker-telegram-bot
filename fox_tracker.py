import logging
from environs import Env
from telegram_bot import TelegramBot
from scrapers.unieuro_scraper import UnieuroScraper

env = Env()
env.read_env()

# init logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# init bot
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')

# init users ACL
USERS_WHITELIST = env.list('USERS_WHITELIST')
USERS_ADMIN = env.list('USERS_ADMIN')

UNIEURO_URLS = env.list('UNIEURO_URLS')

scrapers = []
scrapers.append(UnieuroScraper(UNIEURO_URLS))

bot = TelegramBot(token=TELEGRAM_BOT_TOKEN, users_whitelist=USERS_WHITELIST, users_admin=USERS_ADMIN, scrapers=scrapers)

def update_prices():
    bot.update_prices()

def send_prices_to_subscriptions():
    bot.send_prices_to_subscriptions()

def main():
    # start bot
    logging.info("Starting bot..")
    bot.run()

if __name__ == '__main__':
    main()
