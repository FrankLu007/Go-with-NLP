import torch
import torch.nn as nn


CONNECT_LENGTH = 361
EPOCH_NUM = 100

def get_data(filename):
	dataset = []

	with open('data.txt', 'r', errors='ignore') as file:
		while True:
			word = file.readline()
			if word:
				tmp = file.readline().split(' ')
				tmp.pop(-1)
				tmp = torch.IntTensor([int(i) for i in tmp]).view(19, 19)
				print(tmp)
				break
				#chess = torch().view(19, 19)
				dataset.append([word, chess])
			else :
				break
		file.close()

	return dataset


class NET(nn.Module):
	def __init__(self):
		super(NET, self)
		#nn.Conv2d(batch size, #filter, kernel size, stride, padding)
		#nn.BatchNorm2d(batch size)
		self.go_cnn_layer[8]
		self.go_relu_layer[5]
		self.go_linear_layer = nn.Linear(361, CONNECT_LENGTH)
		self.nlp_lstm = lstm(CONNECT_LENGTH, CONNECT_LENGTH, bidirectional = True)
		self.nlp_hidden = (torch.randn(CONNECT_LENGTH, CONNECT_LENGTH), torch.randn(CONNECT_LENGTH, CONNECT_LENGTH))
		self.num_cnn
		self.num_relu
		for i in range(8):
			go_cnn_layer[i] = nn.Sequential(nn.Conv2d(1, 32, 3, 1, 1), 
									nn.BatchNorm2d(32), 
									nn.Parameter(torch.Tensor(1), requires_grad = True))
			if i < 6:
				go_relu_layer[i] = nn.ReLu()
	def cnn(x, layer = 1):
		num_cnn += layer
		if layer == 1:
			return go_cnn_layer[num_cnn - 1](x)
		return go_cnn_layer[num_cnn - 2](relu(go_cnn_layer[num_cnn - 1](x)))

	def relu(x):
		num_relu += 1
		return go_relu_layer[num_relu - 1](x)

	def foward(self, x):
		num_cnn = 0
		num_relu = 0
		spilt[2]

		#GO
		spilt[1] = spilt[0] = relu(cnn(x))
		spilt[0] = cnn(spilt[0], 2);
		spilt[1] = spilt[0] = relu(spilt[0] + spilt[1])
		spilt[0] = cnn(spilt[0], 2);
		spilt[1] = spilt[0] = relu(spilt[0] + spilt[1])
		spilt[0] = cnn(spilt[0], 2);
		spilt[0] = relu(spilt[0] + spilt[1])
		spilt[0] = cnn(spilt[0])
		spilt[0] = go_linear_layer(spilt[0])

		#NLP
		output, _ = nlp_lstm(spilt[0], nlp_hidden)
		nlp_lstm.zero_grid()

		return output

dataset = get_data('data.txt')
print('Size of data: ', len(dataset))
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
