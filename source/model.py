import torch
import torch.nn as nn

class Encoder(nn.Module) :
	def __init__(self, hidden_size, num_layer, batch_size, device) :
		super(Encoder, self).__init__()
		self.lstm = nn.LSTM(361, hidden_size, num_layers = num_layer, batch_first = True, bidirectional = True)
		self.h = torch.autograd.Variable(torch.rand(num_layer * 2, batch_size, hidden_size), requires_grad = True).to(device)
		self.c = torch.autograd.Variable(torch.rand(num_layer * 2, batch_size, hidden_size), requires_grad = True).to(device)
		self.device = device

	def forward(self, data) :
		lstm_input = torch.FloatTensor([]).to(self.device)
		board = torch.FloatTensor([0 for i in range(361)]).to(self.device).view(1, 1, 361)
		
		for case in data :
			sentence = torch.FloatTensor([]).to(self.device)
			for index in range(17) :
				if index == 0 :
					for pos in case[0] :
						board[0][0][:] = 0
						if pos != -1 :
							board[0][0][pos] = 1
						sentence = torch.cat((sentence, board), dim = 1)
				else :
					board[0][0][:] = 0
					board[0][0][case[index]] = 1
					sentence = torch.cat((sentence, board), dim = 1)
			lstm_input = torch.cat((lstm_input, sentence), dim  = 0)

		del sentence

		lstm_output = torch.FloatTensor([]).to(self.device)
		for index in range(24) :
			partial_output, (self.h, self.c) = self.lstm(lstm_input[:, index, :].view(len(lstm_input), 1, 361), (self.h, self.c))
			lstm_output = torch.cat((lstm_output, partial_output), dim = 1)
		return lstm_output # batch, num_feature, 2 * hidden_size

class Decoder(nn.Module) :
	def __init__(self, embed_dim, num_word, batch_size, num_feature, embedding, sentence_length, device) :
		super(Decoder, self).__init__()
		self.softmax = nn.Softmax(dim = 1)
		self.linear = nn.Linear(num_word * 2, num_word)
		self.shrink = nn.Linear(num_word * 3, num_word)
		self.lstm = nn.LSTMCell(embed_dim + num_word * 2, num_word)
		self.b_o = torch.autograd.Variable(torch.rand(batch_size, num_word * 3), requires_grad = True).to(device)
		self.w_o = torch.autograd.Variable(torch.rand(batch_size, num_word * 3), requires_grad = True).to(device)
		self.w_c = torch.autograd.Variable(torch.rand(num_word), requires_grad = True).to(device)
		self.h = torch.autograd.Variable(torch.rand(batch_size, num_word), requires_grad = True).to(device)
		self.c = torch.autograd.Variable(torch.rand(batch_size, num_word), requires_grad = True).to(device)
		self.embedding = embedding
		self.sentence_length = sentence_length
		self.num_feature = num_feature
		self.device = device

	def forward(self, hidden_e, target = torch.LongTensor([])) :

		batch_size = len(hidden_e)
		output = torch.FloatTensor([]).to(self.device)
		for length in range(self.sentence_length) :
			a = torch.FloatTensor([]).to(self.device)
			for batch_index, batch in enumerate(hidden_e) :
				tmp_a = torch.FloatTensor([]).to(self.device)
				for index in range(self.num_feature) :
					tmp = torch.dot(self.h[batch_index] * self.w_c, self.linear(batch[index]))
					tmp_a = torch.cat((tmp_a, tmp.view(1, 1)), dim = 1)
				a = torch.cat((a, tmp_a), dim = 0)
			a = self.softmax(a).view(batch_size, self.num_feature, 1)
			c = torch.sum(a * hidden_e, dim =  1)
			if len(target) != 0:
				word = target[:, length]
			else :
				if length == 0 :
					word = torch.LongTensor([0 for i in range(batch_size)]) # 0 is the index of '</s>' (start)
				else :
					word = torch.LongTensor([]).to(self.device)
					for batch in p :
						word = torch.cat((word, torch.argmax(batch[0]).view(1)))
			self.h, self.c = self.lstm(torch.cat((self.embedding[word], c), dim = 1), (self.h, self.c))
			p = self.softmax(self.shrink(self.w_o * torch.cat((self.h, c), dim = 1) + self.b_o)).view(batch_size, 1, -1)
			output = torch.cat((output, p), dim = 1)
		return output