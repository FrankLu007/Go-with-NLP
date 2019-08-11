import torch
import torch.nn as nn
import random
import operator

# args
SENTENCE_LENGTH = 719
NUM_TEST = 10
END_INDEX = 0


def error_message(info) :
	print('Error :', info)
	quit()

def get_dataset(size) :
	data = [x for x in range(size)]
	random.shuffle(data)
	return data[0 : NUM_TEST]

class DATA() :
	def __init__(self, board_file, comment_file, embedding_file) :

		# GPU
		self.comment = torch.LongTensor([])
		self.board = torch.tensor([])
		self.table_vector = torch.tensor([])

		# CPU
		self.table_word = []
		self.num_step = []
		self.num_data = 0
		self.num_word = 0
		self.sentence_length = SENTENCE_LENGTH
		self.embedding_dim = 0

		with open(embedding_file, 'r', errors = 'ignore') as file :

			tmp = file.readline().split(' ')
			self.num_word = int(tmp[0])
			self.embedding_dim = int(tmp[1])

			while True :
				tmp = file.readline().split(' ')
				tmp.pop(-1) # abandon the newline	
				if not tmp :
					break
				word = tmp[0]
				tmp.pop(0)
				if len(tmp) != self.embedding_dim :
					error_message('embedding data error')
				vector = torch.FloatTensor([float(x) for x in tmp]).view(1, self.embedding_dim)
				if word == '</end>' :
					END_INDEX = len(self.table_word)
				self.table_word.append(word)
				self.table_vector = torch.cat((self.table_vector, vector), dim = 0)
			file.close()

		print('# Word :', self.num_word)


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
				self.board = torch.cat((self.board, torch.FloatTensor([float(x) for x in tmp]).view(1, 19, 19)), dim = 0)
			file.close()

		with open(comment_file, 'r', errors = 'ignore') as file :
			while True :
				tmp = file.readline().split(' ')
				tmp.pop(-1) # abandon the newline
				if not tmp :
					break
				sentence = torch.LongTensor([self.table_word.index('</s>')])
				for word in tmp :
					if word not in self.table_word :
						error_message('the word ' + word + ' is not in table.')
					else :
						sentence = torch.cat((sentence, torch.LongTensor([self.table_word.index(word)])), dim = 0)
				if len(sentence) < self.sentence_length :
					sentence = torch.cat((sentence, torch.LongTensor([-1 for i in range(self.sentence_length - len(sentence))])))
				self.comment = torch.cat((self.comment, sentence.view(1, self.sentence_length)), dim = 0)
		file.close()

		if len(self.comment) != len(self.board) :
			error_message('size is not match')
		else :
			self.num_data = len(self.board)
		print('# Data :', self.num_data)

class NET(nn.Module):
	def __init__(self, data, device):
		super(NET, self).__init__()

		# nn.Conv2d(in channel, out channel, kernel size, stride, padding)
		# nn.BatchNorm2d(batch size)
		tmp = nn.Sequential(nn.Conv2d(1, 1, 3, 1, 1), nn.BatchNorm2d(1))

		# model
		self.cnn_list = nn.ModuleList([tmp for i in range(8)])
		self.parameter_list = [nn.Parameter(torch.FloatTensor(1).fill_(1.0).to(device), requires_grad = True) for i in range(8)]
		self.relu = nn.ReLU()
		self.embed = nn.Embedding.from_pretrained(data.table_vector)
		self.linear = nn.Linear(361, data.embedding_dim)
		self.lstm = nn.LSTMCell(data.embedding_dim, data.embedding_dim, bias = True)
		self.lstm_decoder = nn.Linear(data.embedding_dim, data.num_word)

		# data
		self.num_data = data.num_data
		self.num_word = data.num_word
		self.embedding_dim = data.embedding_dim

	def forward(self, board) :

		self.zero_grad()

		# GO
		data1 = self.cnn_list[0](board.view(1, 1, 19, 19))
		data1 = self.parameter_list[0] * data1
		data1 = data2 = self.relu(data1)

		for cnn_index in range(1, 6, 2) :
			data1 = self.cnn_list[cnn_index](data1)
			data1 = self.parameter_list[cnn_index] * data1
			data1 = self.relu(data1)
			data1 = self.cnn_list[cnn_index + 1](data1)
			data1 = self.parameter_list[cnn_index + 1] * data1
			data1 = data2 = self.relu(data1 + data2)

		data1 = self.cnn_list[7](data1)
		data1 = self.relu(data1)
		data1 = self.linear(data1.view(361))

		lstm_input = data1.view(1, self.embedding_dim)

		#NLP
		output = torch.tensor([]).to(device)

		h, c = self.lstm(lstm_input)
		output = torch.cat((output, self.lstm_decoder(h).view(1, self.num_word)), dim = 0)

		while True :

			h, c = self.lstm(h, (h, c))
			output = torch.cat((output, self.lstm_decoder(h).view(1, self.num_word)), dim = 0)

			if torch.argmax(output[-1]) == 3 :
				print("END")
				break

			if len(output) > 100:
				break

		return self.relu(output)

# main
device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
data = DATA('board.txt', 'comment.txt', 'embeddings/embedding_256D.txt')
model = NET(data, device).to(device)
model.load_state_dict(torch.load('tmp.bin', map_location = device))
# loss_func = nn.NLLLoss(ignore_index = -1)
dataset = get_dataset(data.num_data)

print('\nStart Testing......\n')

for index, test_data in enumerate(dataset) :

	output = model(data.board[test_data].to(device))
	target = data.comment[test_data]

	print('#' + str(index) + ' Target :')
	for word in target :
		if word == -1 :
			break
		value = data.table_word[word]
		if value[0 : 7] == '</step-' :
			print(data.num_step[test_data] - int(value[7 : -1]), end = '')
		else :
			print(value, end = '')
	print('')

	print('#' + str(index) + ' Output :')
	for word in output :
		value = data.table_word[torch.argmax(word)]
		if value[0 : 7] == '</step-' :
			print(data.num_step[test_data] - int(value[7 : -1]), end = '')
		else :
			print(value, end = '')
	print('\n')