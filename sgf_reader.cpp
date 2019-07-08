#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <unordered_set>
#include <queue>

void error_message(const char * str) {std::fprintf(stderr, "\033[1;31mError\033[0m: %s\n", str); exit(-1);}
bool valid_postion(const unsigned position){return position && position < 361;}
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
unsigned encode_pos(const char * position) {return (*(position+1) - 'A') * 19 + * position - 'A';} // from the sgf
class MOVE
{
	char board[361], * comment;
	unsigned color, position;
public:
	unsigned step;
	MOVE * last;
	std::vector<MOVE *> child;
	MOVE():comment(NULL), step(0), color(-1), position(383), last(NULL)
	{
		std::memset(board, 0, 381);
		child.clear();
	}
	MOVE(const unsigned _step, const unsigned _color, const unsigned _position, const char * _board): step(_step), color(_color), position(_position), comment(NULL)
	{
		std::memcpy(board, _board, 381);
		child.clear();
		put_stone();
	}
	MOVE * add_child(const unsigned position, char * _comment)
	{
		MOVE * next = new MOVE(step + 1, -color, position, board);
		next->last = this;
		next->comment = _comment;
		child.push_back(next);
		return next;
	}
	void put_stone()
	{
		board[position] = color;
		if(valid_postion(position - 1) && board[position] == -color) get_stone(position - 1);
		if(valid_postion(position + 1) && board[position] == -color) get_stone(position + 1);
		if(valid_postion(position - 19) && board[position] == -color) get_stone(position - 19);
		if(valid_postion(position + 19) && board[position] == -color) get_stone(position + 19);
	}
	void get_stone(const unsigned _position)
	{
		static std::unordered_set <unsigned char> pos;
		static std::queue <unsigned char> que;
		bool alive = 0;

		pos.clear();
		while(!que.empty()) que.pop();
		pos.insert(_position);
		que.push(_position);

		while(que.size())
		{
			unsigned char current = que.front();
			que.pop();
			if(valid_postion(current + 1))
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
			if(valid_postion(current - 1))
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
			if(valid_postion(current + 19))
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
			if(valid_postion(current - 19))
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
		const char RED[] = "\033[1;31;2;43m", WHITE[] = "\033[1;37;2;43m", BLACK[] = "\033[1;30;2;43m";
		
		for(unsigned i = 0 ; i < 361 ; i++)
		{
			if(i && !(i % 19)) std::printf(" \033[0m\n");
			if(i == position) std::printf("\033[1;31;2;43m(");
			else if(i - 1 != position)std::printf("\033[2;43m ");
			switch(board[i])
			{
				case 1:
					std::printf("\033[1;30;2;43m0");
					break;
				case -1:
					std::printf("\033[1;37;2;43m0");
					break;
				case 0:
					std::printf("\033[1;30;2;43m.");
					break;
				default:
					error_message("wrong board.");
			}
			if(i == position) std::printf("\033[1;31;2;43m)");
		}
		std::printf(" \033[0m\n\033[43m%39s\033[0m\n", "");
		std::printf("The last step is %s at %s\n", color == 1 ? "BLACK" : "WHITE", decode_pos(position));
	}
	void clear()
	{
		for(auto child_pointer : child) child_pointer->clear();
		delete this;
	}
}board_root, * current = & board_root;
void clear() {for(auto child : board_root.child) child->clear();}
void build(char * sgf_raw_data, const char * end, MOVE * current)
{
	unsigned position;
	char * comment = NULL;
	while(std::strncmp(sgf_raw_data, ";B[", 3) && std::strncmp(sgf_raw_data, ";W[", 3) && std::strncmp(sgf_raw_data, ";C[", 3) && sgf_raw_data < end) 
	{
		if(* sgf_raw_data == ')' && * (sgf_raw_data - 1) != '(') return;
		sgf_raw_data++;
	}
	if(sgf_raw_data == end) return;
	if(!std::strncmp(sgf_raw_data, ";B[", 3) || !std::strncmp(sgf_raw_data, ";W[", 3)) position = encode_pos(sgf_raw_data);
	sgf_raw_data += 6;
	if(sgf_raw_data == end) return;
	while(std::strncmp(sgf_raw_data, ";B[", 3) && std::strncmp(sgf_raw_data, ";W[", 3) && std::strncmp(sgf_raw_data, ";C[", 3) && sgf_raw_data < end) sgf_raw_data++;
	if(sgf_raw_data == end) return;
	if(!std::strncmp(sgf_raw_data, ";C[", 3)) 
	{
		comment = sgf_raw_data + 3;
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

	for(index = 0 ; index < len ; index++) if(!std::strncmp(sgf_raw_data + index, ";B[", 3)) break;
	build(sgf_raw_data + index, sgf_raw_data + len, & board_root);
}

int main(const int argc, const char ** argv)
{
	if(argc > 2) error_message("wrong usage.\nUsage: ./sgf_reader [sgf_file]");
	if(argc == 2) load(argv[1]);

	static char command[100];

	while(std::scanf("%s", command))
	{
		if(!std::strcmp(command, "load") || !std::strcmp(command, "L"))
		{
			std::scanf("%s", command);
			load(command);
		}
		else if(!std::strcmp(command, "next") || !std::strcmp(command, "N"))
		{
			if(current->child.size()) current = current->child[0];
			current->display();
		}
		else if(!std::strcmp(command, "jump") || !std::strcmp(command, "J"))
		{
			unsigned step;
			std::scanf("%u", & step);
			if(step > current->step)
				while(current->child.size() && current->step != step) current = current->child[0];
			else if(step < current->step) 
				while(current->last && current->step != step) current = current->last;
			current->display();
		}
	}
	return 0;
}
