from DataParser import DataParser as dp
from DataParser import Group
from DataParser import Faculties

parser = dp()

df = parser.GetAllDataByGroup(Group(Faculties.MT, 6, 1, 1, True))

print(1)