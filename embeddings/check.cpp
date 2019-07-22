#include <cstdio>
#include <cstring>
#include <string>
#include <unordered_set>
using namespace std;
unordered_set <string> dict;
int main()
{
	dict.clear();
	static char input[100000];
	string character;
	unsigned counter = 0;

	fgets(input, 100000, stdin);
	while(fgets(input, 100000, stdin))
	{
		character = string(strtok(input, " "));
		if(dict.find(character) == dict.end()) dict.insert(character);
		else std::printf("Collide : %s\n", character.c_str());
		counter++;
	}
	std::printf("#Case : %u\n#Word : %u\n", counter, dict.size());
	return 0;
}