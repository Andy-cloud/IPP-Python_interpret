from copy import deepcopy
import getopt
import xml.etree.ElementTree as ET
import re
import sys
file_name=""
input_file=""
variables_diction_GF={}
variables_diction_LF=None
variables_diction_TF=None
stack_frame = []
stack_data = []
intern_counter = 0

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
            print("Použit špatný paramentr")
            exit(10)
#kontrola zda je proměnná zapsána správně nebo konstanta a jestli existuje rámec            
def check_frames(variable):
    global variables_diction_GF
    global variables_diction_LF
    global variables_diction_TF
    global intern_counter
    error = 0
    tmp = []
    splited = []
    try:
        for i in range(len(variable)):
            
            if re.match('GF@\S+', variable[i].text):
                
                split = variable[i].text.split("@")
                splited.append(split[1])
                
                if not splited[i] in variables_diction_GF:
                    error = 1
                else:
                    tmp.append(variables_diction_GF)
                    
            elif re.match('LF@\S+', variable[i].text):
                
                split = variable[i].text.split("@")
                splited.append(split[1])
                
                if not splited[i] in variables_diction_LF:
                    error = 1
                else:
                    tmp.append(variables_diction_LF)
                    
            elif re.match('TF@\S+', variable[i].text):
                
                split = variable[i].text.split("@")
                splited.append(split[1])
                
                if not splited[i] in variables_diction_TF:
                    error = 1
                else:
                    tmp.append(variables_diction_TF)
            else:
                array_tmp = []
                splited.append(variable[i].text)
                if variable[i].attrib["type"] == "int":
                    try:
                        array_tmp.append(int(variable[i].text))
                    except ValueError: 
                        print(str(intern_counter) + ". Špatná hodnota konstanty")
                        exit(53)
                else:
                    array_tmp.append(variable[i].text)
                    
                array_tmp.append(variable[i].attrib["type"])
                tmp.append(array_tmp)
                
        return error, tmp, splited
    
    except TypeError:
        print(str(intern_counter) + ". Není vytvořený daný rámec")
        exit(55)
#zpracování instrukce move        
def move(variable):
    global intern_counter
    tmp = []
    splited = []
    error, tmp, splited = check_frames(variable)
    if error:
        print(str(intern_counter) + ". Proměnná není vytvořená")
        exit(54)
    else:
        if not type(tmp[1]) is dict:
            tmp[0][splited[0]] = tmp[1]
        else:
            tmp[0][splited[0]] = tmp[1][splited[1]]
