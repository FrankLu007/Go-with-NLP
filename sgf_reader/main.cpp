#include <dirent.h>
#include "sgf_reader.cpp"

READER reader;

int main(const int argc, const char ** argv)
{
	if(argc == 2)
	{
		reader.load(std::string(argv[1]));
		reader.panel(0);
		return 0;
	}
	DIR * dir = opendir("../sgf/");
	struct dirent * sgf;
	while(sgf = readdir(dir))
	{
		if(sgf->d_name[0] == '.') continue;
		reader.load(std::string("../sgf/") + std::string(sgf->d_name));
	}
	std::printf("Collecting...\n");
	reader.collect(std::fopen("../data/data.txt", "w"));
}