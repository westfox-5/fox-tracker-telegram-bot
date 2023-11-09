import logging
import threading
import schedule
import time
import pytz
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from scrapers.base_scraper import BaseScraper


class TelegramBot:
	__START_MSG = """👋Hi
This bot scrapes the whole internet in order to provide you the best price for products in our catalog.
Use /subscribe to get daily updates on prices
Or simply /prices to get instant price update
Thank you ❤️"""
	__USER_UNAUTHORIZED_MSG = "❌ Sorry, you're not allowed in here! But you can always PET THAT DAWG 🐶"
	__USER_SUBSCRIBED_MSG = """🎉 Well done! You will now receive daily updates on our catalog!
Use /prices to get the price update message
Use /unsubscribe if you wish to stop receive the messages (pls dont 🥺)"""
	__USER_UNSUBSCRIBED_MSG = """😭 Seems like you are leaving th e. 
	You can always hop back in using the /subscribe command.
	Bye bye 👋"""
	__USER_UNAUTHORIZED_ADMIN_MSG = "❌ Sorry, you're not allowed to perform this action!"
	__UPDATING_PRICES_MSG = """⌛ Scraping in process.."""

	def __init__(self, token: str, users_whitelist: list[str], users_admin: list[str], scrapers: list[BaseScraper]):
		self.bot = Bot(token=token)
		self.updater = Updater(bot=self.bot, use_context=True, workers=4)
		self.users_whitelist: list[str] = users_whitelist
		self.users_admin: list[str] = users_admin
		self.subscriptions: dict[int, bool] = {}
		
		self.scrapers: list[BaseScraper] = scrapers

	def run(self) -> None:
		self.updater.dispatcher.add_handler(CommandHandler(['start'], self.__start ))
		self.updater.dispatcher.add_handler(CommandHandler('update', self.__middleware_check_admin))
		self.updater.dispatcher.add_handler(CommandHandler('subscribe', self.__middleware_check_user ))
		self.updater.dispatcher.add_handler(CommandHandler('unsubscribe', self.__middleware_check_user))
		self.updater.dispatcher.add_handler(CommandHandler('prices', self.__middleware_check_user))
		self.updater.dispatcher.add_handler(CommandHandler('unieuro', self.__middleware_check_user))
		self.updater.dispatcher.add_handler(CommandHandler('amazon', self.__middleware_check_user))

		# do first scraping on start
		logging.info("Performing initial scraping..")
		self.update_prices()
		
		scheduler_thread = threading.Thread(target=self.__run_scheduler, args=(0.1,))
		scheduler_thread.start()

		self.updater.start_polling(poll_interval=0.5)
		self.updater.idle()
		
		scheduler_thread.join()

	def __run_scheduler(self, poll_interval):
		logging.info("Setting up scheduled jobs..")
		schedule.every().hour.do(self.update_prices)
		schedule.every().day.at("07:00", tz="Europe/Rome").do(self.send_prices_to_subscriptions)
		
		while True:
			schedule.run_pending()
			time.sleep(poll_interval)

	def __start(self, update: Update, context: CallbackContext):
		chat_id = update._effective_chat.id if update._effective_chat is not None else None
		self.send_message(chat_id, self.__START_MSG) 

	def __call_method_internal(self, update: Update, context: CallbackContext):
		handler_name = f"_TelegramBot__{update.message.text[1::]}"
		if hasattr(self, handler_name) and callable(func := getattr(self, handler_name)):
			func(update, context)

	def __middleware_check_admin(self, update: Update, context: CallbackContext):
		username = update.effective_user.username if update.effective_user is not None else None
		chat_id = update._effective_chat.id if update._effective_chat is not None else None
		if username not in self.users_whitelist and username not in self.users_admin:
			logging.error(f"UNAUTHORIZED for username {username}, chat_id {chat_id}")
			self.send_message(chat_id, self.__USER_UNAUTHORIZED_ADMIN_MSG) 
		else:
			self.__call_method_internal(update, context)

	def __middleware_check_user(self, update: Update, context: CallbackContext):
		username = update.effective_user.username if update.effective_user is not None else None
		chat_id = update._effective_chat.id if update._effective_chat is not None else None
		if username not in self.users_whitelist:
			logging.error(f"UNAUTHORIZED for username {username}, chat_id {chat_id}")
			self.send_message(chat_id, self.__USER_UNAUTHORIZED_MSG) 
		else:
			self.__call_method_internal(update, context)

	def __subscribe(self, update: Update, context: CallbackContext) -> None:
		chat_id = update._effective_chat.id if update._effective_chat is not None else None
		username: str|None = str(update.effective_user.username) if update.effective_user is not None else None

		if chat_id is not None and chat_id not in self.subscriptions: 
			logging.info(f"SUBSCRIBE for username {username}, chat_id {chat_id}")
			self.subscriptions[chat_id] = True
			self.send_message(chat_id, self.__USER_SUBSCRIBED_MSG) 
	
	def __unsubscribe(self, update: Update, context: CallbackContext) -> None:
		chat_id = update._effective_chat.id if update._effective_chat is not None else None
		username: str|None = str(update.effective_user.username) if update.effective_user is not None else None

		if chat_id is not None and chat_id in self.subscriptions: 
			logging.info(f"UNSUBSCRIBE for user {username}, chat_id {chat_id}")
			del self.subscriptions[chat_id]
			self.send_message(chat_id, self.__USER_UNSUBSCRIBED_MSG) 

	def __prices(self, update: Update, context: CallbackContext) -> None:
		chat_id = update._effective_chat.id if update._effective_chat is not None else None
		[ self.send_message(chat_id, scraper.get_prices_msg()) for scraper in self.scrapers ]

	def __update(self, update: Update, context: CallbackContext) -> None:
		chat_id = update._effective_chat.id if update._effective_chat is not None else None
		self.send_message(chat_id, self.__UPDATING_PRICES_MSG)
		self.update_prices()
		[ self.send_message(chat_id, scraper.get_prices_msg()) for scraper in self.scrapers ]

	def __amazon(self, update: Update, context: CallbackContext) -> None:
		chat_id = update._effective_chat.id if update._effective_chat is not None else None
		[ self.send_message(chat_id, scraper.get_prices_msg()) for scraper in self.scrapers if scraper.title == "Amazon" ]

	def __unieuro(self, update: Update, context: CallbackContext) -> None:
		chat_id = update._effective_chat.id if update._effective_chat is not None else None
		[ self.send_message(chat_id, scraper.get_prices_msg()) for scraper in self.scrapers if scraper.title == "Unieuro" ]

	def send_prices_to_subscriptions(self) -> None:
		logging.info(f"Sending the price update message to {len(self.subscriptions)} chats")
		[ [ self.send_message(chat_id, scraper.get_prices_msg()) for chat_id in self.subscriptions ] for scraper in self.scrapers ]

	def send_message(self, chat_id, text) -> None:
		self.bot.send_message(chat_id, text)

	def update_prices(self):
		logging.info("Updating prices..")
		[ scraper.scrape_all() for scraper in self.scrapers]
	
