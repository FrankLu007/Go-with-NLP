#!/usr/bin/python3.6

word = ['飛', '掛角', '尖', '挖', 'A', '黑']
count = {}

for w in word :
	count[w] = 0

with open('data.txt', 'r', errors = 'ignore') as file :
	while True :
		tmp = file.readline()
		if not tmp :
			break
		tmp = file.readline()
		for w in word :
			if tmp.find(w) != -1 :
				count[w] += 1
				if w == '尖':
					print(w, tmp, end = '')

for w in count :
	print(w, count[w])

