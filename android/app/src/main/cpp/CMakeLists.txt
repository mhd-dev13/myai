cmake_minimum_required(VERSION 3.10.2)

project("myai")

add_library(
        llama
        SHARED
        llama_bridge.cpp
)

find_library(log-lib log)

target_link_libraries(llama ${log-lib})
