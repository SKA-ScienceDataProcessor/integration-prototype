# Testing with CTest

Ctest is a testing tool distributed by CMake

There are two basic modes of operation for CTest.

In the first mode, CMake is used to configure and build a project, using
special commands in the CMakeLists.txt file to create tests. CTest can
then be used to execute the tests, and optionally upload their results
to a dashboard server. 

Performing tests on the project is a great software development practice
and can result in significant improvement on the quality of the project.
CTest provides a simple and reliable way of performing nightly,
continuous, and experimental tests.

## Example

Here is a self contained example that shows how to add valgrind tests to a 
CMake project. The example consists of a single C++ source file main.cpp:

Commands to run the example:

```bash
mkdir build && cd build 
cmake ..
make
```

To run tests with valgrind we have to use CMake's ctest executable with 
the test action memcheck:

```bash
ctest -T memcheck
```

ctest prints a summary of the memory checking results. The detailed output 
of valgrind is located in a temporary directory in the build tree ./Testing/Temporary/MemoryChecker.*.log: