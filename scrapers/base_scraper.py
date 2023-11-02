from bs4 import BeautifulSoup, ResultSet

class BaseScraper:
	def __init__(self, urls: list[str]):
		self.urls = urls

	@classmethod
	def wrap(cls, content: str | list[ResultSet]) -> BeautifulSoup:
		return BeautifulSoup(str(content), "html.parser")