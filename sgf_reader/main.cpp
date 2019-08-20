#include <dirent.h>
#include "sgf_reader.cpp"

READER reader;

int main()
{
	DIR * dir = opendir("../sgf/");
	struct dirent * sgf;
	while(sgf = readdir(dir))
	{
		if(sgf->d_name[0] == '.') continue;
		reader.load(std::string("../sgf/") + std::string(sgf->d_name));
	}
	reader.collect(stdout);
}