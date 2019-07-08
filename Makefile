all:
	g++ -g -o sgf_reader -O3 sgf_reader.cpp
clean:
	rm sgf_reader