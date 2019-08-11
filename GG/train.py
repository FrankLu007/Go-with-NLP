import torch
import torch.nn as nn
import torch.optim as optim
from argparser import *
import random

# args
SENTENCE_LENGTH = 719
BATCH_SIZE = 32
EPOCH_NUM = 10000
LEARNING_RATE = 0.0001
NUM_TEST = 25 * BATCH_SIZE
NUM_VALIDATION = 25 * BATCH_SIZE

def error_message(info) :
	print('Error :', info)
	quit()

def cut_dataset(data, size) : # [1- rate], [rate]
	random.shuffle(data)
	return data[size : ], data[0 : size]

def get_batch(data) :
	random.shuffle(data)
	return data[0 : BATCH_SIZE]

class DATA() :
	def __init__(self, board_file, comment_file, embedding_file) :

		# GPU
		self.comment = torch.LongTensor([])
		self.board = torch.tensor([])
		self.table_vector = torch.tensor([])

		# CPU
		self.table_word = []
		self.num_step = []
		self.num_data = 0
		self.num_word = 0
		self.sentence_length = SENTENCE_LENGTH
		self.embedding_dim = 0

		with open(embedding_file, 'r', errors = 'ignore') as file :

			tmp = file.readline().split(' ')
			self.num_word = int(tmp[0])
			self.embedding_dim = int(tmp[1])

			while True :
				tmp = file.readline().split(' ')
				tmp.pop(-1) # abandon the newline	
				if not tmp :
					break
				word = tmp[0]
				tmp.pop(0)
				if len(tmp) != self.embedding_dim :
					error_message('embedding data error')
				vector = torch.FloatTensor([float(x) for x in tmp]).view(1, self.embedding_dim)
				self.table_word.append(word)
				self.table_vector = torch.cat((self.table_vector, vector), dim = 0)
			file.close()

		print('# Word :', self.num_word)


		with open(board_file, 'r', errors = 'ignore') as file :

			while True :
				tmp = file.readline().split(' ')
				tmp.pop(-1) # abandon the newline
				if not tmp :
					break
				tmp.pop(0) # abandon the name of the game
				self.num_step.append(int(tmp[0]))
				tmp.pop(0) # abandon the number of step
				if len(tmp) != 361 :
					error_message('board data error')
				self.board = torch.cat((self.board, torch.FloatTensor([float(x) for x in tmp]).view(1, 19, 19)), dim = 0)
			file.close()

		with open(comment_file, 'r', errors = 'ignore') as file :
			while True :
				tmp = file.readline().split(' ')
				tmp.pop(-1) # abandon the newline
				if not tmp :
					break
				sentence = torch.LongTensor([self.table_word.index('</s>')])
				for word in tmp :
					if word not in self.table_word :
						error_message('the word ' + word + ' is not in table.')
					else :
						sentence = torch.cat((sentence, torch.LongTensor([self.table_word.index(word)])), dim = 0)
				if len(sentence) < self.sentence_length :
					sentence = torch.cat((sentence, torch.LongTensor([-1 for i in range(self.sentence_length - len(sentence))])))
				self.comment = torch.cat((self.comment, sentence.view(1, self.sentence_length)), dim = 0)
		file.close()

		if len(self.comment) != len(self.board) :
			error_message('size is not match')
		else :
			self.num_data = len(self.board)
		print('# Data :', self.num_data)

