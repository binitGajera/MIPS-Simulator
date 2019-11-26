# -*- coding: utf-8 -*-
"""
@author: binit_gajera
"""

class Init_MIPS:
    def __init__(self, config, inst, data, reg):
        self.config_dict = self.load_config(config)
        self.reg_val = self.load_registers(reg)
        self.data = self.load_data(data)
        self.instructions, self.loops = self.load_inst(inst)
        
    def load_registers(self, reg):
        data_file = open(reg, "r", encoding="utf-8")        
        reg = dict()
        char = "R"
        for i, line in enumerate(data_file):
            val = int(line, 2)
            reg[char+str(i)] = reg.get(char+str(i), val)
        return reg
        
    def load_data(self, data):
        data_file = open(data, "r", encoding="utf-8")
        mem = dict()
        mem_start = 256
        for line in data_file:
            val = int(line, 2)
            mem[hex(mem_start)] = mem.get(hex(mem_start), val)
            mem_start += 1
        return mem
        
    def load_config(self, inp):
        data_file = open(inp, "r", encoding="utf-8")        
        reg = dict()
        for line in data_file:
            line = line.replace(" ", "")
            content = line.split(":")
            if content[0] == "FPadder":
                reg_type = "ADD"
            elif content[0] == "FPMultiplier":
                reg_type = "MULT"
            elif content[0] == "FPdivider":
                reg_type = "DIV"
            elif content[0] == "Mainmemory":
                reg_type = "MEM"
            elif content[0] == "I-Cache" or content[0] == "D-Cache":
                reg_type = content[0]
            reg_val = content[1].split(",")            
            if len(reg_val) > 1:
                if reg_val[1] == "yes\n":
                    reg_val = (int(reg_val[0]), True)
                else:
                    reg_val = (int(reg_val[0]), False)
            else:
                reg_val = int(reg_val[0])
            
            reg[reg_type] = reg.get(reg_type, reg_val)
            
        return reg
    
    def load_inst(self, inst):
        data_file = open(inst, "r", encoding="utf-8")
        inst_list = list()
        loops = dict()
        for i, line in enumerate(data_file):
            n_temp = line.upper().split(",")            
            temp = n_temp[0].split()
            if ":" in temp[0]:
                loop = temp[0].split(":")
                loops[loop[0]] = loops.get(loop[0], i)
                temp = ' '.join(temp[1:])
            if not isinstance(temp, list):
                temp = temp.split()
            if len(n_temp)>1:
                d = ' '.join(n_temp[1:])
                temp.extend(d.split())
            inst_list.append(temp)
        return inst_list, loops
        
if __name__ == "__main__" :    
    
    config = "./config.txt"
    inst = "./inst.txt"
    data = "./data.txt"
    reg = "./reg.txt"
    
    init_mips = Init_MIPS(config, inst, data, reg)    
    print(init_mips.instructions)