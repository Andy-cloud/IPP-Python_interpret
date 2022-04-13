from copy import deepcopy
import getopt
import xml.etree.ElementTree as ET
import re
import sys
file_name=""
input_file=""
input_file_data=""
variables_diction_GF={}
variables_diction_LF=None
variables_diction_TF=None
stack_frame = []
stack_data = []
stack_intern_counter = []
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
def check_frames(variable, can_empty):
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
                        print(str(intern_counter) + ". Špatná hodnota konstanty int")
                        exit(52)
                elif variable[i].attrib["type"] == "bool":
                    if variable[i].text.lower() == "false":
                        array_tmp.append(False)
                    elif variable[i].text.lower() == "true":
                        array_tmp.append(True)
                    else:
                        print("Nepodporovaný typ pro bool")
                        exit(52)
                else:
                    array_tmp.append(variable[i].text)
                    
                array_tmp.append(variable[i].attrib["type"])
                tmp.append(array_tmp)
    
        if not can_empty:
            for j in range(1,len(tmp)):
                if type(tmp[j]) is dict:
                    arg = tmp[j][splited[j]]  
                else:
                    arg = tmp[j]
                if not arg:
                    print("Prázdná proměnná jako argument")
                    exit(56) 
        return error, tmp, splited
    
    except TypeError:
        print(str(intern_counter) + ". Není vytvořený daný rámec")
        exit(55)
#zpracování instrukce move        
def move(variable):
    global intern_counter
    variable_frame = []
    splited_variable = []
    error, variable_frame, splited_variable = check_frames(variable,False)
    if error:
        print(str(intern_counter) + ". Proměnná není vytvořená")
        exit(54)
    else:
        if not type(variable_frame[1]) is dict:
            variable_frame[0][splited_variable[0]] = variable_frame[1]
        else:
            variable_frame[0][splited_variable[0]] = variable_frame[1][splited_variable[1]]
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
#zpracování instrukce add/sub/mul/idiv        
def process(variable, op):
    global intern_counter
    variable_frame = []
    splited_variable = []
    args_for_op = []
    error, variable_frame, splited_variable = check_frames(variable,False)
    if error:
        print(str(intern_counter) + ". Proměnná není vytvořená")
        exit(54)
    else:
        for i in range(1,len(variable_frame)):
            
            if not type(variable_frame[i]) is dict:
                if variable_frame[i][1] != "int":
                    print(op + ": se může provádět jen nad int")
                    exit(53)
                else: 
                    args_for_op.append(variable_frame[i][0])
            else:
                try:
                    if variable_frame[i][splited_variable[i]][1] != "int":
                        print(op + ": se může provádět jen nad int")
                        exit(53)
                    else:
                        args_for_op.append(variable_frame[i][splited_variable[i]][0])
                except IndexError:
                    print("Neinicializovaná proměnná")
  
        variable_frame[0][splited_variable[0]] = [select_sign(args_for_op[0],args_for_op[1],op),"int"]
        
def do_comparation(arg1, arg2, operator):
    if operator == "<": 
        if arg1[0] < arg2[0]:
            return True
        else:
            return False
    elif operator == ">":
        if arg1[0] > arg2[0]:
            return True
        else:
            return False
    elif operator == "=":
        if arg1[0] == arg2[0]:
            return True
        else:
            return False
    elif operator == "and":
        return arg1[0] and arg2[0]
    elif operator == "or":
        return arg1[0] or arg2[0]
    elif operator == "not":
        return not arg1[0]
