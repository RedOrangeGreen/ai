# RSS Agent

A self-contained news headline fetcher using LLM (Large Language Model) with tool calling.

## Overview

This agent fetches 5 current international news headlines from BBC World News RSS feed and displays them using a locally-running Gemma 4 LLM. It runs forever with 2-second delays between each news fetch.

## Directory Structure

```
rssagent/
├── CMakeLists.txt          # CMake build file
├── README.md              # This file
├── rssagent.html         # Documentation (generated separately)
├── src/                  # Core agent.cpp source files
│   ├── agent.cpp
│   ├── agent.h
│   ├── callbacks.h
│   ├── error.h
│   ├── model.cpp
│   ├── model.h
│   ├── tool.h
│   └── tool_result.h
├── deps/                 # Dependencies (llama.cpp common)
│   ├── chat.h
│   ├── chat.cpp
│   ├── chat-peg-parser.h
│   ├── chat-peg-parser.cpp
│   └── ... (other common files)
└── example/              # Example application
    ├── rssagent.cpp     # Main rssagent code
    └── fetch_news.py    # Python script to fetch BBC RSS feed
```

## Prerequisites

On the new machine, you need:

1. **Build tools**: cmake, g++, make, git
2. **llama.cpp**: Built from https://github.com/ggml-org/llama.cpp
3. **Python 3**: For RSS feed parsing (urllib, xml.etree)
4. **Gemma 4 GGUF model**: Download from https://huggingface.co/ggml-org/gemma-4-E4B-it-GGUF

## Building on New Machine

### Step 1: Build llama.cpp

```bash
git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -j$(nproc)
```

This will create `build/bin/libllama.so` and `build/bin/libllama-common.so`.

### Step 2: Build rssagent

Option A: If llama.cpp is in ../llama.cpp-master relative to rssagent:

```bash
cd rssagent
mkdir build && cd build
cmake ..
make -j$(nproc)
```

Option B: Specify llama.cpp path:

```bash
cd rssagent
mkdir build && cd build
cmake -DLLAMA_LIB_PATH=/path/to/llama.cpp/build/bin ..
make -j$(nproc)
```

Option C: Install llama.cpp system-wide first, then build rssagent:

```bash
# Install llama.cpp
cd llama.cpp
cmake -B build -DCMAKE_INSTALL_PREFIX=/usr/local
cd build
make install

# Build rssagent
cd ../rssagent
mkdir build && cd build
cmake ..
make -j$(nproc)
```

## Running

```bash
./rssagent /path/to/gemma-4-E4B-it-Q4_K_M.gguf
```

The agent will:
- Fetch 5 current international news headlines from BBC News
- Display them as readable text
- Wait 2 seconds
- Repeat forever (press Ctrl+C to stop)

## Expected Output

```
=== News Agent - Getting Headlines Forever ===
Press Ctrl+C to stop

--- News Check #1 ---
Response: The 5 current international news headlines are:
1. Myanmar ex-leader Aung San Suu Kyi moved to house arrest
2. Oil price hits highest since 2022
3. Islamist group tightens blockade on Mali capital
4. Israel intercepts Gaza flotilla near Crete
5. US House votes to end government shutdown
Waiting 2 seconds...

--- News Check #2 ---
...
```

## Files Requiring Modification

To modify or extend the agent:

1. **example/rssagent.cpp** - Main application logic
   - Change news source by modifying `fetch_news.py`
   - Adjust delay timing (line with `std::this_thread::sleep_for`)
   - Change prompt to fetch different types of news

2. **example/fetch_news.py** - RSS feed parser
   - Change RSS feed URL for different news source
   - Modify parsing logic for different XML formats

3. **src/model.cpp** - Model interaction
   - Modify `generate()` for different response parsing
   - Adjust model parameters (temperature, top_p, etc.)

4. **src/agent.cpp** - Agent loop logic
   - Modify tool call handling
   - Change how tool results are processed

## Dependencies

- **llama.cpp**: LLM inference engine (https://github.com/ggml-org/llama.cpp)
- **Gemma 4 E4B**: LLM model (https://ai.google.dev/gemma)
- **Python 3**: For RSS parsing with urllib and xml.etree

## License

This project uses code from:
- agent.cpp (Mozilla) - Check original repo for license
- llama.cpp (ggml-org) - MIT License
- Gemma 4 (Google) - Apache 2.0 License
