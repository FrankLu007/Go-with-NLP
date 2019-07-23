all:
	g++ -g -o sgf_reader -O3 sgf_reader.cpp
	g++ -g -o output_reader -O3 output_reader.cpp
clean:
	rm sgf_reader
