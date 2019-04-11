include_directories(${PROJECT_SOURCE_DIR}/gtest/include)

set(name recv_test)
set(${name}_SRC Tests.cpp)

add_executable(${name} ${${name}_SRC})
target_link_libraries(${name} gtest_main vis_recv)
add_test(${name} ${name})
