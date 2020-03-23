import torch
import torch.nn as nn
# import sys

# class Bert(nn.Module) :
# 	def __init__(self, device, num_layer = 8, head_size = 17) :
# 		super(Bert, self).__init__()
# 		encoder_layer = nn.TransformerEncoderLayer(17, head_size, dim_feedforward = 361)
# 		self.bert = nn.TransformerEncoder(encoder_layer, num_layer)
# 		self.device = device
# 		self.softmax = nn.Softmax(dim = 1)
# 		self.linear = nn.Linear(17 * 361, 361)

# 	def forward(self, batch_data) :
# 		board = torch.FloatTensor([0 for i in range(361)]).to(self.device).view(1, 1, 361)
# 		bert_input = torch.FloatTensor([]).to(self.device)
# 		for data in batch_data :
# 			feature_board = torch.FloatTensor([]).to(self.device)
# 			for index, feature in enumerate(data) :
# 				if index == 16 :
# 					board[0][0][:] = feature
# 				else :
# 					board[0][0][:] = 0
# 					board[0][0][feature] = 1
# 				feature_board = torch.cat((feature_board, board), dim = 1)
# 			bert_input = torch.cat((bert_input, feature_board), dim = 0)

# 		bert_input = bert_input.transpose(1, 2)
# 		bert_input = bert_input.transpose(0, 1)

# 		bert_output = self.bert(bert_input)

# 		bert_output = bert_output.transpose(0, 1)
# 		bert_output = bert_output.transpose(1, 2)
# 		bert_output = bert_output.reshape(-1, 17 * 361)

# 		return self.softmax(self.linear(bert_output))

class CNN(nn.Module) :
    def __init__(self, device, num_block = 3, channel_size = 256) :
        super(CNN, self).__init__()

        cnn_start = nn.Sequential(nn.Conv2d(17, channel_size, 3, 1, 1), nn.BatchNorm2d(channel_size, momentum = 0.9))
        cnn_middle = nn.Sequential(nn.Conv2d(channel_size, channel_size, 3, 1, 1), nn.BatchNorm2d(channel_size, momentum = 0.9))
        cnn_end = nn.Sequential(nn.Conv2d(channel_size, 1, 1, 1, 0), nn.BatchNorm2d(1, momentum = 0.9))

        self.cnn_list = nn.ModuleList([cnn_start] + [cnn_middle for i in range(num_block * 2)] + [cnn_end])
        self.relu = nn.ReLU()
        self.device = device

    def forward(self, batch_data) :

        board = torch.FloatTensor([0 for i in range(361)]).to(self.device)
        cnn_input = torch.FloatTensor([]).to(self.device)
        # cnn_output = torch.FloatTensor([]).to(self.device)

        for data in batch_data :
            feature_board = torch.FloatTensor([]).to(self.device)
            for index, feature in enumerate(data) :
            	if index == 16 : # C16
            		board[:] = feature
            	else : # C0 ~ C15
            		board[:] = 0
            		board[feature] = 1
            	feature_board = torch.cat((feature_board, board.view(1, 1, 19, 19)), dim = 1)
            cnn_input = torch.cat((cnn_input, feature_board), dim = 0) # (batch, feature_map, 19, 19)
        residual = self.relu(self.cnn_list[0](cnn_input))
        for cnn_index in range(1, len(self.cnn_list) - 2, 2) :
        	data = self.relu(self.cnn_list[cnn_index](residual))
        	residual = self.relu(self.cnn_list[cnn_index + 1](data) + residual)
            # cnn_output = torch.cat((cnn_output, self.relu(self.cnn_list[-1](residual)).view(-1, 361)), dim = 0)
        return self.relu(self.cnn_list[-1](residual)).view(-1, 361)

