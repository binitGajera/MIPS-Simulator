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
    for i in range(0,32):
        reg_stat["F"+str(i)] = 0
    mem_stat = 0
    for inst in insts[:3]:
        if inst[0] == "L.D":
            n_cycles = config["MEM"] + 1                        
            if IF == 0:
                IF = IF + 1
            else:
                IF = ID
            ID = IF + 1
            stalls = mem_stat - (ID + n_cycles - config["MEM"])     
            if stalls > 0:
                EX = ID + n_cycles + stalls
                mem_stat = EX
                RAW, WAR, WAW, Struct = "N", "N", "N", "Y"
            else:
                EX = ID + n_cycles
                mem_stat = EX
                RAW, WAR, WAW, Struct = "N", "N", "N", "N"
            WB = EX + 1
        result.append([IF, ID, EX, WB, RAW, WAR, WAW, Struct])
        

if __name__ == "__main__" :
    init_mips = Init_MIPS("./config.txt", "./inst.txt", "./data.txt", "./reg.txt")
    instr = init_mips.instructions
    processor(init_mips)
    pp(result)