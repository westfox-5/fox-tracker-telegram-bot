import logging
import requests
import time
import pytz
from datetime import datetime, timedelta
from abc import abstractmethod
from bs4 import BeautifulSoup, ResultSet

class BaseScraper:
	__MAX_RETRY = 5

	__TIMEZONE = pytz.timezone('Europe/Rome')

	def __init__(self, title: str, urls: list[str]):
		self.title = title
		self.urls = urls
		self.prices : dict[str, dict[str, str]] = {}
		self.prices_update_tms: datetime | None  = None
	
	@classmethod
	def wrap(cls, content: str | list[ResultSet]) -> BeautifulSoup:
		return BeautifulSoup(str(content), "html.parser")
	
	@abstractmethod
	def do_scrape(self, text: str) -> (str, str, str): # type: ignore
		pass

	def scrape(self, url: str) -> dict[str, str] | None:
		result = {"title": "", "price": "", "available": False}

		max_retry = self.__MAX_RETRY
		while max_retry > 0:
			response = requests.get(url)
			if response.status_code == 200:
				title, price, available = self.do_scrape(response.text)
				result["title"] = title
				result["price"] = price
				result["available"] = available
				return result
			else:
				logging.error(f"Error in HTTP request: {response.status_code}")
				time.sleep(3)
				max_retry = max_retry - 1

		logging.error(f"Error while scraping url {url}: max retries exceeded")
		return None
	
	def scrape_all(self):
		new_prices = {}
		for url in self.urls:
			logging.info(f"Scraping url '{url}'")
			result = self.scrape(url)
			if result is None:
				return
			new_prices[result["title"]] = {"url": url, "price": result["price"], "available": result["available"]}
		
		# only update if all succeded
		self.prices = new_prices
		self.prices_update_tms = datetime.now(self.__TIMEZONE)
	
	def get_prices_msg(self) -> str:
		header = f"""📣 {self.title} 
		Last update: 🕑 """
		if self.prices_update_tms is not None:
			diff = datetime.now(self.__TIMEZONE) - self.prices_update_tms
			header = header + f"{'Today' if diff.days == 0 else 'Yesterday' if diff.days == 1 else self.prices_update_tms.strftime('%A').title()} at {self.prices_update_tms.strftime('%H:%M')}\n"""
		else:
			header = header + "NA"
			
		msg = "\n".join([
			f"""✨ {title} {"🟢" if self.prices[title]['available'] else "🔴"}
			{self.prices[title]['url']}
			💸 {self.prices[title]['price']}
			""" for title in self.prices ])
		return f"{header}\n{msg}"