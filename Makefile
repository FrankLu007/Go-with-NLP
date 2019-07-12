all:
	g++ -o train -O3 -fopenmp train.cpp
	g++ -g -o sgf_reader -O3 sgf_reader.cpp
clean:
	rm sgf_reader data.txt