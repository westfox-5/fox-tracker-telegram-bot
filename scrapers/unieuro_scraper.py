import logging
import requests
from bs4 import BeautifulSoup, ResultSet
from scrapers.base_scraper import BaseScraper

class UnieuroScraper(BaseScraper):
	__title_class =  "pdp-right__title"
	__price_class =  "pdp-right__price"
	
	def __init__(self, urls: list[str]):
		super().__init__(urls)

	def scrape(self, url: str):
		result = {"title": "", "price": ""}

		response = requests.get(url)
		if response.status_code == 200:
			soup = BaseScraper.wrap(response.text)

			titleSpans = BaseScraper.wrap(soup.find_all(class_=self.__title_class)).find_all("span")
			result["title"] = ''.join([BaseScraper.wrap(titleSpan).text for titleSpan in titleSpans])

			priceSpans = BaseScraper.wrap(soup.find_all(class_=self.__price_class)).find_all("span")
			result["price"] = ''.join([BaseScraper.wrap(priceSpan).text for priceSpan in priceSpans])
		else:
			print(f"Errore nella richiesta HTTP: {response.status_code}")

		return result
