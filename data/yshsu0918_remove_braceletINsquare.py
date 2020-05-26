# coding=utf-8

# ParseSGF
import os
from minimal_chessboard_tool import *
import chardet
from chardet.universaldetector import UniversalDetector

def timesinlist(ch,lst):
    c = 0
    for x in lst:
        if x == ch:
            c += 1
    return c

def check_bracelet(sgfstr):
    print('the number of (', timesinlist('(', sgfstr))
    print('the number of )', timesinlist(')', sgfstr))

def nearby( idx , sgfstr, interval = 3):
    start = idx - interval if idx - interval >= 0 else 0
    end = idx + interval if idx + interval < len(sgfstr) else len(sgfstr) 
    return sgfstr[start:end]

def check_sgfstr(QAQ):
    sgfstr = QAQ
    state = ''
    record = ''
    printrecord = False
    for idx ,ch in enumerate(sgfstr) :
        if ch == '[':
            state = '['
            record = '['
            printrecord = False
        elif ch in '()':
            record+=ch
            if state == '[':
                printrecord = True
            print(nearby(idx,sgfstr,10))
        elif ch == ']':
            state = ''
            if printrecord :
                print(record + ']')
            record = ''
        else:
            record += ch

def remove_braceletINsquare(sgfstr):
    ALLTAG = '\[[^\]]*\]'
    before_alltag = [ x for x in re.findall(ALLTAG, sgfstr) ]    
    after_alltag = [ x.replace('(','-').replace(')','-') for x in before_alltag]
    result = sgfstr
    # print('-------- before,after ------')
    for before,after in zip(before_alltag, after_alltag):
        if before != after:
            # print(before)
            # print(after)
            # print('--------------')    
            result = result.replace(before, after)
    # print('-------- before,after ------')
    return result

def remove_addition_information(sgfstr):
    sgfstr = sgfstr.replace('()','')
    new_sgfstr = '('
    layer = 1
    for idx, ch in enumerate(sgfstr[1:]):
        new_sgfstr += ch
        if ch in '()':
            layer += 1 if ch == '(' else -1
        if layer == 0:
            break
    return new_sgfstr

if __name__ == '__main__':
    SgfPath = './NoNull000'
    output_path = './Cleansgf'
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    #os.path.join(output_path)

    for filename in os.listdir(SgfPath):
        # if 'btjs_06' not in filename :
        #     continue
        fpath = os.path.join(SgfPath, filename)
        


        # detector = UniversalDetector()
        # print('####', filename)
        # with open(fpath, 'rb') as FILE:
        #     file_encoding = chardet.detect(FILE.read())['encoding']
        #     print('file_encoding', file_encoding)
        # if file_encoding == None:
        #     print('@ERROR', filename, 'cant find encoding')
        #     continue
        
# target = open('output.txt', 'wb')
# target.write(text.encode('ascii', 'ignore'))
# target.close()

        file_encoding = 'utf-8'
        with open(fpath, 'rb') as FILEREADER:
            sgfstr = FILEREADER.read().decode('utf-8','ignore')
            check_bracelet(sgfstr)
            sgfstr = remove_braceletINsquare(sgfstr)
            print('@@@')
            print('after remove_braceletINsquare')
            check_bracelet(sgfstr)
            sgfstr = remove_addition_information(sgfstr)
            print('after remove_addition_information')
            check_bracelet(sgfstr)
            with open( os.path.join(output_path, filename), 'w') as f:
                # print('---------------checksgfstr---------------')
                # check_sgfstr(sgfstr.replace(' ',''))
                # print('-----------------------------------------')
                f.write(sgfstr.replace(' ',''))
            # print(problem.sgfstr.replace('\n','').replace('(','@@@').replace(')','###').replace(' ',''))
            # for x in problem.sgfs:
            #     print(x.replace('\n',''))

    #sgfstr = '(abcd(e(f)(gh))(i(j)(k)(l)))'