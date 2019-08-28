import torch
import os
from argparser import get_args
from data_handler import DATA
from model import Encoder, Decoder

args = get_args()
device = torch.device(('cuda:' + args['gpu']) if torch.cuda.is_available() else 'cpu')
data = DATA(args['input_board'], args['input_comment'], args['embedding_file'], args['sentence_length'])
data.to(device)
data.cut_data(args['validation'], args['test'], args['batch_size'])
encoder = Encoder(data.num_word, 1, args['batch_size'], device).to(device)
decoder = Decoder(data.embedding_dim, data.num_word, args['batch_size'], 24, data.table_vector, args['sentence_length'], device).to(device)
optimzer = torch.optim.Adam(list(encoder.parameters()) + list(decoder.parameters()), lr = args['learning_rate'])
loss_func = torch.nn.CrossEntropyLoss(ignore_index = -1)


if args['weight'] and os.path.isfile('e' + args['weight']) and os.path.isfile('d' + args['weight']):
	encoder.load_state_dict(torch.load('e' + args['weight']))
	decoder.load_state_dict(torch.load('d' + args['weight']))

print('Start Training : \n')

last_loss = 0.0
update = 0
dataset = data.get_data('validation')
for num in range(0, len(dataset), args['batch_size']) :
	with torch.no_grad() :
		target = dataset[num : num + args['batch_size']]
		board = []
		for index in target :
			board.append(data.board[index])
		hidden = encoder(board)
		result = decoder(hidden)
		last_loss += loss_func(result.view(args['batch_size'] * args['sentence_length'], -1), data.comment[target].view(args['batch_size'] * args['sentence_length']).to(device)).item()
	if num == 0 :
		for prob in result[0] :
			index = torch.argmax(prob)
			print(data.table_word[index], end = '')
		print('')
last_loss /= len(dataset) / args['batch_size']
print('Initial Validation Loss :', last_loss)

for epoch in range(args['epoch']) :

	dataset = data.get_data('train')[0 : args['batch_size']]
	board = []
	for index in dataset :
		board.append(data.board[index])
	hidden = encoder(board)
	result = decoder(hidden, data.comment[dataset]).view(args['batch_size'] * args['sentence_length'], -1)
	loss = loss_func(result, data.comment[dataset].view(args['batch_size'] * args['sentence_length']).to(device))
	print('#' + str(epoch) + ' Training Loss :', loss.to(torch.device('cpu')).item())
	encoder.zero_grad()
	decoder.zero_grad()
	loss.backward()
	optimzer.step()

	del loss
	del hidden
	del result


	loss = 0.0
	dataset = data.get_data('validation')
	for num in range(0, len(dataset), args['batch_size']) :
		with torch.no_grad() :
			target = dataset[num : num + args['batch_size']]
			board = []
			for index in target :
				board.append(data.board[index])
			hidden = encoder(board)
			result = decoder(hidden)
			loss += loss_func(result.view(args['batch_size'] * args['sentence_length'], -1), data.comment[target].view(args['batch_size'] * args['sentence_length']).to(device)).item()
		if num == 0 :
			for prob in result[0] :
				index = torch.argmax(prob)
				print(data.table_word[index], end = '')
			print('')
	loss /= len(dataset)/args['batch_size']
	print('#' + str(epoch) + ' Validation Loss :', loss)

	if loss < last_loss :
		last_loss = loss
		torch.save(encoder.state_dict(), 'etmp.bin')
		torch.save(decoder.state_dict(), 'dtmp.bin')
		update = 1
		print('Update successfully.\n')
	elif update :
		update = 0
		encoder.load_state_dict(torch.load('etmp.bin'))
		decoder.load_state_dict(torch.load('dtmp.bin'))
		print('Restore.\n')
	else :
		print('Again.\n')

if args['weight'] :
	encoder.load_state_dict(torch.load('e' + args['weight']))
	decoder.load_state_dict(torch.load('d' + args['weight']))
