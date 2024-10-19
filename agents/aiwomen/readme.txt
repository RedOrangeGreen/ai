Development And Testing:
Platform: Ubuntu Linux 24.04.1 LTS
Pilot: AI Playground (Quasimodo), https://redorangegreen.github.io/ai
Copilot: Perplexity AI Free, https://www.perplexity.ai

Project Structure:
project_root/
├── public/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── templates/
│   └── index.html
├── crow.h
├── main.cpp
├── Makefile
└── ollama.sh

crow.h is Version 1.2.0 downloaded as crow_all.h from https://github.com/CrowCpp/Crow/releases/tag/v1.2.0

Install And Run Ollama AI (Homepage https://ollama.com) In Terminal1:
chmod +x ./ollama.sh
./ollama.sh
1. Install Ollama
2. Chat with Ollama

Build And Run Agent In Terminal2 And Use Agent In Browser:
sudo apt install build-essential
sudo apt install --no-install-recommends libasio-dev
make
./aiwomen
http://127.0.0.1:18080
