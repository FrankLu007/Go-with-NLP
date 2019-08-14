#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <unordered_map>

typedef unsigned short move_t;

void error_message(const std::string & str) {std::fprintf(stderr, "\033[1;31mError\033[0m: %s\n", str.c_str()); exit(-1);}
void warning_message(const std::string & str) {std::fprintf(stderr, "\033[1;31mWarning\033[0m: %s\n", str.c_str());}
class GAME
{
	std::string filename;
	std::vector <move_t> move;
	std::unordered_map <unsigned short, std::string> comment; // move id --> comment
public:
	GAME()
	{
		filename.clear();
		move.clear();
		comment.clear();
	}
	GAME(std::string & filename) : filename(filename)
	{
		move.clear();
		comment.clear();
	}
	inline void add_data(std::string & key, std::string & data)
	{
		if(key == "AB" || key == "AW") error_message(std::string("shouldn't read \"") + key + std::string("\" in ") + filename);
		else if(key == "B" || key == "W")
		{
			if((move.size() & 1) ^ (key == "W")) error_message(std::string("wrong order in : ") + filename);
			if(data.length() != 2) error_message(std::string("wrong position : ") + data);
			move.push_back((data[1] - 'a') * 19 + data[0] - 'a');
		}
		else if(key == "C") comment[move.size() - 1] = data;
	}
};
class READER
{
	std::unordered_map <std::string, GAME> game_set;
public:
	READER()
	{
		game_set.clear();
	}
	void load(std::string filename)
	{
		FILE * fp = std::fopen(filename.c_str(), "r");
		if(!fp) error_message(std::string("can't open file : ") + filename);

		if(game_set.find(filename) != game_set.end())
		{
			warning_message(std::string("file exists : ") + filename);
			return ;
		}

		std::string raw_sgf_data = get_sgf_data(fp);
		std::fclose(fp);

		GAME game(filename);
		unsigned len = raw_sgf_data.length();
		std::string key, value, buffer;
		buffer.clear();

		for(unsigned i = 0 ; i < len ; i++)
		{
			if(raw_sgf_data[i] == ')') break;
			switch(raw_sgf_data[i])
			{
				case '\n':
				case '\r':
				case ';' :
					break;
				case '[' :
					key = buffer;
					buffer.clear();
					break;
				case ']' :
					value = buffer;
					buffer.clear();
					game.add_data(key, value);
					break;
				default :
					buffer += raw_sgf_data[i];
			}
		}

		game_set[filename] = game;
	}
	std::string get_sgf_data(FILE * fp)
	{
		#define DATA_BUFFER 100000
		static char buffer[DATA_BUFFER];
		std::fread(buffer, 1, DATA_BUFFER, fp);
		return std::string(buffer);
	}
	void display()
	{	
		// std::printf("\033[43m%41s\033[0m\n\033[43m ", "");
		// for(unsigned i = 0 ; i < 361 ; i++)
		// {
		// 	if(i && !(i % 19)) 
		// 	{
		// 		if(i - 1 != position) std::printf("\033[2;43m \033[0m");
		// 		std::printf("\033[2;43m \033[0m\n\033[2;43m ");
		// 	}
		// 	if(i == position) std::printf("\033[1;31;2;43m(\033[0m");
		// 	else if(i - 1 != position || !(i % 19)) std::printf("\033[2;43m \033[0m");
		// 	switch(board[i])
		// 	{
		// 		case 1:
		// 			std::printf("\033[2;30;2;43m0\033[0m");
		// 			break;
		// 		case -1:
		// 			std::printf("\033[1;37;2;43m0\033[0m");
		// 			break;
		// 		case 0:
		// 			std::printf("\033[1;30;2;43m.\033[0m");
		// 			break;
		// 		default:
		// 			error_message("wrong board.");
		// 	}
		// 	if(i == position) std::printf("\033[1;31;2;43m)\033[0m");
		// }
		// std::printf("\033[2;43m  \033[0m\n\033[43m%41s\033[0m\n", "");
		// std::printf("The %uth step is %s at %s\n", step, color == 1 ? "BLACK" : "WHITE", decode_pos(position));
		// if(comment) {std::printf("Comment: %s\n\n", comment);  std::printf("\n");}
	}
	void control()
	{
		static char command[100];
		std::printf("Enter control mode :\n");
	}
};
int main(const int argc, const char ** argv)
{
	static READER reader;
	static char command[100];

	while(std::printf("sgf_reader > ") && std::scanf("%s", command))
	{
		if(!strcmp(command, "load"))
		{
			std::scanf("%s", command);
			reader.load(std::string(command));
			reader.control();
		}
	}
	return 0;
}