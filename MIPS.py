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
        self.iu_cycles = 0
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
            self.iu_cycles = 1
            self.cycles = 1
            self.pip = None
        elif self.name in ["LW", "SW", "L.D", "S.D"]:
            self.iu_cycles = 1
            self.cycles = config["MEM"]
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
    def __init__(self, instructions, reg, data, loops, original_inst, config):
        self.incomplete = True
        self.IFbusy, self.IDbusy, self.MEMbusy, self.WBbusy = [0, None], [0, None], [0, None], [0, None]
        self.reg_stat = dict()
        self.IU, self.ADD, self.MULT, self.DIV = [0, None], [0, None], [0, None], [0, None]
        self.clock = 0
        self.loops = loops
        self.config = config
        self.or_inst = original_inst
        self.inst_list = instructions
        self.reg = reg
        self.data = data
        self.loops = loops
        self.final = list()
        self.run_loop(0)

    def run_loop(self, idx):          
        tmp, new_loop = self.run(self.inst_list[idx:], self.reg, self.data, self.loops)        
        if new_loop[0]:
            print("Running loop...", new_loop)
            for el in tmp[:-1]:
                self.final.append([el.name, el.op1, el.op2, el.op3, el.IF, el.ID, el.EX, el.WB, el.RAW, el.WAR, el.WAW, el.Struct])            
            for i, k in enumerate(self.or_inst):
                    self.inst_list[i].__init__(k, self.config)            
            self.run_loop(new_loop[1])
        else:
            for el in tmp:
                self.final.append([el.name, el.op1, el.op2, el.op3, el.IF, el.ID, el.EX, el.WB, el.RAW, el.WAR, el.WAW, el.Struct])            
                
    def run(self, instructions, reg, data, loops):