class NET(nn.Module):
	def __init__(self, data, device):
		super(NET, self).__init__()

		# nn.Conv2d(in channel, out channel, kernel size, stride, padding)
		# nn.BatchNorm2d(batch size)
		tmp = nn.Sequential(nn.Conv2d(1, 1, 3, 1, 1), nn.BatchNorm2d(1))

		# model
		self.cnn_list = nn.ModuleList([tmp for i in range(8)])
		self.relu = nn.ReLU()
		self.embed = nn.Embedding.from_pretrained(data.table_vector)
		self.linear = nn.Linear(361, data.embedding_dim)
		self.lstm = nn.LSTMCell(data.embedding_dim, data.embedding_dim, bias = True)
		self.lstm_decoder = nn.Linear(data.embedding_dim, data.num_word)

		# data
		self.num_data = data.num_data
		self.num_word = data.num_word
		self.embedding_dim = data.embedding_dim
		# self.table_vector = torch.tensor([])

		# for vector in data.table_vector :
		# 	self.table_vector = torch.cat((self.table_vector, vector.view(1, data.embedding_dim)), dim = 0)
		# self.table_vector = self.table_vector.to(device)

	def forward(self, board, comment, training = True) :

		self.zero_grad()

		# GO
		lstm_input = torch.tensor([]).to(device)

		for index in range(BATCH_SIZE) :

			data1 = self.cnn_list[0](board[index].view(1, 1, 19, 19))
			data1 = data2 = self.relu(data1)

			for cnn_index in range(1, 6, 2) :
				data1 = self.cnn_list[cnn_index](data1)
				data1 = self.relu(data1)
				data1 = self.cnn_list[cnn_index + 1](data1)
				data1 = data2 = self.relu(data1 + data2)

			data1 = self.cnn_list[7](data1)
			data1 = self.relu(data1)
			data1 = self.linear(data1.view(361))

			lstm_input = torch.cat((lstm_input, data1.view(1, self.embedding_dim)), dim = 0)

		#NLP
		output = torch.tensor([]).to(device)
		each_word = torch.tensor([]).to(device)
		zero = torch.zeros(1, self.embedding_dim).to(device)

		h, c = self.lstm(lstm_input)
		for index in range(BATCH_SIZE) :
			tmp = self.lstm_decoder(h[index]).view(1, 1, self.num_word)
			each_word = torch.cat((each_word, tmp), dim = 0)
		output = torch.cat((output, each_word), dim = 1)

		for i in range(1, SENTENCE_LENGTH):

			# decide the next input
			if training :
				tmp = torch.tensor([]).to(device)
				for j in range(BATCH_SIZE) :
					if comment[j][i] == -1 :
						tmp = torch.cat((tmp, zero), dim = 0)
					else :
						tmp = torch.cat((tmp, self.embed(comment[j][i]).view(1, self.embedding_dim)), dim = 0)
			else :
				tmp = h

			h, c = self.lstm(tmp, (h, c))

			# decode the output
			each_word = torch.tensor([]).to(device)
			for index in range(BATCH_SIZE) :
				tmp = self.lstm_decoder(h[index]).view(1, 1, self.num_word)
				each_word = torch.cat((each_word, tmp), dim = 0)
			output = torch.cat((output, each_word), dim = 1)

		return output

# main

device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
data = DATA('board.txt', 'comment.txt', 'embeddings/embedding_256D.txt')
model = NET(data, device).to(device)
# model.load_state_dict(torch.load('tmp.bin', map_location = device))
optimzer = optim.Adam(model.parameters(), lr = LEARNING_RATE)
loss_func = nn.CrossEntropyLoss(ignore_index = -1)

training_data, testing_data = cut_dataset([x for x in range(data.num_data)], NUM_TEST) # return lists of indices
training_data, validation_data = cut_dataset(training_data, NUM_VALIDATION)

print('\nStart Training......\n')

last_loss = 100
update = 0

for epoch in range(EPOCH_NUM):

	# Training
	dataset = get_batch(training_data)
	output = model(data.board[dataset].to(device), data.comment[dataset].to(device)).view(BATCH_SIZE * SENTENCE_LENGTH, data.num_word)
	target = data.comment[dataset].view(BATCH_SIZE * SENTENCE_LENGTH).to(device)
	loss = loss_func(output, target)
	loss.backward()
	optimzer.step()
	
	print('#' + str(epoch) + ' Training Loss :', loss.to(torch.device('cpu')).item())

	# Validation
	Vloss = 0.0
	for i in range(25) :
		dataset = validation_data[BATCH_SIZE * i : BATCH_SIZE * (i + 1)]
		output = model(data.board[dataset].to(device), data.comment[dataset].to(device), training = False).view(BATCH_SIZE * SENTENCE_LENGTH, data.num_word)
		target = data.comment[dataset].view(BATCH_SIZE * SENTENCE_LENGTH).to(device)
		Vloss += loss_func(output, target).to(torch.device('cpu')).item()
		model.zero_grad()
	Vloss /= 25
	print('#' + str(epoch) + ' Validation Loss :', Vloss)

	print('Last loss :', last_loss)
	if Vloss < last_loss :
		last_loss = Vloss
		torch.save(model.state_dict(), 'tmp.bin')
		update = 1
		print('Update successfully.\n')
	elif update :
		update = 0
		model.load_state_dict(torch.load('tmp.bin'))
		print('Restore.\n')
	else :
		print('Again.\n')

	# Store the weights
	if epoch and epoch % 20 == 0 :
		torch.save(model.state_dict(), 'weight.bin')
		Vloss = 0.0
		for i in range(25) :
			dataset = testing_data[BATCH_SIZE * i : BATCH_SIZE * (i + 1)]
			output = model(data.board[dataset].to(device), data.comment[dataset].to(device), training = False).view(BATCH_SIZE * SENTENCE_LENGTH, data.num_word)
			target = data.comment[dataset].view(BATCH_SIZE * SENTENCE_LENGTH).to(device)
			Vloss += loss_func(output, target).to(torch.device('cpu')).item()
			model.zero_grad()
		Vloss /= 25
		print('#' + str(epoch) + ' Testing Loss :', Vloss, end = '\n\n')

