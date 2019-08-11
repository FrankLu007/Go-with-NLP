# The program will divide the boards(GO) and the comments.

import os
import jieba
import monpa

replace_old = ['０', '１', '２', '３', '４', '５', '６', '７', '８', '９', '三·三', '：', '①', '②']
replace_new = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '三三', ':', '1', '2']

def is_alpha(character) :
	if len(character) != 1 :
		return False
	if character >= 'a' and character <= 'z' :
		return True
	if character >= 'A' and character <= 'Z' :
		return True
	return False

def is_number(number) :
	if len(number) != 1 :
		return False
	if number >= '0' and number <= '9' :
		return True
	return False

def meanless(sentence) :
	item = ['譜（', '以下類同', '以下同', '，下同']
	for word in item:
		if sentence.find(word) != -1 :
			return True
	if sentence in ['實戰。\n', '[要點\n', '實戰\n'] :
		return True
	if sentence[0] in ['一', '二', '三'] :
		return True
	return False

def replace(sentence, old, new) :
	if len(old) != len(new) :
		print('WTF')
		return []
	for index in range(len(old)) :
		sentence = sentence.replace(old[index], new[index])
	return sentence

def extra_analysis(sentence) :
	item = ['圖一', '圖二', '圖三', '圖四', '圖五', '圖六', '圖七', '圖八', '圖九', '圖十', \
			'▲', '圖1', '圖2', '圖3', '圖4', '圖5', '圖6', '圖7', '圖8', '圖9', '△', \
			'變化圖', '叄考圖']
	for word in item:
		if sentence.find(word) != -1 :
			return True
	for word_index in range(len(sentence)) :
		if word_index and is_alpha(sentence[word_index - 1]) and not is_alpha(sentence[word_index]) :
			return True
	return False

def special_case(sentence) :
	if len(sentence) <= 3 :
		return True
	return False

def get_input(filename) :
	chess = []
	comment = []
	with open(filename, 'r', errors = 'ignore') as file :
		while True :
			input_item = file.readline()
			if not input_item :
				break
			chess.append(input_item)
			comment.append(file.readline())

	file.close()
	if len(chess) != len(comment) :
		print('Input error !')
	print('Input from', filename, ': ', len(chess))
	return chess, comment

def log(function, output_item) :
	with open('abandon.txt', 'a') as file :
		file.write('')
		if function == meanless :
			file.write('----------meanless ' + str(len(output_item)) + '----------\n')
		elif function == extra_analysis :
			file.write('----------extra_analysis ' + str(len(output_item)) +  '----------\n')
		elif function == special_case :
			file.write('----------special_case ' + str(len(output_item)) +  '----------\n')
		for line in output_item :
			file.write(line)
		file.write('')
	file.close()

def filter(input_chess, input_comment, function, value) :
	chess = []
	comment = []
	abandon = []
	for line_index in range(len(input_chess)) :
		if function(input_comment[line_index]) == value :
			chess.append(input_chess[line_index])
			comment.append(input_comment[line_index])
		else :
			abandon.append(input_comment[line_index])

	if len(chess) != len(comment) or len(input_comment) != len(input_chess):
		print('filter error !')
	log(function, abandon)
	return chess, comment

def modify(comment) :
	changed = []
	output_comment = []
	for line in comment :
		changed.append(line)
		if line[1] == '：' or line[1] == ':' :
			line = line[2:]
			if line[0] == '-':
				line = line[1:]
		elif len(line) > 2 and (line[2] == '：' or line[2] == '譜' or line[2] == ':') :
			line = line[3:]
			if line[0] == '-':
				line = line[1:]
		elif len(line) > 3 and (line[3] == '：' or line[3] == '譜' or line[3] == ':'):
			line = line[4:]
			if line[0] == '-':
				line = line[1:]
		elif line[0] == '#' or line[0] == '*' :
			line = line[1:]
			if line[0] == '-':
				line = line[1:]
		elif line[0] == '（' :
			while len(line) > 1 and line[0] != '-':
				line = line[1:]
			if len(line) > 0 :
				line = line[1:]
		if len(line) and (line[0] == ':' or line[0] == '：') :
			line = line[1:]
		output_comment.append(line)
	log(modify, changed)
	return output_comment

def cut(input_comment) :
	output_comment = []
	for line in input_comment :
		output_comment.append(list(jieba.cut(line)))
		# print(output_comment[-1])
	return output_comment

def add_label(chess, comment) :
	output_comment = []
	num = 0
	unit = ['分白', '分', '小時', '勝', ':', '年', '日', '負的', '屆亞洲', '屆', '負', '目', '枚', '號的', '月', '年來訪', '分鐘', '目半', '段', '期', '局', '連勝', '目大空', '比', '人', '敗', '歲', '屆本', '年生', '年升']
	for line_index in range(len(comment)) :
		line = comment[line_index]
		tmp = []
		
		for word_index in range(len(line)) :
			if word_index + 1 < len(line) and line[word_index].isdigit() and line[word_index + 1] not in unit and line[word_index - 1] not in [':', '比']:
				dis = int(chess[line_index].split(' ')[1]) - int(line[word_index])
				if dis > 10 or dis < -50 :
					tmp.append(line[word_index])
					continue
				tmp.append('</step-' + str(dis) + '>')
				if dis < 0 and line[word_index - 1] not in ['~', '-']:
					num += 1
					#print(chess[line_index].split(' ')[0], int(chess[line_index].split(' ')[1]))
					#print(line[word_index - 1], line[word_index], line[word_index + 1])
			else :
				tmp.append(line[word_index])
		output_comment.append(tmp)
	print('# Label error : ', num)
	return output_comment

def save(chess, comment) :
	with open('board.txt', 'w') as file :
		for line in chess :
			file.write(line)
	file.close()

	max_length = 0
	with open('comment.txt', 'w') as file :
		for line in comment :
			if len(line) > max_length :
				max_length = len(line)
			for word in line :
				if word == '\n' :
					file.write('</end>\n')
				else :
					file.write(word)
					file.write(' ')
	file.close()

	print('Max Length :', max_length)

# main
chess, comment = get_input('data.txt')

if os.path.exists('abandon.txt') :
	os.remove('abandon.txt')

chess, comment = filter(chess, comment, meanless, False)
print('After filter \'meanless\', #data :', len(comment))
chess, comment = filter(chess, comment, extra_analysis, False)
print('After filter \'extra_analysis\', #data :', len(comment))
comment = modify(comment)
chess, comment = filter(chess, comment, special_case, False)
print('After filter \'special_case\', #data :', len(comment))
for index in range(len(comment)) :
	comment[index] = replace(comment[index], replace_old, replace_new)
comment = cut(comment)
comment = add_label(chess, comment)
save(chess, comment)
