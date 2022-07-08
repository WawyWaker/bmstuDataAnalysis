from enum import Enum
import re


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
