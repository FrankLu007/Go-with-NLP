comment = []
with open('comment.txt', 'r', errors = 'ignore') as file :
	while True :
		sentence = []
		input_item = file.readline()
		if len(input_item) == 0 :
			break
		for word in input_item :
			sentence.append(word.encode('utf-8').decode())
			if word != '\n':
				sentence.append(' ')
		comment.append(sentence)
with open('comment.txt', 'w', errors = 'ignore') as file :
	for line in comment :
		for word in line :
			file.write(word)