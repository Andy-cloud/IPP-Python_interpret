from cmath import nan
from copy import deepcopy
from email.policy import default
import getopt
import xml.etree.ElementTree as ET
import re
import sys
file_name=""
input_file=""
variables_diction={}
stack = []

def print_help():
    print("help")
def process_arguments(arguments):
    global file_name
    global input_file
    for o in arguments:
        if o[0] == "--help":
            print_help()
        elif o[0] == "--source":
            file_name = o[1]
        elif o[0] == "--input":
            input_file = o[1]
        else:
            exit(10)
            
def process_child(root,parent):
    for child in parent:
        #write
        if str(child.attrib["opcode"]).lower() == "write":
            print(child[0].tag)
            print(child[0].attrib["type"])
        #defvar 
        elif str(child.attrib["opcode"]).lower() == "defvar":
            if str(child[0].attrib["type"]) == "var":
                if child[0].text in variables_diction:
                    print("již existuje proměnná")
                else:
                    variables_diction[child[0].text] = list()
            else:
                """můžeš definovat pouze proměnnou"""
                print("Error")
            """ variables_diction[child[0].text].append("int") """
            print(variables_diction)
        #jump
        elif str(child.attrib["opcode"]).lower() == "jump":
            for i in range(len(default)):
                if (default[i][0].text == child[0].text and str(default[i].attrib).lower() == "label"):
                    parent = deepcopy(root[i:])
                    for j in parent:
                        print(j.attrib)
                    return parent  
    return []
        
        
try:
    opts, args = getopt.getopt(sys.argv[1:],"", ["help", "source=", "input="])
except getopt.GetoptError:
    print("Špatné parametry")
    exit(10)
process_arguments(opts)
if file_name:
    try:
        inf = open(file_name)
    except:
        print("Chyba při otevírání souboru")
        exit(11)
    try:
        tree = ET.parse(inf)
        root = tree.getroot()
    except ET.ParseError:
        print("Špatný formát xml")
        exit(31)
else:
    inf = sys.stdin
    string = inf.read()
    print(string)
    try:
        root = ET.fromstring(string)
    except ET.ParseError:
        print("Špatný formát xml")
        exit(31)
root[:] = sorted(root, key=lambda child: int(child.get('order')))
default = deepcopy(root)
    
while root:
    """ if int(min.get("order")) == prev_min:
        print("duplicitní pořadí")
        exit(32)
    if int(min.get("order")) < 0:
        print("order menší jak nula")
        exit(32) """
    for o in root:
        print(o.attrib)
    print("\n")
    root = process_child(default,root)
    for o in root:
        print(o.attrib)
    

if inf is not sys.stdin:
    inf.close()