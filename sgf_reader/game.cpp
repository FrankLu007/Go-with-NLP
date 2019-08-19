#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <unordered_map>

typedef unsigned short move_t; // used in postion and number of move

class GAME
{
	std::string filename;
	std::vector <move_t> move;
	std::unordered_map <move_t, std::string> comment; // move id --> comment
public:
	GAME()
	{
		filename = std::string("(NULL)");
		move.clear();
		comment.clear();
	}
	GAME(std::string & _filename) : filename(_filename)
	{
		move.clear();
		comment.clear();
	}
	inline void error_message(const std::string & str) {std::fprintf(stderr, "\033[1;31mError\033[0m: %s in %s\n", str.c_str(), filename.c_str()); exit(-1);}
	inline void add_data(const std::string & key, const std::string & data)
	{
		if(key == "AB" || key == "AW") error_message(std::string("shouldn't read \"") + key); // Add Black/White
		else if(key == "B" || key == "W")
		{
			std::printf("%s %s\n", key.c_str(), data.c_str());
			if((move.size() & 1) ^ (key == "W")) error_message(std::string("wrong order of ") + key + std::string(" ") + data );
			move_t pos = (data[1] - 'a') * 19 + data[0] - 'a';
			if(data.length() != 2 || pos > 361) error_message(std::string("wrong position : ") + data);
			move.push_back(pos);
		}
		else if(key == "C") comment[move.size()] = data;
	}
	inline move_t get_move(move_t step) {if(step > move.size()) error_message(std::string("too large step ") + std::to_string(step)); return move[step - 1];}
	inline std::string get_comment(move_t step) {return comment.find(step) == comment.end() ? std::string("(NULL)") : comment[step];}
	inline std::string & name() {return filename;}
	inline const char * name() const {return filename.c_str();}
	inline move_t size() const {return move.size();}
	inline move_t num_comment() const {return comment.size();}
};