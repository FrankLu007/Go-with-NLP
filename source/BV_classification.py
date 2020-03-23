from multiprocessing import Process, Queue, Pool

def load_data(source) :

	file_list = os.listdir(source)
	filename = source + file_list[random.randint(0, len(file_list) - 1 - 256 * 800)]

	game = []
	with open(filename, 'r') as file :
		while True :
			tmp = file.readline().split(' ')
			if tmp[0] == '' :
				break
			if tmp[0] == 'C' :
				continue
			if game and game[-1][0] == tmp[0] :
				break
			game.append(tmp)
	if len(game) > 0 :
		return game
	else :
		return load_data(source)

def prepare_data(input_queue, source, batch_size) :

	while True :
		batch_data = [None] * batch_size
		target = [None] * batch_size
		move = [None] * batch_size

		for index in range(batch_size) :
			while True :
				data = load_data(source)
				move_number = random.randint(0, len(data) - 1)
				feature_map = get_feature_map(data[: move_number])
				if len(feature_map) == 0 :
					# something wrong with this data, so we abandon it
					continue
				else :
					batch_data[index] = feature_map
					target[index] = int(data[move_number][1])
					move[index] = int(move_number)
					break
		input_queue.put([batch_data, target, move], False)