cmake_minimum_required(VERSION 3.1)
project(vis_recv_c C CXX)
find_package(Threads REQUIRED)

option(COVERALLS "Turn on coveralls support" OFF)
option(COVERALLS_UPLOAD "Upload the generated coveralls json" ON)

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

find_program(CMAKE_CXX_CPPCHECK NAMES cppcheck)

if (CMAKE_CXX_CPPCHECK)
    message("-- Cppcheck found " ${CMAKE_CXX_CPPCHECK})
    list(
        APPEND CMAKE_CXX_CPPCHECK
            "--enable=warning,style,portability" 
            "--suppress=*:${PROJECT_SOURCE_DIR}/gtest*"
    )
else()
    message("-- Cppcheck not found")
    set(CMAKE_CXX_CPPCHECK "")
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
enable_testing()
add_subdirectory(test)

# Build unit testing framework.
add_subdirectory(gtest)