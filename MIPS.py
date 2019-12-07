# -*- coding: utf-8 -*-
"""
@author: binit_gajera
"""

from load_data import Init_MIPS
from prettytable import PrettyTable
import argparse
    
class Instructions:
    def __init__(self, instruction, config):
        self.IF = 0
        self.ID = 0
        self.EX = 0
        self.WB = 0
        self.RAW = 'N'
        self.WAR = 'N'
        self.WAW = 'N'
        self.SETTING = 0
        self.Struct = 'N'
        self.stat = 0
        self.IHIT = False
        self.IMISS = False
        self.DHIT = False
        self.DMISS = False
        self.iu_cycles = 0
        self.name = instruction[0]
        self.D_FLAG = False
        if len(instruction)>1:
            self.op1 = instruction[1]
            self.op2 = None if len(instruction[1:]) == 1 else instruction[2]
            self.op3 = None if len(instruction[1:]) == 2 or len(instruction[1:]) == 1 else instruction[3]
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
            self.cycles = 0
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
        self.icache = dict.fromkeys([0, 1, 2, 3])
        self.dcache = dict.fromkeys([0, 1])
        self.dcache[0] = dict.fromkeys([0, 1, 'LRU', 'D'])
        self.dcache[1] = dict.fromkeys([0, 1, 'LRU', 'D'])
        self.hits = 0
        self.dhits = 0
        self.ireq = 0
        self.dreq = 0
        self.or_inst = original_inst
        self.inst_list = instructions
        self.reg = reg
        self.data = data
        self.loops = loops
        self.loop_pos = list()
        self.final = list()
        self.run_loop(0, 0)

    def run_loop(self, idx, cl):
        tmp_loop = dict((v,k) for k, v in self.loops.items())
        tmp, new_loop, new_clock = self.run(self.inst_list[idx:], self.reg, self.data, self.loops, idx, cl)        
        if new_loop[0]:            
            te = 1 if len(self.final)==0 else len(self.final)
            for k, v in tmp_loop.items():                        
                if k == (k%te):                            
                    self.loop_pos.append((len(self.final), v))
            for d, el in enumerate(tmp[:-1]):                                
                self.final.append([el.name, el.op1, el.op2, el.op3, el.IF, el.ID, el.EX, el.WB, el.RAW, el.WAR, el.WAW, el.Struct])            
            for i, k in enumerate(self.or_inst):
                    self.inst_list[i].__init__(k, self.config)            
            self.run_loop(new_loop[1], new_clock)
        else:
            for k, v in tmp_loop.items():
                if len(self.final) == 0:
                    self.loop_pos.append((k, v))
                else:
                    self.loop_pos.append((len(self.final), v))
            for d, el in enumerate(tmp):                                        
                self.final.append([el.name, el.op1, el.op2, el.op3, el.IF, el.ID, el.EX, el.WB, el.RAW, el.WAR, el.WAW, el.Struct])                    
                
    def run(self, instructions, reg, data, loops, loop_idx, clock):
        x = 1000
        SET1, SET2 = False, False
        i = 0
        send_cl = 0
        BUS = [False, None]
        self.clock = clock        
        NEED_LOOP = [False, None]        
        while i<x:
            self.clock += 1            
            for j, inst in enumerate(instructions):                  
                if inst.WB == 0:                    
                    if inst.stat == 0 and (self.IFbusy[0] == 0 or self.IFbusy[1] == j):                        
                        if (self.IFbusy[1] != j and not NEED_LOOP[0]) or (j+1<len(instructions) and instructions[j].name == "HLT" and instructions[j+1].name == "HLT"):                            
                            if send_cl > 0:
                                pass
                            else:                                
                                self.ireq += 1                            
                                i_key = j+loop_idx
                                iblock = int((i_key)/4) % 4
                                if self.icache[iblock] is not None:
                                    if i_key in self.icache[iblock]:                                    
                                        if_penalty = self.config["I-Cache"]                                        
                                        self.hits += 1
                                        inst.IHIT = True
                                    else:                                                            
                                        if BUS[0]:
                                            continue
                                        else:
                                            inst.IMISS = True 
                                            BUS = [True, j]
                                        if_penalty = 2 * (self.config["I-Cache"] + self.config["MEM"])
                                        self.icache[iblock] = list(range(i_key, i_key+4))
                                else:                   
                                    inst.IMISS = True   
                                    if BUS[0]:
                                        continue
                                    else:
                                        BUS = [True, j]
                                    if_penalty = 2 * (self.config["I-Cache"] + self.config["MEM"])
                                    self.icache[iblock] = list(range(i_key, i_key+4))                            
                        
                        if inst.name == "HLT":                            
                            if NEED_LOOP[0]:                                                                                      
                                if instructions[j-1].name == "HLT":                                    
                                    if send_cl == 0:                                        
                                        send_cl = self.clock                                          
                                    instructions[j-1].IF = send_cl                                    
                                    for tmp_inst in instructions:
                                        if tmp_inst.name != "HLT":
                                            if tmp_inst.stat != 4:                                            
                                                send = False
                                                break
                                            else:                                                
                                                send = True                                    
                                    if send:                                        
                                        return instructions, NEED_LOOP, send_cl                                    
                                else:                                                       
                                    pass                                    
                            else:                                
                                if inst.IMISS and BUS[0] and BUS[1]!=j:
                                    inst.Struct = "Y"
                                    continue
                                elif inst.IMISS and not BUS[0] or BUS[1] == j:
                                 if if_penalty != 0:                                
                                        if_penalty -= 1                                    
                                        self.IFbusy = [1, j]                                
                                        if if_penalty == 0:
                                            BUS = [False, None]
                                            inst.IF = self.clock
                                            inst.stat = 1  
