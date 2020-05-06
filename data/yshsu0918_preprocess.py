# ParseSGF
import os
from minimal_chessboard_tool import *
import chardet
from chardet.universaldetector import UniversalDetector


class tagparser:
    def __init__(self, sgf_str):
        def make_tag_idx_pairs(tags, idx, tagname):
            if len(tags) != len(idx):
                print('ERROR')
           
            return [ [tagname, idx[i], tags[i]] for i in range(len(idx))]
            

        self.sgf_str = sgf_str
        TagBPattern = '[^AP]B(\[..\])+'
        TagWPattern = '[^AP]W(\[..\])+'
        TagCPattern = '[^AP]C\[([^\]]*)\]'
        self.BTag = [ x[1:3].lower() for x in re.findall(TagBPattern, self.sgf_str)]
        self.BIdx = [ m.start(0) for m in re.finditer(TagBPattern, self.sgf_str)]

        self.WTag = [ x[1:3].lower() for x in re.findall(TagWPattern, self.sgf_str)]
        self.WIdx = [ m.start(0) for m in re.finditer(TagWPattern, self.sgf_str)]
        
        self.CTag = [ x.replace('\n','').replace(' ','') for x in re.findall(TagCPattern, self.sgf_str) ]
        self.CIdx = [ m.start(0) for m in re.finditer(TagCPattern, self.sgf_str)]

        self.chrono = []

        for Q in [ (self.BTag, self.BIdx, 'B'), (self.WTag, self.WIdx, 'W'), (self.CTag, self.CIdx, 'C')]:
            self.chrono.extend( make_tag_idx_pairs( Q[0], Q[1], Q[2]) ) # tagname , char_idx, tags_content

        self.chrono = sorted(self.chrono, key=lambda x: x[1])
        print(self.chrono[:5])

        self.abandon_content = []
        
        self.AllComments2Templates()

    def AllComments2Templates(self):
        current_color = 'B'
        for i, item in enumerate(self.chrono):
            if item[0] == 'C':
                chrono_content = ''
                for line in item[2].split('。') :
                    template, no_tag_flag = self.CTag2templates( line, current_color, i+1)
                    if no_tag_flag:
                        self.abandon_content.append( (i, template) )
                        chrono_content += 'Abandon(' + template + ')\n'
                    else:
                        chrono_content += template + '\n'
                    
                self.chrono[i][2] = chrono_content
            elif item[0] in 'BW':
                current_color = item[0]

    def CTag2templates(self, line, color, stepnum):
        word_index = 0
        no_tag_flag = True
        tmp = ''
        unit = ['分白', '分', '小時', '勝', ':', '年', '日', '負的', '屆亞洲', '屆', '負', '目', '枚', '號的', '月', '年來訪', '分鐘', '目半', '段', '期', '局', '連勝', '目大空', '比', '人', '敗', '歲', '屆本', '年生', '年升']
        while word_index < len(line) :
            flag = 1
            if line[word_index].isdigit() :
                num = int(line[word_index])
                while line[word_index + 1].isdigit() :
                    num = num * 10 + int(line[word_index + 1])
                    word_index += 1
                if word_index + 1 < len(line) and line[word_index + 1] not in unit:
                    tmp += ' </step-' + str(num - stepnum) + '>'
                else:
                    tmp += str(num)

            elif line[word_index] in ['黑', '白'] :
                if line[word_index] == '黑' and color == 'W':
                    tmp += '<rcolor>'
                else :
                    tmp += '<color>'
            elif line[word_index] in ['目', '子'] :
                tmp += '<territory>'
            elif line[word_index] in ['好','壞','優','劣']:
                tmp += '<pros&cons>'
            elif line[word_index] in ['死','活']:
                tmp += '<status>'
            elif line[word_index] in ['上','下','左','右','中']:
                tmp += '<location>'
            else:
                flag -= 1 
                tmp += line[word_index]
            if flag:
                no_tag_flag = False
            word_index += 1
        return tmp, no_tag_flag
    
    def output(self):
        
        sgf = '(;CA[UTF-8]SZ[19]'
        content = ''
        for i , item in enumerate(self.chrono):
            if item[0] == 'C':
                content += 'step #{}'.format(i) + sgf + ')\n' + item[2] + '\n'
            elif item[0] in 'BW':
                sgf += ';{}[{}]'.format( item[0] , item[2])                
        return content

SgfPath = './sgf'


for filename in os.listdir(SgfPath)[:5]:
    fpath = os.path.join(SgfPath, filename)
    detector = UniversalDetector()
    print('####', filename)
    with open(fpath, 'rb') as FILE:
        sgf_str = FILE.read()
        file_encoding = chardet.detect(sgf_str)['encoding']
    
    if file_encoding == None:
        print('@ERROR', filename, 'cant find encoding')
        continue

    with open(fpath, 'r', encoding = file_encoding) as FILEREADER:
        sgf_str = FILEREADER.read()
        print(sgf_str[:10])
        problem = tagparser(sgf_str)
        print( problem.output() )
        
        