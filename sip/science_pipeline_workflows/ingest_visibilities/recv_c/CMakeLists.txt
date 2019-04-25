cmake_minimum_required(VERSION 3.1)
project(vis_recv_c C CXX)
find_package(Threads REQUIRED)

# Code Coverage Configuration
add_library(coverage_config INTERFACE)

option(CODE_COVERAGE "Enable coverage reporting" ON)
if(CODE_COVERAGE AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  # Add required flags (GCC & LLVM/Clang)
  target_compile_options(coverage_config INTERFACE
    -O0        # no optimization
    -g         # generate debug info
    --coverage # sets all required flags
  )
  if(CMAKE_VERSION VERSION_GREATER_EQUAL 3.13)
    target_link_options(coverage_config INTERFACE --coverage)
  else()
    target_link_libraries(coverage_config INTERFACE --coverage)
  endif()
endif(CODE_COVERAGE)


# List of source files.
include_directories(src)
set(recv_SRC
    src/buffer.c
    src/receiver.c
    src/stream.c
    src/thread_barrier.c
    src/thread_pool.c
    src/timer.c
)

# Get version number from file and add to definitions for compiler.
file(STRINGS "VERSION" RECV_VERSION)
add_definitions(-DRECV_VERSION="${RECV_VERSION}")

# Build library.
add_library(vis_recv ${recv_SRC})
target_link_libraries(vis_recv Threads::Threads)

# Build executable.
add_executable(recv src/main.c)
target_link_libraries(recv vis_recv Threads::Threads)

# Build tests.
enable_testing()
add_subdirectory(test)

# Build unit testing framework.
add_subdirectory(gtest)
