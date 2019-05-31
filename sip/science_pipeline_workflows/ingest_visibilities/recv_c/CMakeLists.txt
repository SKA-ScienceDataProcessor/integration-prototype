cmake_minimum_required(VERSION 3.2)
project(vis_recv_c C CXX)
find_package(Threads REQUIRED)

# -----------------------------------------------------------------------------
# List of source files.
# -----------------------------------------------------------------------------

include_directories(src)
set(recv_SRC
    ${PROJECT_SOURCE_DIR}/src/buffer.c
    ${PROJECT_SOURCE_DIR}/src/receiver.c
    ${PROJECT_SOURCE_DIR}/src/stream.c
    ${PROJECT_SOURCE_DIR}/src/thread_barrier.c
    ${PROJECT_SOURCE_DIR}/src/thread_pool.c
    ${PROJECT_SOURCE_DIR}/src/timer.c
)

# -----------------------------------------------------------------------------
# Coveralls
# -----------------------------------------------------------------------------

option(COVERALLS "Turn on coveralls support" OFF)
option(COVERALLS_UPLOAD "Upload the generated coveralls json" ON)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}
	${PROJECT_SOURCE_DIR}/coveralls-cmake/cmake)

if (COVERALLS)
	include(Coveralls)
	coveralls_turn_on_coverage()
endif()

if (COVERALLS)
	coveralls_setup(
        "${recv_SRC}"
        ${COVERALLS_UPLOAD}
        "${PROJECT_SOURCE_DIR}/coveralls-cmake/cmake")
endif()

# -----------------------------------------------------------------------------
# Google Sanitizers
# -----------------------------------------------------------------------------

if(ENABLE_ASAN)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O1")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fuse-ld=gold")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-omit-frame-pointer")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=leak")
endif()

if(ENABLE_USAN)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fuse-ld=gold")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=undefined")
endif()

if(ENABLE_TSAN)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fuse-ld=gold")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=thread")
endif()

# -----------------------------------------------------------------------------
# Valgrind
# -----------------------------------------------------------------------------

include (CTest)

# -----------------------------------------------------------------------------
# Unit test
# -----------------------------------------------------------------------------

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