#výběr operace a provedení a vrácení výsledku        
def select_sign(arg1,arg2,operator):
    global intern_counter
    if operator == "+":
        return int(arg1 + arg2)
    elif operator == "-":
        return int(arg1 - arg2)
    elif operator == "*":
        return int(arg1 * arg2)
    elif operator == "/":
        try:
            return int(arg1 // arg2)
        except ZeroDivisionError:
            print(str(intern_counter) + ". Nelze dělit nulou")
            exit(57)
        
def process(variable, op):
    global intern_counter
    tmp = []
    splited = []
    j = 1
    args_for_op = []
    error, tmp, splited = check_frames(variable)
    if error:
        print(str(intern_counter) + ". Proměnná není vytvořená")
        exit(54)
    else:
        for i in range(1,len(tmp)):
            
            if not type(tmp[i]) is dict:
                if tmp[i][1] != "int":
                    print(op + ": se může provádět jen nad int")
                    exit(53)
                else: 
                    args_for_op.append(tmp[i][0])
            else:
                if tmp[i][splited[j]][1] != "int":
                    print(op + ": se může provádět jen nad int")
                    exit(53)
                else:
                    args_for_op.append(tmp[i][splited[j]][0])
                    
                j += 1
                
        tmp_array = []
        tmp_array.append(select_sign(args_for_op[0],args_for_op[1],op))
        tmp_array.append("int")
        
        tmp[0][splited[0]] = tmp_array
        
def process_child(root,parent):
    global variables_diction_GF
    global variables_diction_LF
    global variables_diction_TF
    global stack_frame
    global intern_counter
    
    for child in parent:
        intern_counter += 1
        #print(str(intern_counter) + ". " + str(child.attrib["opcode"]))
        #add
        if str(child.attrib["opcode"]).lower() == "add":
            process(child, "+")
        #sub
        elif str(child.attrib["opcode"]).lower() == "sub":
            process(child, "-")
        #mul
        elif str(child.attrib["opcode"]).lower() == "mul":
            process(child, "*")
        #idiv
        elif str(child.attrib["opcode"]).lower() == "idiv":
            process(child, "/")
        #move
        elif str(child.attrib["opcode"]).lower() == "move":
            move(child)
        #pushs
        elif str(child.attrib["opcode"]).lower() == "pushs":
            error, tmp , splited = check_frames(child)
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:
                if not type(tmp[0]) is dict:
                    stack_data.append(tmp[0])
                else:
                    stack_data.append(tmp[0][splited[0]])
        #pops
        elif str(child.attrib["opcode"]).lower() == "pops":
            error, tmp , splited = check_frames(child)
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:
                if stack_data:
                    tmp[0][splited[0]] = stack_data.pop()
                else:
                    print(str(intern_counter) + ". Prázdný zásobník nelze dělat pops")
                    exit(56)
        #int2char
        elif str(child.attrib["opcode"]).lower() == "int2char":
            error, tmp , splited = check_frames(child)
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:
                if not type(tmp[1]) is dict:
                    arg_int = tmp[1]
                else:
                    arg_int = tmp[1][splited[1]] 
                try:
                    tmp[0][splited[0]] = [chr(arg_int[0]),"string"]
                except ValueError:
                    print("Zadána špatná ascii hodnota")
                    exit(58)
        #str2int
        elif str(child.attrib["opcode"]).lower() == "str2int":
            error, tmp , splited = check_frames(child)
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:
                if not type(tmp[1]) is dict:
                    arg_str = tmp[1]
                else:
                    arg_str = tmp[1][splited[1]] 
                if not type(tmp[2]) is dict:
                    arg_int = tmp[2]
                else:
                    arg_int = tmp[2][splited[2]] 
                try:
                    tmp[0][splited[0]] = [ord(arg_str[0][arg_int[0]]), "int"]
                except IndexError:
                    print("Špatný index řetězce")
                    exit(58)
        #write
        elif str(child.attrib["opcode"]).lower() == "write":
            error, tmp , splited = check_frames(child)   
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:
                if not type(tmp[0]) is dict:
                    arg_write = tmp[0]
                else:
                    arg_write = tmp[0][splited[0]]
                if arg_write[1] == "string" or arg_write[1] == "int":
                    print(arg_write[0],end='') 
                elif arg_write[1] == "nil":
                    print(" ")   
                  
        #createframe
        elif str(child.attrib["opcode"]).lower() == "createframe":
            
            if variables_diction_TF == None:
                variables_diction_TF = {}
            else:
                variables_diction_TF.clear()
        #pushframe
        elif str(child.attrib["opcode"]).lower() == "pushframe":
            
            if variables_diction_TF == None:
                print(str(intern_counter) + ". Nelze pushnout nedefinovaný rámec")
                exit(55)
                
            if variables_diction_LF != None:
                stack_frame.append(variables_diction_LF)
                
            variables_diction_LF = variables_diction_TF
            variables_diction_TF = None
        #popframe
        elif str(child.attrib["opcode"]).lower() == "popframe":
            
            if variables_diction_LF != None:
                variables_diction_TF = variables_diction_LF
                
                if stack_frame:
                    variables_diction_LF = stack_frame.pop()
                else:
                    variables_diction_LF = None
                    
            else:
                print(str(intern_counter) + ". Prázdný zásobník rámců")
                exit(55)
        #defvar 
        elif str(child.attrib["opcode"]).lower() == "defvar":
            
            if str(child[0].attrib["type"]) == "var":
                splited = child[0].text.split("@")
                
                if splited[0] == "GF":
                    
                    if child[0].text in variables_diction_GF:
                        print(str(intern_counter) + ". již existuje proměnná")
                        exit(52)
                    else:
                        variables_diction_GF[splited[1]] = list()
                        
                elif splited[0] == "LF":
                    
                    if variables_diction_LF == None:
                        print(str(intern_counter) + ". Nedefinovaný rámec LF")
                        exit(55)
                        
                    if child[0].text in variables_diction_LF:
                        print(str(intern_counter) + ". již existuje proměnná")
                        exit(52)
                    else:
                        variables_diction_LF[splited[1]] = list()
                        
                elif splited[0] == "TF":
                    
                    if variables_diction_TF == None:
                        print(str(intern_counter) + ". Nedefinovaný rámec TF")
                        exit(55)
                        
                    if child[0].text in variables_diction_TF:
                        print(str(intern_counter) + ". již existuje proměnná")
                        exit(52)
                    else:
                        variables_diction_TF[splited[1]] = list()
                        
            else:
                print(str(intern_counter) + ". můžeš definovat pouze proměnnou")
                exit(53)
        #jump
        elif str(child.attrib["opcode"]).lower() == "jump":
            
            for i in range(len(root)):
                
                if (root[i][0].text == child[0].text and str(root[i].attrib['opcode']).lower() == "label"):
                    parent = deepcopy(root[i:])
                    return parent 
            
            print(str(intern_counter) + ". Neexistuje návěstí s tímto jménem")
            exit(52)
        
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
save_copy = deepcopy(root)

#kontrola duplicitního orderu
prev = -1
for o in root:
    if int(o.attrib["order"]) >= 0:
        if int(o.attrib["order"]) == prev:
            print(str(intern_counter) + ". Duplicitní order")
            exit(32)
    else:
        print(str(intern_counter) + ". záporný order")
        exit(32)
    prev = int(o.attrib["order"])
    
while root:
    """ if int(min.get("order")) == prev_min:
        print("duplicitní pořadí")
        exit(32)
    if int(min.get("order")) < 0:
        print("order menší jak nula")
        exit(32) """
    root = process_child(save_copy,root)
    print("\n")
    print(str(variables_diction_GF) + " --> GF")
    print(str(variables_diction_LF) + " --> LF")
    print(str(variables_diction_TF) + " --> TF")
    

if inf is not sys.stdin:
    inf.close()