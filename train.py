# embedding : https://code.google.com/archive/p/word2vec/
import os
import torch
import torch.nn as nn
import torch.optim as optim

CONNECT_LENGTH = 361
EPOCH_NUM = 100
converter = {} # character -> vector


def get_data(filename, embedding = []):
	dataset = []
	error = []
	zero = torch.zeros(1, 361)
	global converter

	# build converter
	if embedding:
		with open(embedding, 'r', errors = 'ignore', encoding = 'UTF-8') as file:
			file.readline() # number and dimension
			while True:
				tmp = file.readline().split(' ')
				if tmp:
					character = tmp[0] # fist is a character
					tmp.pop(0)
					if len(tmp) == 0:
						break
					tmp.pop(-1) # pop '\n'
					if character in converter:
						error.append(character)
					else : 
						tmp = torch.FloatTensor([float(i) for i in tmp])
						converter[character] = tmp
		if len(error):
			print(len(error), ' error(s) in embeddings : ', error)
	error = []
	# build the dataset
	with open(filename, 'r', errors = 'ignore') as file:
		while True:
			tmp = file.readline().split(' ')
			tmp.pop(-1) # pop '\n'
			if tmp:
				if embedding : # comment
					sentence = torch.tensor([])
					for i in tmp :
						if i == '\t' or i == '\n' :
							continue
						if i not in converter:
							error.append(character)
						else :
							sentence = torch.cat((sentence, converter[i].view(1, 361)), dim = 0)
					sentence = torch.cat((sentence, zero), dim = 0)
					dataset.append(sentence)
				else : # Go chess
					tmp = torch.FloatTensor([float(i) for i in tmp]).view(19, 19)
					dataset.append(tmp)
			else :
				break
		if len(error):
			print(len(error), ' error(s) in converter : ', error)
		file.close()

	return dataset

class NET(nn.Module):
	def __init__(self):
		super(NET, self).__init__()
		#nn.Conv2d(in channel, out channel, kernel size, stride, padding)
		#nn.BatchNorm2d(batch size)
		self.go_cnn_layer = []
		self.go_relu_layer = []
		self.go_scalar = []	
		self.go_linear_layer = nn.Linear(361, CONNECT_LENGTH)
		self.nlp_lstm = nn.LSTM(CONNECT_LENGTH, CONNECT_LENGTH, bidirectional = False)
		self.num_cnn = 0
		self.num_relu = 0
		for i in range(8):
			self.go_cnn_layer.append(nn.Sequential(nn.Conv2d(1, 1, 3, 1, 1), 
									nn.BatchNorm2d(1)))
			self.go_scalar.append(nn.Parameter(torch.FloatTensor(1).fill_(1.0), requires_grad = True))
			self.go_relu_layer.append(nn.ReLU())
	def cnn(self, x, layer = 1):
		self.num_cnn += layer
		if layer == 1:
			return self.go_cnn_layer[self.num_cnn - 1](x) * self.go_scalar[self.num_cnn - 1]
		return self.go_cnn_layer[self.num_cnn - 1](self.relu(self.go_cnn_layer[self.num_cnn - 2](x) * self.go_scalar[self.num_cnn -2]))

	def relu(self, x):
		self.num_relu += 1
		return self.go_relu_layer[self.num_relu - 1](x)

	def forward(self, x, bb):
		self.num_cnn = 0
		self.num_relu = 0
		split = [x, x]	

		self.zero_grad()

		#GO
		split[1] = split[0] = self.relu(self.cnn(x))
		split[0] = self.cnn(split[0], 2);
		split[1] = split[0] = self.relu(split[0] + split[1])
		split[0] = self.cnn(split[0], 2);
		split[1] = split[0] = self.relu(split[0] + split[1])
		split[0] = self.cnn(split[0], 2);
		split[0] = self.relu(split[0] + split[1])
		split[0] = self.cnn(split[0])
		split[0] = self.go_linear_layer(split[0].view(361))

		#NLP
		output = torch.tensor([])
		tmp, hidden = self.nlp_lstm(split[0].view(1, 1, 361))
		output = torch.cat((output, tmp), dim = 0)
		for i in range(len(target) - 1):
			tmp, hidden = self.nlp_lstm(tmp, hidden)
			output = torch.cat((output, tmp), dim = 0)
		return output.view(-1, 361)

# main
board = get_data('board.txt')
print('#Data : ', len(board))
comment = get_data('comment.txt', 'embeddings/character_embedding_361D.txt')
print('Size of converter: ', len(converter))
if len(board) != len(comment):
	print('#Data is incorrect.')

model = NET()
optimzer = optim.Adam(model.parameters())
loss_func = nn.NNLoss()

if os.path.exists("weights.bin"):
	model.load_state_dict(torch.load("weights.bin"))

for epoch in range(EPOCH_NUM):
	avg_loss = 0.0
	for i in range(len(board)):
		output = model(board[i].view((1, 1, 19, 19)), len(comment[i]))
		loss = loss_func(output, comment[i])
		loss.backward()
		optimzer.step()
		avg_loss += loss
		print('#loss : ', loss)
		print('Result : ', end = '')
		for i in output:
			value = 0
			word = ''
			for j in converter:
				if torch.dot(i, converter[j]) > value:
					value = torch.dot(i, converter[j])
					word = j;
			print(word, end = '')
		print('\n')
	print('Average Loss : ', avg_loss / len(board))



torch.save(model.state_dict(), "weights.bin")
