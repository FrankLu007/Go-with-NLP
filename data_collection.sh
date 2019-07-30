#!/bin/bash

make
echo -e 'collect\nq\n' | ./sgf_reader
python3.6 data_preprocess.py
if [ -f embeddings/character_embedding_1000D.txt ]
then
	rm embeddings/character_embedding_1000D.txt
fi
echo -e 'embed\n1000\nq\n' | ./sgf_reader