# coding=utf-8

# ParseSGF
import os
from minimal_chessboard_tool import *
import chardet
import sgf
from chardet.universaldetector import UniversalDetector

class CommentTool():
    def __init__(self):
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
        print(self.replaceinfo['<term>'][0])
    def Is_term_in_str(self, piece_comment):
        #print
        for term in self.replaceinfo['<term>'][0]:
            #print(term,piece_comment)
            if term in piece_comment:
                return term
        return None

    def parse_comment(self, comment ):
        for x in re.finditer('[0-9]+', comment):
            upcoming_str = look_for_upcoming_str( x.span()[1], comment)
            term = self.Is_term_in_str(upcoming_str)
            if term != None:
                return x.group(0), term


def look_for_upcoming_str(begin_idx, comment, interval= 10):
    upcoming_str = ''
    for i in range(begin_idx, begin_idx+interval):
        if i == len(comment):
            break
        ch = comment[i]
        if ch in '.,．０１２３４５６７８９0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
            break
        upcoming_str += ch
    return upcoming_str

def output_sgf_by_stepnum(gt,final_stepnum):
    sgf = '(;CA[UTF-8]SZ[19]AP[MultiGo:3.6.0]'
    cur_stepnum = 0
    #print('final_stepnum', final_stepnum)
    for node in gt:
        for key in node.properties.keys():
            if key in 'BW':
                sgf += ';{}[{}]'.format(key,node.properties[key][0])
                cur_stepnum += 1
                if cur_stepnum == int(final_stepnum):
                    return sgf+')'
    #print('cur_stepnum',cur_stepnum)

def parse_properties(pp):
    r = ''
    c = ''
    for key in pp.keys():
        #print(key)
        if key in 'BWC':
            r += ';{}[{}]'.format(key,pp[key][0])
        if key in 'C':
            c += pp[key][0]
    return r,c

def parse_gametree(gt):
    sgf = '(;CA[UTF-8]SZ[19]AP[MultiGo:3.6.0]'
    comments = []
    for node in gt:
        r,c = parse_properties(node.properties)
        sgf += r
        comments.append(c)
    sgf+=')'
    return sgf,comments


CT = CommentTool()
def parse_all_comments(comments):
    pair = dict()
    for c in comments:
        Q = CT.parse_comment( c )
        if Q != None:
            stepnum = Q[0]
            term = Q[1]
            pair[stepnum] = term
    return pair

if __name__ == '__main__':
    
    SgfPath = './Cleansgf'
    output_path = './Sgf_term_pair'
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    #os.path.join(output_path)
    for filename in os.listdir(SgfPath):
        # if 'btjs_06' not in filename :
        #     continue    
        
        fpath = os.path.join(SgfPath, filename)    
        with open(fpath, 'r') as f:
            sgf_str = f.read()
            try:
                collection = sgf.parse(sgf_str)
            except:
                print('####', filename, 'cant parse.')
                continue
            gametree = collection[0]
            singlepath_sgf,comments = parse_gametree(gametree)

            with open(os.path.join(output_path,filename), 'w') as f:
                f.write(singlepath_sgf)
            with open(os.path.join(output_path,filename).replace('.sgf','_comments.txt'), 'w') as f:
                content = ''
                for comment in comments:
                    content += comment.replace('\n','').replace(' ','') + '\n'
                f.write(content)
            with open(os.path.join(output_path,filename).replace('.sgf','_pair.txt'), 'w') as f:
                content = ''
                pair = parse_all_comments(comments)
                for stepnum in pair.keys():
                    content += '{} {} {}\n'.format(stepnum, pair[stepnum], output_sgf_by_stepnum(gametree, stepnum) )
                f.write(content)

            

# #sgf_str = '(abcd(e(f)(gh))(i(j)(k)(l)))'