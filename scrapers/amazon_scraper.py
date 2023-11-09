from scrapers.base_scraper import BaseScraper

class AmazonScraper(BaseScraper):
	__title_id: str =  "productTitle"
	__price_class: str =  "a-price-whole"
	__available_id: str = "availability"
	
	__available_str: str = "Disponibilità immediata"

	def __init__(self, urls: list[str]):
		super().__init__("Amazon", urls)

	def do_scrape(self, text: str):
		soup = BaseScraper.wrap(text)

		titleElems = BaseScraper.wrap(soup.find_all(id=self.__title_id)).find_all("span")
		title = ''.join([BaseScraper.wrap(title).text for title in titleElems]).strip()

		priceElems = BaseScraper.wrap(soup.find_all(class_=self.__price_class)).find_all("span")
		price = f"€ {BaseScraper.wrap(priceElems[0]).text[:-1]}"

		availableElems = BaseScraper.wrap(soup.find_all(id=self.__available_id)).find_all("span")
		availableStr =  ''.join([BaseScraper.wrap(available).text for available in availableElems]).strip()
		available = True if availableStr==self.__available_str else False

		return title, price, available
