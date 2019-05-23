cmake_minimum_required(VERSION 3.1)
project(vis_recv_c C CXX)
find_package(Threads REQUIRED)

option(COVERALLS "Turn on coveralls support" OFF)
option(COVERALLS_UPLOAD "Upload the generated coveralls json" ON)

# Include extra CMake files that are used for testing and linting.
include(${PROJECT_SOURCE_DIR}/cmake/clang_tools.cmake)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} 
	${PROJECT_SOURCE_DIR}/coveralls-cmake/cmake)

if (COVERALLS)
	include(Coveralls)
	coveralls_turn_on_coverage()
endif()

# List of source files.
include_directories(src)
set(recv_SRC
    ${PROJECT_SOURCE_DIR}/src/buffer.c
    ${PROJECT_SOURCE_DIR}/src/receiver.c
    ${PROJECT_SOURCE_DIR}/src/stream.c
    ${PROJECT_SOURCE_DIR}/src/thread_barrier.c
    ${PROJECT_SOURCE_DIR}/src/thread_pool.c
    ${PROJECT_SOURCE_DIR}/src/timer.c
)

if (COVERALLS)
	coveralls_setup(
        "${recv_SRC}" 
        ${COVERALLS_UPLOAD}                 
        "${PROJECT_SOURCE_DIR}/coveralls-cmake/cmake")
endif()

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
include(CTest)
add_subdirectory(test)

# Build unit testing framework.
add_subdirectory(gtest)