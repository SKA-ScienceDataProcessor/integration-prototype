cmake_minimum_required(VERSION 2.8)

project (ValgrindExample)

# Here it is important to include the CTest module with include instead of
# just enabling tests with enable_testing(). The CTest module takes care of
# setting up the machinery for being able to run memory checks with tests
# (e.g., it locates the valgrind executable).
include (CTest)
add_executable(example main.cpp)
add_test(example_test example)