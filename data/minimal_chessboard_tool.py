from functools import cmp_to_key
import numpy as np
import re
import datetime
import os
import time
import json
class coor_tool:
    def __init__(self , mode = 'sgf'):
        self.alphabet = 'abcdefghijklmnopqrs'
        self.sgf_eng = 'abcdefghijklmnopqrs'
        self.sgf_dict = dict()
        self.elf_eng = 'abcdefghjklmnopqrst' # no i
        self.elf_dict = dict()
        for i in range(len(self.elf_eng)):
            self.sgf_dict[self.sgf_eng[i]] = i
            self.elf_dict[self.elf_eng[i]] = i
        self.mode = mode
    def charnum2charchar(self, ch):
        return ch[0].lower()+ self.num2char( 19-int(ch[1:]) )
    def charchar2charnum(self, ch):
        return ch[0].upper()+ str(19 - self.char2num(ch[1]))
    def char2num(self, ch):
        if self.mode == 'elf':
            if(ch == 'i'):
                print('Error, char i shouldnt appear')
            return self.elf_dict[ch]
        else:
            return self.sgf_dict[ch]
    def num2char(self, num):
        if self.mode == 'elf':
            return self.elf_eng[num]
        else:
            return self.sgf_eng[num]
    def numnum2charchar(self, numnum):
        return self.num2char( numnum[0] )+self.num2char( numnum[1] )


def sgfcc2elfcn(charchar):
    A = coor_tool(mode = 'sgf')
    B = coor_tool(mode = 'elf')
    X = charchar[0]
    Y = charchar[1]
    return B.num2char(A.char2num(X)) + str(19 - A.char2num(Y))
ct_sgf = coor_tool('sgf')
def coor_type_casting( alphabet_pairs ):
    return [ ( ct_sgf.char2num(x[0]) , ct_sgf.char2num(x[1]) ) for x in alphabet_pairs  ]
def num_type_casting( coors ):
    return [ ct_sgf.numnum2charchar(coor) for coor in coors]


