# -*- coding: utf-8 -*-
"""
@author: binit_gajera
"""

from load_data import Init_MIPS
from pprint import pprint as pp

IF, ID, EX, WB = 0, 0, 0, 0
RAW, WAR, WAW, Struct = "N", "N", "N", "N"

result = list()

def processor(mips):
    insts, config, reg, loops, data = mips.instructions, mips.config_dict, mips.reg_val, mips.loops, mips.data
    global IF, ID, EX, WB, RAW, WAR, WAW, Struct, result
    reg_stat = dict()    
    mem_stat = 0
    for inst in insts[:11]:
        if inst[0] == "L.D":
            n_cycles = config["MEM"] + 1                        
            IF = update_IF(IF, ID)
###########-Verify this logic for RAW-###########
            ID, RAW = update_ID("IU", reg_stat, IF, inst)
###########-###########-###########-#############
            stalls = mem_stat - (ID + n_cycles - config["MEM"])     
            EX, mem_stat, Struct = update_EX("IU", mem_stat, ID, n_cycles, stalls)
            WB = EX + 1
            reg_stat[inst[1]] = WB
        elif inst[0] == "ADD.D" or inst[0] == "SUB.D":
            n_cycles = config["ADD"][0]
            pip = config["ADD"][1]
            IF = update_IF(IF, ID)
###########-Verify this logic for RAW-###########
            ID, RAW = update_ID("MATH", reg_stat, IF, inst)
###########-###########-###########-#############    
            if pip:
###########-Modify this logic for pipeline-###########                
                EX = ID + n_cycles                
###########-###########-###########-##################
            else:
                EX = ID + n_cycles
            WB = EX + 1
            reg_stat[inst[1]] = WB
            Struct = "N"
        elif inst[0] == "MUL.D":
            n_cycles = config["MULT"][0]
            pip = config["MULT"][1]
            IF = update_IF(IF, ID)
###########-Verify this logic for RAW-###########
            ID, RAW = update_ID("MATH", reg_stat, IF, inst)
###########-###########-###########-#############    
            if pip:
###########-Modify this logic for pipeline-###########                
                EX = ID + n_cycles                
###########-###########-###########-##################
            else:
                EX = ID + n_cycles
            WB = EX + 1
            reg_stat[inst[1]] = WB
            Struct = "N"
        elif inst[0] == "DADDI" or inst[0] == "DSUB":
            n_cycles = config["MEM"]            
            IF = update_IF(IF, ID)
###########-Verify this logic for RAW-###########
            ID, RAW = update_ID("IU", reg_stat, IF, inst)
###########-###########-###########-#############                        
            stalls = mem_stat - (ID + n_cycles - config["MEM"])     
            EX, mem_stat, Struct = update_EX("IU", mem_stat, ID, n_cycles, stalls)
            WB = EX + 1
            reg_stat[inst[1]] = WB
        elif inst[0] == "BNE":
            IF = update_IF(IF, ID)
###########-Verify this logic for RAW-###########
            ID, RAW = update_ID("IU", reg_stat, IF, inst)
###########-###########-###########-#############
            EX, WB = "-","-"
            WAR, WAW, Struct = "N","N","N"
        result.append([IF, ID, EX, WB, RAW, WAR, WAW, Struct])
        
def update_IF(IF, ID):
    res = 0 
    if IF == 0:
        res = IF + 1
    else:
        res = ID
    
    return res

def update_ID(iname, reg_st, IF, inst):
    if iname == "IU":
        if reg_st.get(inst[1], 0) > IF + 1:
            ID = reg_st[inst[1]]
            RAW = "Y"
        else:
            ID = IF + 1
            RAW = "N"
        return ID, RAW
    elif iname == "MATH":
        if reg_st.get(inst[2], 0) > IF + 1 and reg_st.get(inst[3], 0) > IF + 1:
                ID = max(reg_st[inst[2]], reg_st[inst[3]])
                RAW = "Y"
        elif reg_st.get(inst[2], 0) > IF + 1:                
            ID = reg_st[inst[2]]
            RAW = "Y"
        elif reg_st.get(inst[3], 0) > IF + 1:                
            ID = reg_st[inst[3]]
            RAW = "Y"
        else:
            ID = IF + 1
            RAW = "N"
        return ID, RAW

def update_EX(iname, mem_st, ID, n_c, sts, pip=False):
    if iname == "IU":
        if sts > 0:
            EX = ID + n_c + sts
            mem_st = EX
            Struct = "Y"
        else:
            EX = ID + n_c
            mem_st = EX
            Struct = "N"
        return EX, mem_st, Struct
    
if __name__ == "__main__" :
    init_mips = Init_MIPS("./config.txt", "./inst.txt", "./data.txt", "./reg.txt")
    d = init_mips.config_dict
    b = init_mips.instructions
    processor(init_mips)
    pp(result)    