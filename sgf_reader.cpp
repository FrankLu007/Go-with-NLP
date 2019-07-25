#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <unordered_set>
#include <queue>
#include <dirent.h>
#include <unistd.h>
#include <sys/stat.h>

void error_message(const char * str) {std::fprintf(stderr, "\033[1;31mError\033[0m: %s\n", str); exit(-1);}
bool valid_postion(const unsigned position) {return position >= 0 && position < 361;}
char * decode_pos(const unsigned position) // position on the real board, can't be used in sgf
{
	static char ret[3];
	if(position == 361) return "PASS";
	if(!valid_postion(position)) error_message("wrong position in decoder.");
	std::memset(ret, 0, 3);
	ret[0] = position % 19 + 'A';
	if(ret[0] >= 'I') ret[0]++;
	ret[1] = position / 19 + '1';
	if(ret[1] > '9')
	{
		ret[2] = ret[1] - 10;
		ret[1] = '1';
	}
	return ret;
}
void unicode_handler(char * olds, char * news, unsigned & o_index, unsigned & n_index)
{
	unsigned offset = 0;
	if(!(olds[o_index] & 0x80)) offset = 1;
	else if(!(olds[o_index] & 0x20)) offset = 2;
	else if(!(olds[o_index] & 0x10)) offset = 3;
	else if(!(olds[o_index] & 0x08)) offset = 4;
	else if(!(olds[o_index] & 0x04)) offset = 5;
	else if(!(olds[o_index] & 0x02)) offset = 6;
	else error_message("wrong unicode.");

	while(offset--) news[n_index++] = olds[o_index++];
}
unsigned encode_pos(const char * position) {return (position[1] - 'a') * 19 + position[0] - 'a';} // from the sgf
class MOVE
{
	char board[361];
	unsigned color, position;
public:
	char * comment;
	unsigned step;
	MOVE * last;
	std::vector<MOVE *> child;
	MOVE():comment(NULL), step(0), color(-1), position(361), last(NULL)
	{
		std::memset(board, 0, 361);
		child.clear();
	}
	MOVE(const unsigned _step, const unsigned _color, const unsigned _position, const char * _board): step(_step), color(_color), position(_position), comment(NULL)
	{
		std::memcpy(board, _board, 361);
		child.clear();
		put_stone();
	}
	MOVE * add_child(const unsigned position, char * _comment)
	{
		MOVE * next = new MOVE(step + 1, -color, position, board);
		next->last = this;
		next->comment = _comment;
		if(_comment) next->arrange_comment();
		if(next->comment && !std::strlen(next->comment)) next->comment = NULL;	
		child.push_back(next);
		return next;
	}
	void put_stone()
	{
		board[position] = color;
		if(position % 19 && valid_postion(position - 1) && board[position - 1] == -color) get_stone(position - 1);
		if(position % 19 != 18 && valid_postion(position + 1) && board[position + 1] == -color) get_stone(position + 1);
		if(position / 19 && valid_postion(position - 19) && board[position - 19] == -color) get_stone(position - 19);
		if(position / 19 != 18 && valid_postion(position + 19) && board[position + 19] == -color) get_stone(position + 19);
	}
	void get_stone(const unsigned _position)
	{
		static std::unordered_set <unsigned> pos;
		static std::queue <unsigned> que;
		bool alive = 0;

		pos.clear();
		while(!que.empty()) que.pop();
		pos.insert(_position);
		que.push(_position);

		while(que.size())
		{
			unsigned current = que.front();
			que.pop();
			if(current % 19 != 18 && valid_postion(current + 1))
			{
				if(!board[current + 1]) {alive = 1; break;}
				if(board[current + 1] == board[current])
				{
					if(pos.find(current + 1) == pos.end())
					{
						pos.insert(current + 1);
						que.push(current + 1);
					}
				}
			}
				if(current % 19 && valid_postion(current - 1))
			{
				if(!board[current - 1]) {alive = 1; break;}
				if(board[current - 1] == board[current])
				{
					if(pos.find(current - 1) == pos.end())
					{
						pos.insert(current - 1);
						que.push(current - 1);
					}
				}
			}
			if(current / 19 != 18 && valid_postion(current + 19))
			{
				if(!board[current + 19]) {alive = 1; break;}
				if(board[current + 19] == board[current])
				{
					if(pos.find(current + 19) == pos.end())
					{
						pos.insert(current + 19);
						que.push(current + 19);
					}
				}
			}
			if(current / 19 && valid_postion(current - 19))
			{
				if(!board[current - 19]) {alive = 1; break;}
				if(board[current - 19] == board[current])
				{
					if(pos.find(current - 19) == pos.end())
					{
						pos.insert(current - 19);
						que.push(current - 19);
					}
				}
			}
		}
		if(alive) return;
		for(auto dead_stone : pos) board[dead_stone] = 0;
	}
	void display()
	{	
		std::printf("\033[43m%41s\033[0m\n\033[43m ", "");
		for(unsigned i = 0 ; i < 361 ; i++)
		{
			if(i && !(i % 19)) 
			{
				if(i - 1 != position) std::printf("\033[2;43m \033[0m");
				std::printf("\033[2;43m \033[0m\n\033[2;43m ");
			}
			if(i == position) std::printf("\033[1;31;2;43m(\033[0m");
			else if(i - 1 != position || !(i % 19)) std::printf("\033[2;43m \033[0m");
			switch(board[i])
			{
				case 1:
					std::printf("\033[2;30;2;43m0\033[0m");
					break;
				case -1:
					std::printf("\033[1;37;2;43m0\033[0m");
					break;
				case 0:
					std::printf("\033[1;30;2;43m.\033[0m");
					break;
				default:
					error_message("wrong board.");
			}
			if(i == position) std::printf("\033[1;31;2;43m)\033[0m");
		}
		std::printf("\033[2;43m  \033[0m\n\033[43m%41s\033[0m\n", "");
		std::printf("The %uth step is %s at %s\n", step, color == 1 ? "BLACK" : "WHITE", decode_pos(position));
		if(comment) {std::printf("Comment: %s\n\n", comment);  std::printf("\n");}
	}
	void clear()
	{
		for(auto child_pointer : child) child_pointer->clear();
		if(comment) delete comment;
		delete this;
	}
	void print_board(FILE * fp)
	{
		for(unsigned i = 0 ; i < 361 ; i++) std::fprintf(fp, "%d ", i == position ? board[i] * 10 : board[i]);
		std::fprintf(fp,"\n");
	}
	void arrange_comment()
	{
		char * tmp = comment;
		comment = new char[10000];
		unsigned len = std::strlen(tmp), real = 0;
		for(unsigned i = 0 ; i < len ;)
		{
			if(tmp[i] == ' ' || tmp[i] == '\n' || tmp[i] == '\r' || tmp[i] == '\t' || tmp[i] == '\\') {i++; continue;}
			//unicode_handler(tmp, comment, i, real);
			comment[real++] = tmp[i++];
		}
		comment[real] = 0;
	}
}board_root, * current = & board_root;
void clear() {for(auto child : board_root.child) child->clear();}
void build(char * sgf_raw_data, const char * end, MOVE * current)
{
	unsigned position;
	char * comment = NULL;
	while(sgf_raw_data < end && std::strncmp(sgf_raw_data, ";B[", 3) && std::strncmp(sgf_raw_data, ";W[", 3)) 
	{
		if(* sgf_raw_data == ')') return;
		sgf_raw_data++;
	}
	if(sgf_raw_data >= end) return;
	position = encode_pos(sgf_raw_data + 3);
	sgf_raw_data += 6;
	while(sgf_raw_data < end && std::strncmp(sgf_raw_data, ";B[", 3) && std::strncmp(sgf_raw_data, ";W[", 3) && std::strncmp(sgf_raw_data, "C[", 2))
	{
		if(* sgf_raw_data == ')') return;
		sgf_raw_data++;
	}
	if(sgf_raw_data >= end) return;
	if(!std::strncmp(sgf_raw_data, "C[", 2) && std::strncmp(sgf_raw_data, "C[]", 3)) 
	{
		comment = sgf_raw_data += 2;
		while(* sgf_raw_data != ']') sgf_raw_data++;
		* sgf_raw_data = 0;
		sgf_raw_data++;
	}
	
	build(sgf_raw_data, end, current->add_child(position, comment));
}
void load(const char * file_name)
{
	static char sgf_raw_data[100000];
	char * comment;
	FILE * fp = std::fopen(file_name, "r");
	std::fread(sgf_raw_data, 1, 100000, fp);
	std::fclose(fp);

	unsigned len = std::strlen(sgf_raw_data), index;
	board_root = MOVE();

	clear();
	for(index = 0 ; index < len ; index++) if(!std::strncmp(sgf_raw_data + index, ";B[", 3)) break;
	build(sgf_raw_data + index, sgf_raw_data + len, & board_root);
	current = & board_root;
}

