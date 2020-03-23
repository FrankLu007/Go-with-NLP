#include <queue>
#include <cstring>
#include <unordered_set>
#include "game.cpp"

class READER
{
	move_t board[362];
	std::unordered_map <std::string, GAME> game_set; // file name --> game
public:
	READER()
	{
		game_set.clear();
	}
	inline void error_message(const std::string & str, const std::string & filename) {std::fprintf(stderr, "\033[1;31mError\033[0m: %s in %s\n", str.c_str(), filename.c_str()); exit(-1);}
	inline void error_message(const std::string & str) {std::fprintf(stderr, "\033[1;31mError\033[0m: %s\n", str.c_str()); exit(-1);}
	void load(std::string filename) // non-concurrent
	{
		FILE * fp = std::fopen(filename.c_str(), "r");
		if(!fp) error_message(std::string("can't open file : ") + filename);
		if(game_set.find(filename) != game_set.end()) return ;

		#define DATA_BUFFER 100000	
		static char input_buffer[DATA_BUFFER];
		std::fread(input_buffer, 1, DATA_BUFFER, fp);
		std::string raw_sgf_data(input_buffer);
		std::fclose(fp);

		GAME game(filename);
		unsigned len = raw_sgf_data.length();
		bool bracelet = 0;
		static std::string key, value, buffer;
		buffer.clear();

		for(unsigned i = 0 ; i < len ; i++)
		{
			if(raw_sgf_data[i] == ')' && !bracelet) break;
			switch(raw_sgf_data[i])
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
					game.add_data(key, value);
					break;
				case '(' :
					if(!bracelet) break;
				default :
					buffer += raw_sgf_data[i];
			}
		}
		game_set[filename] = game;
	}
	
	void panel(unsigned game_no)
	{
		if(game_no >= game_set.size()) {error_message(std::string("invalid range.")); return ;}

		static char command[100];
		std::unordered_map <std::string, GAME>::iterator game = game_set.begin();
		while(game_no--) game++;
		move_t current = 0;

		std::printf("Enter the control panel : %s : %u\n", game->first.c_str(), game->second.size());
		while(std::printf("[%s] %d > ", game->first.c_str(), current) && std::scanf("%s", command))
		{
			if(!strcmp(command, "show"))display(current, game->second.get_comment(current));
			else if(!strcmp(command, "next"))
			{
				get_board(++current, game->second);
				display(current, game->second.get_comment(current));
			}
			else if(!strcmp(command, "back"))
			{
				get_board(--current, game->second);
				display(current, game->second.get_comment(current));
			}
			else if(!strcmp(command, "jump"))
			{
				move_t step;
				std::scanf("%u", & step);
				get_board(current = step, game->second);
				display(current, game->second.get_comment(current));
			}
			else if(!strcmp(command, "quit")) break;
			else
			{
				if(!strcmp(command, "help")) std::fprintf(stderr, "unrecognized command : %s\n", command);
				std::printf("\tshow          - display the board.\n"
							"\tnext          - go to next move.\n"
							"\tback          - go back to last move.\n"
							"\tjump [number] - jump to the specific step.\n"
							"\thelp          - show this message.\n");
			}
		}
		std::printf("Exit the control panel.\n");
	}
	void display(move_t step, std::string comment)
	{
		std::printf("\033[43m   ");
		for(char a = 'A' ; a < 'T'; a++) std::printf("\033[30m %c", a); // print A ~ S
		step = step ? step : 500;
		for(move_t i = 0 ; i < 361 ; i++)
		{
			if(i && board[i-1] == step) std::printf("\033[31m)\033[30m");
			if(!(i % 19)) 
			{
				if(!i || board[i - 1] != step) std::printf(" ");
				std::printf(" \033[0m\n\033[30;43m %c ", 'A' + i / 19);
			}
			if(board[i] == step) std::printf("\033[31m(\033[30m");
			else if(!(i%19) || board[i - 1] != step) std::printf(" ");
			if(!board[i]) std::printf(".");
			else if(board[i] & 1) std::printf("0");
			else std::printf("\033[37m0\033[30m");
		}
		if(step != board[360]) std::printf(" ");
		std::printf(" \033[0m\n\033[43m%43s\033[0m\n", "");
		std::printf("Comment : %s\n", comment.c_str());
	}
	inline void get_board(move_t step, GAME & game)
	{
		bool color;
		static std::unordered_set <move_t> death;
		std::memset(board, 0, sizeof(board));
		if(!step) return ;
		for(move_t i = 1 ; i <= step ; i++)
		{
			move_t position = game.get_move(i);
			if(board[position]) {error_message(std::to_string(i) + std::string("th the stone has existed at ") + std::to_string(position), game.name());}
			board[position] = i;
			color = i & 1;
			if(position % 19 && (board[position - 1] & 1) != (board[position] & 1) && board[position - 1] && get_group(position - 1, death, NULL, 0)) for(auto pos : death) board[pos] = 0;
			if(position > 18 && (board[position - 19] & 1) != (board[position] & 1) && board[position - 19] && get_group(position - 19, death, NULL, 0)) for(auto pos : death) board[pos] = 0;
			if(position % 19 != 18 && (board[position + 1] & 1) != (board[position] & 1) && board[position + 1] && get_group(position + 1, death, NULL, 0)) for(auto pos : death) board[pos] = 0;
			if(position < 342 && (board[position + 19] & 1) != (board[position] & 1) && board[position + 19] && get_group(position + 19, death, NULL, 0)) for(auto pos : death) board[pos] = 0;
		}
	}

	bool get_group(const move_t position, std::unordered_set <move_t> & group, std::unordered_set <move_t> * life, const unsigned chi = 361)
	{
		// position : the beginning of the search
		// group : the target
		// life : the rest of chi
		// chi : if the group has more than N chi, return false
		static std::queue <move_t> q; // store position, used in bfs
		while(!q.empty()) q.pop();
		q.push(position);
		group.clear();
		group.insert(position);
		if(life) life->clear();

		const bool color = board[position] & 1;
		while(!q.empty())
		{
			move_t pos = q.front();
			q.pop();

			if(pos % 19)
			{
				if(!board[pos - 1])
				{
					if(life) 
					{
						life->insert(pos - 1);
						if(life->size() > chi) return false;
					}
					if(!chi) return false;
				}
				else if((board[pos - 1] & 1) == color && group.find(pos - 1) == group.end())
				{
					q.push(pos - 1);
					group.insert(pos - 1);
				}
			}
			if(pos > 18)
			{
				if(!board[pos - 19])
				{
					if(life) 
					{
						life->insert(pos - 19);
						if(life->size() > chi) return false;
					}
					if(!chi) return false;
				}
				else if((board[pos - 19] & 1) == color && group.find(pos - 19) == group.end())
				{
					q.push(pos - 19);
					group.insert(pos - 19);
				}
			}
			if(pos % 19 != 18)
			{
				if(!board[pos + 1])
				{
					if(life) 
					{
						life->insert(pos + 1);
						if(life->size() > chi) return false;
					}
					if(!chi) return false;
				}
				else if((board[pos + 1] & 1) == color && group.find(pos + 1) == group.end())
				{
					q.push(pos + 1);
					group.insert(pos + 1);
				}
			}
			if(pos < 342)
			{
				if(!board[pos + 19])
				{
					if(life) 
					{
						life->insert(pos + 19);
						if(life->size() > chi) return false;
					}
					if(!chi) return false;
				}
				else if((board[pos + 19] & 1) == color && group.find(pos + 19) == group.end())
				{
					q.push(pos + 19);
					group.insert(pos + 19);
				}
			}
		}
		return life ? life->size() == chi : true;
	}

	void collect(FILE * fp, unsigned N = 8)
	{
		unsigned count = 0;
		static std::unordered_set <move_t> group, life;
		std::unordered_set <move_t> def[N + 1], att[N + 1];
		for(std::unordered_map <std::string, GAME>::iterator it = game_set.begin() ; it != game_set.end() ; it++)
		{
			GAME & game = it->second;
			for(move_t step = 1 ; step <= game.size() ; step++)
			{
				std::string comment = game.get_comment(step);
				if(comment == "(NULL)") continue;
				std::printf("%s\n", game.name().c_str());
				for(move_t i = 1 ; i <= N ; i++) {def[i].clear(); att[i].clear();}

				std::fprintf(fp, "%u\n", step);
				// previous N step
				for(move_t i = N ; i ; i--) 
				{
					get_board(step <= i - 1 ? 0 : step - i + 1, game);
					for(move_t pos = 0 ; pos < 361 ; pos++) if(board[pos] == 1) std::fprintf(fp, "%u ", pos); // black
					std::fprintf(fp, "\n");
					for(move_t pos = 0 ; pos < 361 ; pos++) if(board[pos] == -1) std::fprintf(fp, "%u ", pos); // white
					std::fprintf(fp, "\n");
				}

				// // 1~8+ liberty & capture size
				// get_board(step <= 1 ? 0 : step - 1, game);
				// for(move_t pos = 0 ; pos < 361 ; pos++)
				// 	if(board[pos])
				// 	{
				// 		get_group(pos, group, & life);
				// 		if((board[pos] & 1) == (step & 1)) def[life.size() >= N ? N : life.size()].insert(group.begin(), group.end());
				// 		else att[life.size() >= N ? N : life.size()].insert(life.begin(), life.end());
				// 	}
				// for(move_t i = 1 ; i <= N ; i++) {for(auto pos : def[i]) std::fprintf(fp, "%u ", pos); std::fprintf(fp, "\n");}
				// for(move_t i = 1 ; i <= N ; i++) {for(auto pos : att[i]) std::fprintf(fp, "%u ", pos); std::fprintf(fp, "\n");}
				// for(move_t i = 1 ; i <= N ; i++) {def[i].clear(); att[i].clear();}

				// // self-Atari size
				// for(move_t pos = 0 ; pos < 361 ; pos++)
				// 	if((board[pos] & 1) == (step & 1))
				// 	{
				// 		get_board(step <= 1 ? 0 : step - 1, game);
				// 		if(get_group(pos, group, & life, 2))
				// 		{
				// 			move_t a = * life.begin(), b = * (life.begin() ++);
				// 			board[a] = step;
				// 			if(get_group(pos, group, & life, 1)) 
				// 				att[group.size() >= N ? N : group.size()].insert(a);
				// 			board[a] = 0;
				// 			board[b] = step;
				// 			if(get_group(pos, group, & life, 1)) 
				// 				att[group.size() >= N ? N : group.size()].insert(b);
				// 			board[b] = 0;
				// 		}
				// 	}
				// for(move_t i = 1 ; i <= N ; i++) {for(auto pos : att[i]) std::fprintf(fp, "%u ", pos); std::fprintf(fp, "\n");}


				// // liberty after move
				// get_board(step, game);
				// for(move_t pos = 0 ; pos < 361 ; pos++)
				// {
				// 	if(board[pos] && (board[pos] & 1) == (step & 1))
				// 	{
				// 		get_group(pos, group, & life);
				// 		def[life.size() >= N ? N : life.size()].insert(group.begin(), group.end());
				// 	}
				// }
				// for(move_t i = 1 ; i <= N ; i++) {for(auto pos : def[i]) std::fprintf(fp, "%u ", pos); std::fprintf(fp, "\n");}

				// // turn color
				// std::fprintf(fp, "%d\n", step & 1);

				// comment
				std::fprintf(fp, "%s\n", comment.c_str());

				count++;
			}
		}
		std::printf("Count : %u\n", count);
	}
};