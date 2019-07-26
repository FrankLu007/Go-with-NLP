# The program will divide the boards(GO) and the comments.

import os

replace_old = ['０', '１', '２', '３', '４', '５', '６', '７', '８', '９', '三·三', '：']
replace_new = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '三三', ':']

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
			file.write('----------meanless' + str(len(output_item)) + '----------')
		elif function == extra_analysis :
			file.write('----------extra_analysis' + str(len(output_item)) +  '----------')
		elif function == special_case :
			file.write('----------special_case' + str(len(output_item)) +  '----------')
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

def save(chess, comment) :
	with open('board.txt', 'w') as file :
		for line in chess :
			file.write(line)
	file.close()

	with open('comment.txt', 'w') as file :
		for line in comment :
			file.write(line)
	file.close()

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
save(chess, comment)
