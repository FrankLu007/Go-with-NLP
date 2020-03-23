import os


count = [0] * 361
board_size = 19

def position_decoder(position) :
	y = position % board_size
	x = int(board_size - (position - y) / board_size)
	y += ord('A')
	if y > ord('H') :
		y += 1
	y = chr(y)
	return y + str(x)

source = '../data/games/'
for sgf in os.listdir(source) :
	with open(source + sgf, 'r') as file :
		while True :
			tmp = file.readline().split(' ')
			if tmp[0] == 'B' and int(tmp[1]) == 72 :
				tmp = file.readline().split(' ')
				if tmp[0] == 'W' :
					count[int(tmp[1])] += 1
			else :
				break
			# tmp = file.readline().split(' ')
			# if tmp[0] == 'W' :
			# 	count[int(tmp[1])] += 1
			# else :
			# 	break
			# tmp = file.readline().split(' ')
			# if tmp[0] == 'B' :
			# 	count[int(tmp[1])] += 1
			# else :
			# 	break
			# tmp = file.readline().split(' ')
			# if tmp[0] == 'W' :
			# 	count[int(tmp[1])] += 1
			# else :
			# 	break
			# tmp = file.readline().split(' ')
			# if tmp[0] == 'B' :
			# 	count[int(tmp[1])] += 1
			break


pos = sorted(range(len(count)), key = lambda k : count[k], reverse = True)
for p in pos :
	print(position_decoder(p), count[p], end = ' ')
print(' ')