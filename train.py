from argparser import get_args
from data_handler import DATA

args = get_args()
data = DATA(args['input_board'], args['input_comment'], args['embedding_file'], args['sentence_length'])