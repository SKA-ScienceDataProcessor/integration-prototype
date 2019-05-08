cmake_minimum_required(VERSION 3.1)
project(vis_recv_c C CXX)
find_package(Threads REQUIRED)

SET(COVERAGE OFF CACHE BOOL "Coverage")

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

if (COVERAGE)
    target_compile_options(recv PRIVATE --coverage)
    target_link_libraries(recv PRIVATE --coverage)
endif()

# Build tests.
enable_testing()
add_subdirectory(test)

# Build unit testing framework.
add_subdirectory(gtest)
