from enum import Enum
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import re

import os

class Faculties(Enum):
    MT = 'МТ'
    SM = 'СМ'
    IU = 'ИУ'
    IBM = 'ИБМ'
    RK = 'РК'
    RKT = 'РКТ'
    RL = 'РЛ'
    FN = 'ФН'
    E = 'Э'
    UR = 'ЮР'


class Group:
    def __init__(self, faculty : Faculties, departmentNum : int, sessionNumber : int, groupNum : int, isBachelor : bool):
        self.faculty = faculty
        self.departmentNum = departmentNum
        self.sessionNumber = sessionNumber
        self.groupNum = groupNum
        self.isBachelor = isBachelor * 1

    @classmethod
    def FromString(self, group : str):        
        gr = re.split('(\d+)',group)

        faculty = next((f for f in Faculties if f.value == gr[0]), "none")
        if faculty == "none": return None

        department = gr[1]

        if len(gr[3]) == 2: sessionId = gr[3][0]
        else: sessionId = gr[3][0:2]

        groupNum = gr[3][-1]
        isBachelor = gr[-1] == "Б"

        return Group(faculty, department, sessionId, groupNum, isBachelor)


    @property
    def IsBachelor(self):
        return self.isBachelor == 1

    def ToString(self):
        isBac = "Б" * self.IsBachelor
        return '{}{}-{}{}{}'.format(self.faculty.value, self.departmentNum, self.sessionNumber, self.groupNum, isBac)
    

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

    def GetAllDataByGroup(self, gr : Group) -> pd.DataFrame:
        groupDataFrames = []

        remainder = -1
        if int(gr.sessionNumber) % 2 == 0: remainder = 1           
        else: remainder = 0

        suitableLinks = [link for link in self.SessionLinks if int(link.split("=")[-1]) % 2 == remainder]

        for sL in suitableLinks:
            sessionId = int(sL.split("=")[-1])

            allGroupLinks = self.__GetAllGroups(sL)
            group = next((link for link in allGroupLinks if link.text == gr.ToString()), "none")
            if group == "none": continue            
            groupDataFrames.append(self.__GetGroupData(self._mainPage + group.get("href"), sessionId))

        return pd.concat(groupDataFrames)

    def __CorrectField(self, mark : str):
        if mark == "Зчт":
            return True
        elif mark == "Отл":
            return 5.0
        elif mark == "Хор":
            return 4.0
        elif mark == "Удов":
            return 3.0
        elif any(mark == elem for elem in ["Я", "Нзч", "Дк", "НА", "Неуд"]):
            return False
        else:
            return mark

    def __GetGroupData(self, groupLink : str, sessionId : int) -> pd.DataFrame:
            
            self.chromeDriver.get(groupLink)          
            soup = BeautifulSoup(self.chromeDriver.page_source)

            #if there is no data return an empty DF
            if not soup.find("div", id="content"): return pd.DataFrame()
            splitedContent = ' '.join(soup.find("div", id="content").text.split())
            if splitedContent == 'В этой группе нет студентов' or splitedContent == 'В этой группе нет дисциплин':
                return pd.DataFrame()

            table = soup.find("table", {"class" : "eu-table sortable-table"})
            groupName = soup.find("h1").text.split()[0]

            tHeadValues = table.find("thead").find_all("th") 
            tBodyRows = table.find("tbody").find_all("tr")
        
            subjects = ["#Группы", "#Сессии", "ФИО", "Номер зачетки"] + [th.find("span").text for th in tHeadValues[3:]]
            data = [[groupName, sessionId] + [next((t.find("span").text for t in [td] if t.find("span")), None) or 
                                              None for \
                                                    td in row.find_all("td")[1:]] \
                                                                    for row in tBodyRows]

            #converting str marks to int
            for i in range(len(data)):
                for j in range(2, len(data[0])):
                    data[i][j] = self.__CorrectField(data[i][j])

            return pd.DataFrame(data, columns=subjects)

    def SaveAllDataByFaculty(self, faculty : Faculties):

        savePath = "C:\\Users\\Wawe\\PycharmProjects\\dataAnalysis\\bmstuDataAnalysis\\data"
        facultyPath = os.path.join(savePath, faculty.value)        

        if not os.path.exists(facultyPath): os.makedirs(facultyPath) 

        log = "{}\\log.txt".format(facultyPath)
        
        lastLink = ""
        start = -1

        if os.stat(log).st_size != 0:
            with open(log, "r") as f:
                for link in f:
                    lastLink = link
                    start = self.SessionLinks.index(lastLink.strip())
        else: start = 0
        
        for sL in self.SessionLinks[start:]:
            sessionId = int(sL.split("=")[-1])            

            self.chromeDriver.get(sL)
            soup = BeautifulSoup(self.chromeDriver.page_source)

            faculties = [li for li in soup.find("span", id="left-column").find_all("li") if li.find("b")]
            facultyLi = next((f for f in faculties if f.text.split()[0] == faculty.value), "none")

            facultyGroups = [a for a in facultyLi.find_all("a")]

            for gr in facultyGroups:
                group = Group.FromString(gr.text)
                groupPath = "{}\\{}\\".format(facultyPath, group.ToString())

                if not os.path.exists(groupPath):
                    os.makedirs(groupPath) 

                grSessionPath = "{}{}.txt".format(groupPath, str(sessionId))
                if not os.path.exists(grSessionPath):
                    data = self.__GetGroupData(self._mainPage + gr.get("href"), sessionId)
                    if data.empty: continue
                    data.to_csv(grSessionPath, sep="\t", encoding="utf-8")

            with open(log, "a") as f:
                f.write("{}\n".format(sL))


