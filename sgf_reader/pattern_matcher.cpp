#include <csdtio>
class PATTERN
{
	bool is_corner;
	std::vector<std::string> name;
	unsigned char board[19][19], height;
	PATTERN()
	{
		is_corner = false;
		name.clear();
		std::memset(board, 0, sizeof(board));
		height = 0;
	}
};
std::vector <PATTERN> pattern_list;
void input_pattern_file(char * filename)
{
	FILE * fp = fopen(filename, "r");
	char input_buffer[10000];
	pattern_list.clear();

	std::fscanf(fp, "(");
	while(std::fscanf(fp, "%s", input_buffer) && input_buffer[0] != ')')
	{
		std::fscanf(fp, ";%s", input_buffer);
		pattern_list.push_back(input_parser(input_buffer));
		std::fscanf(fp, ")");
	}
	std::printf("# Pattern : %u\n", pattern_list.size());
	std::fclose(fp);
}
PATTERN input_parser(char * data_buffer)
{
	PATTERN pattern;
	std::string key(""), value("");
	bool bracelet = false;

	for(unsigned i = 0 ; i < std::strlen(data_buffer) ; i++)
	{
		if(!bracelet)
		{
			if(data_buffer[i] != '[') key += data_buffer[i];
			else 
			{
				bracelet = true;
				value = "";
			}
		}
		else
		{
			if(data_buffer[i] != ']') value += data_buffer[i];
			else 
			{
				bracelet = false;
				if(i + 1 < std::strlen(data_buffer) && data_buffer[i + 1] != '[') key = "";
			}
		}
	}
}