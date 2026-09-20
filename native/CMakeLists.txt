cmake_minimum_required(VERSION 3.16)
project(gbrowser_native LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT WIN32)
    message(FATAL_ERROR "gbrowser_native currently supports Windows only")
endif()

find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(gbrowser_native
    module.cpp
    effects_win.cpp
    discord_rpc.cpp
)

target_link_libraries(gbrowser_native PRIVATE dwmapi user32 kernel32)
target_compile_definitions(gbrowser_native PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN)