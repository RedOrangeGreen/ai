/*
Description:
AIWomen Agent
A C++ web server built using the Crow framework, which calls the Ollama AI REST interface (loaded with the 'revolutionary tiny, fast and free' Meta Llama 3.2 1B model) to perform AI 'personality' lookup queries on three fictitious AI women.

Development And Testing:
Ubuntu Linux 24.04.1 LTS
Pilot: AI Playground (Quasimodo), https://redorangegreen.github.io/ai
Copilot: Perplexity AI Free, https://www.perplexity.ai
*/

#include "crow.h"
#include <fstream>
#include <string>
#include <string_view>
#include <curl/curl.h>
#include <unordered_map>
#include <memory>
#include <optional>
#include <array>
#include <algorithm>

constexpr std::string_view API_URL = "http://localhost:11434/api/generate";
constexpr std::string_view MODEL_NAME = "llama3.2:1b";
constexpr int LISTEN_PORT = 18080;

[[nodiscard]] std::string get_mime_type(std::string_view path) noexcept;
[[nodiscard]] std::unique_ptr<CURL, decltype(&curl_easy_cleanup)> curlinit();
static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) noexcept;
[[nodiscard]] std::optional<std::string> extractResponse(std::string_view jsonLine) noexcept;
[[nodiscard]] std::string curlcall(CURL *curl, const std::string& jsonData);
[[nodiscard]] std::string handleProfileRequest(CURL *curl, const crow::request& req, std::string_view name);
[[nodiscard]] std::string getCustomPrompt(const crow::request& req, std::string_view defaultPrompt);
[[nodiscard]] std::string createJsonData(std::string_view prompt);

struct Female {
    int id;
    std::string name;
    int age;
    std::string nationality;
};

int main() {
    crow::SimpleApp app;
    auto curl = curlinit();
   
    // Serve static files from the 'public' directory
    CROW_ROUTE(app, "/public/<path>")
    ([](const crow::request& req, crow::response& res, std::string path) {
        (void)req;
        std::ifstream file("public/" + path, std::ios::binary);
        if (file) {
            std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
            res.write(content);
            res.set_header("Content-Type", get_mime_type(path));
        } else {
            res.code = 404;
            res.write("File not found");
        }
        res.end();
    });

    // Serve the main HTML page
    CROW_ROUTE(app, "/")
    ([]() {
        std::ifstream file("templates/index.html");
        if (file) {
            return crow::response(std::string((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>()));
        } else {
            return crow::response(404, "File not found");
        }
    });

    // Routes which interact with Ollama AI 
    CROW_ROUTE(app, "/profile/<string>")
    .methods(crow::HTTPMethod::GET, crow::HTTPMethod::POST)
    ([&curl](const crow::request& req, const std::string& name) {    
        return handleProfileRequest(curl.get(), req, name);
    });

    app.port(LISTEN_PORT).multithreaded().run();
    return 0;
}

constexpr std::array<std::pair<const char*, const char*>, 9> mime_types {{
    {".html", "text/html"},
    {".css", "text/css"},
    {".js", "application/javascript"},
    {".json", "application/json"},
    {".png", "image/png"},
    {".jpg", "image/jpeg"},
    {".gif", "image/gif"},
    {".svg", "image/svg+xml"},
    {".ico", "image/x-icon"}
}};

std::string get_mime_type(std::string_view path) noexcept {
    auto dot_pos = path.find_last_of('.');
    if (dot_pos != std::string_view::npos) {
        std::string_view ext = path.substr(dot_pos);
        auto it = std::find_if(mime_types.begin(), mime_types.end(),
            [ext](const auto& pair) { return ext == pair.first; });
        if (it != mime_types.end()) {
            return it->second;
        }
    }
    return "application/octet-stream";
}
  
std::unique_ptr<CURL, decltype(&curl_easy_cleanup)> curlinit() {
    curl_global_init(CURL_GLOBAL_DEFAULT);
    std::unique_ptr<CURL, decltype(&curl_easy_cleanup)> curl(curl_easy_init(), curl_easy_cleanup);
    if (curl) {
        curl_easy_setopt(curl.get(), CURLOPT_URL, API_URL.data());
        curl_easy_setopt(curl.get(), CURLOPT_WRITEFUNCTION, WriteCallback);
    }
    return curl;
}

static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) noexcept {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

std::optional<std::string> extractResponse(std::string_view jsonLine) noexcept {
    constexpr std::string_view response_key = "\"response\":\"";
    size_t start = jsonLine.find(response_key);
    if (start != std::string_view::npos) {
        start += response_key.length();
        size_t end = jsonLine.find("\"", start);
        if (end != std::string_view::npos) {
            return std::string(jsonLine.substr(start, end - start));
        }
    }
    return std::nullopt;
}
    
std::string curlcall(CURL *curl, const std::string& jsonData) {
    std::string readBuffer;
    std::string result;

    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, jsonData.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

    CURLcode res = curl_easy_perform(curl);

    if (res != CURLE_OK) {
        std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << "\n";
    } else {
        size_t pos = 0;
        while ((pos = readBuffer.find("\n")) != std::string::npos) {
            std::string_view line(readBuffer.data(), pos);
            if (auto response = extractResponse(line)) {
                result += *response;
            }
            readBuffer.erase(0, pos + 1);
        }
    }
    return result;
}

std::string handleProfileRequest(CURL *curl, const crow::request& req, std::string_view name) {
    static const std::vector<Female> females = {
        {1, "colette", 22, "French"},
        {2, "gloria", 24, "Italian"},
        {3, "annika", 21, "Danish"}
    };

    auto it = std::find_if(females.begin(), females.end(),
                           [name](const Female& f) { return f.name == name; });
    if (it != females.end()) {
        const auto& [id, _, age, nationality] = *it;
        std::string result;

        if (curl) {
            // Translate "Hello!" to nationality language using Ollama AI
            auto aiRequest = createJsonData(getCustomPrompt(req, "Translate the word Hello! to " + nationality + ", only use one word in the translation answer."));
            std::string aiHello = curlcall(curl, aiRequest);
          
            // Get some details of a typical woman of the nationality using Ollama AI
            aiRequest = createJsonData(getCustomPrompt(req, "Write a 10 word first person profile listing favourite hobbies and interests for an attractive female fashion model aged " + std::to_string(age) + " from " + nationality));
            std::string aiHobbies = curlcall(curl, aiRequest);

            result = nationality + ", " + std::to_string(age) + ". " + aiHello + " " + aiHobbies;
        }

        return result;
    }
    return "Sorry, name not supported!";
}

std::string getCustomPrompt(const crow::request& req, std::string_view defaultPrompt) {
    if (req.method == crow::HTTPMethod::POST) {
        auto& params = req.url_params;
        auto custom_prompt = params.get("prompt");
        if (custom_prompt) {
            return std::string(custom_prompt);
        }
    }
    return std::string(defaultPrompt);
}

std::string createJsonData(std::string_view prompt) {
    return "{\"model\":\"" + std::string(MODEL_NAME) + "\",\"prompt\":\"" + std::string(prompt) + "\"}";
}
