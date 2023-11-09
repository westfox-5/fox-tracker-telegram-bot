import logging
import time
from scrapers.base_scraper import BaseScraper

class UnieuroScraper(BaseScraper):
	__title_class: str =  "pdp-right__title"
	__price_class: str =  "pdp-right__price"
	__available_class: str = "product-availability"
	
	__available_str: str = "Disponibile"

	def __init__(self, urls: list[str]):
		super().__init__("Unieuro", urls)

	def do_scrape(self, text: str):
		soup = BaseScraper.wrap(text)

		titleElems = BaseScraper.wrap(soup.find_all(class_=self.__title_class)).find_all("span")
		title = ''.join([BaseScraper.wrap(title).text for title in titleElems])

		priceElems = BaseScraper.wrap(soup.find_all(class_=self.__price_class)).find_all("span")
		price = ''.join([BaseScraper.wrap(price).text for price in priceElems])

		availableElems = BaseScraper.wrap(soup.find_all(class_=self.__available_class)).find_all("span", class_="message")
		availableStr = ''.join(set([BaseScraper.wrap(available).text for available in availableElems]))
		available = True if availableStr==self.__available_str else False

		return title, price, available
