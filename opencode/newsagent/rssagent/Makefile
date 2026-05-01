# Simple Makefile for building rssagent
# Usage: make LLAMA_PATH=/path/to/llama.cpp/build/bin

CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall
INCLUDES = -I./src -I./deps -I./example
LDFLAGS = -lpthread -ldl

# llama.cpp library path (can be set via command line)
LLAMA_PATH ?= /usr/local/lib
LLAMA_LIBS = -L$(LLAMA_PATH) -llama -llama-common

# Source files
DEP_SOURCES = $(wildcard deps/*.cpp)
AGENT_SOURCES = src/agent.cpp src/model.cpp
EXAMPLE_SOURCE = example/rssagent.cpp

# Object files
DEP_OBJS = $(DEP_SOURCES:.cpp=.o)
AGENT_OBJS = $(AGENT_SOURCES:.cpp=.o)
EXAMPLE_OBJ = $(EXAMPLE_SOURCE:.cpp=.o)

# Targets
all: rssagent

# Build rssagent executable
rssagent: $(DEP_OBJS) $(AGENT_OBJS) $(EXAMPLE_OBJ)
	$(CXX) -o $@ $^ $(LLAMA_LIBS) $(LDFLAGS)

# Compile dependency objects
deps/%.o: deps/%.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c -o $@ $<

# Compile agent objects
src/%.o: src/%.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c -o $@ $<

# Compile example object
example/%.o: example/%.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c -o $@ $<

# Clean build files
clean:
	rm -f $(DEP_OBJS) $(AGENT_OBJS) $(EXAMPLE_OBJ) rssagent

# Install
install: rssagent
	cp rssagent /usr/local/bin/
	cp example/fetch_news.py /usr/local/share/rssagent/

.PHONY: all clean install

# Print help
help:
	@echo "RSS Agent Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  all (default)  - Build rssagent"
	@echo "  clean          - Remove build files"
	@echo "  install        - Install to /usr/local"
	@echo ""
	@echo "Variables:"
	@echo "  LLAMA_PATH     - Path to llama.cpp libraries (default: /usr/local/lib)"
	@echo ""
	@echo "Example:"
	@echo "  make LLAMA_PATH=/home/user/llama.cpp/build/bin"
