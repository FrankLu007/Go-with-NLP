import torch
from torch import *


CONNECT_LENGTH = 361
EPOCH_NUM = 100

def get_data(filename):
	self.dataset = []

	file = f(filename, 'r')
	chess = file.readline()
	word = file.readline()
	while chess:
		dataset.append([chess, word])
		chess = file.readline()
		word = file.readline()
	fp.close()

	return dataset


class NET(nn.module):
	def __init__(self):
		super(NET, self)
		#nn.Conv2d(batch size, #filter, kernel size, stride, padding)
		#nn.BatchNorm2d(batch size)
		self.go_cnn_layer[8]
		self.go_relu_layer[5]
		self.go_linear_layer = nn.Linear(361, CONNECT_LENGTH)
		self.nlp_lstm = lstm(CONNECT_LENGTH, CONNECT_LENGTH, bidirectional = True)
		self.nlp_hidden = (torch.randn(CONNECT_LENGTH, CONNECT_LENGTH), torch.randn(CONNECT_LENGTH, CONNECT_LENGTH))

		for i in range(8):
			go_cnn_layer[i] = nn.Sequential(nn.Conv2d(1, 32, 3, 1, 1), 
									nn.BatchNorm2d(32), 
									nn.Parameter(torch.Tensor(1), requires_grad = True))
			if i < 6:
				go_relu_layer[i] = nn.ReLu()

	def foward(self, w):
		num_cnn = 0
		num_relu = 0
		spilt[2]

		#GO
		spilt[1] = spilt[0] = go_relu_layer[num_relu++](go_cnn_layer[num_cnn++](x))
		spilt[0] = go_cnn_layer[num_cnn++](go_relu_layer[num_relu++](go_cnn_layer[num_cnn++](spilt[0])))
		spilt[1] = spilt[0] = go_relu_layer[num_relu++](spilt[0] + spilt[1])
		spilt[0] = go_cnn_layer[num_cnn++](go_relu_layer[num_relu++](go_cnn_layer[num_cnn++](spilt[0])))
		spilt[1] = spilt[0] = go_relu_layer[num_relu++](spilt[0] + spilt[1])
		spilt[0] = go_cnn_layer[num_cnn++](go_relu_layer[num_relu++](go_cnn_layer[num_cnn++](spilt[0])))
		spilt[0] = go_relu_layer[num_relu++](spilt[0] + spilt[1])
		spilt[0] = go_cnn_layer[num_cnn++](spilt[0])
		spilt[0] = go_linear_layer(spilt[0])

		#NLP
		output, _ = nlp_lstm(spilt[0], nlp_hidden)
		nlp_lstm.zero_grid()

		return output
dataset = get_data('data.txt')
print dataset
# model = NET()
# cost = nn.CrossEntropyLoss()
# optimzer = optim.Adam(model.parameters())

# for epoch in range(EPOCH_NUM):
# 	loss = 0.0
# 	for data, word in dataset:
# 		output = NET(data)
# 		loss = nn.CrossEntropyLoss(output, word).backword()
# 		optimzer.step()
# 		print(output)
