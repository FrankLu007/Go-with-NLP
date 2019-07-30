# embedding : https://code.google.com/archive/p/word2vec/

import os
import torch
import torch.nn as nn
import torch.optim as optim
import random
import math

PERCENTAGE_TEST = 0.1
BATCH_SIZE = 64
EPOCH_NUM = 100

def error_message(info) :
	print('Error :', info)
	quit()

class DATA() :
	def __init__(self, board_file, comment_file, embed_file) :
		self.table_w = [] # size --> word
		self.table_v = torch.tensor([]) # size x embed_dim --> word vector
		self.board = [] # size x 19 x 19
		self.num_step = []
		self.comment = [] # size x length --> word index
		self.num_word = 0
		self.embed_dim = 0
		self.test_data = []
		self.validation = [] # each is one third of training data

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
				self.board.append(torch.FloatTensor([float(x) for x in tmp]).view(19, 19))
		file.close()
		print('#Board data :', len(self.board))

		with open(embed_file, 'r', errors = 'ignore') as file :
			tmp = file.readline().split(' ')
			self.num_word = int(tmp[0])
			self.embed_dim = int(tmp[1])
			while True :
				tmp = file.readline().split(' ')
				tmp.pop(-1) # abandon the newline	
				if not tmp :
					break
				word = tmp[0]
				tmp.pop(0)
				if len(tmp) != self.embed_dim :
					error_message('embedding data error')
				vector = torch.FloatTensor([float(x) for x in tmp]).view(1, self.embed_dim)
				self.table_w.append(word)
				self.table_v = torch.cat((self.table_v, vector), dim = 0)
		file.close()
		if len(self.table_w) != self.num_word :
			error_message('embed data error')
		print('#Word :', self.num_word)

		with open(comment_file, 'r', errors = 'ignore') as file :
			while True :
				sentence = []
				tmp = file.readline().split(' ')
				tmp.pop(-1) # abandon the newline
				if not tmp :
					break
				for word in tmp :
					if word not in self.table_w :
						error_message('the word ' + word + ' is not in table.')
					sentence.append(self.table_w.index(word))
				self.comment.append(sentence)
		file.close()
		print('#Comment data :', len(self.comment))
		

		if len(self.comment) != len(self.board) :
			error_message('size of board and comment don\'t match.')

		# set testing, validation data
		data = [x for x in range(len(self.board))]
		random.shuffle(data)
		self.test_data = data[0 : math.ceil(len(self.board) * PERCENTAGE_TEST)]
		data = data[math.ceil(len(self.board) * PERCENTAGE_TEST) + 1 :] # pop the testing dataset
		len_validation = math.ceil(len(data) / 3)
		self.validation.append(data[0 : len_validation - 1])
		self.validation.append(data[len_validation : len_validation * 2 - 1])
		self.validation.append(data[len_validation * 2 : ])

	def get_comment(index1, index2) : # index1 is a list ; index2 in an int
		output = torch.tensor([])
		for index in index1 :
			if index >= len(self.comment) :
				error_message('too large index ' + str(index))
			elif index < 0 :
				error_message('too small index ' + str(index))
			output = torch.cat((output, table_v[self.comment[index][index2]]), dim = 0)
		return output

	def get_target(index) : # index is a list
		output = torch.tensor([])
		for item in index :
			sentence = torch.tensor([])
			for word in self.comment[item] :
				sentence = torch.cat((sentence, nn.functional.one_hot(word, num_classes = self.embed_dim).view(1, 1, self.embed_dim)), dim = 1)
			output = torch.cat((output, sentence), dim = 0)
		return output

	def max_length(index) : # index is a list
		max_len = 0
		for line in self.comment :
			if len(line) > max_len :
				max_len = len(line)
		return max_len

class NET(nn.Module):
	def __init__(self, data):
		super(NET, self).__init__()
		#nn.Conv2d(in channel, out channel, kernel size, stride, padding)
		#nn.BatchNorm2d(batch size)
		first = nn.Sequential(nn.Conv2d(1, 32, 3, 1, 1), nn.BatchNorm2d(32))
		middle = nn.Sequential(nn.Conv2d(32, 32, 3, 1, 1), nn.BatchNorm2d(32))
		end = nn.Sequential(nn.Conv2d(32, 1, 3, 1, 1), nn.BatchNorm2d(1))

		self.cnn_list = nn.ModuleList([first])
		for i in range(6) :
			self.cnn_list.append(middle)
		self.cnn_list.append(end)
		self.parameter_list = [nn.Parameter(torch.FloatTensor(1).fill_(1.0), requires_grad = True) for i in range(8)]
		self.relu = nn.ReLU()
		# self.embed = nn.Embedding.from_pretrained(data.table_v)
		self.linear = nn.Linear(361, data.embed_dim)
		self.lstm = nn.LSTMCell(data.embed_dim, data.embed_dim, bias = True)
		self.lstm_decoder = nn.Linear(data.embed_dim, data.num_word)

	def forward(self, input_data, data):

		self.zero_grad()

		#GO
		lstm_input = torch.tensor([])

		for index in input_data :

			data1 = self.cnn_list[0](data.board[index])
			data1 = self.parameter_list[0](data1)
			data1 = data2 = self.relu(data1)

			for cnn_index in range(1, 6, 2) :
				data1 = self.cnn_list[cnn_index](data1)
				data1 = self.parameter_list[cnn_index](data1)
				data1 = self.relu(data1)
				data1 = self.cnn_list[cnn_index + 1](data1)
				data1 = self.parameter_list[cnn_index + 1](data1)
				data1 = data2 = self.relu(data1 + data2)

			data1 = self.cnn_list[7](data1)
			data1 = self.relu(data1)
			data1 = self.linear(data1.view(361))

			lstm_input = torch.cat((lstm_input, data1.view(1, data.embed_dim)), dim = 0)

		#NLP
		output = torch.tensor([])
		h, c = self.lstm(data1)
		for index in range(BATCH_SIZE) :
			h[index] = self.lstm_decoder(h[index])
		output = torch.cat((output, h.view(BATCH_SIZE, 1, data.num_word)), dim = 1)
		for i in range(data.max_length(input_data)):
			h, c = self.lstm(data.get_comment(input_data, i), (h, c))
			for index in range(BATCH_SIZE) :
				h[index] = self.lstm_decoder(h[index])
			output = torch.cat((output, h.view(BATCH_SIZE, 1, data.num_word)), dim = 1)
		return output

# main
data = DATA('board.txt', 'comment.txt', 'embeddings/character_embedding_1000D.txt')
model = [NET(data) for i in range(3)]
optimzer = [optim.Adam(model[i].parameters()) for i in range(3)]
loss_func = [nn.NLLLoss() for i in range(3)]

if os.path.exists("weights.bin"):
	model.load_state_dict(torch.load("weights.bin"))

for epoch in range(EPOCH_NUM):
	avg_loss = 0.0
	training_loss = []
	testing_loss = []
	for i in range(3):
		dataset = data.validation[i]
		random.shuffle(dataset)
		output = model[i](dataset, data)
		loss = loss_func[i](output, data.get_target(dataset))
		loss.backword()
		optimzer[i].step()
		training_loss.append(loss)
		output = model[i](data.test_data, data)
		loss = loss_func[i](output, data.get_output(data.test_data))
		testing_loss.append(loss)
		avg_loss += loss

	print(training_loss)
	print('Average Loss : ', avg_loss / 3)

torch.save(model.state_dict(), "weights.bin")