int main(const int argc, const char ** argv)
{
	if(argc > 2) error_message("wrong usage.\nUsage: ./sgf_reader [sgf_file]");
	if(argc == 2) load(argv[1]);

	static char command[100];

	while(std::printf("sgf_reader > ") && std::scanf("%s", command))
	{
		if(!std::strcmp(command, "load") || !std::strcmp(command, "l"))
		{
			std::scanf("%s", command);
			load(command);
		}
		else if(!std::strcmp(command, "next") || !std::strcmp(command, "n"))
		{
			if(current->child.size()) current = current->child[0];
			current->display();
		}
		else if(!std::strcmp(command, "jump") || !std::strcmp(command, "j"))
		{
			unsigned step;
			std::scanf("%u", & step);
			if(step > current->step)
				while(current->child.size() && current->step != step) current = current->child[0];
			else if(step < current->step) 
				while(current->last && current->step != step) current = current->last;
			current->display();
		}
		else if(!std::strcmp(command, "back") || !std::strcmp(command, "b"))
		{
			if(current->last) current = current->last;
			current->display();
		}
		else if(!std::strcmp(command, "display") || !std::strcmp(command, "d")) current->display();
		else if(!std::strcmp(command, "help") || !std::strcmp(command, "h"))
		{
			std::printf("\tload/l    [sgf file] : load the file.\n"
						"\tnext/n               : display the next step.\n"
						"\tback/b               : go back to the last step.\n"
						"\tjump/j    #step      : jump the the specific step.\n"
						"\tdisplay/d            : display the current board.\n"
						"\tquit/q               : exit.\n");
		}
		else if(!std::strcmp(command, "quit") || !std::strcmp(command, "q")) break;
		else if(!std::strcmp(command, "collect"))
		{
			DIR * dir = opendir("sgf/");
			FILE * board = std::fopen("board.txt", "w"), * comment = std::fopen("comment.txt", "w");
			static char path[100];
			struct dirent * sgf;

			while(sgf = readdir(dir))
			{
				if(sgf->d_name[0] == '.') continue;
				std::sprintf(path, "sgf/%s", sgf->d_name);
				load(path);
				while(current->child.size())
				{
					if(current->comment)
					{
						current->print_board(board);
						std::fprintf(comment, "%s\n", current->comment);
					}
					current = current->child[0];
				}
			}
			std::fclose(board);
			std::fclose(comment);
		}
		else if(!std::strcmp(command, "embed"))
		{
			if(access("comment.txt", F_OK ) == -1)
			{
				std::printf("Please commit \"collect\" first.\n");
				continue;
			}
			unsigned sz;
			
			static char path[200], input[100000];
			
			std::printf("Input the embedding size (less than 1000): ");
			std::scanf("%u", &sz);
			std::sprintf(path, "embeddings/character_embedding_%uD.txt", sz);
			if(access(path, F_OK ) == -1)
			{
				std::sprintf(path, "embeddings/word2vec/trunk/word2vec -train comment.txt -output embeddings/character_embedding_%uD.txt -size %u -iter 100 -threads 6 -min-count 0\n", sz, sz);
				system(path);
				std::printf("\n");
			}
			else std::printf("File exists.\n");
		}
	}
	return 0;
}
