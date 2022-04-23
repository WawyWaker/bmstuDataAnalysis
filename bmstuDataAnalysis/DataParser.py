from enum import Enum

from bs4 import BeautifulSoup
from selenium import webdriver
import time


class Groups(Enum):
    MT = 'МТ'
    SM = 'СМ'
    IU = 'ИУ'


class DataParser:

    def __init__(self):
        self.chromeDriver = webdriver.Chrome()

        self._mainPage = 'https://eu.bmstu.ru/'
        self._sessionLinks = []

        self.chromeDriver.get(self._mainPage)
        time.sleep(10)

    @property
    def SessionLinks(self):
        if len(self._sessionLinks) == 0:
            self.chromeDriver.get('https://eu.bmstu.ru/modules/session/')
            soup = BeautifulSoup(self.chromeDriver.page_source)
            self._sessionLinks = [self._mainPage + a.get("href") for a in soup.
                                                                            find("ul", {"class" : "module-menu"}).
                                                                            find_all("a", {"class" : "change-term"})]
            return self._sessionLinks
        else:
            return self._sessionLinks