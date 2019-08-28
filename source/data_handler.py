import torch
import random

def error_message(info) :
	print('Error :', info)
	quit()

class DATA() :
	def __init__(self, board_file, comment_file, embedding_file, sentence_length) :

		# GPU
		self.comment = torch.LongTensor([])
		self.table_vector = torch.tensor([])

		# CPU
		self.board = []
		self.table_word = []
		self.num_step = []
		self.num_data = 0
		self.num_word = 0
		self.sentence_length = sentence_length
		self.embedding_dim = 0
		self.data = {'train' : [], 'test' : [], 'validation' : []}

		print('\nData :')

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
				self.table_word.append(word)
				self.table_vector = torch.cat((self.table_vector, vector), dim = 0)
		print('# Word :', self.num_word)

		with open(board_file, 'r', errors = 'ignore') as file :
			while True :
				case = []
				tmp = file.readline().split(' ')
				tmp.pop(-1) # abandon the newline
				if not tmp :
					break
				case.append([int(num) for num in tmp])
				for i in range(16) :
					tmp = file.readline().split(' ')
					tmp.pop(-1)
					case.append([int(num) for num in tmp])
				tmp = file.readline().split(' ')
				self.num_step.append(int(tmp[0]))
				self.board.append(case)

		with open(comment_file, 'r', errors = 'ignore') as file :
			while True :
				tmp = file.readline().split(' ')
				tmp.pop(-1) # abandon the newline
				if not tmp :
					break
				sentence = torch.LongTensor([])
				for word in tmp :
					if word not in self.table_word :
						if word :
							error_message('the word ' + word + ' is not in table.')
					else :
						sentence = torch.cat((sentence, torch.LongTensor([self.table_word.index(word)])), dim = 0)
				if len(sentence) < self.sentence_length :
					sentence = torch.cat((sentence, torch.LongTensor([-1 for i in range(self.sentence_length - len(sentence))])))
				elif len(sentence) > self.sentence_length :
					sentence = sentence[0 : self.sentence_length - 1]
					sentence = torch.cat((sentence, torch.LongTensor([self.table_word.index('</end>')])), dim = 0)
				self.comment = torch.cat((self.comment, sentence.view(1, self.sentence_length)), dim = 0)

		if len(self.comment) != len(self.board) :
			print('Board :', len(self.board))
			print('Comment :', len(self.comment))
			error_message('size is not match')
		else :
			self.num_data = len(self.board)
		print('# Data :', self.num_data)

	def cut_data(self, num_validation, num_test, batch_size) :
		num_validation = int(self.num_data * num_validation / batch_size) * batch_size
		num_test = int(self.num_data * num_test / batch_size) * batch_size
		all = [x for x in range(self.num_data)]
		random.shuffle(all)
		self.data['train'] = all[0 : self.num_data - num_validation - num_test]
		self.data['validation'] = all[self.num_data - num_validation - num_test : self.num_data - num_test]
		self.data['test'] = all[self.num_data - num_test :]

	def get_data(self, type) :
		if len(self.data['validation']) == 0 :
			error_message('should cut the data first')
		random.shuffle(self.data[type])
		return self.data[type]

	def to(self, device) :
		# self.comment = self.comment.to(device)
		# self.board = self.board.to(device)
		self.table_vector = self.table_vector.to(device)
