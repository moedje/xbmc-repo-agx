# -*- coding: utf-8 -*-
import re

def jsunprotect(html):
    targetVar = re.compile("window.location.href='/\?'\+(.*?)\+").findall(html)
    if not targetVar:
        #probably not the exspected protection
        return False
    targetVar = targetVar[0]
    functions = re.compile('function\s*(.*?)\s*\((.*?)\)\s*{(.*?)}').findall(html)
    html = re.sub('function(.*?)}','',html)
    arrayVar = re.compile('var\s*(.*?)\s*=\s*\[(.*?)\]').findall(html)[0]
    starter = re.compile(';'+arrayVar[0]+'\s*=\s*([^\(]+)\('+arrayVar[0]+'\)').findall(html)[0]
    starterNr = re.compile('.*?([1-9]+)').findall(starter)[-1]

    arrayName = arrayVar[0]
    array = arrayVar[1].replace("'",'').split(',')
    
    switchTree = getSwitches(functions, arrayVar[0])
    array = switching(switchTree,starterNr, array)
    result = ''.join(array)
    return result

def getSwitches(functions, varname):
    switchers = {}
    for func in functions:
        if func[1] != varname:
            continue
        name = func[0]
        code = func[2]
        code = code.split(';')
        switcherNum = re.compile('.*?([0-9]+)').findall(name)
        if switcherNum:
            switcherNum = switcherNum[-1]
            switchers[switcherNum] = []
        else:
            continue
        for line in code:
            switch = re.compile('\('+varname+',([0-9]+),([0-9]+)\)').findall(line)
            if switch:
                switchers[switcherNum].append(switch[0])
            else:
                switch = re.compile('([0-9]+)\('+varname+'\)').findall(line)
                if switch:
                    switchers[switcherNum].append(switch[0])
    return switchers 

def switching(tree,number,array):
    for exp in tree[number]:
        if type(exp) is tuple and len(exp)>1:
            a=int(exp[0])
            b=int(exp[1])
            temp = array[a]
            array[a]=array[b]
            array[b]=temp
        elif exp:
            array = switching(tree,exp,array)
    return array    