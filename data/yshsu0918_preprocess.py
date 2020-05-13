# coding=utf-8

# ParseSGF
import os
from minimal_chessboard_tool import *
import chardet
from chardet.universaldetector import UniversalDetector

class tagparser:
    def __init__(self, sgf_str, CTAG_replace_lines=True):
        def make_tag_idx_pairs(tags, idx, tagname):
            if len(tags) != len(idx):
                print('ERROR')           
            return [ [tagname, idx[i], tags[i]] for i in range(len(idx))]
        
        self.sgf_formats = []
        self.sgf_str = sgf_str
        TagBPattern = '[^AP]B(\[..\])+'
        TagWPattern = '[^AP]W(\[..\])+'
        TagCPattern = '[^AP]C\[([^\]]*)\]'
        self.BTag = [ x[1:3].lower() for x in re.findall(TagBPattern, self.sgf_str)]
        self.BIdx = [ m.start(0) for m in re.finditer(TagBPattern, self.sgf_str)]

        self.WTag = [ x[1:3].lower() for x in re.findall(TagWPattern, self.sgf_str)]
        self.WIdx = [ m.start(0) for m in re.finditer(TagWPattern, self.sgf_str)]
        
        if CTAG_replace_lines:
            self.CTag = [ x.replace('\n','').replace(' ','') for x in re.findall(TagCPattern, self.sgf_str) ]
        else:
            self.CTag = [ x for x in re.findall(TagCPattern, self.sgf_str) ]
        self.CIdx = [ m.start(0) for m in re.finditer(TagCPattern, self.sgf_str)]

        self.LeftparenthesisIdx = [ ('(', m.start(0) ,'(') for m in re.finditer('\(', self.sgf_str)]
        self.RightparenthesisIdx = [ (')', m.start(0),')') for m in re.finditer('\)', self.sgf_str)]

        self.chrono = []

        for Q in [ (self.BTag, self.BIdx, 'B'), (self.WTag, self.WIdx, 'W'), (self.CTag, self.CIdx, 'C')]:
            self.chrono.extend( make_tag_idx_pairs( Q[0], Q[1], Q[2]) ) # tagname , char_idx, tags_content
        
        for Q in [self.LeftparenthesisIdx, self.RightparenthesisIdx ]:
            self.chrono.extend( list(Q) )
        


        self.chrono = sorted(self.chrono, key=lambda x: x[1])
        ##print(self.chrono[:5])

        self.load_replacement()

    def load_replacement(self):
        self.replaceinfo = dict()
        with open('replacement.json', 'r') as f:
            data = json.load(f)
            ##print(data)
            for x in data.keys():
                buf = data[x].split('|')
                ##print(len(buf))
                self.replaceinfo[x] = [ sorted(buf[0].split(' '), key=lambda x: len(x) ,reverse=True), 
                                        sorted(buf[1].split(' '), key=lambda x: len(x), reverse=True) ] 
        
        
        for x in self.replaceinfo.keys():
            self.replaceinfo[x][0] = [ x for x in self.replaceinfo[x][0] if len(x) ]
            self.replaceinfo[x][1] = [ x for x in self.replaceinfo[x][1] if len(x) ]
            
            ##print(self.replaceinfo[x][0],"@@@", self.replaceinfo[x][1])

    def AllComments2Templates(self):
        current_color = 'B'
        stepnum = 0
        for i, item in enumerate(self.chrono):
            if item[0] == 'C':
                chrono_content = ''
                for line in item[2].split('。') :
                    template, no_tag_flag = self.CTag2templates( line, current_color, stepnum)
                    chrono_content += line + '\n' + template + '\n'
                    
                self.chrono[i][2] = chrono_content
            elif item[0] in 'BW':
                current_color = item[0]
                stepnum += 1

    def CTag2templates(self, line, color, stepnum):

        original_line = line
        word_index = 0

        incremental_newline = ''
        last_idx = 0
        for x in re.finditer(r'[0-9]+', line):
            num = x.group()
            incremental_newline += line[last_idx: x.span()[0]] + '<step#{}>'.format(str(int(num)-int(stepnum)))
            last_idx = x.span()[1]

        line = incremental_newline + line[last_idx:]
        
        alphabet = 'abcdefghihklmnopqrstuvwxyz'
        for i, x in enumerate( line[:-1] ):
            if x in 'abcdeABCDE' and line[i+1] not in alphabet+alphabet.upper() :
                line = line[:i]+'☆'+line[i+1:]
        line = line.replace('☆', '<location>')

        for x in self.replaceinfo.keys():
            for del_seq in self.replaceinfo[x][1]:
                line = line.replace(del_seq, '')
            if x == '<location>':
                continue

            if x == '<color>' or x == '<rcolor>':
                ##print('@CTAG', x)
                if stepnum % 2 == 0:
                    line = line.replace('黑', '<rcolor>')
                    line = line.replace('白', '<color>')
                else:
                    line = line.replace('白', '<rcolor>')
                    line = line.replace('黑', '<color>')
                continue
            
            
            for replace_seq in self.replaceinfo[x][0]:
                #print(x)
                line = line.replace(replace_seq, x)

        

        return line, original_line != line
    
    def output(self):
        
        sgf = '(;CA[UTF-8]SZ[19]'
        content = ''
        self.step_sgf_comment = []
        stepnum = 0
        for i , item in enumerate(self.chrono):
            if item[0] == 'C':
                content += 'step #{}\n'.format(stepnum) + sgf + ')\n' + item[2] + '\n'
                self.step_sgf_comment.append( [str(stepnum), sgf, item[2]] )
            elif item[0] in 'BW':
                sgf += ';{}[{}]'.format( item[0] , item[2])
                stepnum += 1
        return content
    
    def cal_sgfs(self):
        current_sgf = ''
        history = []
        self.sgfs = []
        for i, item in enumerate( self.chrono):
            #print('step', i , item)
            if item[0] == 'C':
                #current_sgf += 'step #{}'.format(i) + sgf + ')\n' + item[2] + '\n'
                current_sgf += '{}[{}]'.format( item[0] , item[2])
            elif item[0] in 'BW':
                current_sgf += ';{}[{}]'.format( item[0] , item[2])
            elif item[0] == '(':
                history.append( current_sgf )
                #print('history', history)
            elif item[0] == ')':
                current_sgf = history[-1]
                del history[-1]
                #print(current_sgf)
                self.sgfs.append( current_sgf )
        

