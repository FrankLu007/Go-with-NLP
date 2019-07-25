def is_alpha(character):
	if len(character) != 1 :
		return False
	if character >= 'a' and character <= 'z' :
		return True
	if character >= 'A' and character <= 'Z' :
		return True
	return False

def test(sentence):
	if sentence == '實戰。\n' or sentence == '[要點\n' or sentence == '實戰':
		return False
	item = ['圖一', '圖二', '圖三', '圖四', '圖五', '圖六', '圖七', '圖八', '圖九', '圖十', '譜（', \
			'▲', '圖1', '圖2', '圖3', '圖4', '圖5', '圖6', '圖7', '圖8', '圖9', '以下類同。', '△', \
			'變化圖', '叄考圖', '以下同。']
	for word in item:
		if sentence.find(word) != -1 :
			return False
	return True

def pop(sentence, x):
	for i in range(x) :
		sentence.pop(0)

num = 0
comment = []
chess = []
with open('data.txt', 'r', errors = 'ignore') as file :
	while True :
		sentence = []
		input_item = file.readline()
		if len(input_item) == 0 :
			break
		tmp = input_item
		input_item = file.readline()
		num += 1
		if not test(input_item):
			continue
		for word in input_item :
			sentence.append(word.encode('utf-8').decode())
			if word != '\n':
				sentence.append(' ')
		chess.append(tmp)
		comment.append(sentence)
if len(chess) != len(comment) :
	print('Error in step 1!')
print('Original data size : ', num)

num = 0
output = []
output_chess = []
for line_index in range(len(comment)) :
	keep = 1
	if comment[line_index][0] == '一' or comment[line_index][0] == '二' or comment[line_index][0] == '三':
		continue
	for word_index in range(len(comment[line_index])) :
		if is_alpha(comment[line_index][word_index]) and not is_alpha(comment[line_index][word_index + 2]) :
			keep = 0
			break
	if keep != 0:
		num += 1
		output.append(comment[line_index])
		output_chess.append(chess[line_index])
if len(output_chess) != len(output) :
	print('Error in step 2!')
print('After first process, data size : ', num)

num = 0
chess = []
with open('comment.txt', 'w', errors = 'ignore') as file :
	for index in range(len(output)) :
		line = output[index]
		chess.append(output_chess[index])
		if line[2] == '：' :
			pop(line, 4)
			if line[0] == '-':
				pop(line, 2)
		elif len(line) > 4 and (line[4] == '：' or line[4] == '譜') :
			pop(line, 6)
			if line[0] == '-':
				pop(line, 2)
		elif len(line) > 6 and (line[6] == '：' or line[6] == '譜'):
			pop(line, 8)
			if line[0] == '-':
				pop(line, 2)
		elif line[0] == '#' or line[0] == '*' :
			pop(line, 2)
			if line[0] == '-':
				pop(line, 2)
		elif line[0] == '（' :
			while len(line) > 0 and line[0] != '-':
				pop(line, 1)
			if len(line) > 0 :
				pop(line, 1)
		elif len(line) > 8 and line[8] == '譜':
			pop(line, 10)
			if line[0] == '-':
				pop(line, 2)
		if len(line) < 5 or line[0] == ' ' or line == ['實', ' ', '戰', ' ', '\n'] or line[0] == '\n' or line == ['\u3000', ' ', '\u3000', ' ', '\n'] or line == ['-', ' ', '+', ' ', '\n'] :
			continue
		# if len(line) < 7:
		# 	print(line)
		num += 1
		for word in line :
			file.write(word)
with open('board.txt', 'w', errors = 'ignore') as file :
	for data in chess:
		for value in data:
			file.write(value)
print('Final data size : ', num)