import word2vec

word2vec.word2vec('comment.txt', 'comment.bin', size=300,verbose=True)
model = word2vec.load('comment.bin')
print model