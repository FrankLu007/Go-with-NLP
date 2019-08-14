import torch
import torch.nn as nn

class Encoder(nn.Module) :
	def __init__(self, feature_size, hidden_size, num_layer) :
		super(Encoder, self).__init__()
		self.lstm = nn.LSTM(feature_size, hidden_size, num_layers = num_layer, batch_first = True, bidirectional = True)

	def forward(self, data) :
		return self.lstm(data)