#                                            if instructions[j-1].name == "HLT":
#                                                x = False                                                
                                elif inst.IHIT:
                                    if if_penalty != 0:                                
                                        if_penalty -= 1                                    
                                        self.IFbusy = [1, j]                                
                                        if if_penalty == 0:                                    
                                            inst.IF = self.clock
                                            inst.stat = 1  
#                                            if instructions[j-1].name == "HLT":
#                                                x = False                                                
                                else:
                                    inst.Struct = "Y"
                                        
                        else:                      
                            if inst.IMISS and BUS[0] and BUS[1]!=j:
                                inst.Struct = "Y"
                                continue
                            elif inst.IMISS and not BUS[0] or BUS[1] == j:
                             if if_penalty != 0:                                
                                    if_penalty -= 1                                    
                                    self.IFbusy = [1, j]                                
                                    if if_penalty == 0:
                                        BUS = [False, None]
                                        inst.IF = self.clock
                                        inst.stat = 1  
                            elif inst.IHIT:
                                if if_penalty != 0:                                
                                    if_penalty -= 1                                    
                                    self.IFbusy = [1, j]                                
                                    if if_penalty == 0:                                    
                                        inst.IF = self.clock
                                        inst.stat = 1  
                            else:
                                inst.Struct = "Y"
                                                            
                    elif inst.stat == 1 and (not self.IDbusy[0] or self.IDbusy[1] == j):                        
                        if inst.op1 in self.reg_stat.keys() and j != self.reg_stat[inst.op1] and inst.name not in ["BNE", "BEQ"]:
                            if inst.name not in ["SW", "S.D"]:
                                inst.WAW = "Y"
                                continue
                        if inst.name in ["LW", "SW", "L.D", "S.D", "DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:                                                            
                                if inst.name in ["SW", "S.D"]:                                    
                                    if inst.op1 not in self.reg_stat.keys():                                        
                                        if self.IFbusy[1] != j:
                                            pass
                                        else:
                                            self.IFbusy = [0, None]
                                        self.IDbusy = [1, j]
                                        inst.ID = self.clock    
                                        inst.stat = 2                                    
                                    else:                                        
                                        if inst.RAW == "N":                                            
                                            self.IFbusy = [0, None]
                                        self.IDbusy = [1, j]
                                        inst.RAW = "Y"
                                        continue
                                else:               
                                    if SET1 or not self.IU[0]:                                             
                                        if (instructions[j-1].ID - inst.IF) > 0:
                                            inst.IF = instructions[j-1].ID
                                        self.reg_stat[inst.op1] = j
                                        self.IFbusy = [0, None]                                    
                                        self.IDbusy = [1, j]                                        
                                        inst.ID = self.clock    
                                        inst.stat = 2
                                    else:                                        
                                        continue
                        elif inst.name in ["ADD.D", "SUB.D", "MUL.D", "DIV.D"]:                             
                            if inst.op2 not in self.reg_stat.keys() and inst.op3 not in self.reg_stat.keys():                                
                                if inst.name in ["ADD.D", "SUB.D"]:
                                    tmp = self.ADD[0]
                                elif inst.name == "MUL.D":
                                    tmp = self.MULT[0]
                                elif inst.name == "DIV.D":
                                    tmp = self.DIV[0]
                                if not tmp:
                                    self.IFbusy = [0, None]                        
                                    self.IDbusy = [1, j]
                                    self.reg_stat[inst.op1] = j
                                    inst.ID = self.clock       
                                    inst.stat = 2
                                else:                                                                         
                                    inst.Struct = "Y"                                                  
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
                                    pass
                                inst.stat = 4
                            else:                                
                                inst.RAW = "Y"
                        elif inst.name == "BEQ" and inst.ID == 0:                            
                            if inst.op1 not in self.reg_stat.keys() and inst.op2 not in self.reg_stat.keys():                                
                                self.IFbusy = [0, None]                        
#                                self.IDbusy = [1, j]                                
                                inst.ID = self.clock                                
                                if reg[inst.op1] == reg[inst.op2]:
                                    NEED_LOOP = [True, loops.get(inst.op3)]                                      
                                else:
                                    pass
                                inst.stat = 4
                            else:                                
                                inst.RAW = "Y"
                        elif inst.name == "HLT":
                            if not instructions[j-1].name == "HLT" and inst.ID==0:                                 
                                self.IFbusy = [0, None]
                                inst.ID = self.clock
                                inst.stat = 4
                            
                        
                    elif inst.stat == 2:     
                                                                                         
                        if inst.name in ["LW", "SW", "L.D", "S.D", "DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:                            
                            if inst.name in ["LW", "SW", "L.D", "S.D"]:
                                if inst.D_FLAG == False:                                       
                                    id_penalty = 2 * (self.config["D-Cache"] + self.config["MEM"])                                
                                    or_data = int(inst.op2[0]) + self.reg[inst.op2[-3:-1]]
                                    if inst.name in ["L.D", "S.D"]:
                                        or_data = [or_data, or_data+4]
                                    elif inst.name in ["LW", "SW"]:
                                        or_data = [or_data]
                                    for or_d in or_data:                                        
                                        dc_set = int(or_d/16) % 2
                                        range_data = int(or_d/16) * 16                                
                                        check_set = [next((kem for kem, v in self.dcache[dc_set].items() if v is not None and kem!="LRU" and or_d in v), None)]                                        
                                        if check_set[0] is not None:                                                
                                            inst.D_FLAG = True
                                            self.dhits += 1     
                                            self.dreq += 1
                                            inst.DHIT = True                                                             
                                            inst.cycles += self.config["D-Cache"]                                            
                                        else:               
                                             
                                             if BUS[0]:                                                
                                                continue
                                             else:
                                                inst.DMISS = True
                                                self.dreq += 1
                                                inst.D_FLAG = True
                                                BUS = [True, j]
                                             if self.dcache[dc_set]['LRU'] is not None:                                                
                                                 nope = self.dcache[dc_set]['D'][self.dcache[dc_set]['LRU']]
                                                 if inst.name == "S.D":
                                                    self.dcache[dc_set][self.dcache[dc_set]['LRU']] = list(range(range_data, range_data+16, 4))                                                    
                                                    if nope == 0:                                                        
                                                        self.dcache[dc_set]["D"][self.dcache[dc_set]['LRU']] = 1
                                                    else:
                                                        inst.cycles += id_penalty + self.config["D-Cache"]
                                                    inst.cycles += id_penalty + self.config["D-Cache"]                                                    
                                                 elif inst.name == "SW":
                                                    self.dcache[dc_set][self.dcache[dc_set]['LRU']] = list(range(range_data, range_data+16, 4))                                                                                            
                                                    self.dcache[dc_set]["D"][nope] = 1
                                                    inst.cycles += id_penalty
                                                 else:
                                                    if nope == 0:
                                                        pass
                                                    else:
                                                        self.dcache[dc_set]['D'][self.dcache[dc_set]['LRU']] = 0
                                                    self.dcache[dc_set][self.dcache[dc_set]['LRU']] = list(range(range_data, range_data+16, 4))
                                                    inst.cycles += id_penalty                                                
                                                 self.dcache[dc_set]['LRU'] = self.dcache[dc_set]['LRU'] ^ 1
                                             else:
                                                 self.dcache[dc_set]["D"] = [0, 0]
                                                 nope = self.dcache[dc_set]['D'][0]
                                                 if inst.name == "S.D":
                                                    self.dcache[dc_set][0] = list(range(range_data, range_data+16, 4))
                                                    if nope == 0:                                                        
                                                        self.dcache[dc_set]["D"][0] = 1
                                                    else:
                                                        inst.cycles += id_penalty + self.config["D-Cache"]
                                                    inst.cycles += id_penalty + self.config["D-Cache"]                                                    
                                                 elif inst.name == "SW":
                                                    self.dcache[dc_set][0] = list(range(range_data, range_data+16, 4))
                                                    self.dcache[dc_set]["D"][nope] = 1
                                                    inst.cycles += id_penalty
                                                 else:
                                                    if nope == 0:
                                                        pass
                                                    else:
                                                        self.dcache[dc_set]['D'][0] = 0
                                                    self.dcache[dc_set][0] = list(range(range_data, range_data+16, 4))
                                                    inst.cycles += id_penalty                                                
                                                 self.dcache[dc_set]['LRU'] = 1
                                                
                                                                            
                            if not self.IU[0] and inst.iu_cycles == 1:                                                                                                
                                if self.MEMbusy[1] == j-1:
                                    inst.SETTING += 1
                                if instructions[j-1].SETTING > 1:
                                    inst.Struct = "Y"
                                if SET2 or not self.MEMbusy[0]: 
                                    self.IDbusy = [0, None]  
                                    self.IU = [1, j]                                    
                                    inst.iu_cycles -= 1   
                                    SET1 = True
                                else:
                                    inst.Struct = "Y"                                    
                                    continue
                            else:                                
                                if inst.DMISS and BUS[0] and BUS[1]!=j:
                                    inst.Struct = "Y"
                                    continue
                                elif (inst.DMISS and not BUS[0]) or BUS[1] == j:                                                                         
                                    if self.MEMbusy[0] == 0 or self.MEMbusy[1] == j:                                    
                                        if self.MEMbusy[0] == 0:
                                            self.IU = [0, None]
                                            SET1 = False
                                        self.MEMbusy = [1, j]                                         
                                        inst.cycles -= 1                                    
                                        if inst.cycles <= 0:
                                            BUS = [False, None]
                                            SET2 = True
                                            inst.EX = self.clock
                                            inst.stat = 3                                              
                                    else:                 
                                        inst.Struct = "Y"
                                elif inst.DHIT or inst.name in ["DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:
                                    if self.MEMbusy[0] == 0 or self.MEMbusy[1] == j:                                    
                                        if self.MEMbusy[0] == 0:
                                            self.IU = [0, None]
                                            SET1 = False                                        
                                        self.MEMbusy = [1, j]                                    
                                        inst.cycles -= 1                                    
                                        if inst.cycles <= 0:                                            
                                            SET2 = True
                                            inst.EX = self.clock
                                            inst.stat = 3                                    
                                    else:                 
                                        inst.Struct = "Y"
                                else:
                                    inst.Struct = "Y"
                        elif inst.name in ["ADD.D", "SUB.D"]:
                            self.IDbusy = [0, None]
                            if not inst.pip:                                 
                                if self.ADD[0] == 0 or self.ADD[1] == j:
                                    self.ADD = [1, j]
                                    inst.cycles -= 1                                    
                                    if inst.cycles == 0:
                                        self.ADD = [0, None]
                                        inst.EX = self.clock
                                        inst.stat = 3
                            else:
                                inst.cycles -= 1
                                if inst.cycles == 0:
                                    self.ADD = [0, None]
                                    inst.EX = self.clock
                                    inst.stat = 3
                        elif inst.name == "MUL.D":
                            self.IDbusy = [0, None]
                            if not inst.pip:                                
                                if self.MULT[0] == 0 or self.MULT[1] == j:
                                    self.MULT = [1, j]
                                    inst.cycles -= 1
                                    if inst.cycles == 0:
                                        self.MULT = [0, None]
                                        inst.EX = self.clock
                                        inst.stat = 3        
                            else:
                                inst.cycles -= 1
                                if inst.cycles == 0:
                                    self.MULT = [0, None]
                                    inst.EX = self.clock
                                    inst.stat = 3
                        elif inst.name == "DIV.D":
                            self.IDbusy = [0, None]
                            if not inst.pip:
                                if self.DIV[0] == 0 or self.DIV[1] == j:
                                    self.DIV = [1, j]
                                    inst.cycles -= 1
                                    if inst.cycles == 0:
                                        self.DIV = [0, None]
                                        inst.EX = self.clock
                                        inst.stat = 3
                            else:
                                inst.cycles -= 1
                                if inst.cycles == 0:
                                    self.DIV = [0, None]
                                    inst.EX = self.clock
                                    inst.stat = 3

                    elif inst.stat == 3:
                        if not self.WBbusy[0]:
                            if inst.name in ["LW", "SW", "L.D", "S.D", "DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:                                
                                if SET2:                                    
                                    self.MEMbusy = [0, None]
                                    SET2 = False
                                    inst.WB = self.clock
                                    inst.stat = 4
                                    self.WBbusy = [1, self.clock]
                                    if inst.name not in ["SW", "S.D"]:
                                        del self.reg_stat[inst.op1]
                                    else:
                                        pass
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
                                    elif inst.op2 is not None:
                                        if inst.name in ["AND", "ANDI"]:
                                            if inst.op3 in reg.keys():
                                                #inside AND
                                                reg[inst.op1] = reg[inst.op2] & reg[inst.op3]
                                            else:
                                                #inside ANDI
                                                reg[inst.op1] = reg[inst.op2] & int(inst.op3)
                                        elif inst.name in ["OR", "ORI"]:
                                            if inst.op3 in reg.keys():
                                                #inside OR
                                                reg[inst.op1] = reg[inst.op2] | reg[inst.op3]
                                            else:
                                                #inside ORI
                                                reg[inst.op1] = reg[inst.op2] | int(inst.op3)
                                        elif inst.name == "LW":
                                            haha = int(inst.op2[0]) + self.reg[inst.op2[-3:-1]]
                                            if haha in data.keys():                                                
                                                reg[inst.op1] = data[haha]                                                
                                            else:
                                                print(str(inst.op2)+" not in data.txt for LW!!")
                                        elif inst.name == "SW":
                                            haha = int(inst.op2[0]) + self.reg[inst.op2[-3:-1]]
                                            if haha in data.keys():                                                
                                                data[haha] = reg[inst.op1]                                                
                                            else:
                                                print(str(inst.op2)+" not in data.txt for SW!!")
                                else:                                    
                                    continue
                            else:
                                inst.stat = 4
                                del self.reg_stat[inst.op1]
                                inst.WB = self.clock
                                self.WBbusy = [1, self.clock]                            
                        else:
                            if self.clock == self.WBbusy[1]:                                
                                inst.Struct = "Y"                                
                                if inst.name in ["LW", "SW", "L.D", "S.D", "DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:
                                    inst.EX = self.clock
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
        return instructions, NEED_LOOP, self.clock
        
def print_table(inst, l, pos):
    x = PrettyTable()
    x.border = False        
    x.field_names = ["","Instruction","FT", "ID", "EX", "WB", "RAW", "WAR", "WAW", "Struct"]
    x.align["Instruction"] = "l"
    tmp = list()
    for i, el in enumerate(inst):
        op1 = "" if el[1] is None else el[1]
        op2 = "" if el[2] is None else ", "+el[2]
        op3 = "" if el[3] is None else ", "+el[3]
        tmp_name = el[0]+" "+op1+op2+op3
        loop = ""
        el[4] = " " if el[4] is 0 else el[4]
        el[5] = " " if el[5] is 0 else el[5]
        el[6] = " " if el[6] is 0 else el[6]
        el[7] = " " if el[7] is 0 else el[7]
        if i == len(inst)-1:
            el[8], el[9], el[10], el[11] = " ", " ", " ", " "
        tmp.append([loop,tmp_name,el[4], el[5], el[6], el[7], el[8], el[9], el[10], el[11]])
        
    for i in pos:
        tmp[i[0]][0] = i[1]+":"
    
    for el in tmp:
        x.add_row(el)
        
    x.right_padding_width = 4
    
    return x

if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description='Parsing input files')
    parser.add_argument('--inst', type=str, help='instruction file')
    parser.add_argument('--data', type=str, help='data file')
    parser.add_argument('--reg', type=str, help='reg file')
    parser.add_argument('--config', type=str, help='config file')
    parser.add_argument('--result', type=str, help='result file')
    
    args = parser.parse_args()
    
    root = "./test/test_case_1/"
#    init_mips = Init_MIPS(root+"config.txt", root+"inst.txt", root+"data.txt", root+"reg.txt")    
    init_mips = Init_MIPS(root+args.config, root+args.inst, root+args.data, root+args.reg)    
    a = init_mips.reg_val
    b = init_mips.data
    instructionObjs = list()
    for el in init_mips.instructions:
        instructionObjs.append(Instructions(el, init_mips.config_dict))    
    mips = Processor(instructionObjs, init_mips.reg_val, init_mips.data, init_mips.loops, init_mips.instructions, init_mips.config_dict)
    
#    file = open(root+args.result, "w+", encoding="utf-8")
#    file.write(str(print_table(mips.final, init_mips.loops, mips.loop_pos)))
#    file.write("\n\nTotal number of access requests for instruction cache: " + str(mips.ireq))
#    file.write("\n\nNumber of instruction cache hits: " + str(mips.hits))
#    file.write("\n\nTotal number of access requests for data cache: " + str(mips.dreq))
#    file.write("\n\nNumber of data cache hits: " + str(mips.dhits))
#    file.close()
    
    print(print_table(mips.final, init_mips.loops, mips.loop_pos))
    print("\nTotal number of access requests for instruction cache:", mips.ireq)
    print("Number of instruction cache hits:", mips.hits)
    print("Total number of access requests for data cache:", mips.dreq)
    print("Number of data cache hits:", mips.dhits)