import torch

board_size = 19
def position_decoder(position) :
	y = position % board_size
	x = int(board_size - (position - y) / board_size)
	y += ord('A')
	if y > ord('H') :
		y += 1
	y = chr(y)
	return y + str(x)

def get_feature_map(move_list, pre_N_step = 8) :
	board = torch.IntTensor(19, 19)
	board[:][:] = 0
	feature_map_list = []

	length = len(move_list)

	if length < pre_N_step :
		for i in range(pre_N_step - length) :
			feature_map_list.append([])
			feature_map_list.append([])

	for index, move in enumerate(move_list) :
		if move[0] == 'B' or move[0] == 'b':
			color = 1
		else :
			color = -1
		if not put_stone(board, int(move[1]), color) :
			print('Putting Stone causes error.')
			return []
		if index + pre_N_step >= length :
			feature_map_list.append((board.view(-1) == 1).nonzero().view(-1).tolist())
			feature_map_list.append((board.view(-1) == -1).nonzero().view(-1).tolist())

	# tmp = []
	# for i in feature_map_list[-2] :
	# 	tmp.append(position_decoder(i))
	# print(tmp)
	# tmp = []
	# for i in feature_map_list[-1] :
	# 	tmp.append(position_decoder(i))
	# print(tmp)
	if length % 2 == 1 :
		feature_map_list.append(0)
	else :
		feature_map_list.append(1)

	return feature_map_list



def put_stone(board, position, color) :

	if board.view(-1)[position] :
		print('Stone exists', position)
		return False

	board.view(-1)[position] = color
	if position < board_size * (board_size - 1) and board.view(-1)[position + board_size] == -color :
		board.view(-1)[get_group(board.view(-1), position + board_size)] = 0
	if position >= board_size and board.view(-1)[position - board_size] == -color :
		board.view(-1)[get_group(board.view(-1), position - board_size)] = 0
	if position % board_size != 0 and board.view(-1)[position - 1] == -color :
		board.view(-1)[get_group(board.view(-1), position - 1)] = 0
	if position % board_size != board_size - 1 and board.view(-1)[position + 1] == -color :
		board.view(-1)[get_group(board.view(-1), position + 1)] = 0

	if len(get_group(board.view(-1), position)) :
		print('Dead stone.', position)
		return False

	return True

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