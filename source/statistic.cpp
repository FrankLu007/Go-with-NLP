#include <iostream>
#include <fstream>
#include <cstring>
double loss_sum[1000], acc_sum[1000];
int main(int argc, char ** argv)
{
	int count = 0;
	double loss, acc;
	std::memset(loss_sum, 0, sizeof(loss_sum));
	std::memset(acc_sum, 0, sizeof(acc_sum));
	std::ifstream fin(argc > 1 ? argv[1] : "record.txt");
	while(fin >> loss >> acc)
	{
		loss_sum[count/100] += loss;
		acc_sum[count/100] += acc;
		count++;
	}
	for(int i = 0 ; i < 60 ; i++)
		std::printf("%.4lf\t\t\t%.2lf%\n", loss_sum[i]/100.0, acc_sum[i]);
	return 0;
}