class min_sgfstr_tool:
    def __init__(self, sgf_str,filename):
        if len(sgf_str) == 0:
            return
        self.sgf_str = sgf_str
        self.has_spin = True
        self.filename = filename
        self.calculate_attribute_by_sgfstr()
    def calculate_attribute_by_sgfstr(self):
        self.has_spin = True
        AB = re.search('AB(\[..\])*', self.sgf_str)
        self.section_AB = [ x[1:3].lower() for x in re.findall('\[..\]', AB.group(0)) ] if AB else []
        AW = re.search('AW(\[..\])*', self.sgf_str)
        self.section_AW = [ x[1:3].lower() for x in re.findall('\[..\]', AW.group(0)) ] if AW else []
        self.section_B = [ x[1:3].lower() for x in re.findall('[^A]B(\[..\])+', self.sgf_str)]
        self.section_W = [ x[1:3].lower() for x in re.findall('[^A]W(\[..\])+', self.sgf_str)]
        self.sections  = [self.section_AB,self.section_AW, self.section_B,self.section_W]
        self.calculate_coor_by_section()
    def calculate_coor_by_section(self, union_flag = False):
        self.coor_AB = coor_type_casting( self.section_AB )
        self.coor_AW = coor_type_casting( self.section_AW )
        self.coor_B  = coor_type_casting( self.section_B )
        self.coor_W  = coor_type_casting( self.section_W )
        self.coors   = [ self.coor_AB , self.coor_AW , self.coor_B , self.coor_W ]

        if self.section_AB and self.section_AW:
            self.find_bounding_box()
            #self.original_bdbox = self.bounding_box
        else:
            self.error_msg('missing AB or missing AW.')
        if self.section_B or self.section_W:
            self.who_outside()
            self.answer_step , self.firststep_color = self.find_first_step()
        else:
            self.error_msg('missing B and missing W.')
    def error_msg(self,msg,type_flag='error'):
        content = '{}, {}: {}'.format(self.filename, type_flag,msg)
        print(content)
    def inbox( self, coor, bounding_box = None, distance2wall = 0):
        X = distance2wall #padding = 0
        if bounding_box == None:
            bounding_box = self.bounding_box
        #print([bounding_box[0]-X, bounding_box[1]+X,bounding_box[2]-X,bounding_box[3]+X], coor, end='')
        #print(outside_bounding_box ,coor, (coor[0] > bounding_box[0]-X) and (coor[0] < bounding_box[1]+X) and (coor[1] > bounding_box[2]-X) and (coor[1] < bounding_box[3]+X) )
        if (coor[0] >= bounding_box[0]-X ) and (coor[0] <= bounding_box[1]+X) and (coor[1] >= bounding_box[2]-X) and (coor[1] <= bounding_box[3]+X) :
            #print('DEL')
            return True
        #print('')
        return False
    def find_maxblock(self, target_block_color ,datasource = 'section_BW',mode = 'max'):
        def surrounding( xy ):
            def inside(x):
                return x>=0 and x<19
            tool = coor_tool()
            x = tool.char2num(xy[0])
            y = tool.char2num(xy[1])
            r = []
            for delta_x,delta_y in [ (1,0),(0,1),(0,-1), (-1,0) ]:
                if inside(x+delta_x) and inside( y+delta_y):
                    r.append(  tool.num2char( x+delta_x ) +  tool.num2char( y+delta_y) )
            return r
        #chess_onboard = self.section_B.copy() if self.firststep_color == 'b' else self.section_W.copy()
        chess_onboard = []
        print('target_block_color', target_block_color)
        chess_onboard.extend( self.section_AB.copy() if target_block_color == 'b' else self.section_AW.copy() )
        if('ae' in chess_onboard):
            print('ae is in chess_onboard')
        blocks =[]
        while len(chess_onboard) != 0:
            current_block = []
            need2check = [ chess_onboard.pop() ]
            if('ae' in need2check):
                print('ae is in need2check')
            while len(need2check) != 0:
                cur = need2check.pop()
                if 'ae' in cur:
                    print('ae is in cur')
                current_block.append(cur)
                for n in surrounding(cur):
                    if n in chess_onboard and n not in current_block:
                        need2check.append(n)
                        chess_onboard.remove(n)
            if( len(current_block) < 15):
                blocks.append(current_block)
        max_block_size = 0
        max_block = []
        for block in blocks:
            if len(block) > max_block_size:
                max_block = block
                max_block_size = len(block)
        count = 0
        for block in blocks:
            if len(block) >= max_block_size:
                count += 1
        if(count > 1):
            self.error_msg('May have multiple max target block','Warning')
        if mode == 'max':
            return max_block[0]
        elif mode =='all':
            # heuristic parition 
            print('blockinfo', blocks, len(blocks), [ x[0] for x in blocks ] )
            partA = []
            partB = []
            for block in [ x[0] for x in blocks ]:
                if block[0] in 'abcde' and block[1] in 'opqrs':
                    partA.append(block)
                else:
                    partB.append(block)
            return [partA,partB]
    def find_first_step(self):
        try:
            Bindex = re.search('[^AL]B\[', self.sgf_str).span()[0]
            Windex = re.search('[^AL]W\[', self.sgf_str).span()[0]
            if Bindex < Windex:
                return self.sgf_str[ Bindex+3 : Bindex+5] , 'b'
            else:
                return self.sgf_str[ Windex+3 : Windex+5] , 'w'
        except:
            self.error_msg('find_first_step: cant find first step.')
            return 'no_first_step', 'n'
    def BW2str(self):
        #print( '解答中黑白各有幾手: ', len(self.section_B) , len(self.section_W))
        #若白先走, 則先取一個白. 其他按照黑先白後之順序
        result_sgf = ''
        flag_first_step = 0
        if abs( len(self.section_B) - len(self.section_W) ) > 1:
            print('BW 數量可能有問題')
        if self.firststep_color == 'w':
            flag_first_step = 1
        for i in range(  len(self.section_B) + len(self.section_W) ):
            if i % 2 == flag_first_step:
                result_sgf += ';B[' + self.section_B[ int(i/2) ] + ']'
            else:
                result_sgf += ';W[' + self.section_W[ int(i/2) ] + ']'
        return result_sgf
    def make_info_dict(self, mask_type = 'automask'):
        A = dict()
        #self.targetblock =
        
        A['filename'] = self.filename
        A["type"] = 'config'
        A['rawsgf'] = self.sgf_str
        #A['origin_sgf'] = self.None_ABAW_SGF()

        #A["to_play"] =  self.firststep_color #temporaray setting
        A["black_crucial_stone"] = "" # section
        A["white_crucial_stone"] = "" # section
        A["category"] = "" # to_live,to_death, ko_live, ko_death, seki, unknown

        A['winning_color'] = self.firststep_color
        A['turn_color'] = self.firststep_color
        A['date'] = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime()) 
        A['answer_firstmove'] = self.answer_step
        A['mask_type'] = mask_type #default automask
        A['distance2wall'] = 4
        A['mask_filename'] = '' # if
        A['mask_sgf'] = '(;FF[4]CA[UTF-8]AP[GoGui:1.4.9]KM[6.5]DT[2020-03-25]AB[ap][bp][dp][cp][ep][eq][er][es][br][ar][bs]AW[cr][cs][bq])'
        A['add_pieces_before_masked'] = ''
        A['remove_pieces_before_masked'] = ''
        A['add_pieces_after_masked'] = ''
        A['remove_pieces_after_masked'] = ''
        self.A = A
    
    def after_mask_json(self, masked_sgf_str, allow_ko_flag = True):
        B = dict()
        B['date'] = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime()) 
        if self.origin_target_color == 'b':
            B["black_crucial_stone"] = self.targetblockcontent
            B["white_crucial_stone"] = ""
        else:
            B["white_crucial_stone"] = self.targetblockcontent
            B["black_crucial_stone"] = "" 

        if self.firststep_color == 'b':
            B["black_search_goal"] = self.target
            B["white_search_goal"] = "TOKILL" if self.target == 'TOLIVE' else 'TOLIVE'
        else:
            B["black_search_goal"] = "TOKILL" if self.target == 'TOLIVE' else 'TOLIVE'
            B["white_search_goal"] = self.target
        
        if allow_ko_flag:
            B["black_ko_rule"] = "allow_ko" #disallow_ko/allow_ko
            B["white_ko_rule"] = "allow_ko" #disallow_ko/allow_ko
        else:
            B["black_ko_rule"] = "allow_ko" #disallow_ko/allow_ko
            B["white_ko_rule"] = "allow_ko" #disallow_ko/allow_ko
        B["category"] = self.target # to_live,to_death, ko_live, ko_death, seki, unknown
    
        #B['mask_type'] = 'dual_region' #default automask

        print(self.A)
        for x in B.keys():
            if x not in self.A.keys():
                self.A[x] = B[x]
            elif self.A[x] == "":
                self.A[x] = B[x]
        #每次都可以更新的東西
        self.A['date'] = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime()) 
        self.A["masked_sgf_str"] = masked_sgf_str
        self.A['type'] = 'masked'
        return self.A

    def dictinfo_reorder(self):
        B = dict()
        order = ["filename","type","rawsgf","date","category","winning_color","turn_color","black_crucial_stone",
        "white_crucial_stone","black_search_goal", "white_search_goal", "black_ko_rule","white_ko_rule",
        "answer_firstmove","mask_type","distance2wall","mask_filename","mask_sgf","add_pieces_before_masked",
        "remove_pieces_before_masked","add_pieces_after_masked","remove_pieces_after_masked","masked_sgf_str"]
        for x in order:
            if x in self.A.keys():
                B[x] = self.A[x]
        self.A = B


    def check_ABAWBW_error_occur(self): #if there are same coor => error
        for x in self.sections:
            for y in self.sections:
                if x == y :
                    break
                for a in x:
                    if a in y:
                        self.error_msg('Find invalid sgf while doing cross check ABAW')
                        return False
        return True
    def find_bounding_box(self, box_width = 0,mode = 'spin'):
        '''
        AB[aa][bb][cc][ak] => (0,2,0,10)
        '''
        pnts = []
        for x in self.coors:
            pnts.extend(x)
        xs = [pnt[0] for pnt in pnts]
        ys = [pnt[1] for pnt in pnts]
        xs.sort()
        ys.sort()
        if mode == 'spin':
            self.bounding_box = (-1, xs[-1]+box_width , -1, ys[-1]+box_width)
        elif mode == 'origin':
                self.bounding_box = (xs[0]-box_width, xs[-1]+box_width , ys[0]-box_width, ys[-1]+box_width)
        if(xs[0] > 10 or ys[0] > 10):
            self.error_msg('May have sgf not spinned.')
        
    def who_outside(self):
        def distance2center(coor):
            return (coor[0]-9)**2+(coor[1]-9)**2
        if len(self.coor_AB) == 0:
            self.who_outside_color ='b'
            return
        distances = []
        for coor in self.coor_AB:
            distances.append( (distance2center(coor) , 'b',coor) )
        for coor in self.coor_AW:
            distances.append( (distance2center(coor) , 'w',coor) )
        distances.sort(key=lambda x:x[0])
        #print('distance:' ,distances)
        self.who_outside_color = distances[0][1]
        if distances[0][1] != distances[1][1]:
            self.error_msg('Ambigious bound', 'warning')
    def minus(self, bounding_box, distance2wall): #類似集合中的差集，把bounding_box + distance2wall中的棋子全部刪除
        
        buf = self.bounding_box
        self.bounding_box = bounding_box
        #print('#inminus', buf, bounding_box)
        print([len(x) for x in self.sections])
        
        for pieces in self.sections:
            self.numboard(coor_type_casting(pieces), color=1, mode='debug')
            #print(len(pieces),pieces)
            tool = coor_tool()
            for coor in coor_type_casting(pieces):
                piece = tool.num2char(coor[0])+tool.num2char(coor[1])
                if self.inbox( coor , distance2wall=1):
                    pieces.remove(piece)
            #print(len(pieces),count ,pieces)            
            self.numboard(coor_type_casting(pieces), color=1, mode='debug')
        
        
        self.bounding_box = buf
        print([len(x) for x in self.sections])
        self.section_AB.extend(self.section_B)
        self.section_AW.extend(self.section_W)
        print([len(x) for x in self.sections])
        return self.section_AB,self.section_AW

    def union_fix_mask(self, mask, distance2wall):
        #print('mask', len(mask.section_AB), len(mask.section_AW), len(mask.section_B), len(mask.section_W))
        AB,AW= mask.minus(self.bounding_box, distance2wall)
        AB.extend(self.section_AB)
        AW.extend(self.section_AW)
        self.section_AB = AB
        self.section_AW = AW
        return self.None_ABAW_SGF(target_flag=True,mode='fixmask')

    def coor_eliminate_bdbox(self, bdbox, coors):
        r = []
        for coor in coors:
            if not self.inbox(coor,bdbox):
                r.append(coor)
            else:
                #print(coor)
                pass
        return r

    def gen_automask_boundary(self, bdbox):
        tool = coor_tool()
        # mask_boundary = [tool.num2char(bdbox[1])+tool.num2char(i) for i in range(bdbox[3])]
        # mask_boundary.extend([ tool.num2char(j)+tool.num2char(bdbox[3]) for j in range(bdbox[1])])
        # mask_boundary.append( tool.num2char(bdbox[1])+tool.num2char(bdbox[3]) )
        mask_boundary = [ (bdbox[1], i) for i in range(bdbox[3])]
        mask_boundary.extend( [ (i, bdbox[3]) for i in range(bdbox[1])] )
        mask_boundary.append( (bdbox[1],bdbox[3]) )
        print('automask boundary')
        self.numboard(mask_boundary, color= 1, mode='debug')
        return [tool.num2char(x)+tool.num2char(y) for x,y in mask_boundary]
    
    def gen_automask_coor(self, need_how_much_terrioritory, paste_kozone_flag = True, eye_flag = True):
        outsides =[]
        remain_x_width = 19 - self.bounding_box[1] - 2
        remain_y_width = 19 - self.bounding_box[3] - 2
        if remain_x_width > need_how_much_terrioritory / 19 :
            print('@gen_automask_coorsituation1')
            x_width = int(need_how_much_terrioritory/19)
            outsides.append([ 18-x_width+1,18, 0 , 18])
            need_how_much_terrioritory -= cal_area( outsides[-1] )
            if need_how_much_terrioritory != 0:
                outsides.append( [18-x_width , 18-x_width, 18 - need_how_much_terrioritory +  1 ,18] )
                need_how_much_terrioritory -= cal_area( outsides[-1] )
        else:
            print('@gen_automask_coorsituation2')
            x_width = 18 - (self.bounding_box[1] + 2 ) + 1
            outsides.append([ 18-x_width+1,18, 0, 18])
            need_how_much_terrioritory -= cal_area( outsides[-1] )
            
            x_width = int(need_how_much_terrioritory / remain_y_width)
            
            outsides.append( [ self.bounding_box[1]+1 - x_width + 1 , self.bounding_box[1] + 1, self.bounding_box[3]+1, 18 ] )
            need_how_much_terrioritory -= cal_area( outsides[-1] )
            if need_how_much_terrioritory != 0:
                outsides.append( [self.bounding_box[1]+1 - x_width , self.bounding_box[1]+1 - x_width , 18 - need_how_much_terrioritory +  1 ,18] )
                need_how_much_terrioritory -= cal_area( outsides[-1] )
        temp_AB = []
        temp_AW = []
        inside = temp_AB if self.who_outside_color =='b' else temp_AW
        outside =  temp_AW if self.who_outside_color =='b' else temp_AB
        print('inbox', self.inbox)
        for i in range(19):
            for j in range(19):
                flag = 1
                if self.inbox( (i,j) ):
                    flag = 0
                for bdbox in outsides:
                    if self.inbox( (i,j), bounding_box=bdbox ):
                        outside.append( (i,j) )
                        flag = 0
                if flag:
                    inside.append( (i,j) )
        if eye_flag:
            try:
                temp_AB.remove((15,0))
                temp_AB.remove((18,0))
                temp_AW.remove((0,15))
                temp_AW.remove((0,18))
            except:
                self.error_msg('@gen_automask_coor Can\'t remove eyes')

        print('@gen_automask_coor')
        for x in outsides:
            print('@gen_automask_coor',x)
        print('need_how_much_terrioritory',need_how_much_terrioritory)
        self.numboard(temp_AB,mode='debug')
        self.numboard(temp_AW,mode='debug')
        
        return temp_AB,temp_AW    


    # def gen_automask_coor(self, need_how_much_terrioritory, paste_kozone_flag = True, eye_flag = True):
    #     remain_x_width = 19 - self.bounding_box[1] - 2
    #     remain_y_width = 19 - self.bounding_box[3] - 2
    #     outsides = []
    #     print('need_how_much_terrioritory', need_how_much_terrioritory)
    #     print('remain_x_width', remain_x_width)
    #     print('remain_y_width', remain_y_width)
    #     if remain_x_width*19 > need_how_much_terrioritory:
    #         print('situation1')
    #         outsides.append( [ self.bounding_box[1] + 2 , 18, 0, int(need_how_much_terrioritory / remain_x_width) - 1 ] )
    #         if cal_area(outsides[0]) < need_how_much_terrioritory:
    #             fix = need_how_much_terrioritory - cal_area(outsides[0])
    #             lastline_y = int(need_how_much_terrioritory / remain_x_width)
    #             outsides.append( [18 - fix + 1, 18, lastline_y , lastline_y ])
    #     else:
    #         print('situation2')
    #         outsides.append( [ self.bounding_box[1] + 2 , 18, 0, 18 ]  )
    #         tmp_need_how_much_terrioritory = need_how_much_terrioritory - cal_area(outsides[0])
    #         outsides.append( [ self.bounding_box[1] - (int(tmp_need_how_much_terrioritory / remain_y_width) ) + 2 , self.bounding_box[1]+1 ,self.bounding_box[3] + 2, 18 ] )
    #         if cal_area(outsides[1]) < tmp_need_how_much_terrioritory:
    #             fix = tmp_need_how_much_terrioritory - cal_area(outsides[1])
    #             lastline_x = self.bounding_box[1] - (int(tmp_need_how_much_terrioritory / remain_y_width) ) + 1
    #             outsides.append( [ lastline_x,lastline_x, self.bounding_box[3] + 2 , self.bounding_box[3] + 2 + fix - 1] ) 
    #     for rect in outsides:
    #         print('rect: ', rect, cal_area(rect))
        
        
    #     temp_AB = []
    #     temp_AW = []
    #     inside = temp_AB if self.who_outside_color =='b' else temp_AW
    #     outside =  temp_AW if self.who_outside_color =='b' else temp_AB
        

    #     print('inbox', self.inbox)
    #     for i in range(19):
    #         for j in range(19):
    #             flag = 1
    #             if self.inbox( (i,j) ):
    #                 flag = 0
    #             for bdbox in outsides:
    #                 if self.inbox( (i,j), bounding_box=bdbox ):
    #                     outside.append( (i,j) )
    #                     flag = 0
    #             if flag:
    #                 inside.append( (i,j) )
    #     if eye_flag:
    #         try:
    #             temp_AB.remove((15,0))
    #             temp_AB.remove((18,0))
    #             temp_AW.remove((0,15))
    #             temp_AW.remove((0,18))
    #         except:
    #             self.error_msg('@gen_automask_coor Can\'t remove eyes')

    #     # 清出一塊kozone要用的地方
    #     if paste_kozone_flag == True:
    #         #dbox = (12,18,0,8)
    #         bdbox = self.paste_kozone_bdbox
    #         temp_AB = self.coor_eliminate_bdbox(bdbox,temp_AB )
    #         temp_AW = self.coor_eliminate_bdbox(bdbox,temp_AW )
    #         self.numboard(temp_AB,mode='debug')
    #         self.numboard(temp_AW,mode='debug')


    #     return temp_AB,temp_AW
    
    def Combine_BMP2_ABAW(self, mask_boundary, mask_coors_AB, mask_coors_AW ,problem_section_AB,problem_section_AW ):
        tool = coor_tool()
        mask_boundary_AB = []
        mask_boundary_AW = []
        if self.who_outside_color == 'b':
            mask_boundary_AB = mask_boundary
        elif self.who_outside_color == 'w':
            mask_boundary_AW = mask_boundary
            
        self.section_AB = mask_boundary_AB + [ tool.num2char(coor[0])+tool.num2char(coor[1]) for coor in mask_coors_AB ] + problem_section_AB
        self.section_AW = mask_boundary_AW + [ tool.num2char(coor[0])+tool.num2char(coor[1]) for coor in mask_coors_AW ] + problem_section_AW
    
    def paste_kozone(self, mask_AB,mask_AW):
        if self.who_outside_color == 'w':
            BUF = self.paste_kozone_AB.copy()
            self.paste_kozone_AB = self.paste_kozone_AW.copy()
            self.paste_kozone_AW = BUF.copy()
        mask_AB.extend(self.paste_kozone_AB)
        mask_AW.extend(self.paste_kozone_AW)


    def deal_with_kozone(self, temp_AB ,temp_AW, rotate=False):
        def transpose():
            if rotate == True:
                self.coor_AB = [ (y,x) for x,y in self.coor_AB]
                self.coor_AW = [ (y,x) for x,y in self.coor_AW]
                self.who_outside_color = negative(self.who_outside_color)
                self.bounding_box = [self.bounding_box[2],self.bounding_box[3],self.bounding_box[0],self.bounding_box[1]]
            print('afterrotate')
            self.numboard()
        if rotate:
            transpose()

        ko_zone = self.find_ko_zone(self.original_bdbox)
        ko_zone_info = self.make_ko_zone(ko_zone)
        zone_color = ko_zone_info['zone_color']
        kozone_color_remove_coors = ko_zone_info['kozone_color_remove_coors']
        kozone_neg_color_coors = ko_zone_info['kozone_neg_color_coors']
        if rotate:
            transpose()
            A = [ (y,x) for x,y in kozone_color_remove_coors]
            B = [ (y,x) for x,y in kozone_neg_color_coors]
            kozone_color_remove_coors = A
            kozone_neg_color_coors = B
            self.numboard( A, color=1,mode='debug')
            self.numboard( B, color=1,mode='debug')

        if zone_color == 'b':
            for rm_coor in kozone_color_remove_coors + kozone_neg_color_coors:
                temp_AB.remove(rm_coor)
            for add_coor in kozone_neg_color_coors:
                temp_AW.append(add_coor)
        elif zone_color == 'w':
            for rm_coor in kozone_color_remove_coors + kozone_neg_color_coors:
                temp_AW.remove(rm_coor)
            for add_coor in kozone_neg_color_coors:
                temp_AB.append(add_coor)
    def kozone_relate2size(self):
        kozone_sizelist = [ ]
        for i in range(5,9):
            for j in range(i,12):
                kozone_sizelist.append((i,j))
        

        print(kozone_sizelist)
        self.bounding_box()


    def tworegion_automask(self,box_width =2 ,mask = None):
        self.find_bounding_box(2)
        self.origin_target_color = negative(self.who_outside_color)
        def gen_coors_by_rect(bdbox):
            result = []
            for x in range(bdbox[0],bdbox[1]+1):
                for y in range(bdbox[2],bdbox[3]+1):
                    result.append((x,y))
            return result
        def remove_coors(A,B):
            return list( set(A)-set(B) )
        def union_coors(A,B):
            return list(set(A).union(set(B)))
        self.find_bounding_box(box_width)
        print(self.bounding_box)

        outside_color_coors = gen_coors_by_rect([0,18,0,18])

        self.numboard(outside_color_coors, 2 , mode='debug')
        mask.find_bounding_box(mode='origin')
        print(mask.bounding_box)
        
        if self.who_outside_color == 'b': #這裡要反轉mask的顏色 (mask只有一種)
            mask_outside_color_coors = mask.coor_AW
            mask_inside_color_coors = mask.coor_AB
        else:
            mask_outside_color_coors = mask.coor_AW
            mask_inside_color_coors = mask.coor_AB
        
        outside_color_coors = remove_coors(outside_color_coors, gen_coors_by_rect(mask.bounding_box))
        outside_color_coors = remove_coors(outside_color_coors, gen_coors_by_rect(self.bounding_box))
        
        outside_color_coors.extend(mask_outside_color_coors)
        inside_color_coors = mask_inside_color_coors.copy()

        print('outside_color_coors0')
        self.numboard(outside_color_coors, 2 , mode='debug')
        print('inside_color_coors0')
        self.numboard(inside_color_coors, 1 , mode='debug')

        need_how_much_terrioritory = 174 if self.who_outside_color == 'b' else 180
        need_how_much_terrioritory -= cal_area(mask.bounding_box)
        temp_AB , temp_AW = self.gen_automask_coor(need_how_much_terrioritory ,paste_kozone_flag = False, eye_flag=False)

        inside_color_automask_coors = temp_AW if self.who_outside_color == 'b' else temp_AB
        # inside_color_coors = union_coors(inside_color_coors, inside_color_automask_coors)


        # mask_deltax = mask.bounding_box[1] - mask.bounding_box[0] + 1
        # mask_deltay = mask.bounding_box[3] - mask.bounding_box[2] + 1
        # compensate_mask_bdbox = [ self.bounding_box[1]+2, self.bounding_box[1] + mask_deltax +1, 0, mask_deltay - 1]
        # print(compensate_mask_bdbox)
        # inside_color_automask_coors = remove_coors(inside_color_automask_coors, gen_coors_by_rect(compensate_mask_bdbox))

        print('inside_color_automask_coors')
        self.numboard(inside_color_automask_coors, 2 , mode='debug')

        outside_color_coors = remove_coors(outside_color_coors, inside_color_automask_coors)
        inside_color_coors.extend(inside_color_automask_coors)

        print('outside_color_coors1')
        self.numboard(outside_color_coors, 2 , mode='debug')
        print('inside_color_coors1')
        self.numboard(inside_color_coors, 1 , mode='debug') 
        
        for x in self.conv(['111','111','111'],(3,3),step_size = (2,2), some_pieces=outside_color_coors,color=1) :
            outside_color_coors.remove((x[0]+1,x[1]+1))
        for x in self.conv(['222','222','222'],(3,3),step_size = (2,2), some_pieces=inside_color_coors,color=2):
            inside_color_coors.remove((x[0]+1,x[1]+1))

        if self.who_outside_color =='b':
            self.section_AB = num_type_casting(outside_color_coors) + self.section_AB
            self.section_AW = num_type_casting(inside_color_coors) + self.section_AW
        else:
            self.section_AB = num_type_casting(inside_color_coors) + self.section_AB
            self.section_AW = num_type_casting(outside_color_coors) + self.section_AW

        self.calculate_coor_by_section()
        print('final ver')
        self.numboard()
        return self.None_ABAW_SGF(mode='automask',check = True,target_flag=True,targetblock_flag=True)

    def dynamic_mask(self, box_width = 4,kozone = True,paste_kozone_flag = False, paste_kozone_AB = None, paste_kozone_AW=None):
        if paste_kozone_AB:
            self.paste_kozone_AB = paste_kozone_AB
            self.paste_kozone_AW = paste_kozone_AW           

        self.find_bounding_box(box_width)
        self.origin_target_color = negative(self.who_outside_color)
        # 1. given a bounding box
        # 2. bdbox裡面要全殺A)或活一塊B)
        #     A) bdbox 空 + 外圍的目 -/+ 貼目 > 184/178
        #     B) 外面的空 + bdbox中做活一小塊 -/+ 貼目 > 184/178

        need_how_much_terrioritory = 174 if self.who_outside_color == 'b' else 180
        bdbox = self.bounding_box
        print( 'indynamic', bdbox)
        
        mask_boundary = self.gen_automask_boundary(bdbox)
        mask_coors_AB, mask_coors_AW = self.gen_automask_coor(need_how_much_terrioritory, paste_kozone_flag)
        # self.numboard(temp_AB, 1 , mode='debug')
        # self.numboard(temp_AW, 2 , mode='debug')

        self.section_B.clear()
        self.section_W.clear()
        problem_section_AW = self.section_AW.copy()
        problem_section_AB = self.section_AB.copy()

        # self.numboard()
        # 會在 mask_coors 增加 kozone
        if kozone:
            if paste_kozone_flag:
                self.paste_kozone(mask_coors_AB, mask_coors_AW) 
                self.Combine_BMP2_ABAW( mask_boundary, mask_coors_AB, mask_coors_AW ,problem_section_AB,problem_section_AW)
            else:
                # 拼裝 / 要計算kozone之前要先把automask套在原題上面, 並重新計算coors
                self.Combine_BMP2_ABAW( mask_boundary, mask_coors_AB, mask_coors_AW ,problem_section_AB,problem_section_AW)
                self.calculate_coor_by_section()
                self.deal_with_kozone(mask_coors_AB, mask_coors_AW) 
                self.Combine_BMP2_ABAW( mask_boundary, mask_coors_AB, mask_coors_AW ,problem_section_AB,problem_section_AW)
                self.calculate_coor_by_section()
                self.numboard()
        else:
            self.Combine_BMP2_ABAW( mask_boundary, mask_coors_AB, mask_coors_AW ,problem_section_AB,problem_section_AW)
            self.calculate_coor_by_section()
        # 去掉一些點 x, 老師說不影響
        # 把 boundary 以及 automask 以及 原本題目
        tool = coor_tool()
        for x in self.conv(['111','111','111'],(3,3),step_size = (2,2), some_pieces=self.coor_AB,color=1) :
            self.coor_AB.remove((x[0]+1,x[1]+1))
            self.section_AB.remove( tool.numnum2charchar( [x[0]+1,x[1]+1] ) )
        for x in self.conv(['222','222','222'],(3,3),step_size = (2,2), some_pieces=self.coor_AW,color=2):
            self.coor_AW.remove((x[0]+1,x[1]+1))
            self.section_AW.remove( tool.numnum2charchar( [x[0]+1,x[1]+1] ) )
        self.calculate_coor_by_section()

        return self.None_ABAW_SGF(mode='automask',check = False,target_flag=True,targetblock_flag=True)
        
    def ABAW2str(self,auto_balance_length = True):
        #oldmask通常不會有 B ,W
        #黑先就代表 len(AB) == len(AW)
        #白先就代表 len(AB)+1 == len(AW)
        temp_AW =self.section_AW.copy()
        temp_AB =self.section_AB.copy()
        fix = abs(len(self.section_AB) - len(self.section_AW))
        print("before",fix , len(self.section_AB) , len(self.section_AW), self.firststep_color)
        if( len(self.section_AB) > len(self.section_AW) ):
            if( self.firststep_color == 'w'):
                fix -= 1
            temp_AW =  [''] * fix + self.section_AW.copy()
        else:
            if( self.firststep_color == 'w'):
                fix += 1
            temp_AB = [''] * fix + self.section_AB.copy()
        result_sgf = ''
        for i in range( max(len(temp_AB) , len(temp_AW) ) ):
            try:
                result_sgf += ';B[' + temp_AB[i] + ']'
            except:
                result_sgf += ';B[]' if auto_balance_length else ''
            try:
                result_sgf += ';W[' + temp_AW[i] + ']'
            except:
                result_sgf += ';W[]' if auto_balance_length else ''
        return result_sgf.replace(';B[];W[]','').replace(';W[];B[]','') #delete double pass
    def None_ABAW_SGF(self,target_flag = False, mode='automask',targetblock_flag=False,check = True): #通常不會有 B ,W
        if check and self.check_ABAWBW_error_occur() == 'INVALID':
            self.error_msg('check_ABAWBW_error_occur ERROR')
            return None
        if target_flag:
            if self.firststep_color == negative(self.origin_target_color):
                self.target = "TOKILL"
                self.target_first_color = "BLACK" if self.firststep_color == 'b' else "WHITE"
            else:
                self.target = "TOLIVE"
                self.target_first_color = "BLACK" if self.firststep_color == 'b' else "WHITE"
            if targetblock_flag:
                self.targetblock = self.find_maxblock(self.origin_target_color,datasource='mix', mode = 'all')
                content = ''
                for blocks in self.targetblock:
                    for block in blocks:
                        content += block + ','
                    content += '&'
                content = content[:-2]
                if content[0] == '&':
                    content = content[1:]
                self.targetblockcontent = content
                
            else:
                self.targetblock = ''
            #result_sgf = '(;CA[UTF-8]GM[1]AP[StoneBase:SGFParser.3.0]SZ[19]HA[0]'+"TARGET[{}-{}-{}]".format(self.target,self.target_first_color,self.targetblockcontent)
            result_sgf = '(;CA[UTF-8]GM[1]AP[StoneBase:SGFParser.3.0]SZ[19]HA[0]'
        else:
            result_sgf = '(;CA[UTF-8]GM[1]AP[StoneBase:SGFParser.3.0]SZ[19]HA[0]'
        if mode == 'automask':
            result_sgf += self.ABAW2str()
        elif mode == 'fixmask':
            result_sgf += self.ABAW2str()
        result_sgf += ')'
        return result_sgf

    def print_board(self):
        index_A = '0123456789abcdefghi'
        for c in ' '+index_A:
            print(c,end=' ')
        print()
        for i, line in enumerate(self.board):
            print(index_A[i],end=' ')
            for value in line:
                c = ''
                if value == 0:
                    c = '.'
                elif value==1: 
                    #c = '●'
                    c = 'x'
                elif value==2: 
                    c = 'o'
                    #c = '○'
                print(c, end=' ')
            print()
        print()

    def numboard(self, some_pieces = None, color = 1, mode = 'ABAW', print='True'):
        # mode ALL / ABAW / BW
        self.board = []
        for i in range(19):
            self.board.append([0]*19)
        if mode == 'ABAW':
            for coor in self.coor_AB:
                self.board[ coor[1] ][ coor[0] ] = 1
            for coor in self.coor_AW:
                self.board[ coor[1] ][ coor[0] ] = 2
        elif mode == 'debug':
            for coor in some_pieces:
                self.board[ coor[1] ][ coor[0] ] = color
        if print=='True':
            self.print_board()

    def find_ko_zone(self,bdbox):
        # bwwbbb
        # wwwbbb
        # wwwbbb
        # wwwbbb
        # wwwbbb  => b is zone_color

        zone_color = negative(self.who_outside_color)
        # 1. 找左上角
        zone_color_coors = self.coor_AB if zone_color == 'b' else self.coor_AW
        #neg_zone_color_coors = self.coor_AW if zone_color == 'b' else self.coor_AB
        print('zone_color', zone_color)
        print('bdbox', bdbox)
        most_left_zc_piece_xindex = 20
        for coor in zone_color_coors:
            if self.inbox(coor,bdbox):
                continue
            if coor[1] != 0: 
                continue
            if coor[0] < most_left_zc_piece_xindex:
                most_left_zc_piece_xindex = coor[0]
        print("most_left_zc_piece xy", (most_left_zc_piece_xindex,0))            
        
        if most_left_zc_piece_xindex > 13:
            self.error_msg('space not enough to create ko zone')
        
        xa = most_left_zc_piece_xindex+1
        xb = 18
        ya = 2
        yb = ya
        while (xa,yb) in zone_color_coors: 
            yb += 1
        yb -= 2
        ko_zone_bdbox = [xa,xb,ya,yb]
        print('ko_zone_bdbox', ko_zone_bdbox)
        return ko_zone_bdbox
    

    def make_ko_zone(self, ko_zone):
        xa,xb,ya,yb = ko_zone
        print('ko_zone', ko_zone)
        ylength = yb-ya+1
        ylength_replace_long = ylength - 2
        ylength_replace_short = ylength - 6
        print(ylength,ylength_replace_long,ylength_replace_short)
        kozone_color_remove_coors = []
        kozone_neg_color_coors = []

        short = ylength - 6 < 1

        for x in range(xa,xb+1):
            if (x-xa) % 2 == 0:
                if short:
                    temp_ya = ya
                    temp_yb = temp_ya + ylength_replace_long - 1 
                else:
                    temp_ya = ya+1
                    temp_yb = temp_ya + ylength_replace_long - 1 
            else:
                if short:
                    temp_ya = ya
                    temp_yb = temp_ya + ylength_replace_long - 3
                    kozone_color_remove_coors.extend([(x,temp_ya + ylength_replace_long)])
                else:
                    temp_ya = ya+3
                    temp_yb = temp_ya + ylength_replace_short - 1 
                    kozone_color_remove_coors.extend([(x,ya), (x,yb)])
            for y in range(temp_ya,temp_yb+1):
                kozone_neg_color_coors.append((x,y))
        
        
        self.numboard(some_pieces=kozone_neg_color_coors,mode='debug')
        self.numboard(some_pieces=kozone_color_remove_coors,mode='debug')

        print((xb,int((ya+yb)/2)-1))
        #if not short:
        kozone_neg_color_coors.remove((xb,int((ya+yb)/2)-1))
        kozone_color_remove_coors.append((xb,int((ya+yb)/2)-1))

        #self.numboard(some_pieces=kozone_color_remove_coors,mode='debug')
        # if short:
        #     kozone_neg_color_coors.remove((xa,ya))
        #     kozone_color_remove_coors.append((xa,ya))
        zone_color = negative(self.who_outside_color)
        return {'zone_color': zone_color, 'kozone_color_remove_coors': kozone_color_remove_coors, 'kozone_neg_color_coors': kozone_neg_color_coors}
        

    def conv(self, feature , feature_size, step_size=(1,1), some_pieces = None, color = 1):
        # given feature, shape 
        # return all of the match cases
        size_x = feature_size[0]
        size_y = feature_size[1]
        step_size_x = step_size[0]
        step_size_y = step_size[1]
        
        print('in conv')
        self.numboard(some_pieces, color, mode ='debug', print='True')
        ans = []
        for offset_x in range(0,19 - size_x,step_size_x):
            for offset_y in range(0,19 - size_y,step_size_y):
                flag = 1
                for x in range(size_x):
                    for y in range(size_y):                        
                        if self.board[offset_y+y][offset_x+x] != int(feature[y][x]) :        
                            flag = 0
                            break
                if flag:
                    print('ans append', (offset_x,offset_y))
                    ans.append( (offset_x,offset_y))
        print('ans', len(ans) , ans)
        return ans

