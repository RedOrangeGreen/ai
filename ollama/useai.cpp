#include <iostream>
#include <string>
#include <curl/curl.h>

// Callback function to write the response data into a string
size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

// Function to extract the "response" field from the JSON string
std::string extractResponse(const std::string& jsonLine) {
    std::string key = "\"response\":\"";
    size_t start = jsonLine.find(key);
    if (start != std::string::npos) {
        start += key.length();
        size_t end = jsonLine.find("\"", start);
        if (end != std::string::npos) {
            return jsonLine.substr(start, end - start);
        }
    }
    return "";
}

int main() {
    CURL* curl;
    CURLcode res;
    std::string readBuffer;
    std::string result;

    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl = curl_easy_init();
    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, "http://localhost:11434/api/generate");

        // Set the POST data
        std::string jsonData = R"({"model": "tinyllama", "prompt": "Why is the sky blue?"})";
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, jsonData.c_str());

        // Set the callback function to capture the response
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

        // Perform the request
        res = curl_easy_perform(curl);

        // Check for errors
        if(res != CURLE_OK) {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        } else {
            // Parse the response line by line
            size_t pos = 0;
            while ((pos = readBuffer.find("\n")) != std::string::npos) {
                std::string line = readBuffer.substr(0, pos);
                std::string response = extractResponse(line);
                if (!response.empty()) {
                    result += response;
                    std::cout << "Extracted: " << response << std::endl;
                }
                readBuffer.erase(0, pos + 1);
            }
        }

        // Clean up
        curl_easy_cleanup(curl);
    }

    curl_global_cleanup();

    // Output the final result
    std::cout << "Final Result: " << result << std::endl;

    return 0;
}
