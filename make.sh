#!/bin/sh

#source ./env/bin/activate.csh
#python3 MIPS.py
#deactivate

usage ()
{  
  echo " "
  echo $"Usage: ./make.sh inst.txt data.txt reg.txt config.txt result.txt"
  echo " "
  exit
}

if [ "$#" -ne 5 ] || [ "$1" == "--help" ] || [ "$1" == "-h" ]
then
  usage
fi

cd ./venv/bin/ && ./python3 ../../MIPS.py --inst $1 --data $2 --reg $3 --config $4 --result $5 && rm -rf ../../__pycache__