def sgfs2strs(path):
    sgf_filenames = []
    for filename in os.listdir(path):
        if 'sgf' not in filename:
            continue
        sgf_filenames.append( filename )
    sgf_strs = []
    for filename in sgf_filenames:
        sgf_strs.append( sgf2str(os.path.join(path,filename)) )
    return sgf_strs, os.listdir(path)
def sgf2str(fpath):
    with open(fpath, 'r', encoding = 'UTF-8') as f:
        sgf = f.read()
        f.close()
    return sgf


def cal_area(A):
    return (A[3]-A[2]+1) * (A[1]-A[0]+1)
def mycmp( A,B, coor_fix = (18,0)):
    def Q(coor):
        return abs(coor_fix[0] - coor[0])+abs(coor_fix[1] - coor[1])
    if Q(A) == Q(B):
        return A[0] - B[0]
    else:
        return Q(A) - Q(B)

def parse_coor(sgf_str):
    coor = re.findall('(\[..\])', sgf_str)
    tool = coor_tool()
    r = []
    for x in coor:
        if x[1] in tool.alphabet and x[2] in tool.alphabet:
            r.append(x[1:3])
    return r
def str2sgf(fpath, sgf_str):
    with open(fpath , 'w', encoding='UTF-8') as f:
        f.write(sgf_str)
        f.close()
def negative(color):
    if color == 'b':
        return 'w'
    return 'b'

def test_coor_type_casting():
    print(coor_type_casting( ['ad']))  # 0,3

if __name__ == "__main__":
    # test_coor_type_casting()
    problem = min_sgfstr_tool("(;CA[UTF-8]GM[1]AP[StoneBase:SGFParser.3.0]SZ[19]HA[0]AEC[左上: 120頁, 黑先活下邊: 121頁, 白先活右上: 122頁, 白先活]AB[ae][be][cb][cc][cd][da]AW[bf][ca][ce][cf][db][dd][eb][ed](;B[ac]N[左上];W[ba];B[bb];W[ea];B[bd]C[正解])","test.sgf")
    problem.original_bdbox = problem.bounding_box
    
    print(problem.dynamic_mask(box_width=4, kozone=False))
    problem.kozone_relate2size()
    problem.numboard()
    # problem.conv(['002','001','001'],(3,3))
    