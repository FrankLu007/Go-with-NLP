#!/bin/bash

make
echo -e 'collect\nq\n' | ./sgf_reader > /dev/null
python3.6 data_preprocess.py
if [ -f embeddings/character_embedding_$1D.txt ]
then
	rm embeddings/character_embedding_$1D.txt
fi
echo -e 'embed\n'$1'\nq\n' | ./sgf_reader > /dev/null