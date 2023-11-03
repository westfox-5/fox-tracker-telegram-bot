import logging
import requests
from bs4 import BeautifulSoup, ResultSet
from scrapers.base_scraper import BaseScraper

class UnieuroScraper(BaseScraper):
	__title_class =  "pdp-right__title"
	__price_class =  "pdp-right__price"
	__available_class = "product-availability"
	
	def __init__(self, urls: list[str]):
		super().__init__(urls)

	def scrape(self, url: str):
		result = {"title": "", "price": "", "available": False}

		response = requests.get(url)
		if response.status_code == 200:
			soup = BaseScraper.wrap(response.text)

			titleElems = BaseScraper.wrap(soup.find_all(class_=self.__title_class)).find_all("span")
			result["title"] = ''.join([BaseScraper.wrap(title).text for title in titleElems])

			priceElems = BaseScraper.wrap(soup.find_all(class_=self.__price_class)).find_all("span")
			result["price"] = ''.join([BaseScraper.wrap(price).text for price in priceElems])

			availableElems = BaseScraper.wrap(soup.find_all(class_=self.__available_class)).find_all("span", class_="message")
			availableStr = ''.join(set([BaseScraper.wrap(available).text for available in availableElems]))
			result["available"] = True if availableStr=="Disponibile" else False

		else:
			print(f"Errore nella richiesta HTTP: {response.status_code}")

		return result
