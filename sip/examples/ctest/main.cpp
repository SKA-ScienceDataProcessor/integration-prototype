#include <iostream>

int main()
{
    double* leak = new double[10];
    std::cout << "Hello!" << std::endl;
}