SgfPath = './sgf'

output_path = './output'
if not os.path.isdir(output_path):
    os.mkdir(output_path)

os.path.join(output_path)

for filename in os.listdir(SgfPath)[:20]:
    #if 'btjs_05.sgf' not in filename:
        #continue
    ##try:
    fpath = os.path.join(SgfPath, filename)
    detector = UniversalDetector()
    print('####', filename)
    with open(fpath, 'rb') as FILE:
        sgf_str = FILE.read()
        file_encoding = chardet.detect(sgf_str)['encoding']
    
    if file_encoding == None:
        ##print('@ERROR', filename, 'cant find encoding')
        continue

    with open(fpath, 'r', encoding = file_encoding) as FILEREADER:
        
        sgf_str = FILEREADER.read()
        #delete tag content
        # for x in re.finditer(r'[C|N]\[([^\]]*)\]', sgf_str):
        #     sgf_str = sgf_str.replace(x.group(),'')
        #x , sgftree = parseintotree( sgf_str )
        
        
        problem = tagparser( sgf_str )
        try:
            problem.cal_sgfs()
        except:
            print('Error: Cannot parse {}', filename)
            continue

        problem_output = []
        db = []
        for i , sgf_content in enumerate(problem.sgfs):
            single_path_problem = tagparser( sgf_content, CTAG_replace_lines = False )
            single_path_problem.AllComments2Templates()
            single_path_problem.output()
            for x in single_path_problem.step_sgf_comment:
                if x[0]+x[1] not in db:#stepnum + sgf in db
                    db.append(x[0]+x[1])
                    problem_output.append(x)
            #problem_output.append(['----','----','----'])
        
        content = ''
        for x in problem_output:
            content += x[0] + '\n' + x[1] + '\n' + x[2] + '\n'
        with open( os.path.join(output_path, '{}_traindata_output.txt'.format(filename.replace('.sgf','')) ) , 'w', encoding = file_encoding) as f:
            f.write(content)


#sgf_str = '(abcd(e(f)(gh))(i(j)(k)(l)))'