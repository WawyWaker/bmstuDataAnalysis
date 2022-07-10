from enum import Enum
import re

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


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
    faculty: Faculties
    dep_id: int
    ses_id: int
    gr_num: int
    is_bac: bool
    is_sp: bool
    is_phd: bool

    def __init__(self, faculty: Faculties, dep_id: int, ses_id: int, gr_num: int,
                 is_bac: bool, is_sp: bool, is_phd: bool):
        self.faculty = faculty
        self.dep_id = dep_id
        self.ses_id = ses_id
        self.gr_num = gr_num
        self.is_bac = is_bac
        self.is_sp = is_sp
        self.is_phd = is_phd

    @classmethod
    def from_string(cls, group: str):
        gr = re.split('(\d+)', group)

        faculty = next((f for f in Faculties if f.value == gr[0]), None)
        if not faculty: return None

        department = gr[1]

        if len(gr[3]) == 2: ses_id = gr[3][0]
        else: ses_id = gr[3][0:2]

        gr_num = gr[3][-1]
        is_bac = gr[-1] == "Б"
        is_phd = gr[-1] == "А"
        is_sp = not is_bac and not is_phd

        return Group(faculty, int(department), int(ses_id), int(gr_num), is_bac, is_sp, is_phd)

    def to_string(self) -> str:
        postfix = self.is_bac * "Б" + self.is_phd * "А"
        return f'{self.faculty.value}{self.dep_id}-{self.ses_id}{self.gr_num}{postfix}'


def parse_use() -> pd.DataFrame:
    driver = webdriver.Chrome()
    driver.get("https://bmstu.ru/bachelor/previous-points")
    soup = BeautifulSoup(driver.page_source)

    table = soup.find("table", {"class": "_1Ii2q _24JIz _2dfKK"})
    table_head = table.find("thead").find_all("tr")
    table_body = table.find("tbody").find_all("tr")

    columns = [th.text for th in table_head[0].find_all("th")]
    values = [[td.text for td in tr.contents] for tr in table_body]

    data_rows = [row[:5] + row[5:][0::2] for row in values]

    driver.close()
    return pd.DataFrame(data=data_rows, columns=columns)
