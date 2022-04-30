from DataParser import DataParser as dp
from DataParser import Group
from DataParser import Faculties

import pandas as pd

import os

parser = dp()
data = parser.GetAllDataByGroup(Group.FromString("МТ6-71Б"))
print(1)
#parser.SaveAllDataByFaculty(Faculties.IU)
