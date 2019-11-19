# -*- coding: utf-8 -*-
"""
@author: binit_gajera
"""

from load_data import Init_MIPS
from pprint import pprint as pp

IF, ID, EX, WB = 0, 0, 0, 0
RAW, WAR, WAW, Struct = "N", "N", "N", "N"



if __name__ == "__main__" :
    init_mips = Init_MIPS("./config.txt", "./inst.txt", "./data.txt", "./reg.txt")
    pp(init_mips.instructions)