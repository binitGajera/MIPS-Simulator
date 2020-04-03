## CMSC 611 - MIPS Simulator

The project is written in Python. The main files for the project are named "load_data.py" and "MIPS.py". The "load_data.py" is build for parsing the data while the other is the main MIPS simulator.

### Instructions

To run the project, you can simply call the below mentioned command on any linux machine:
```
./make.sh inst.txt data.txt reg.txt config.txt result.txt
```
This will generate the result.txt wherever the path specified, the arguments to the above shell script should be the path to respective file such as path to "inst.txt" and so on. The command will also print the result written in the file for a quick view.

I have used a python library "PrettyTable" to print the table, no other external library have been imported. The user will not have to install any such libraries though because I have provided a virtual environment in the zip file of the project. The libraries from the zip file will automatically be called and imported when running the shell script.

I would like to point out though that the arguments passed to the shell script are positional so I would recommend running the following command and checking the shell script's usage before actually calling it, to check it's usage you can use the following command.
```
./make.sh -h 

./make.sh --help
```
### ABOUT THE PROJECT

The project simualtes the MIPS processor as expected. I would like to specify that although the simulator supports more than average instructions from the MIPS it would not support the jump instruction but Branch instructions would be called successfully on it.
