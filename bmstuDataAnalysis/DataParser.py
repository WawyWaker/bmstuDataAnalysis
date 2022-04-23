from enum import Enum
import pandas as pd
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

        self._mainPage = 'https://eu.bmstu.ru'
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

    def __GetAllGroups(self, sessionLink : str):
        self.chromeDriver.get(sessionLink)
        soup = BeautifulSoup(self.chromeDriver.page_source)
        filteredLis = list(filter(lambda li: li.find("b"), soup.find("ul", id="session-structure").find_all("li")))

        allGroupLinks = [li.find_all("a") for li in filteredLis]
        return [li for subLi in allGroupLinks for li in subLi]
        
