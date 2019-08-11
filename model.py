import torch
import torch.nn as nn

class encoder(nn.Module) :
	def __init__(self, board, device, output_dim):
		super(encoder, self).__init__()
		# nn.Conv2d(in channel, out channel, kernel size, stride, padding)
		# nn.BatchNorm2d(batch size)
		tmp = nn.Sequential(nn.Conv2d(1, 1, 3, 1, 1), nn.BatchNorm2d(1))

		# model
		self.cnn_list = nn.ModuleList([tmp for i in range(8)])
		self.relu = nn.ReLU()
		self.linear = nn.Linear(361, output_dim)

		# data1
		self.output_dim = output_dim
		self.board = board.to(device)

	def foward(self, input_index) :

		output = torch.tensor([]).to(device)

		for index in input_index :

			data1 = self.cnn_list[0](self.board[index].view(1, 1, 19, 19))
			data1 = data2 = self.relu(data1)

			for cnn_index in range(1, 6, 2) :
				data1 = self.cnn_list[cnn_index](data1)
				data1 = self.relu(data1)
				data1 = self.cnn_list[cnn_index + 1](data1)
				data1 = data2 = self.relu(data1 + data2)

			data1 = self.cnn_list[7](data1)
			data1 = self.relu(data1)
			data1 = self.linear(data1.view(361))

			output = torch.cat((output, data1.view(1, self.output_dim)), dim = 0)

		return output

class decoder(nn.Module) :

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