#        idx = len(instructions)
        x = 80
        i = 0
        while i<x:
            self.clock += 1
            NEED_LOOP = [False, None]                        
            for j, inst in enumerate(instructions):                  
                if inst.WB == 0:                           
                    if inst.stat == 0 and not self.IFbusy[0]:
                        if inst.name == "HLT":
                            if NEED_LOOP[0]:
                                inst.IF = self.clock
                                if instructions[j-1].name == "HLT":   
                                    print("Returning loop...", NEED_LOOP, self.clock)
                                    return instructions, NEED_LOOP
                                else:
                                    pass
                            else:
                                inst.IF = self.clock
                                self.IFbusy = [1, j]
                                inst.stat = 1
                        else:                            
                            inst.IF = self.clock
                            inst.stat = 1
                            self.IFbusy = [1, j]
                        
                    elif inst.stat == 1 and not self.IDbusy[0]:
                        if inst.op1 in self.reg_stat.keys() and j != self.reg_stat[inst.op1] and inst.name != "BNE":
                                inst.WAW = "Y"
                                continue                            
                        if inst.name in ["LW", "SW", "L.D", "S.D", "DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:                            
                                self.reg_stat[inst.op1] = j
                                self.IFbusy = [0, None]                        
                                self.IDbusy = [1, j]
                                inst.ID = self.clock    
                                inst.stat = 2
                        elif inst.name in ["ADD.D", "SUB.D", "MUL.D", "DIV.D"]:                            
                            if inst.op2 not in self.reg_stat.keys() and inst.op3 not in self.reg_stat.keys():                                
                                self.IFbusy = [0, None]                        
                                self.IDbusy = [1, j]
                                self.reg_stat[inst.op1] = j
                                inst.ID = self.clock       
                                inst.stat = 2
                            elif (inst.op2 in self.reg_stat.keys() and (j == self.reg_stat.get(inst.op2, None)) or (inst.op3 in self.reg_stat.keys())\
                                  and j == self.reg_stat.get(inst.op3, None)):
                                self.IFbusy = [0, None]                        
                                self.IDbusy = [1, j]                                
                                inst.ID = self.clock       
                                inst.stat = 2
                            else:                                
                                inst.RAW = "Y"
                        elif inst.name == "BNE" and inst.ID == 0:                            
                            if inst.op1 not in self.reg_stat.keys() and inst.op2 not in self.reg_stat.keys():                                
                                self.IFbusy = [0, None]                        
#                                self.IDbusy = [1, j]                                
                                inst.ID = self.clock                                
                                if reg[inst.op1] != reg[inst.op2]:
                                    NEED_LOOP = [True, loops.get(inst.op3)]                                      
                                else:
                                    self.IDbusy = [1, j]
                                    inst.stat = 2
                            else:                                
                                inst.RAW = "Y"
                        elif inst.name == "HLT":
                            if not instructions[j-1].name == "HLT" and inst.ID==0:                            
                                self.IFbusy = [0, None]
                                inst.ID = self.clock
                            
                        
                    elif inst.stat == 2:                                                
                        self.IDbusy = [0, None]
                        if inst.name in ["LW", "SW", "L.D", "S.D", "DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:                            
                            if not self.IU[0] and inst.iu_cycles == 1:
                                self.IU = [1, j]                                 
                                inst.iu_cycles -= 1                                
                            else:                                
                                if self.MEMbusy[0] == 0 or self.MEMbusy[1] == j:                                    
                                    if self.MEMbusy[0] == 0:
                                        self.IU = [0, None]
                                    self.MEMbusy = [1, j]                                    
                                    inst.cycles -= 1
                                    if inst.cycles == 0:                                        
                                        inst.EX = self.clock
                                        inst.stat = 3                                    
                                else:
                                    inst.Struct = "Y"
                        elif inst.name in ["ADD.D", "SUB.D"]:
                            if not inst.pip:                                 
                                if self.ADD[0] == 0 or self.ADD[1] == j:                                    
                                    print(self.ADD , j, inst.cycles, self.clock)
                                    self.ADD = [1, j]                                    
                                    inst.cycles -= 1
                                    if inst.cycles == 0:
                                        inst.EX = self.clock
                                        inst.stat = 3
                            else:
                                inst.cycles -= 1
                                if inst.cycles == 0:
                                    inst.EX = self.clock
                                    inst.stat = 3
                        elif inst.name == "MUL.D":
                            if not inst.pip:
                                if self.MULT[0] == 0 or self.MULT[1] == j:
                                    self.MULT = [1, j]
                                    inst.cycles -= 1
                                    if inst.cycles == 0:
                                        inst.EX = self.clock
                                        inst.stat = 3
                            else:
                                inst.cycles -= 1
                                if inst.cycles == 0:
                                    inst.EX = self.clock
                                    inst.stat = 3
                        elif inst.name == "DIV.D":
                            if not inst.pip:
                                if self.DIV[0] == 0 or self.DIV[1] == j:
                                    self.DIV = [1, j]
                                    inst.cycles -= 1
                                    if inst.cycles == 0:
                                        inst.EX = self.clock
                                        inst.stat = 3
                            else:
                                inst.cycles -= 1
                                if inst.cycles == 0:
                                    inst.EX = self.clock
                                    inst.stat = 3

                    elif inst.stat == 3:
                        if not self.WBbusy[0]:
                            if inst.name in ["LW", "SW", "L.D", "S.D", "DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:                            
                                if inst.name == "DSUBI":
                                    print("Freeing MEM at", self.clock)
                                self.MEMbusy = [0, None]
                                inst.WB = self.clock
                                inst.stat = 4
                                self.WBbusy = [1, self.clock]                            
                                del self.reg_stat[inst.op1]
                                if inst.op3 is not None:
                                    if inst.name in ["DADD", "DADDI"]:
                                        if inst.op3 in reg.keys():
                                            #inside DADD
                                            reg[inst.op1] = reg[inst.op2] + reg[inst.op3]
                                        else:
                                            #inside DADDI
                                            reg[inst.op1] = reg[inst.op2] + int(inst.op3)
                                    elif inst.name in ["DSUB", "DSUBI"]:
                                        if inst.op3 in reg.keys():
                                            #inside DSUB
                                            reg[inst.op1] = reg[inst.op2] - reg[inst.op3]
                                        else:
                                            #inside DSUBI
                                            reg[inst.op1] = reg[inst.op2] - int(inst.op3)                                
                            elif inst.name in ["ADD.D", "SUB.D"]:
                                self.ADD = [0, None]
                                inst.stat = 4
                                del self.reg_stat[inst.op1]
                                inst.WB = self.clock
                                self.WBbusy = [1, self.clock]
                            elif inst.name == "MUL.D":
                                self.MULT = [0, None]
                                inst.stat = 4
                                del self.reg_stat[inst.op1]
                                inst.WB = self.clock
                                self.WBbusy = [1, self.clock]
                            elif inst.name == "DIV.D":
                                self.DIV = [0, None]
                                del self.reg_stat[inst.op1]
                                inst.stat = 4
                                inst.WB = self.clock
                                self.WBbusy = [1, self.clock]
                        else:
                            if self.clock == self.WBbusy[1]:
                                inst.Struct = "Y"
                            elif self.clock > self.WBbusy[1]:
                                inst.WB = self.clock
                                if inst.name in ["ADD.D", "SUB.D"]:
                                    self.ADD = [0, None]
                                    del self.reg_stat[inst.op1]
                                elif inst.name == "MUL.D":
                                    self.MULT = [0, None]
                                    del self.reg_stat[inst.op1]
                                elif inst.name == "DIV.D":
                                    self.DIV = [0, None]
                                    del self.reg_stat[inst.op1]
                                elif inst.name in ["LW", "SW", "L.D", "S.D", "DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:
                                    self.MEMbusy = [0, None]                                    
                                    del self.reg_stat[inst.op1]
                                self.WBbusy = [1, self.clock]
                                
                                inst.stat = 4
                elif inst.stat == 4:
                    ak = 0 if self.WBbusy[1] == None else self.WBbusy[1]
                    if self.clock > ak:
                        self.WBbusy = [0, None]
#            for k in instructions:                
#                print(k.IF, k.ID, k.EX, k.WB)
#            print("\n")                
            i+=1            
            
        return instructions, NEED_LOOP
        
def print_table(inst):
    x = PrettyTable()
    x.border = False
    x.field_names = ["Instruction","FT", "ID", "EX", "WB", "RAW", "WAR", "WAW", "Struct"]
    for i, el in enumerate(inst):
        op1 = "" if el[1] is None else el[1]
        op2 = "" if el[2] is None else el[2]
        op3 = "" if el[3] is None else el[3]
        tmp = el[0]+" "+op1+" "+op2+" "+op3
        x.add_row([tmp,el[4], el[5], el[6], el[7], el[8], el[9], el[10], el[11]])
    return x

if __name__ == "__main__" :
    init_mips = Init_MIPS("./config.txt", "./inst.txt", "./data.txt", "./reg.txt")
    r = init_mips.reg_val
    d = init_mips.data    
    instructionObjs = list()
    for el in init_mips.instructions:
        instructionObjs.append(Instructions(el, init_mips.config_dict))
    a = init_mips.reg_val
    mips = Processor(instructionObjs, init_mips.reg_val, init_mips.data, init_mips.loops, init_mips.instructions, init_mips.config_dict)
        
    print(print_table(mips.final))
    
    print("MIPS:", len(mips.final))