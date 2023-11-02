import datetime
import logging
from typing import Any
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

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
	Bye bye 👋
"""

	def __init__(self, token, users_whitelist):
		self.bot = Bot(token=token)
		self.updater = Updater(bot=self.bot, use_context=True)
		self.users_whitelist: list[str] = users_whitelist
		self.subscriptions: dict[int, bool] = {}
		self.prices_update_tms = None
		self.prices : dict[str, Any]= {}

	def run(self) -> None:
		self.updater.dispatcher.add_handler(CommandHandler('subscribe', self.__middleware_check_user ))
		self.updater.dispatcher.add_handler(CommandHandler('unsubscribe', self.__middleware_check_user))
		self.updater.dispatcher.add_handler(CommandHandler('prices', self.__middleware_check_user))

		self.updater.start_polling(poll_interval=0.5)
		self.updater.idle()

	def __middleware_check_user(self, update: Update, context: CallbackContext):
		username = update.effective_user.username if update.effective_user is not None else None
		chat_id = update._effective_chat.id if update._effective_chat is not None else None
		if username not in self.users_whitelist:
			logging.error(f"UNAUTHORIZED for user {username}")
			self.send_message(chat_id, self.__USER_UNAUTHORIZED_MSG) 
		else:
			handler_name = f"_TelegramBot__{update.message.text[1::]}"
			print(handler_name)
			if hasattr(self, handler_name) and callable(func := getattr(self, handler_name)):
				print(func)
				func(update, context)

	def __subscribe(self, update: Update, context: CallbackContext) -> None:
		chat_id = update._effective_chat.id if update._effective_chat is not None else None
		username: str|None = str(update.effective_user.username) if update.effective_user is not None else None

		if chat_id is not None and chat_id not in self.subscriptions: 
			logging.info(f"SUBSCRIBE for user {username}")
			self.subscriptions[chat_id] = True
			self.send_message(chat_id, self.__USER_SUBSCRIBED_MSG) 
	
	def __unsubscribe(self, update: Update, context: CallbackContext) -> None:
		chat_id = update._effective_chat.id if update._effective_chat is not None else None
		username: str|None = str(update.effective_user.username) if update.effective_user is not None else None

		if chat_id is not None and chat_id in self.subscriptions: 
			logging.info(f"UNSUBSCRIBE for user {username}")
			del self.subscriptions[chat_id]
			self.send_message(chat_id, self.__USER_UNSUBSCRIBED_MSG) 

	def __prices(self, update: Update, context: CallbackContext) -> None:
		chat_id = update._effective_chat.id if update._effective_chat is not None else None
		username: str|None = str(update.effective_user.username) if update.effective_user is not None else None

		self.send_message(chat_id, self.get_prices_msg())

	def send_prices_to_subscriptions(self) -> None:
		logging.info(f"Sending the price update message to {len(self.subscriptions)} chats")
		[ self.send_message(chat_id, self.get_prices_msg()) for chat_id in self.subscriptions ]

	def send_message(self, chat_id, text) -> None:
		self.bot.send_message(chat_id, text)

	def update_prices(self, prices):
		self.prices_update_tms = datetime.datetime.now()
		self.prices = prices

	def get_prices_msg(self) -> str:
		header = f"Prices update time: 🕑 {self.prices_update_tms.strftime('%H:%M:%S') if self.prices_update_tms is not None else '--' }\n"
		formatted_prices = "\n".join([f"""
✨ {"".join(title)}
{self.prices[title]["url"]}
💸 {self.prices[title]["price"]}""" for title in self.prices.keys()])
		return header + formatted_prices