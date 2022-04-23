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