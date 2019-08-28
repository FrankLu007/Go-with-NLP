import sys

args = {'gpu' : 0, 'epoch' : 1000, 'learning_rate' : 0.0001, 'batch_size' : 32,\
		'test' : 0.1, 'validation' : 0.1, 'input_board' : '../data/board.txt', 'input_comment' : '../data/comment.txt',\
		'embedding_file' : '../data/embedding_256D.txt', 'sentence_length' : 2010, 'weight' : None}
float_args = ['learning_rate', 'test', 'validation']
str_args = ['input_board', 'input_comment', 'embedding_file', 'gpu', 'weight']
args_parse = 0 # 1 if args have been parsed

def error_message(info) :
	print('Error :', info)
	quit()

def print_args() :
	if not args_parse :
		get_args()
	else :
		print('\nProgram :', sys.argv[0])
		print('\nArgument :')
		for arg in args :
			print('%-20s    '%arg, args[arg])
	
def get_args() :
	global args_parse
	if args_parse :
		return args
	for index in range(1, len(sys.argv), 2) :
		arg = sys.argv[index][2:]
		if sys.argv[index][:2] == '--' and arg in args :
			if arg in float_args :
				args[arg] = float(sys.argv[index + 1])
			elif arg in str_args:
				args[arg] = sys.argv[index + 1]
			else :
				args[arg] = int(sys.argv[index + 1])
		else :
			error_message('Unrecognized argument : ' + sys.argv[index])
	args_parse = 1
	print_args()
	return args

