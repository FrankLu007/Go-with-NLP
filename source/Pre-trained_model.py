import os
import torch
import random
import time
from argparser import get_args
from model import CNN
from board import get_feature_map
from multiprocessing import Process, Queue, Pool

def position_decoder(position) :
	y = position % 19
	x = int(19 - (position - y) / 19)
	y += ord('A')
	if y > ord('H') :
		y += 1
	y = chr(y)
	return y + str(x)
def position_encoder(posstr) :
	position = 19 * (19 - int(posstr[1:])) + ord(posstr[0]) - ord('A')
	if ord(posstr[0]) > ord('H') :
		position -= 1
	return position

# load a single sgf file
# args : `source` : file directory ended with '/'
# return a list of move
# format of each element : [{color | 'B' or 'W'}, {[position | 0~360]}]
def load_data(source) :

	file_list = os.listdir(source)
	filename = source + file_list[random.randint(0, len(file_list) - 1)]

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
	if len(game) > 150 :
		return game
	else :
		return load_data(source)

# def prepare_testing_data(source, batch_size) :
# 	batch_data = [None] * batch_size
# 	target = [None] * batch_size

# 	for index in range(batch_size) :
# 		while True :
# 			data = load_data(source, 'test')
# 			move_number = random.randint(0, len(data) - 1)
# 			feature_map = get_feature_map(data[: move_number])
# 			if len(feature_map) == 0 :
# 				# something wrong with this data, so we change it
# 				continue
# 			else :
# 				batch_data[index] = feature_map
# 				target[index] = int(data[move_number][1])
# 				break
# 	return batch_data, target

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

def print_data(queue, record_file) :
	

	while True :
		data = queue.get()
		if len(data) == 0 :
			break
		acc = 0.0
		for index, result in enumerate(data[2]) :
			if result.index(max(result)) == data[3][index] :
				acc += 1.0
		acc /= len(data[2])
		print('#' + data[0])
		print('Loss :', data[1])
		print('Accuracy :', acc)
		if record_file != None :
			with open(record_file, 'a') as file :
				file.write(str(data[1]) + ' ' + str(acc) + '\n')

if __name__ == '__main__' :

	args = get_args()
	device = torch.device(('cuda:' + args['gpu']) if torch.cuda.is_available() else 'cpu')
	encoder = CNN(device)

	if args['load_weight'] != None and os.path.isfile(args['load_weight']) :
		encoder.load_state_dict(torch.load(args['load_weight'], map_location = device))
	# if args['record'] != None and os.path.isfile(args['record']) :
		# os.remove(args['record'])

	encoder.to(device) # transfer models to GPU
	optimzer = torch.optim.SGD(encoder.parameters(), lr = args['learning_rate'], momentum = 0)
	loss_func = torch.nn.CrossEntropyLoss()

	epoch = 0
	input_data_queue = Queue(32) # set max size to 32
	output_data_queue = Queue()

	data_preparing_thread = []
	for index in range(args['thread']) :
		data_preparing_thread.append(Process(target = prepare_data, args = (input_data_queue, args['input_board'], args['batch_size']), daemon = True))
		data_preparing_thread[-1].start()

	data_printing_thread = Process(target = print_data, args = (output_data_queue, args['record']), daemon = True)
	data_printing_thread.start()

	# print('Preparing Test Data...')
	# pool = Pool()
	# test_data_list = [pool.apply_async(prepare_testing_data, (args['input_board'], args['batch_size'])) for i in range(1)]
	# pool.close()
	# for index, data in enumerate(test_data_list) :
	# 	data = data.get()
	# 	test_data_list[index] = [data[0], torch.LongTensor([i for i in data[1]]).to(device)]
	# with torch.no_grad() :
	# 	loss = 0.0
	# 	for feature_map, label in test_data_list :
	# 		output = encoder(feature_map)
	# 		loss += loss_func(output, label)
	# pool.join()

	print('Start Training...')
	# output_data_queue.put(['INIT', str(loss.item() / 1), output.tolist(), label], False)

	acc = [0.0] * 500
	num = [0.0] * 500
	while epoch < args['epoch'] :

		feature_map, label, move = input_data_queue.get()
		
		output = encoder(feature_map)
		label_cuda = torch.LongTensor([i for i in label]).to(device) # transfer label to GPU
		loss = loss_func(output, label_cuda)
		optimzer.zero_grad()
		output_data_queue.put([str(epoch), str(loss.item()), output.tolist(), label, move], False)

		for index, result in enumerate(output) :
			num[move[index]] += 1.0
			if torch.argmax(result) == label_cuda[index] :
				acc[move[index]] += 1.0
		loss.backward()
		optimzer.step()

		for index, data in enumerate(feature_map) :
			if move[index] != 0:
				continue
			print(position_decoder(label[index]), position_decoder(torch.argmax(output[index])), output[index][torch.argmax(output[index])])
			for pos in range(361) :
				if pos > 0 and pos % 19 == 0 :
					print('')
				if pos in data[12] :
					print('X', end = '')
				elif pos in data[13] :
					print('O', end = '')
				else :
					print('.', end = '')
			print('')
			for pos in range(361) :
				if pos > 0 and pos % 19 == 0 :
					print('')
				if pos in data[14] :
					print('X', end = '')
				elif pos in data[15] :
					print('O', end = '')
				else :
					print('.', end = '')
			print('')
			print(data[16])
			print("GG")
		# with torch.no_grad() :
		# 	loss = 0.0
		# 	for feature_map, label in test_data_list :
		# 		output = encoder(feature_map)
		# 		loss += loss_func(output, label)

		epoch += 1

		if epoch % 10 == 0 and args['save_weight'] != None :
			torch.save(encoder.state_dict(), args['save_weight'])

	if args['save_weight'] != None :
		torch.save(encoder.state_dict(), args['save_weight'])

	while not output_data_queue.empty() :
		a = 1
	for i in range(200) :
		# if i % 10 == 0:
			# print('')
		if num[i] == 0 :
			print('-1', end = '\n')
		else :
			print(acc[i], num[i], end = '\n')
		
