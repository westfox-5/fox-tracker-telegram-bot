import logging
from abc import abstractmethod
from bs4 import BeautifulSoup, ResultSet

class BaseScraper:
	def __init__(self, urls: list[str]):
		self.urls = urls

	@classmethod
	def wrap(cls, content: str | list[ResultSet]) -> BeautifulSoup:
		return BeautifulSoup(str(content), "html.parser")
	
	@abstractmethod
	def scrape(self, url: str) -> dict[str, str]:
		pass
	
	def scrape_all(self):
		prices = {}
		for url in self.urls:
			logging.info(f"Scraping url '{url}'")
			result = self.scrape(url)
			prices[result["title"]] = {"url": url, "price": result["price"]}
		
		return prices