#zpracování instrukce lt/gt/eq/and/or/not       
def comparison_operation(variable, op):
    error, variable_frame, splited_variable = check_frames(variable,True)
    if error:
        print(str(intern_counter) + ". Proměnná není vytvořená")
        exit(54)
    else:
        if not type(variable_frame[1]) is dict:
            arg1 = variable_frame[1]
        else:
            arg1 = variable_frame[1][splited_variable[1]] 
            
        if op == "not":
            arg2 = arg1
        else:
            if not type(variable_frame[2]) is dict:
                arg2 = variable_frame[2]
            else:
                arg2 = variable_frame[2][splited_variable[2]] 
        #pokud mají stejný typy
        if arg1 and arg2:
            if op == "and" or op == "or" or op == "not":
                if arg1[1] == "bool" and arg2[1] == "bool":
                    variable_frame[0][splited_variable[0]] = [do_comparation(arg1, arg2, op),"bool"]
                else:
                    print(variable.attrib["opcode"] + ": Nepodporovaný typ pro tuto operaci")
                    exit(53)    
            else:
                if arg1[1] == arg2[1]:
                    variable_frame[0][splited_variable[0]] = [do_comparation(arg1, arg2, op),"bool"]
                else:
                    print(variable.attrib["opcode"] + ": Nepodporovaný typ pro tuto operaci")
                    exit(53)
        else:
            if op == "=":
                if not arg1:
                    if arg2[1] == "nil":
                        variable_frame[0][splited_variable[0]] = [True,"bool"]
                    else:
                        variable_frame[0][splited_variable[0]] = [False,"bool"]
                elif not arg2:
                    if arg1[1] == "nil":
                        variable_frame[0][splited_variable[0]] = [True,"bool"]
                    else:
                        variable_frame[0][splited_variable[0]] = [False,"bool"]
            else:
                print(variable.attrib["opcode"] + ": Nepodporovaná operace pro typ nil") 
                exit(53)            
              
        
