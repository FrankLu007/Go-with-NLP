from argparser import get_args
from data_handler import DATA
from model import Encoder, Decoder

args = get_args()
data = DATA(args['input_board'], args['input_comment'], args['embedding_file'], args['sentence_length'])

device = torch.device(('cuda:' + args['gpu']) if torch.cuda.is_available() else 'cpu')
encoder = Encoder().to(device)
decoder = Decoder().to(device)
optimzer = optim.Adam(list(encoder.parameters()) + list(decoder.parameters()), lr = args['learning_rate'])
loss_func = nn.CrossEntropyLoss(ignore_index = -1)

last_loss = 100
update = 0
for epoch in range(args['epoch']) :
	dataset = data.get_data('train', args['batch_size'])
	hidden = encoder(data.board[dataset])
	result = decoder(data.comment[dataset], hidden)
	loss = loss_func(result, data.comment[dataset])
	loss.backward()
	optimzer.step()

	print('#' + str(epoch) + ' Training Loss :', loss.to(torch.device('cpu')).item())

	# Validation
	Vloss = 0.0
	for i in range(25) :
		dataset = validation_data[BATCH_SIZE * i : BATCH_SIZE * (i + 1)]
		output = model(data.board[dataset].to(device), data.comment[dataset].to(device), training = False).view(BATCH_SIZE * SENTENCE_LENGTH, data.num_word)
		target = data.comment[dataset].view(BATCH_SIZE * SENTENCE_LENGTH).to(device)
		Vloss += loss_func(output, target).to(torch.device('cpu')).item()
		model.zero_grad()
	Vloss /= 25
	print('#' + str(epoch) + ' Validation Loss :', Vloss)

	print('Last loss :', last_loss)
	if Vloss < last_loss :
		last_loss = Vloss
		torch.save(model.state_dict(), 'tmp.bin')
		update = 1
		print('Update successfully.\n')
	elif update :
		update = 0
		model.load_state_dict(torch.load('tmp.bin'))
		print('Restore.\n')
	else :
		print('Again.\n')