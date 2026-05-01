cmake_minimum_required(VERSION 3.10)
project(rssagent CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(Threads REQUIRED)

# Add include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/deps)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/example)

# Build dependencies from deps folder
set(DEP_SOURCES
    deps/chat.cpp
    deps/chat-peg-parser.cpp
    deps/chat-auto-parser-generator.cpp
    deps/chat-auto-parser-helpers.cpp
    deps/chat-diff-analyzer.cpp
    deps/common.cpp
    deps/console.cpp
    deps/debug.cpp
    deps/arg.cpp
)

add_library(rssagent_deps STATIC ${DEP_SOURCES})

# Source files for rssagent library
set(AGENT_SOURCES
    src/agent.cpp
    src/model.cpp
)

add_library(rssagent_lib STATIC ${AGENT_SOURCES})
target_link_libraries(rssagent_lib rssagent_deps)

# Build the rssagent executable
add_executable(rssagent example/rssagent.cpp)
target_link_libraries(rssagent rssagent_lib ${CMAKE_THREAD_LIBS_INIT} ${CMAKE_DL_LIBS})

# On the new machine, you need to:
# 1. Have llama.cpp built and libraries available
# 2. Set LLAMA_LIB_PATH to point to llama libraries
# 3. Or install llama.cpp system-wide

# Try to find llama libraries
if(NOT DEFINED LLAMA_LIB_PATH)
    # Try common locations
    find_library(LLAMA_LIB llama PATHS 
        ../llama.cpp-master/build/bin
        ../llama.cpp/build/bin
        /usr/local/lib
        /usr/lib
        DOC "Path to llama library"
    )
    find_library(LLAMA_COMMON_LIB llama-common PATHS 
        ../llama.cpp-master/build/bin
        ../llama.cpp/build/bin
        /usr/local/lib
        /usr/lib
        DOC "Path to llama-common library"
    )
else()
    find_library(LLAMA_LIB llama PATHS ${LLAMA_LIB_PATH})
    find_library(LLAMA_COMMON_LIB llama-common PATHS ${LLAMA_LIB_PATH})
endif()

if(LLAMA_LIB AND LLAMA_COMMON_LIB)
    message(STATUS "Found llama: ${LLAMA_LIB}")
    message(STATUS "Found llama-common: ${LLAMA_COMMON_LIB}")
    target_link_libraries(rssagent_lib ${LLAMA_LIB} ${LLAMA_COMMON_LIB})
else()
    message(WARNING "llama libraries not found. You may need to set LLAMA_LIB_PATH or build llama.cpp first.")
    message(STATUS "Expected libraries: libllama.so, libllama-common.so")
endif()

# Install target
install(TARGETS rssagent DESTINATION bin)
install(FILES example/fetch_news.py DESTINATION share/rssagent)

message(STATUS "")
message(STATUS "Build instructions:")
message(STATUS "  1. Build llama.cpp first: https://github.com/ggml-org/llama.cpp")
message(STATUS "  2. cmake -B build -DLLAMA_LIB_PATH=/path/to/llama/build/bin")
message(STATUS "  3. cmake --build build -j$(nproc)")
message(STATUS "")
