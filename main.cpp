#include <iostream>
#include <stdlib.h>

using namespace std;

int main(int argc, char** argv)
{
    if(argc != 4)
         throw runtime_error("pls use ./crf_cws.out model input output");
    string model_file = argv[1];
    string input_file = argv[2];
    string output_file = argv[3];
    string res;
    
    res = "python crf_cws.py " + model_file + " " + input_file + " " + output_file;
    system(res.c_str());
    return 0;
}