# -*- coding: utf-8 -*-
"""
@author: binit_gajera
"""

from load_data import Init_MIPS
from pprint import pprint as pp
from prettytable import PrettyTable
    
class Instructions:
    def __init__(self, instruction, config):
        self.IF = 0
        self.ID = 0
        self.EX = 0
        self.WB = 0
        self.RAW = 'N'
        self.WAR = 'N'
        self.WAW = 'N'
        self.Struct = 'N'
        self.stat = 0
        self.name = instruction[0]
        if len(instruction)>1:
            self.op1 = instruction[1]
            self.op2 = instruction[2]
            self.op3 = None if len(instruction[1:]) == 2 else instruction[3]
        else:
            self.op1 = None
            self.op2 = None
            self.op3 = None
        if self.name in ["HLT", "J"]:
            self.cycles = 0
            self.pip = None
        elif self.name in ["BEQ", "BNE"]:
            self.cycles = 0
            self.pip = None
        elif self.name in ["DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:
            self.cycles = 2
            self.pip = None
        elif self.name in ["LW", "SW", "L.D", "S.D"]:
            self.cycles = 1 + config["MEM"]
            self.pip = None
        elif self.name in ["ADD.D", "SUB.D"]:
            self.cycles = config["ADD"][0]
            self.pip = config["ADD"][1]
        elif self.name in ["MUL.D"]:
            self.cycles = config["MULT"][0]
            self.pip = config["MULT"][1]
        elif self.name in ["DIV.D"]:
            self.cycles = config["DIV"][0]
            self.pip = config["DIV"][1]
            
class Processor:
    def __init__(self, instructions):
        self.incomplete = True
        self.IFbusy, self.IDbusy, self.EXbusy, self.MEMbusy, self.WBbusy = 0, 0, 0, 0, 0
        self.reg_stat = dict()
        self.IU, self.ADD, self.MULT, self.DIV = 0, 0, 0, 0
        self.run(instructions)
                
    def run(self, instructions):
        idx = len(instructions)
        i = 0
        while i<idx:
            for inst in instructions:
                pass
            i+=1

def print_table(inst, b):
    x = PrettyTable()

    x.field_names = ["Instruction","FT", "ID", "EX", "WB", "RAW", "WAR", "WAW", "Struct"]
    
    for i, el in enumerate(instructionObjs):
        if len(b[i]) == 1:
            tmp = b[i][0]
        elif len(b[i]) == 3:
            tmp = b[i][0]+" "+b[i][1]+", "+b[i][2]
        else:
            tmp = b[i][0]+" "+b[i][1]+", "+b[i][2]+", "+b[i][3]
        x.add_row([tmp,el.IF, el.ID, el.EX, el.WB, el.RAW, el.WAR, el.WAW, el.Struct])
        
    return x

if __name__ == "__main__" :
    init_mips = Init_MIPS("./config.txt", "./inst.txt", "./data.txt", "./reg.txt")
    d = init_mips.config_dict
    b = init_mips.instructions
    instructionObjs = list()
    for el in init_mips.instructions:
        instructionObjs.append(Instructions(el, d))
    mips = Processor(instructionObjs)
    
    print(print_table(instructionObjs, b))
    