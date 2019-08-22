import torch
import torch.nn as nn

class Encoder(nn.Module) :
	def __init__(self, feature_size, hidden_size, num_layer) :
		super(Encoder, self).__init__()
		self.lstm = nn.LSTM(feature_size, hidden_size, num_layers = num_layer, batch_first = True, bidirectional = True)

	def forward(self, data) :
		return self.lstm(data)

class Decoder(nn.Module) :
	def __init__(self) :
		super(Decoder, self).__init__()
		self.sofmax = nn.softmax2d()
		self.lstm = nn.LSTMCell()
		self.w_o = Variable(torch.rand(1), requires_grad = True)
		self.w_c = Variable(torch.rand(1), requires_grad = True)

	def forward(self, target, hidden_e) :
