#include "agent.h"
#include "callbacks.h"
#include "chat.h"
#include "error.h"
#include "model.h"
#include "tool.h"
#include <iostream>
#include <string>
#include <thread>
#include <chrono>
#include <cstdio>
#include <sstream>

// Tool to get 5 current international news headlines from RSS feed
class NewsTool : public agent_cpp::Tool {
public:
    common_chat_tool get_definition() const override {
        json schema = {
            {"type", "object"},
            {"properties", json::object()},
            {"required", json::array()}
        };

        return {
            "get_news",
            "Get 5 current international news headlines from BBC World News RSS feed. Returns headlines as readable text.",
            schema.dump()
        };
    }

    std::string get_name() const override { return "get_news"; }

    std::string execute(const agent_cpp::json& ) override {
        // Call Python script to fetch and parse RSS feed
        std::string script_path = "/home/ubuntu/Downloads/agent.cpp-main/examples/price-agent/fetch_news.py";
        std::string cmd = "python3 " + script_path + " 2>/dev/null";

        std::string result;
        char buffer[512];

        FILE* pipe = popen(cmd.c_str(), "r");
        if (!pipe) {
            json error;
            error["error"] = "Failed to fetch news headlines";
            return error.dump();
        }

        while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
            result += buffer;
        }
        int status = pclose(pipe);

        if (status != 0 || result.empty()) {
            json error;
            error["error"] = "Failed to fetch or parse RSS feed";
            return error.dump();
        }

        // Parse headlines
        json output;
        output["source"] = "BBC World News RSS";

        // Get current timestamp
        auto now = std::chrono::system_clock::now();
        time_t tt = std::chrono::system_clock::to_time_t(now);
        output["timestamp"] = std::string(ctime(&tt)).substr(0, 24);

        // Format headlines
        std::stringstream ss(result);
        std::string headline;
        json headlines = json::array();

        while (std::getline(ss, headline)) {
            // Trim whitespace
            headline.erase(0, headline.find_first_not_of(" \t\n\r"));
            headline.erase(headline.find_last_not_of(" \t\n\r") + 1);
            if (!headline.empty()) {
                headlines.push_back(headline);
            }
        }

        output["headlines"] = headlines;
        output["count"] = headlines.size();

        return output.dump();
    }
};

int main(int argc, char** argv) {
    if (argc < 2) {
        printf("Usage: %s <model_path>\n", argv[0]);
        return 1;
    }

    try {
        std::string model_path = argv[1];

        // Initialize model once
        agent_cpp::ModelConfig config;
        config.n_ctx = 2048;
        config.n_batch = 512;
        config.temp = 0.7;
        config.top_p = 0.9;
        config.top_k = 40;

        auto model = agent_cpp::Model::create(model_path, config);

        std::cout << "=== News Agent - Getting Headlines Forever ===" << std::endl;
        std::cout << "Press Ctrl+C to stop" << std::endl;

        int iteration = 0;
        while (true) {
            iteration++;
            std::cout << std::endl << "--- News Check #" << iteration << " ---" << std::endl;

            // Create tools for this iteration
            std::vector<std::unique_ptr<agent_cpp::Tool>> tools;
            tools.push_back(std::make_unique<NewsTool>());

            // Create agent
            auto agent = agent_cpp::Agent(model, std::move(tools));

            std::string prompt = "Please get 5 current international news headlines and display them as readable text.";

            // Create messages vector
            std::vector<common_chat_msg> messages;
            messages.push_back({"user", prompt, {}, {}, {}});

            // Run the agent loop
            std::string response = agent.run_loop(messages, nullptr);

            std::cout << "Response: " << response << std::endl;

            // Wait 2 seconds between news grabs
            std::cout << "Waiting 2 seconds..." << std::endl;
            model->reset();
            std::this_thread::sleep_for(std::chrono::seconds(2));
        }

        std::cout << std::endl << "=== Done ===" << std::endl;

    } catch (const agent_cpp::ModelError& e) {
        fprintf(stderr, "Model error: %s\n", e.what());
        return 1;
    } catch (const std::exception& e) {
        fprintf(stderr, "Error: %s\n", e.what());
        return 1;
    }

    return 0;
}
