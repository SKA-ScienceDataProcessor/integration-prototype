cmake_minimum_required(VERSION 3.1)

# CMake files in this project can refer to the root source directory
# as ${gtest_SOURCE_DIR} and to the root binary directory as
# ${gtest_BINARY_DIR}.
cmake_policy(SET CMP0048 NEW)
project(gtest CXX C)

if (POLICY CMP0063) # Visibility
  cmake_policy(SET CMP0063 NEW)
endif (POLICY CMP0063)

include(cmake/internal_utils.cmake)
config_compiler_and_linker()

# Where Google Test's .h files can be found.
include_directories("${gtest_SOURCE_DIR}/include" "${gtest_SOURCE_DIR}")

cxx_library(gtest "${cxx_strict}" src/gtest-all.cc)
cxx_library(gtest_main "${cxx_strict}" src/gtest_main.cc)
target_link_libraries(gtest_main PUBLIC gtest)
