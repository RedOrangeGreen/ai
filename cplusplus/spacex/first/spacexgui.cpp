/*
Application Details
-------------------
Name: SpaceX Dragon Style GUI
Objective: 'Mimic' Software Architecture Used By SpaceX Dragon
AI Chatbot (Free): https://www.perplexity.ai
Development Environment: Ubuntu 24.04.01 LTS

Specification (Ask AI Chatbot These Questions To Generate Code)
---------------------------------------------------------------
What does SpaceX Dragon use for the display GUI and code backend and what operating system does it run these components on?
Using the C++ crow framework and the crow_all.h header, show me a simple version of the SpaceX Dragon GUI with a button 'Ignition', slider 'Boosters', black background and SpaceX style font as spacexgui.cpp and spacexgui.html. Listen for connections on 127.0.0.1 port 5050. When 'Ignition' is called return a text string and display it on GUI. Maintain the value of the slider in the C++, return it and display it on the GUI for each slider move. Don't embed HTML in the C++ and don't use crow mustache templates, instead read the HTML directly from a file using a new method load_html_from_file(). 

Using The Generated Code
------------------------
Create a new directory
Download crow_all.h from https://crowcpp.org/master/
Download spacexgui.html from https://redorangegreen.github.io/ai/cplusplus/spacex/first
Check that directory contains files crow_all.h, spacexgui.cpp, spacexgui.html
sudo apt install build-essential
sudo apt install --no-install-recommends libasio-dev
g++ spacexgui.cpp -o spacexgui -lpthread
./spacexgui
To test, using any browser to open http://127.0.0.1:5050
*/
#include "crow_all.h"
#include <fstream>
#include <string>

std::string load_html_from_file(const std::string& filename) {
    std::ifstream file(filename);
    if (!file) {
        return "Error: Unable to open file";
    }
    return std::string((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
}

int main() {
    crow::SimpleApp app;
    int booster_value = 0;

    CROW_ROUTE(app, "/")([](){
        return load_html_from_file("spacexgui.html");
    });

    CROW_ROUTE(app, "/ignition").methods("POST"_method)([](const crow::request&){
        return crow::response{"Ignition sequence started!"};
    });

    CROW_ROUTE(app, "/boosters").methods("POST"_method)([&booster_value](const crow::request& req){
        auto value = req.url_params.get("value");
        if (value) {
            booster_value = std::stoi(value);
        }
        return crow::response{std::to_string(booster_value)};
    });

    app.port(5050).bindaddr("127.0.0.1").run();
    return 0;
}
