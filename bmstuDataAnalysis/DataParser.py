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
        
    def __CorrectField(self, mark : str):
        if mark == "Зчт":
            return 1
        elif mark == "Отл":
            return 5
        elif mark == "Хор":
            return 4
        elif mark == "Удов":
            return 3
        else:
            return 0

    def __GetGroupData(self, groupLink : str, sessionId : int) -> pd.DataFrame:
            self.chromeDriver.get(groupLink)
            soup = BeautifulSoup(self.chromeDriver.page_source)

            #if there is no data return an empty DF
            splitedContent = ' '.join(soup.find("div", id="content").text.split())
            if splitedContent == 'В этой группе нет студентов' or splitedContent == 'В этой группе нет дисциплин':
                return pd.DataFrame()

            table = soup.find("table", {"class" : "eu-table sortable-table"})
            groupName = soup.find("h1").text.split()[0]

            tHeadValues = table.find("thead").find_all("th") 
            tBodyRows = table.find("tbody").find_all("tr")
        
            subjects = ["#Группы", "#Сессии", "ФИО", "Номер зачетки"] + [th.find("span").text for th in tHeadValues[3:]]
            data = [[groupName, sessionId] + [td.find("span").text for td in row.find_all("td")[1:]] for row in tBodyRows]

            #converting str marks to int
            for i in range(len(data)):
                for j in range(2, len(data[0])):
                    data[i][j] = self.__CorrectField(data[i][j])

            return pd.DataFrame(data, columns=subjects)