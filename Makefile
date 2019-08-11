all:
	g++ -g -o sgf_reader -O3 -std=c++17 sgf_reader.cpp
clean:
	rm sgf_reader data.txt board.txt comment.txt abandon.txt embeddings/embedding*
