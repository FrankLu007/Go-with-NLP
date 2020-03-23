#include <cstdio>
#include <iostream>
#include <cstdlib>
#include <string>
#include <cstring>
#include <dirent.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define input_buffer_size 100000
#define cgi_buffer_size 100000

unsigned FileNo = 0;
int socket_fd;

std::string position_decoder(int pos)
{
	char ret[10];
	char y = pos % 19, x = 19 - (pos - y) / 19;
	y += 'A';
	if(y > 'H') y++;
	std::memset(ret, 0, 10);
	std::sprintf(ret, "%c%d", y, 20 - x);

	return std::string(ret);
}

int connect(const char * ip = "140.113.86.123", const int port = 16101)
{
	socket_fd = socket(AF_INET, SOCK_STREAM, 0);
	if(socket_fd == -1) {std::fprintf(stderr, "%s\n", "Fail to create socket."); exit(-1);}

	struct sockaddr_in info;
    std::memset(& info, 0, sizeof(info));
    info.sin_family = AF_INET;
    info.sin_addr.s_addr = inet_addr(ip);
    info.sin_port = htons(port);

    if(connect(socket_fd, (struct sockaddr *) & info, sizeof(info)) == -1) {std::fprintf(stderr, "%s\n", "Fail to connect socket."); exit(-1);}

    return socket_fd;
}

void count_value(float board[][19], float * count) //左上、上、右上、左、中、右、左下、下、右下
{
	std::memset(count, 0, sizeof(float) * 9);

	for(int i = 0 ; i < 19 ; i++)
		for(int j = 0 ; j < 19 ; j++)
		{
			if(board[i][j] < 0.1 && board[i][j] > -0.1) continue;
			if(i < 8)
			{
				if(j < 8) count[0] += board[i][j];
				if(j > 3 || j < 15) count[1] += board[i][j];
				if(j > 10) count[2] += board[i][j];
			}
			if(i > 3 || i < 15)
			{
				if(j < 8) count[3] += board[i][j];
				if(j > 3 || j < 15) count[4] += board[i][j];
				if(j > 10) count[5] += board[i][j];
			}
			if(i > 10)
			{
				if(j < 8) count[6] += board[i][j];
				if(j > 3 || j < 15) count[7] += board[i][j];
				if(j > 10) count[8] += board[i][j];
			}
		}
}

int cgi_write(std::string message) { message += "\n"; printf("%s", message.c_str()); return write(socket_fd, message.c_str(), message.length()); }
void cgi_getC17(FILE * file_pointer)
{
	static char buffer[cgi_buffer_size];
	cgi_write(std::string("T_SL_features"));
	while(std::cin.getline(buffer, cgi_buffer_size) && std::strlen(buffer) < 30);
	for(int i = 0 ; i < 16 ; i++)
	{
		for(int j = 0 ; j < 361 ; j++)
			if(buffer[i * 361 + j] == '1') std::fprintf(file_pointer, "%d ", j);
		std::fprintf(file_pointer, "\n");
	}
	std::fprintf(file_pointer, "%c\n", buffer[48 * 361 + 1]);
}

void cgi_getBV(FILE * file_pointer)
{
	static char buffer[cgi_buffer_size];
	static float board[19][19], count[9];
	cgi_write(std::string("dcnn_bv_vn"));
	for(int i = 0 ; i < 19 ; i++)
	{
		while(std::cin.getline(buffer, cgi_buffer_size) && std::strlen(buffer) < 30);
		board[i][0] = std::atof(std::strtok(buffer, " "));
		for(int j = 1 ; j < 19 ; j++) board[i][j] = std::atof(std::strtok(NULL, " "));
	}
	count_value(board, count);
	for(int i = 0 ; i < 9 ; i++) std::fprintf(file_pointer, "%lf ", count[i]);
	std::fprintf(file_pointer, "\n");
}

void transfer(std::string input_file, std::string output_file)
{
	FILE * input_pointer = std::fopen(input_file.c_str(), "r"), * output_pointer = std::fopen(output_file.c_str(), "w");
	static char input_buffer[input_buffer_size];
	std::fread(input_buffer, 1, input_buffer_size, input_pointer);
	std::fclose(input_pointer);

	unsigned len = std::strlen(input_buffer);
	bool bracelet = 0;
	std::string key, value, buffer;
	buffer.clear();

	dup2(socket_fd, STDIN_FILENO);
	cgi_write(std::string("clear_board"));
	cgi_getBV(output_pointer);
	

	for(unsigned i = 0 ; i < len ; i++)
	{
		if(input_buffer[i] == ')' && !bracelet) break;
		switch(input_buffer[i])
		{
			case '\n':
			case '\r':
			case ';' :
			case ' ' :
			case '	':
				break; 
			case '[' :
				key = buffer;
				buffer.clear();
				bracelet = 1;
				break;
			case ']' :
				bracelet = 0;
				value = buffer;
				buffer.clear();
				if(key == "B" || key == "W") 
				{
					int pos = (18 - value[1] + 'a') * 19 + value[0] - 'a';
					std::fprintf(output_pointer, "%s %d\n", key.c_str(), pos);
					cgi_write(std::string("play ") + key + std::string(" ") + position_decoder(pos));
					cgi_getC17(output_pointer);
					cgi_getBV(output_pointer);

					if(key == "W") exit(0);
				}
				else if(key == "C") std::fprintf(output_pointer, "C %s\n", value.c_str());
				else if(key == "SZ" && value != "19") {std::fclose(output_pointer); FileNo--;return; }
				else if(key == "HA" && value != "0") {std::fclose(output_pointer); FileNo--;return; }
				break;
			case '(' :
				if(!bracelet) break;
			default :
				buffer += input_buffer[i];
		}
	}

	std::fclose(output_pointer);
}

int main(const int argc, const char ** argv)
{
	unsigned cnt = 0;
	if(argc != 3)
	{
		std::fprintf(stderr, "Usage : sgf_reader [input folder] [output folder]\nEx. sgf_reader input/ output/\n");
		return -1;
	}
	connect();
	DIR * dir = opendir(argv[1]), * dir2;
	struct dirent * sgf, * chess;
	while(sgf = readdir(dir))
	{
		if(sgf->d_name[0] != '$') continue;
		std::string path = std::string(argv[1]) + std::string(sgf->d_name) + std::string("/");
		dir2 = opendir(path.c_str());
		while(chess = readdir(dir2))
		{
			if(chess->d_name[0] == '.') continue;
			// unsigned len = std::strlen(chess->d_name);
			//if(chess->d_name[len - 4] != '.' || chess->d_name[len - 3] != 's' || chess->d_name[len - 2] != 'g' || chess->d_name[len - 1] != 'f') continue;
			transfer(path + std::string(chess->d_name), std::string(argv[2]) + std::to_string(FileNo));
			FileNo++;
			cnt++;
			if(FileNo == 1) return 0;
		}
		closedir(dir2);
	}
	closedir(dir);
	std::printf("#Game : %u\n", cnt);
	return 0;
}