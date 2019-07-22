# import torch
# import torch.nn as nn


CONNECT_LENGTH = 361
EPOCH_NUM = 100
converter = {} # character -> vector

def get_data(filename, embedding = []):
	dataset = []
	global converter

	# build converter
	if embedding:
		with open(embedding, 'r', errors='ignore') as file:
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
						print('Error : ', character)
						print([ord(c) for c in character])
					converter[character] = tmp

	# build the dataset
	with open(filename, 'r', errors='ignore') as file:
		while True:
			tmp = file.readline().split(' ')
			tmp.pop(-1) # pop '\n'
			if tmp:
				if embedding : # comment
					sentence = []
					for i in tmp :
						if i == '\t' or i == '\n' :
							continue
						sentence.append(converter[i])
					dataset.append(sentence)
				else : #chess
					#tmp = torch.IntTensor([int(i) for i in tmp]).view(19, 19)
					#chess = torch().view(19, 19)
					dataset.append(tmp)
			else :
				break
		file.close()

	return dataset


# class NET(nn.Module):
# 	def __init__(self):
# 		super(NET, self)
# 		#nn.Conv2d(batch size, #filter, kernel size, stride, padding)
# 		#nn.BatchNorm2d(batch size)
# 		self.go_cnn_layer[8]
# 		self.go_relu_layer[5]
# 		self.go_linear_layer = nn.Linear(361, CONNECT_LENGTH)
# 		self.nlp_lstm = lstm(CONNECT_LENGTH, CONNECT_LENGTH, bidirectional = True)
# 		self.nlp_hidden = (torch.randn(CONNECT_LENGTH, CONNECT_LENGTH), torch.randn(CONNECT_LENGTH, CONNECT_LENGTH))
# 		self.num_cnn
# 		self.num_relu
# 		for i in range(8):
# 			go_cnn_layer[i] = nn.Sequential(nn.Conv2d(1, 32, 3, 1, 1), 
# 									nn.BatchNorm2d(32), 
# 									nn.Parameter(torch.Tensor(1), requires_grad = True))
# 			if i < 6:
# 				go_relu_layer[i] = nn.ReLu()
# 	def cnn(x, layer = 1):
# 		num_cnn += layer
# 		if layer == 1:
# 			return go_cnn_layer[num_cnn - 1](x)
# 		return go_cnn_layer[num_cnn - 2](relu(go_cnn_layer[num_cnn - 1](x)))

# 	def relu(x):
# 		num_relu += 1
# 		return go_relu_layer[num_relu - 1](x)

# 	def foward(self, x):
# 		num_cnn = 0
# 		num_relu = 0
# 		spilt[2]

# 		#GO
# 		spilt[1] = spilt[0] = relu(cnn(x))
# 		spilt[0] = cnn(spilt[0], 2);
# 		spilt[1] = spilt[0] = relu(spilt[0] + spilt[1])
# 		spilt[0] = cnn(spilt[0], 2);
# 		spilt[1] = spilt[0] = relu(spilt[0] + spilt[1])
# 		spilt[0] = cnn(spilt[0], 2);
# 		spilt[0] = relu(spilt[0] + spilt[1])
# 		spilt[0] = cnn(spilt[0])
# 		spilt[0] = go_linear_layer(spilt[0])

# 		#NLP
# 		output, _ = nlp_lstm(spilt[0], nlp_hidden)
# 		nlp_lstm.zero_grid()

# 		return output

# main
board = get_data('board.txt')
print('#Data : ', len(board))
comment = get_data('comment.txt', 'embeddings/character_embedding_361D.txt')
print('Size of converter: ', len(converter))
if len(board) != len(comment):
	print('#Data is incorrect.')

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
