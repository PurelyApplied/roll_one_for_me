#!/usr/bin/python3

import os
def main():
    for name in [n for n in os.listdir('logs') if n[-4:] == ".log"]:
        full_name = './logs/'+name
        print("read_logs.py> View log {}?".format(name))
        yn = input("read_logs.py (y/n)> ")
        if 'y' == yn:
            print(open(full_name, 'r').read())
            
        print("read_logs.py> Delete log and pickle associated to {}?".format(name))
        yn = input("read_logs.py (y/n)> ")
        if 'y' == yn:
            print("os.system('rm '+fullname)")
            print("os.system('rm '+fullname[:-4]+'.pickle')")
            #os.system('rm '+fullname)
            #os.system('rm '+fullname[:-4]+'.pickle')
            
if __name__=="__main__":
    main()
