#include <iostream>
#include <string>

int main(int arc, char ** argv)
{
    std::string s;
    std::cin >> s;
    s = s + s;
    std::cout << s << std::endl;
}
