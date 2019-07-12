#include <cstdio>
#include <vector>
#include <cstring>
#include <cmath>
#include <omp.h>

#define LAYER_NUM 3



class DATA
{
public:
	double board[19][19];
	char * comment;
	DATA(): comment(NULL)
	{
		std::memset(board, 0, sizeof(board));
	}
	DATA(const double _board[19][19], const char * _comment)
	{
		std::memcpy(board, _board, sizeof(board));
		comment = strdup(_comment);
	}
};

std::vector <DATA> data_set;
double learning_rate = 0;
unsigned long long epoch_num = 0;
double kernel[3][3], hidden_layer[19][19];

void error_message(const char * message) {std::fprintf(stderr, "\033[1;31mError\033[0m: %s\n", message); exit(-1);}
void read_input(const char * file_name)
{
	static double board[19][19];
	static char comment[10000];
	FILE * fp = std::fopen(file_name, "r");
	if(!fp) error_message("cannot open file.");
	while(1)
	{
		if(!std::fgets(comment, 10000, fp)) break;
		for(unsigned x = 0 ; x < 19 ; x++) for(unsigned y = 0 ; y < 19 ; y++) std::fscanf(fp, "%lf", & board[x][y]);
		std::fgets(comment, 10000, fp);
		data_set.push_back(DATA(board, comment));
	}
	std::fclose(fp);
	std::printf("Number of data: %lu\n", data_set.size());
}
inline double sigmoi(double x) {return 1.0/(double)(1+exp(-x));}
inline double derivate_sigmoi(double z) {return z * (1 - z);}
void init(const unsigned argc, const char ** argv)
{
	bool input = 0;
	for(unsigned i = 0 ; i < argc ; i++)
	{
		if(std::strstr(argv[i], "--input="))
		{
			if(input) error_message("only accept one input file.");
			read_input(argv[i] + 8);
			input = 1;
		}
		else if(std::strstr(argv[i], "--learning_rate="))
		{
			if(learning_rate) error_message("only accept one learning rate.");
			learning_rate = atof(argv[i] + 16);
		}
		else if(std::strstr(argv[i], "--epoch_num="))
		{
			if(epoch_num) error_message("only accept one epoch number.");
			epoch_num = atoll(argv[i] + 12);
		}
	}
	if(!input) error_message("no input file.");
	if(learning_rate <= 0) learning_rate = 0.1;
	if(epoch_num <= 0) epoch_num = 10000;
}
inline double ReLu(double x) {return x > 0 ? x : 0;}
void convolution(double input_board[19][19], double kernel[3][3], double output_board[19][19])
{
	std::memset(output_board, 0, sizeof(output_board));
	for(unsigned x = 1 ; x < 18 ; x++) 
		for(unsigned y = 1 ; y < 18 ; y++) 
		output_board[x][y] = input_board[x - 1][y - 1] * kernel[x - 1][y - 1] + input_board[x][y - 1] * kernel[x][y - 1] + input_board[x + 1][y - 1] * kernel[x + 1][y - 1]
							+ input_board[x - 1][y] * kernel[x - 1][y] + input_board[x][y] * kernel[x][y] + input_board[x + 1][y] * kernel[x + 1][y]
							+ input_board[x - 1][y + 1] * kernel[x - 1][y + 1] + input_board[x][y + 1] * kernel[x][y + 1] + input_board[x + 1][y + 1] * kernel[x + 1][y + 1];
	for(unsigned x = 1 ; x < 18 ; x++) for(unsigned y = 1 ; y < 18 ; y++) output_board[x][y] = ReLu(output_board[x][y]);
}
int main(const int argc, const char ** argv)
{
	init(argc, argv);
	std::printf("Learning rate: %f\nEpoch number: %llu\n", learning_rate, epoch_num);
	for(unsigned epoch = 0 ; epoch < epoch_num ; epoch++)
	{
		if(epoch % 100 == 0)std::printf("%u\n", epoch);
		for(unsigned batch = 0 ; batch < data_set.size() ; batch++)
		{
			convolution(data_set[batch].board, kernel, hidden_layer);
		}
	}
	return 0;
}