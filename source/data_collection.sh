#!/bin/bash

../sgf_reader/sgf_reader
python3.6 data_preprocess.py
../word2vec/trunk/word2vec -train ../data/comment.txt -output ../data/embedding_256D.txt -size 256 -min-count 0 -iter 10000 -threads 4