class BVCNN(nn.Module) :
    def __init__(self, device, num_block = 3, channel_size = 256) :
        super(CNN, self).__init__()

        cnn_start = nn.Sequential(nn.Conv2d(17, channel_size, 3, 1, 1), nn.BatchNorm2d(channel_size, momentum = 0.9))
        cnn_middle = nn.Sequential(nn.Conv2d(channel_size, channel_size, 3, 1, 1), nn.BatchNorm2d(channel_size, momentum = 0.9))
        cnn_end = nn.Sequential(nn.Conv2d(channel_size, 1, 1, 1, 0), nn.BatchNorm2d(1, momentum = 0.9))

        self.cnn_list = nn.ModuleList([cnn_start] + [cnn_middle for i in range(num_block * 2)] + [cnn_end])
        self.fc_layer = nn.Linear(361, 18);
        self.relu = nn.ReLU()
        self.device = device

    def forward(self, batch_data) :

        board = torch.FloatTensor([0 for i in range(361)]).to(self.device)
        cnn_input = torch.FloatTensor([]).to(self.device)
        # cnn_output = torch.FloatTensor([]).to(self.device)

        for data in batch_data :
            feature_board = torch.FloatTensor([]).to(self.device)
            for index, feature in enumerate(data) :
                if index == 16 : # C16
                    board[:] = feature
                else : # C0 ~ C15
                    board[:] = 0
                    board[feature] = 1
                feature_board = torch.cat((feature_board, board.view(1, 1, 19, 19)), dim = 1)
            cnn_input = torch.cat((cnn_input, feature_board), dim = 0) # (batch, feature_map, 19, 19)
        residual = self.relu(self.cnn_list[0](cnn_input))
        for cnn_index in range(1, len(self.cnn_list) - 2, 2) :
            data = self.relu(self.cnn_list[cnn_index](residual))
            residual = self.relu(self.cnn_list[cnn_index + 1](data) + residual)

        return self.fc_layer(self.relu(self.cnn_list[-1](residual)).view(-1, 361))


	# def __init__(self, hidden_size, num_layer, batch_size, device) :
	# 	super(Encoder, self).__init__()
	# 	self.lstm = nn.LSTM(1, hidden_size, num_layers = num_layer, batch_first = True, bidirectional = True)
	# 	self.h = torch.autograd.Variable(torch.rand(num_layer * 2, batch_size, hidden_size), requires_grad = True).to(device)
	# 	self.c = torch.autograd.Variable(torch.rand(num_layer * 2, batch_size, hidden_size), requires_grad = True).to(device)
	# 	self.device = device

	# def forward(self, data) :
	# 	output = torch.FloatTensor([]).to(self.device)
	# 	board = torch.FloatTensor([0 for i in range(361)]).to(self.device).view(1, 361, 1)
		
	# 	for feature in range(49) :
	# 		lstm_input = torch.FloatTensor([]).to(self.device)
	# 		for case in data :
	# 			if feature == 48 :
	# 				board[0][:][0] = case[feature][0]
	# 			else :
	# 				board[0][:][0] = 0
	# 				if case[feature] :
	# 					board[0][case[feature]][0] = 1
	# 			lstm_input = torch.cat((lstm_input, board), dim = 0)
	# 		partial_output, (self.h, self.c) = self.lstm(lstm_input, (self.h, self.c))
	# 		output = torch.cat((output, partial_output.contiguous().view(len(data), 1, -1)), dim = 1)
	# 		del partial_output
	# 	return output # batch, num_feature, 2 * hidden_size * 361

# class Decoder(nn.Module) :
# 	def __init__(self, embed_dim, num_word, batch_size, num_feature, embedding, sentence_length, device) :
# 		super(Decoder, self).__init__()
# 		self.softmax = nn.Softmax(dim = 1)
# 		self.linear = nn.Linear(361, num_word)
# 		self.shrink = nn.Linear(num_word * 2, num_word)
# 		self.lstm = nn.LSTMCell(embed_dim + num_word, num_word)
# 		self.b_o = torch.autograd.Variable(torch.rand(batch_size, num_word * 2), requires_grad = True).to(device)
# 		self.w_o = torch.autograd.Variable(torch.rand(batch_size, num_word * 2), requires_grad = True).to(device)
# 		self.w_c = torch.autograd.Variable(torch.rand(num_word), requires_grad = True).to(device)
# 		self.h = torch.autograd.Variable(torch.rand(batch_size, num_word), requires_grad = True).to(device)
# 		self.c = torch.autograd.Variable(torch.rand(batch_size, num_word), requires_grad = True).to(device)
# 		self.embedding = embedding
# 		self.sentence_length = sentence_length
# 		self.num_feature = num_feature
# 		self.device = device

# 	def forward(self, hidden_e, target = torch.LongTensor([])) :

# 		batch_size = len(hidden_e)
# 		hidden_e = self.linear(hidden_e.view(batch_size * self.num_feature, -1)).view(batch_size, self.num_feature, -1)
# 		output = torch.FloatTensor([]).to(self.device)
# 		for length in range(self.sentence_length) :
# 			a = torch.FloatTensor([]).to(self.device)
# 			for batch_index, batch in enumerate(hidden_e) :
# 				tmp_a = torch.FloatTensor([]).to(self.device)
# 				for index in range(self.num_feature) :
# 					tmp = torch.dot(self.h[batch_index] * self.w_c, batch[index])
# 					tmp_a = torch.cat((tmp_a, tmp.view(1, 1)), dim = 1)
# 				a = torch.cat((a, tmp_a), dim = 0)
# 			a = self.softmax(a).view(batch_size, self.num_feature, 1)
# 			c = torch.sum(a * hidden_e, dim =  1)
# 			if len(target) != 0:
# 				word = target[:, length]
# 			else :
# 				if length == 0 :
# 					word = torch.LongTensor([0 for i in range(batch_size)]) # 0 is the index of '</s>' (start)
# 				else :
# 					word = torch.LongTensor([]).to(self.device)
# 					for batch in p :
# 						print(batch[0].shape)
# 						word = torch.cat((word, torch.argmax(batch[0]).view(1)))
# 			self.h, self.c = self.lstm(torch.cat((self.embedding[word], c), dim = 1), (self.h, self.c))
# 			p = self.softmax(self.shrink(self.w_o * torch.cat((self.h, c), dim = 1) + self.b_o)).view(batch_size, 1, -1)
# 			output = torch.cat((output, p), dim = 1)
# 		return output