# zpracování samotného xml a volání funkcí pro určité instrukce        
def process_child(root,parent):
    global variables_diction_GF
    global variables_diction_LF
    global variables_diction_TF
    global stack_frame
    global intern_counter
    global stack_intern_counter
    
    for child in parent:
        intern_counter += 1
        print(str(intern_counter) + ". " + str(child.attrib["opcode"]))
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
            error, variable_frame , splited_variable = check_frames(child,True)
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:
                if not type(variable_frame[0]) is dict:
                    stack_data.append(variable_frame[0])
                else:
                    stack_data.append(variable_frame[0][splited_variable[0]])
        #pops
        elif str(child.attrib["opcode"]).lower() == "pops":
            error, variable_frame , splited_variable = check_frames(child,True)
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:
                if stack_data:
                    variable_frame[0][splited_variable[0]] = stack_data.pop()
                else:
                    print(str(intern_counter) + ". Prázdný zásobník nelze dělat pops")
                    exit(56)
        #int2char
        elif str(child.attrib["opcode"]).lower() == "int2char":
            error, variable_frame , splited_variable = check_frames(child,False)
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:
                if not type(variable_frame[1]) is dict:
                    arg_int = variable_frame[1]
                else:
                    arg_int = variable_frame[1][splited_variable[1]] 
                try:
                    variable_frame[0][splited_variable[0]] = [chr(arg_int[0]),"string"]
                except ValueError:
                    print("Zadána špatná ascii hodnota")
                    exit(58)
        #str2int
        elif str(child.attrib["opcode"]).lower() == "str2int":
            error, variable_frame , splited_variable = check_frames(child,False)
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:
                if not type(variable_frame[1]) is dict:
                    arg_str = variable_frame[1]
                else:
                    arg_str = variable_frame[1][splited_variable[1]] 
                if not type(variable_frame[2]) is dict:
                    arg_int = variable_frame[2]
                else:
                    arg_int = variable_frame[2][splited_variable[2]] 
                try:
                    variable_frame[0][splited_variable[0]] = [ord(arg_str[0][arg_int[0]]), "int"]
                except IndexError:
                    print("Špatný index řetězce")
                    exit(58)
        #lt
        elif str(child.attrib["opcode"]).lower() == "lt":
            comparison_operation(child, "<")
        #gt
        elif str(child.attrib["opcode"]).lower() == "gt":
            comparison_operation(child, ">")
        #eq
        elif str(child.attrib["opcode"]).lower() == "eq":
            comparison_operation(child, "=")
        #and
        elif str(child.attrib["opcode"]).lower() == "and":
            comparison_operation(child, "and")
        #or
        elif str(child.attrib["opcode"]).lower() == "or":
            comparison_operation(child, "or")
        #not
        elif str(child.attrib["opcode"]).lower() == "not":
            comparison_operation(child, "not")
        #write
        elif str(child.attrib["opcode"]).lower() == "write":
            error, variable_frame , splited_variable = check_frames(child,True)   
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:
                print(variable_frame[0])
                if not type(variable_frame[0]) is dict:
                    arg_write = variable_frame[0]
                else:
                    arg_write = variable_frame[0][splited_variable[0]]
                if arg_write:
                    if arg_write[1] == "string" or arg_write[1] == "int":
                        print(arg_write[0],end='') 
                    elif arg_write[1] == "nil":
                        print("")   
                else:
                    print("Není žádná hodnota v proměnné")
                    exit(56)
                  
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
                    
                    if splited[1] in variables_diction_GF:
                        print(str(intern_counter) + ". již existuje proměnná")
                        exit(52)
                    else:
                        variables_diction_GF[splited[1]] = list()
                        
                elif splited[0] == "LF":
                    
                    if variables_diction_LF == None:
                        print(str(intern_counter) + ". Nedefinovaný rámec LF")
                        exit(55)
                        
                    if splited[1] in variables_diction_LF:
                        print(str(intern_counter) + ". již existuje proměnná")
                        exit(52)
                    else:
                        variables_diction_LF[splited[1]] = list()
                        
                elif splited[0] == "TF":
                    
                    if variables_diction_TF == None:
                        print(str(intern_counter) + ". Nedefinovaný rámec TF")
                        exit(55)
                        
                    if splited[1] in variables_diction_TF:
                        print(str(intern_counter) + ". již existuje proměnná")
                        exit(52)
                    else:
                        variables_diction_TF[splited[1]] = list()
                        
            else:
                print(str(intern_counter) + ". můžeš definovat pouze proměnnou")
                exit(53)
        #call
        elif str(child.attrib["opcode"]).lower() == "call":
            stack_intern_counter.append(intern_counter)
            for i in range(len(root)):

                if str(root[i].attrib['opcode']).lower() == "label":
                    if root[i][0].text == child[0].text:
                        parent = deepcopy(root[i:])
                        
                        intern_counter = i
                        return parent 
            
            print(str(intern_counter) + ". Neexistuje návěstí s tímto jménem")
            exit(52)
        #return
        elif str(child.attrib["opcode"]).lower() == "return":
            print(stack_intern_counter)
            if stack_intern_counter:
                intern_counter = stack_intern_counter.pop()
                parent = deepcopy(root[intern_counter:])
                return parent 
            else:
                print("Prázdný zásobník volání")
                exit(56)
        #read
        elif str(child.attrib["opcode"]).lower() == "read":
            variable_frame = []
            splited = []
            if str(child[0].attrib["type"]) == "var":
                
                splited = child[0].text.split("@")
                
                if splited[0] == "GF" and splited[1] in variables_diction_GF:
                    variable_frame.append(variables_diction_GF)
                    
                elif splited[0] == "LF":
                    
                    if variables_diction_LF == None:
                        print(str(intern_counter) + ". Nedefinovaný rámec LF")
                        exit(55)
                        
                    if splited[1] in variables_diction_LF:
                        variable_frame.append(variables_diction_LF)
                        
                elif splited[0] == "TF":
                    
                    if variables_diction_TF == None:
                        print(str(intern_counter) + ". Nedefinovaný rámec TF")
                        exit(55)
                        
                    if splited[1] in variables_diction_TF:
                        variable_frame.append(variables_diction_TF)   
                else:
                    print("Poměnná neexituje")
                    exit(54)   
                    
                try:
                    value = input_file_data.pop(0)
                except IndexError:
                    value = "nil"
                if value == "nil":
                    variable_frame[splited[1]] = ["nil","nil"] 
                else:    
                    if child[1].attrib["type"] == "type":
                        try:
                            if child[1].text == "int":
                                variable_frame[0][splited[1]] = [int(value),child[1].text] 
                            elif child[1].text == "bool":
                                if value.lower() == "true":
                                    print(variable_frame)
                                    print(splited[1])
                                    variable_frame[0][splited[1]] = [True,child[1].text]
                                else:
                                    variable_frame[0][splited[1]] = [False,child[1].text]
                            elif child[1].text == "string":
                                variable_frame[0][splited[1]] = [value,child[1].text]
                            else:
                                print("Špatný typ operandu")
                                exit(53)
                        except ValueError:
                            print("Špatné typy operandů")
                            exit(53)
                    else:
                        print("Špatný typ paramentu")
                        exit(53)             
            else:
                print(str(intern_counter) + ". Špatný typ paramentru")
                exit(53)
        #type
        elif str(child.attrib["opcode"]).lower() == "type":
            error, variable_frame, splited_variable = check_frames(child, True)
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:
                if not type(variable_frame[1]) is dict:
                    arg_type = variable_frame[1]
                else:
                    arg_type = variable_frame[1][splited_variable[1]]
                if arg_type:
                    variable_frame[0][splited_variable[0]] = [arg_type[1],"string"]
                else:
                    variable_frame[0][splited_variable[0]] = ["","string"]
        #concat
        elif str(child.attrib["opcode"]).lower() == "concat":
            error, variable_frame, splited_variable = check_frames(child, False)
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:  
                if not type(variable_frame[1]) is dict:
                    arg_str1 = variable_frame[1]
                else:
                    arg_str1 = variable_frame[1][splited_variable[1]]
                if not type(variable_frame[2]) is dict:
                    arg_str2 = variable_frame[2]
                else:
                    arg_str2 = variable_frame[2][splited_variable[2]]   
                if arg_str1[1] == arg_str2[1] and arg_str1[1] == "string":
                    variable_frame[0][splited_variable[0]] = [arg_str1[0]+arg_str2[0],"string"]
                else:
                    print("nesprávné datové typy")
                    exit(53) 
        #strlen
        elif str(child.attrib["opcode"]).lower() == "strlen":
            error, variable_frame, splited_variable = check_frames(child, True)
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:  
                if not type(variable_frame[1]) is dict:
                    arg_str = variable_frame[1]
                else:
                    arg_str = variable_frame[1][splited_variable[1]]
                if arg_str[1] == "string":
                    try:
                        variable_frame[0][splited_variable[0]] = [len(arg_str[0]),"int"]
                    except TypeError:
                        print("Špatný typ operandu")
                        exit(53)
                else:
                    print("Špatný typ operandu")
                    exit(53)
        #getchar
        elif str(child.attrib["opcode"]).lower() == "getchar":
            error, variable_frame , splited_variable = check_frames(child,False)
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:
                if not type(variable_frame[1]) is dict:
                    arg_str = variable_frame[1]
                else:
                    arg_str = variable_frame[1][splited_variable[1]] 
                if not type(variable_frame[2]) is dict:
                    arg_int = variable_frame[2]
                else:
                    arg_int = variable_frame[2][splited_variable[2]] 
                if arg_str[1] == "string" and arg_int[1] == "int":
                    try:
                        variable_frame[0][splited_variable[0]] = [arg_str[0][arg_int[0]], "int"]
                    except IndexError:
                        print("Špatný index řetězce")
                        exit(58)  
                else:
                    print("Špatný typ operandu")
                    exit(53)
                    
        #setchar
        elif str(child.attrib["opcode"]).lower() == "setchar":
            error, variable_frame , splited_variable = check_frames(child,True)
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:
                if not type(variable_frame[1]) is dict:
                    arg_int = variable_frame[1]
                else:
                    arg_int = variable_frame[1][splited_variable[1]] 
                if not type(variable_frame[2]) is dict:
                    arg_char = variable_frame[2]
                else:
                    arg_char = variable_frame[2][splited_variable[2]]
                if arg_char:
                    if arg_char[1] == "string" and arg_int[1] == "int":
                        try:
                            help_variable = list(variable_frame[0][splited_variable[0]][0])
                            help_variable[arg_int[0]] = arg_char[0]
                            variable_frame[0][splited_variable[0]][0] = "".join(help_variable)
                        except IndexError:
                            print("Špatný index řetězce")
                            exit(58) 
                    else:
                        print("Špatný typ operandu")
                        exit(53)
                else:
                    print("Prázdný řetězec")
                    exit(58) 
        #jumpifeq/jumpifneq
        elif str(child.attrib["opcode"]).lower() == "jumpifeq" or str(child.attrib["opcode"]).lower() == "jumpifneq":
            error, variable_frame, splited_variable = check_frames(child,False)
            if error:
                print(str(intern_counter) + ". Proměnná není vytvořená")
                exit(54)
            else:
                if not type(variable_frame[1]) is dict:
                    arg1 = variable_frame[1]
                else:
                    arg1 = variable_frame[1][splited_variable[1]] 
                if not type(variable_frame[2]) is dict:
                    arg2 = variable_frame[2]
                else:
                    arg2 = variable_frame[2][splited_variable[2]]  
                if arg2[1] == arg1[1] or arg1[1] == "nil" or arg2[1] == "nil":
                    if str(child.attrib["opcode"]).lower() == "jumpifneq":
                        if not do_comparation(arg1, arg2, "="):
                            for i in range(len(root)):
                                if str(root[i].attrib['opcode']).lower() == "label":
                                    if (root[i][0].text == child[0].text):
                                        parent = deepcopy(root[i:])
                                        intern_counter = i
                                        return parent 
                            
                            print(str(intern_counter) + ". Neexistuje návěstí s tímto jménem")
                            exit(52)
                    else:
                        if do_comparation(arg1, arg2, "="):
                            for i in range(len(root)):
                                if str(root[i].attrib['opcode']).lower() == "label":
                                    if (root[i][0].text == child[0].text):
                                        parent = deepcopy(root[i:])
                                        intern_counter = i
                                        return parent 
                            
                            print(str(intern_counter) + ". Neexistuje návěstí s tímto jménem")
                            exit(52)
                else:
                    print("Nepodporovaná kombinace typů")
                    exit(53)
        #exit
        elif str(child.attrib["opcode"]).lower() == "exit":
            variable_frame = []
            if str(child[0].attrib["type"]) == "var":
                splited = child[0].text.split("@")
                
                if splited[0] == "GF" and splited[1] in variables_diction_GF:
                    variable_frame.append(variables_diction_GF)
                    
                elif splited[0] == "LF":
                    
                    if variables_diction_LF == None:
                        print(str(intern_counter) + ". Nedefinovaný rámec LF")
                        exit(55)
                        
                    if splited[1] in variables_diction_LF:
                        variable_frame.append(variables_diction_LF)
                        
                elif splited[0] == "TF":
                    
                    if variables_diction_TF == None:
                        print(str(intern_counter) + ". Nedefinovaný rámec TF")
                        exit(55)
                        
                    if splited[1] in variables_diction_TF:
                        variable_frame.append(variables_diction_TF)   
                else:
                    print("Poměnná neexituje")
                    exit(54) 
                if variable_frame[0][splited[1]][1] == "int":
                    if int(variable_frame[0][splited[1]][0]) >= 0 and int(variable_frame[0][splited[1]][0]) <= 49:
                        print(variable_frame[0][splited[1]][0])
                        exit(int(variable_frame[0][splited[1]][0]))  
                    else:
                        print("Nevalidní číslená hodnota")
                        exit(57)
            else:
                if child[0].attrib["type"] == "int":
                    if int(child[0].text) >= 0 and int(child[0].text) <= 49:
                        print(int(child[0].text))
                        exit(int(child[0].text))
                    else:
                        print("Nevalidní číslená hodnota")
                        exit(57)
                print(variable_frame)
        #jump
        elif str(child.attrib["opcode"]).lower() == "jump":
            
            for i in range(len(root)):
                if str(root[i].attrib['opcode']).lower() == "label":
                    if (root[i][0].text == child[0].text):
                        parent = deepcopy(root[i:])
                        intern_counter = i
                        return parent 
            
            print(str(intern_counter) + ". Neexistuje návěstí s tímto jménem")
            exit(52)
        else:
            print("neznámá instrukce")
        #TODO: Dprint a break
        
    return []
        
        
try:
    opts, args = getopt.getopt(sys.argv[1:],"", ["help", "source=", "input="])
except getopt.GetoptError:
    print("Špatné parametry")
    exit(10)
process_arguments(opts)
if file_name:
    try:
        inf = open(file_name,'r')
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

if input_file:
    try:
        inf = open(input_file,'r')
    except:
        print("Chyba při otevírání souboru")
        exit(11)
else:
    inf = sys.stdin
input_file_data = inf.read()
input_file_data = input_file_data.split()

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