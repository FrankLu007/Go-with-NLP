import os
import torch
import random
import sys
from board import get_feature_map
from model import CNN

board = torch.FloatTensor(19, 19) # (1, 0, -1) = (black, blank, white)
board_size = 19
move_list = []
device = torch.device('cpu')
cnn = CNN(device, num_block = 3)
cnn.load_state_dict(torch.load('C:\\Users\\Frank\\Go-with-NLP\\source\\CNN_C17_H256_B3.bin', map_location=device))
cnn.eval()
print_without_newline = lambda message : print(message, end = '')
reply = lambda message : print('=' + message, end = '\n\n')

def position_encoder(posstr) :
	position = board_size * (board_size - int(posstr[1:])) + ord(posstr[0]) - ord('A')
	if ord(posstr[0]) > ord('H') :
		position -= 1
	return position

def position_decoder(position) :
	y = position % board_size
	x = int(board_size - (position - y) / board_size)
	y += ord('A')
	if y > ord('H') :
		y += 1
	y = chr(y)
	return y + str(x)

def set_board_size(command) :
	global board_size, board
	board_size = int(command.split(' ')[1])
	board = torch.FloatTensor(board_size, board_size)
	clear('')
	return 'OK'

def clear(command) :
	global board, move_list
	board[:][:] = 0
	move_list = []
	return 'OK'

def put_stone(command) :
	global move_list, board

	color_expression = command.split(' ')[1]
	if color_expression == 'B' or color_expression == 'b' :
		color = 1
	elif color_expression == 'W' or color_expression == 'w' :
		color = -1
	else :
		return 'OK'

	position = position_encoder(command.split(' ')[2])

	board.view(-1)[position] = color
	if position < board_size * (board_size - 1) and board.view(-1)[position + board_size] == -color :
		board.view(-1)[get_group(board.view(-1), position + board_size)] = 0
	if position >= board_size and board.view(-1)[position - board_size] == -color :
		board.view(-1)[get_group(board.view(-1), position - board_size)] = 0
	if position % board_size != 0 and board.view(-1)[position - 1] == -color :
		board.view(-1)[get_group(board.view(-1), position - 1)] = 0
	if position % board_size != board_size - 1 and board.view(-1)[position + 1] == -color :
		board.view(-1)[get_group(board.view(-1), position + 1)] = 0

	move_list.append(['B' if color == 1 else 'W', str(position)])
	return 'OK'

def get_group(flatten_board, start_position, liberty = 0) :
	group = []
	life = []
	queue = []
	color = flatten_board[start_position]

	queue.append(start_position)
	group.append(start_position)
	while len(queue) :
		position = queue[0]
		queue.pop(0)
		if position < board_size * (board_size - 1) : 
			if flatten_board[position + board_size] == 0 :
				life.append(position + board_size)
			elif flatten_board[position + board_size] == color and position + board_size not in group :
				queue.append(position + board_size)
				group.append(position + board_size)
		if position >= board_size : 
			if flatten_board[position - board_size] == 0 :
				life.append(position - board_size)
			elif flatten_board[position - board_size] == color and position - board_size not in group :
				queue.append(position - board_size)
				group.append(position - board_size)
		if position % board_size != 0 : 
			if flatten_board[position - 1] == 0 :
				life.append(position - 1)
			elif flatten_board[position - 1] == color and position -1 not in group :
				queue.append(position - 1)
				group.append(position - 1)
		if position % board_size != board_size - 1 : 
			if flatten_board[position + 1] == 0 :
				life.append(position + 1)
			elif flatten_board[position + 1] == color and position + 1 not in group:
				queue.append(position + 1)
				group.append(position + 1)

		if len(life) > liberty :
			return []

	return group

def display(command) :
	global board

	color_expression = command.split(' ')[1]
	if color_expression == 'b' or color_expression == 'B':
		color = 1
	else :
		color = -1

	candidate = demo()
	# print(candidate)
	position_list = sorted(range(len(candidate)), key = lambda k : candidate[k], reverse = True)
	for pos in position_list :
		print(position_decoder(pos), end = ' ')
	print('')


	# latest_move = int(move_list[-1][1]) if len(move_list) else -1
	# for index, stone in enumerate(board.view(-1)) :
	# 	if index % board_size == 0 :
	# 		print(' ')
	# 	if index == latest_move :
	# 		print_without_newline('(')
	# 	if stone == 0 :
	# 		print_without_newline('-')
	# 	elif stone == 1 :
	# 		print_without_newline('X')
	# 	else :
	# 		print_without_newline('O')
	# 	if index == latest_move :
	# 		print_without_newline(')')
	# 	elif index % board_size == board_size - 1 or index + 1 != latest_move :
	# 		print_without_newline(' ')
	# print('')

	return 'OK'

def generate_move(command) :
	global board

	color_expression = command.split(' ')[1]
	if color_expression == 'b' or color_expression == 'B':
		color = 1
	else :
		color = -1

	candidate = demo()
	# print(candidate)
	position_list = sorted(range(len(candidate)), key = lambda k : candidate[k], reverse = True)
	for pos in position_list :
		print(position_decoder(pos), candidate[pos].item(), end = ' ')


	# random move generator
	# candidate = [i for i in range(361)]
	# random.shuffle(candidate)
	for position in position_list :
		ret = position_decoder(position)
		print(ret)
		if board.view(-1)[position] == 0 :
			put_stone('play ' + command.split(' ')[1] + ' ' + ret)
			if len(get_group(board.view(-1), position)) != 0:
				move_list.pop(-1)
				board.view(-1)[position] = 0
			else :
				return ret

	return 'PASS'

def demo() :
	with torch.no_grad() :
		tmp = get_feature_map(move_list)
		sys.stderr.write(str(tmp[-1]) + '\n')
		for index in range(361) :
			if index % 19 == 0 :
				sys.stderr.write('\n')
			if index in tmp[14] :
				sys.stderr.write('X')
			elif index in tmp[15] :
				sys.stderr.write('O')
			else :
				sys.stderr.write('.')
		sys.stderr.write('\n\n')
		
		return cnn([tmp]).view(361)

# Command Response
reply_text = {'name' : '你好',\
		 'version' : '0.0.1', \
		 'list_commands' : 'display : show the board\n', \
		 'protocol_version' : '2'}

reply_func = {'clear_board' : clear, \
			  'boardsize' : set_board_size, \
			  'play' : put_stone, \
			  'display' : display, \
			  'genmove' : generate_move}

while True:
	command = input()
	if command in reply_text :
		reply(reply_text[command])
	elif command.split(' ')[0] in reply_func :
		reply(reply_func[command.split(' ')[0]](command))
	else :
		reply('Error : Unrecognized Command')